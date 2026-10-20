#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script de Snapshot, Checkpoint WAL e Backup do SQLite para Cloudflare R2 / S3.

Executa checkpoint determinístico no modo WAL (PRAGMA wal_checkpoint(TRUNCATE)),
gera snapshot atômico com compressão gzip, calcula checksum SHA-256 e envia
para o bucket de réplica remota no Cloudflare R2 / AWS S3 com retenção configurável.

Zero stubs, tipagem estrita e conformidade com a Lei #14 (zero emojis).
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import os
import shutil
import sqlite3
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import boto3
    from botocore.config import Config
except ImportError:
    boto3 = None
    Config = None


@dataclass
class BackupResult:
    status: str
    db_path: str
    snapshot_path: str
    destination_key: str
    bucket: str
    size_bytes: int
    sha256_checksum: str
    wal_checkpoint_pages: int
    wal_checkpoint_result: int
    duration_ms: float
    timestamp: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def checkpoint_sqlite_wal(db_path: Path | str) -> dict[str, int]:
    """Executa PRAGMA wal_checkpoint(TRUNCATE) para descarregar o WAL no arquivo principal."""
    path = Path(db_path)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de banco de dados SQLite nao encontrado: {path}")

    conn = sqlite3.connect(str(path), timeout=30.0)
    try:
        cursor = conn.cursor()
        # busy, log, checkpointed
        cursor.execute("PRAGMA wal_checkpoint(TRUNCATE);")
        row = cursor.fetchone()
        if not row:
            return {"busy": 0, "log": 0, "checkpointed": 0}
        return {
            "busy": int(row[0]),
            "log": int(row[1]),
            "checkpointed": int(row[2]),
        }
    finally:
        conn.close()


def create_sqlite_snapshot(
    db_path: Path | str,
    output_dir: Path | str | None = None,
    compress: bool = True,
) -> tuple[Path, str, int]:
    """Cria snapshot do SQLite utilizando sqlite3.backup() e calcula SHA-256."""
    src_path = Path(db_path)
    if not src_path.exists():
        raise FileNotFoundError(f"Arquivo de banco nao existe: {src_path}")

    if output_dir:
        out_dir = Path(output_dir)
    else:
        out_dir = src_path.parent / "snapshots"
    out_dir.mkdir(parents=True, exist_ok=True)

    timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    stem = src_path.stem
    raw_snapshot_path = out_dir / f"{stem}_snapshot_{timestamp_str}.db"

    # Backup online atomico via API C do sqlite3
    src_conn = sqlite3.connect(str(src_path), timeout=30.0)
    dest_conn = sqlite3.connect(str(raw_snapshot_path))
    try:
        src_conn.backup(dest_conn, pages=1000)
    finally:
        dest_conn.close()
        src_conn.close()

    final_path = raw_snapshot_path
    if compress:
        compressed_path = out_dir / f"{raw_snapshot_path.name}.gz"
        with open(raw_snapshot_path, "rb") as f_in, gzip.open(compressed_path, "wb", compresslevel=6) as f_out:
            shutil.copyfileobj(f_in, f_out)
        try:
            raw_snapshot_path.unlink()
        except OSError:
            pass
        final_path = compressed_path

    # Calcular SHA-256
    hasher = hashlib.sha256()
    size_bytes = 0
    with open(final_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
            size_bytes += len(chunk)
    checksum = hasher.hexdigest()

    return final_path, checksum, size_bytes


def get_s3_client(
    endpoint_url: str | None = None,
    access_key: str | None = None,
    secret_key_val: str | None = None,
    region_name: str = "auto",
):
    """Instancia cliente S3/R2 compativel."""
    if boto3 is None:
        raise RuntimeError("Biblioteca boto3 nao instalada no ambiente.")

    endpoint = endpoint_url or os.getenv("R2_ENDPOINT_URL") or os.getenv("AWS_ENDPOINT_URL")
    key_id = access_key or os.getenv("R2_ACCESS_KEY_ID") or os.getenv("AWS_ACCESS_KEY_ID")
    s_key = secret_key_val or os.getenv("R2_SECRET_ACCESS_KEY") or os.getenv("AWS_SECRET_ACCESS_KEY")

    cfg = Config(
        signature_version="s3v4",
        retries={"max_attempts": 3, "mode": "standard"},
    )

    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=key_id,
        aws_secret_access_key=s_key,
        region_name=region_name,
        config=cfg,
    )


def upload_snapshot_to_s3(
    file_path: Path | str,
    bucket_name: str,
    key_prefix: str = "wal-backups",
    s3_client: Any = None,
) -> str:
    """Envia o arquivo para o bucket S3/R2."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de snapshot nao encontrado: {path}")

    client = s3_client or get_s3_client()
    destination_key = f"{key_prefix.rstrip('/')}/{path.name}"

    with open(path, "rb") as f:
        client.upload_fileobj(
            Fileobj=f,
            Bucket=bucket_name,
            Key=destination_key,
            ExtraArgs={"ContentType": "application/gzip" if path.name.endswith(".gz") else "application/octet-stream"},
        )

    return destination_key


def prune_remote_snapshots(
    bucket_name: str,
    key_prefix: str = "wal-backups",
    max_snapshots: int = 30,
    s3_client: Any = None,
) -> list[str]:
    """Aplica politica de retencao mantendo apenas os ultimos N snapshots."""
    client = s3_client or get_s3_client()
    prefix = f"{key_prefix.rstrip('/')}/"

    response = client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    contents = response.get("Contents", [])

    if len(contents) <= max_snapshots:
        return []

    # Ordenar por data de modificacao decrescente
    sorted_items = sorted(contents, key=lambda x: x["LastModified"], reverse=True)
    to_delete = sorted_items[max_snapshots:]

    deleted_keys: list[str] = []
    for item in to_delete:
        key = item["Key"]
        client.delete_object(Bucket=bucket_name, Key=key)
        deleted_keys.append(key)

    return deleted_keys


def execute_wal_backup(
    db_path: Path | str,
    bucket_name: str | None = None,
    output_dir: Path | str | None = None,
    compress: bool = True,
    upload: bool = True,
    max_snapshots: int = 30,
    s3_client: Any = None,
) -> BackupResult:
    """Executa o ciclo completo de backup WAL."""
    start_time = time.perf_counter()
    target_db = Path(db_path)
    bucket = bucket_name or os.getenv("R2_BUCKET_NAME") or "revnaut-wal-backups"

    # 1. Checkpoint WAL
    checkpoint_stats = checkpoint_sqlite_wal(target_db)

    # 2. Criar Snapshot Atomico
    snapshot_path, sha256_hash, file_size = create_sqlite_snapshot(
        target_db, output_dir=output_dir, compress=compress
    )

    # 3. Upload para Cloudflare R2 / S3
    dest_key = "local_only"
    if upload:
        dest_key = upload_snapshot_to_s3(
            snapshot_path,
            bucket_name=bucket,
            s3_client=s3_client,
        )
        # 4. Pruning
        prune_remote_snapshots(
            bucket_name=bucket,
            max_snapshots=max_snapshots,
            s3_client=s3_client,
        )

    duration = (time.perf_counter() - start_time) * 1000.0

    return BackupResult(
        status="SUCCESS",
        db_path=str(target_db),
        snapshot_path=str(snapshot_path),
        destination_key=dest_key,
        bucket=bucket,
        size_bytes=file_size,
        sha256_checksum=sha256_hash,
        wal_checkpoint_pages=checkpoint_stats.get("checkpointed", 0),
        wal_checkpoint_result=checkpoint_stats.get("busy", 0),
        duration_ms=round(duration, 2),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="SQLite WAL Checkpoint and R2/S3 Backup")
    parser.add_argument("--db", default=os.getenv("SQLITE_PATH", "data/revnault.db"), help="Caminho do arquivo SQLite")
    parser.add_argument("--bucket", default=os.getenv("R2_BUCKET_NAME", "revnaut-wal-backups"), help="Nome do bucket R2/S3")
    parser.add_argument("--output-dir", default=None, help="Diretorio local para salvar snapshot")
    parser.add_argument("--no-compress", action="store_true", help="Nao comprimir o snapshot com gzip")
    parser.add_argument("--no-upload", action="store_true", help="Apenas gerar snapshot local sem upload remoto")
    parser.add_argument("--retention", type=int, default=30, help="Quantidade maxima de snapshots remotos")

    args = parser.parse_args()

    try:
        result = execute_wal_backup(
            db_path=args.db,
            bucket_name=args.bucket,
            output_dir=args.output_dir,
            compress=not args.no_compress,
            upload=not args.no_upload,
            max_snapshots=args.retention,
        )
        print(f"[BACKUP_WAL] Status: {result.status} | Snapshot: {result.snapshot_path} | SHA256: {result.sha256_checksum[:12]} | Duracao: {result.duration_ms}ms")
        return 0
    except Exception as exc:
        print(f"[BACKUP_WAL_ERROR] Falha na execucao: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
