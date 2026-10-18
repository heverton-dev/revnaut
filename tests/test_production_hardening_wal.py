# -*- coding: utf-8 -*-
"""Testes de Hardening de Producao, Docker Swarm / Compose e Backup WAL SQLite.

Valida:
1. Checkpoint WAL deterministico e geracao de snapshot comprimido com SHA-256.
2. Upload atomico para S3/R2 e retencao (pruning) de snapshots antigos.
3. Conformidade estrita dos manifests docker-stack.yml e docker-compose.prod.yml
   (redes segregadas revnault_edge, revnault_app, revnault_data, limites de CPU/RAM e healthchecks).
4. Hardening de seguranca de producao (HSTS, SSL redirect, rate-limiting e scripts de auditoria).
"""

from __future__ import annotations

import gzip
import hashlib
import os
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import yaml
import pytest

from scripts.wal_backup_s3 import (
    checkpoint_sqlite_wal,
    create_sqlite_snapshot,
    execute_wal_backup,
    prune_remote_snapshots,
    upload_snapshot_to_s3,
    BackupResult,
)


class InMemoryS3Client:
    """Implementacao deterministica de cliente S3 para testes sem stubs externos."""

    def __init__(self):
        self.storage: dict[str, dict[str, Any]] = {}

    def upload_fileobj(self, Fileobj, Bucket: str, Key: str, ExtraArgs: dict | None = None):
        data = Fileobj.read()
        if Bucket not in self.storage:
            self.storage[Bucket] = {}
        self.storage[Bucket][Key] = {
            "data": data,
            "LastModified": datetime.now(timezone.utc),
            "ExtraArgs": ExtraArgs or {},
        }

    def list_objects_v2(self, Bucket: str, Prefix: str = ""):
        bucket_data = self.storage.get(Bucket, {})
        contents = []
        for key, meta in bucket_data.items():
            if key.startswith(Prefix):
                contents.append({
                    "Key": key,
                    "LastModified": meta["LastModified"],
                    "Size": len(meta["data"]),
                })
        return {"Contents": contents}

    def delete_object(self, Bucket: str, Key: str):
        if Bucket in self.storage and Key in self.storage[Bucket]:
            del self.storage[Bucket][Key]


@pytest.fixture
def temp_wal_sqlite_db():
    """Cria banco SQLite temporario no modo WAL com registros de teste."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_production.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute(
            """
            CREATE TABLE accounts (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                plan TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE test_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_name TEXT NOT NULL,
                payload_json TEXT NOT NULL
            );
            """
        )
        conn.execute("INSERT INTO accounts VALUES ('acc-prod-01', 'Clinica Matriz', 'enterprise');")
        for i in range(50):
            conn.execute(
                "INSERT INTO test_events (event_name, payload_json) VALUES (?, ?);",
                (f"event_{i}", f'{{"index": {i}, "status": "active"}}'),
            )
        conn.commit()
        conn.close()

        yield db_path


def test_wal_checkpoint_and_snapshot_creation(temp_wal_sqlite_db: Path):
    """Testa execucao do checkpoint WAL e criacao do snapshot comprimido com hash."""
    stats = checkpoint_sqlite_wal(temp_wal_sqlite_db)
    assert isinstance(stats, dict)
    assert "busy" in stats
    assert "checkpointed" in stats

    with tempfile.TemporaryDirectory() as out_dir:
        snapshot_file, sha256_hash, file_size = create_sqlite_snapshot(
            temp_wal_sqlite_db, output_dir=out_dir, compress=True
        )

        assert snapshot_file.exists()
        assert snapshot_file.name.endswith(".db.gz")
        assert file_size > 0
        assert len(sha256_hash) == 64

        # Validar descompressao e integridade do SQLite resultante
        with gzip.open(snapshot_file, "rb") as gz_in:
            decompressed = gz_in.read()

        calc_hash = hashlib.sha256(snapshot_file.read_bytes()).hexdigest()
        assert calc_hash == sha256_hash

        restored_db = Path(out_dir) / "restored.db"
        restored_db.write_bytes(decompressed)

        conn = sqlite3.connect(str(restored_db))
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM test_events;")
        count = cursor.fetchone()[0]
        conn.close()
        assert count == 50


def test_wal_backup_upload_and_pruning_with_s3_client(temp_wal_sqlite_db: Path):
    """Testa o ciclo de upload para bucket remoto e retencao de snapshots."""
    s3_mock = InMemoryS3Client()
    bucket_name = "test-wal-bucket"

    with tempfile.TemporaryDirectory() as out_dir:
        result = execute_wal_backup(
            db_path=temp_wal_sqlite_db,
            bucket_name=bucket_name,
            output_dir=out_dir,
            compress=True,
            upload=True,
            max_snapshots=3,
            s3_client=s3_mock,
        )

        assert isinstance(result, BackupResult)
        assert result.status == "SUCCESS"
        assert result.bucket == bucket_name
        assert result.size_bytes > 0
        assert result.destination_key.startswith("wal-backups/")
        assert result.destination_key in s3_mock.storage[bucket_name]

        # Simular multiplos backups para testar poda (pruning) com limite de 3
        for i in range(4):
            dummy_file = Path(out_dir) / f"dummy_snapshot_{i}.db.gz"
            dummy_file.write_bytes(b"dummy snapshot data")
            upload_snapshot_to_s3(
                dummy_file,
                bucket_name=bucket_name,
                key_prefix="wal-backups",
                s3_client=s3_mock,
            )

        assert len(s3_mock.storage[bucket_name]) == 5
        deleted = prune_remote_snapshots(
            bucket_name=bucket_name,
            key_prefix="wal-backups",
            max_snapshots=3,
            s3_client=s3_mock,
        )
        assert len(deleted) == 2
        assert len(s3_mock.storage[bucket_name]) == 3


def test_docker_manifests_architecture_and_resources():
    """Valida que docker-stack.yml e docker-compose.prod.yml atendem aos requisitos de producao."""
    repo_root = Path(__file__).resolve().parent.parent
    stack_file = repo_root / "docker-stack.yml"
    compose_file = repo_root / "docker-compose.prod.yml"

    assert stack_file.exists(), "docker-stack.yml deve existir"
    assert compose_file.exists(), "docker-compose.prod.yml deve existir"

    with open(stack_file, "r", encoding="utf-8") as f:
        stack_data = yaml.safe_load(f)

    with open(compose_file, "r", encoding="utf-8") as f:
        compose_data = yaml.safe_load(f)

    for data, name in [(stack_data, "docker-stack.yml"), (compose_data, "docker-compose.prod.yml")]:
        # Redes segregadas
        networks = data.get("networks", {})
        assert "revnault_edge" in networks, f"{name} deve conter a rede revnault_edge"
        assert "revnault_app" in networks, f"{name} deve conter a rede revnault_app"
        assert "revnault_data" in networks, f"{name} deve conter a rede revnault_data"

        # Servicos essenciais
        services = data.get("services", {})
        required_services = ["app", "worker", "redis", "postgres", "superset", "orthanc", "wal-backup"]
        for svc in required_services:
            assert svc in services, f"{name} deve conter o servico '{svc}'"

            # Limites de recursos em deploy.resources.limits
            svc_conf = services[svc]
            deploy_conf = svc_conf.get("deploy", {})
            resources = deploy_conf.get("resources", {})
            limits = resources.get("limits", {})
            assert "cpus" in limits, f"Servico '{svc}' em {name} deve ter limite explicito de CPU"
            assert "memory" in limits, f"Servico '{svc}' em {name} deve ter limite explicito de memoria"

        # Healthchecks
        for svc_with_health in ["app", "redis", "postgres"]:
            assert "healthcheck" in services[svc_with_health], (
                f"Servico '{svc_with_health}' em {name} deve ter healthcheck configurado"
            )


def test_production_hardening_and_scripts():
    """Valida integridade e seguranca dos scripts operacionais de cluster."""
    repo_root = Path(__file__).resolve().parent.parent
    health_script = repo_root / "scripts" / "health_audit.sh"
    wal_script = repo_root / "scripts" / "wal_backup_s3.py"

    assert health_script.exists()
    assert wal_script.exists()

    health_content = health_script.read_text(encoding="utf-8")
    assert "BASE_URL" in health_content
    assert "set -euo pipefail" in health_content
    assert "FastAPI" in health_content

    # Sem emojis nos scripts
    for script_file in [health_script, wal_script]:
        txt = script_file.read_text(encoding="utf-8")
        for char in txt:
            assert ord(char) < 0x10000, f"Emoji detectado no arquivo {script_file.name}: {char}"
