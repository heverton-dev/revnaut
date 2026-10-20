# -*- coding: utf-8 -*-
"""
Automated Deployer — AIDD Ops Deploy to VPS Swarm
Transfere a aplicação para a VPS, compila a imagem Docker e sobe a stack no Traefik com SSL.
"""

import os
import tarfile
import tempfile
import paramiko
from pathlib import Path
from dotenv import load_dotenv

env_file = Path(__file__).resolve().parent.parent / ".env"
if env_file.exists():
    load_dotenv(env_file)

VPS_HOST = os.environ.get("VPS_HOST", "127.0.0.1")
VPS_PORT = int(os.environ.get("VPS_PORT", 22))
VPS_USER = os.environ.get("VPS_USER", "root")
VPS_PASS = os.environ.get("VPS_PASSWORD", "")
REMOTE_DIR = "/opt/rvops"
REMOTE_SECRETS_FILE = f"{REMOTE_DIR}/.env.secrets"

# Segredos de runtime enviados à VPS (lidos do .env local, nunca versionado nem impresso)
RUNTIME_SECRET_NAMES = (
    "SESSION_SECRET_KEY",
    "VAULT_SECRET_KEY",
    "OMNICHANNEL_WEBHOOK_SECRET",
    "DOCUMENSO_WEBHOOK_SECRET",
    "CALCOM_WEBHOOK_SECRET",
    "LISTMONK_WEBHOOK_SECRET",
)

_DB_SUFFIXES = (".db", ".db-wal", ".db-shm", ".db-journal")


def _data_filter(include_databases: bool):
    """O banco de produção vive no volume da VPS: bancos locais só seguem com --seed-database."""
    def _filter(ti):
        if not include_databases and ti.name.endswith(_DB_SUFFIXES):
            return None
        return ti
    return _filter


def build_secrets_file() -> str:
    missing = [n for n in RUNTIME_SECRET_NAMES if len(os.environ.get(n, "")) < 32]
    if missing:
        raise RuntimeError(f"Segredos ausentes ou curtos no .env local (mínimo 32 caracteres): {', '.join(missing)}")
    lines = [f"{n}={os.environ[n]}" for n in RUNTIME_SECRET_NAMES]
    return "\n".join(lines) + "\n"


def make_tarball(source_dir: Path, output_filename: str, include_databases: bool = False):
    with tarfile.open(output_filename, "w:gz") as tar:
        for file in [
            "Dockerfile",
            "docker-stack.yml",
            "docker-compose.prod.yml",
            "alembic.ini",
            "requirements.txt",
            "run_server.py"
        ]:
            p = source_dir / file
            if p.exists():
                tar.add(str(p), arcname=file)

        tar.add(str(source_dir / "src"), arcname="src")
        tar.add(str(source_dir / "backend"), arcname="backend")
        tar.add(str(source_dir / "data"), arcname="data", filter=_data_filter(include_databases))
        
        migrations_src = source_dir / "migrations"
        if migrations_src.exists():
            tar.add(str(migrations_src), arcname="migrations")

        frontend_src = source_dir / "frontend"
        if frontend_src.exists():
            tar.add(
                str(frontend_src),
                arcname="frontend",
                filter=lambda ti: None if "node_modules" in ti.name or ".vite" in ti.name else ti
            )

        frontend_dist = source_dir / "frontend" / "dist"
        if frontend_dist.exists():
            tar.add(str(frontend_dist), arcname="static")
        else:
            static_src = source_dir / "docs" / "reconstruct_rvops" / "05_reconstructed_app"
            if static_src.exists():
                tar.add(str(static_src), arcname="static")

        manuais_src = source_dir / "docs" / "manuais"
        if manuais_src.exists():
            tar.add(str(manuais_src), arcname="docs/manuais")

        gates_src = source_dir / "gates"
        if gates_src.exists():
            tar.add(str(gates_src), arcname="gates")

        scripts_src = source_dir / "scripts"
        if scripts_src.exists():
            tar.add(str(scripts_src), arcname="scripts")


def deploy(include_databases: bool = False):
    print("=================================================================")
    print(" [DEPLOY] INICIANDO DEPLOY DE PRODUCAO NA VPS:", VPS_HOST)
    print("=================================================================")
    
    source_dir = Path(__file__).resolve().parent.parent
    
    tar_path = str(source_dir / "deploy_package.tar.gz")

    try:
        secrets_content = build_secrets_file()
    except RuntimeError as e:
        print("[ERRO]", e)
        return False
    ssh = None

    try:
        print("[1/5] Compactando artefatos de producao...")
        if include_databases:
            print("[ATENCAO] --seed-database: o banco local SUBSTITUIRA o banco de producao na VPS.")
        make_tarball(source_dir, tar_path, include_databases=include_databases)

        print("[2/5] Conectando via SSH e SFTP...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(VPS_HOST, port=VPS_PORT, username=VPS_USER, password=VPS_PASS, timeout=15)

        sftp = ssh.open_sftp()
        try:
            sftp.stat(REMOTE_DIR)
        except IOError:
            ssh.exec_command(f"mkdir -p {REMOTE_DIR}/data")

        remote_tar = f"{REMOTE_DIR}/deploy.tar.gz"
        print(f"[3/5] Enviando pacote para {remote_tar}...")
        sftp.put(tar_path, remote_tar)
        with sftp.open(REMOTE_SECRETS_FILE, "w") as fh:
            fh.write(secrets_content)
        sftp.chmod(REMOTE_SECRETS_FILE, 0o600)
        sftp.close()

        print("[4/5] Descompactando e compilando imagem Docker na VPS...")
        import time
        version_tag = f"rvops_app:v{int(time.time())}"
        cmd_build = f"cd {REMOTE_DIR} && rm -f data/*.db-wal data/*.db-shm && tar -xzf deploy.tar.gz && cp -f data/revnaut.db data/rvops.db 2>/dev/null || true && docker build -t {version_tag} . && docker tag {version_tag} rvops_app:latest"
        stdin, stdout, stderr = ssh.exec_command(cmd_build)
        exit_status = stdout.channel.recv_exit_status()
        out_build = stdout.read().decode('utf-8')
        err_build = stderr.read().decode('utf-8')
        print("[STDOUT BUILD]", out_build)
        if err_build:
            print("[STDERR BUILD]", err_build)
        if exit_status != 0:
            print(f"[ERRO] Falha no docker build (exit status {exit_status})")
            return False

        print("[5/5] Disparando Docker Stack Deploy com Traefik SSL...")
        cmd_deploy = f"cd {REMOTE_DIR} && sed -i 's|image: rvops_app:.*|image: {version_tag}|' docker-stack.yml && set -a && . {REMOTE_SECRETS_FILE} && set +a && docker stack deploy -c docker-stack.yml rvops && docker service update --image {version_tag} --force rvops_app && docker service update --image {version_tag} --force rvops_worker"
        stdin, stdout, stderr = ssh.exec_command(cmd_deploy)
        deploy_exit_status = stdout.channel.recv_exit_status()
        out_deploy = stdout.read().decode('utf-8')
        err_deploy = stderr.read().decode('utf-8')
        print("[STDOUT DEPLOY]", out_deploy)
        if err_deploy:
            print("[STDERR DEPLOY]", err_deploy)
        if deploy_exit_status != 0:
            print(f"[ERRO] Falha no docker stack deploy (exit status {deploy_exit_status})")
            return False

        print("=================================================================")
        print(" [SUCESSO] DEPLOY CONCLUIDO COM SUCESSO!")
        print(" - Aplicacao & Frontend: https://revnault.vpsconexao.org")
        print(" - Swagger Studio:       https://revnault.vpsconexao.org/docs")
        print(" - Webhook Studio:       https://revnault.vpsconexao.org/webhooks")
        print(" - MCP Studio (IA):      https://revnault.vpsconexao.org/mcp")
        print(" - Guia do Usuario:      https://revnault.vpsconexao.org/docs/guia")
        print("=================================================================")
        return True

    except Exception as e:
        print("[ERRO] Falha durante o deploy:", e)
        return False
    finally:
        if os.path.exists(tar_path):
            os.remove(tar_path)
        if ssh is not None:
            ssh.close()


if __name__ == "__main__":
    import sys

    sys.exit(0 if deploy(include_databases="--seed-database" in sys.argv[1:]) else 1)
