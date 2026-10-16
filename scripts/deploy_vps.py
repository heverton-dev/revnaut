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


def make_tarball(source_dir: Path, output_filename: str):
    with tarfile.open(output_filename, "w:gz") as tar:
        for file in [
            "Dockerfile",
            "docker-stack.yml",
            "requirements.txt",
            "run_server.py"
        ]:
            p = source_dir / file
            if p.exists():
                tar.add(str(p), arcname=file)

        tar.add(str(source_dir / "src"), arcname="src")
        tar.add(str(source_dir / "backend"), arcname="backend")
        tar.add(str(source_dir / "data"), arcname="data")
        
        static_src = source_dir / "docs" / "reconstruct_rvops" / "05_reconstructed_app"
        if static_src.exists():
            tar.add(str(static_src), arcname="static")

        manuais_src = source_dir / "docs" / "manuais"
        if manuais_src.exists():
            tar.add(str(manuais_src), arcname="docs/manuais")

        gates_src = source_dir / "gates"
        if gates_src.exists():
            tar.add(str(gates_src), arcname="gates")


def deploy():
    print("=================================================================")
    print(" 🚀 INICIANDO DEPLOY DE PRODUÇÃO NA VPS:", VPS_HOST)
    print("=================================================================")
    
    source_dir = Path(__file__).resolve().parent.parent
    
    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp_tar:
        tar_path = tmp_tar.name

    try:
        print("[1/5] Compactando artefatos de produção...")
        make_tarball(source_dir, tar_path)

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
        sftp.close()

        print("[4/5] Descompactando e compilando imagem Docker na VPS...")
        import time
        version_tag = f"rvops_app:v{int(time.time())}"
        cmd_build = f"cd {REMOTE_DIR} && tar -xzf deploy.tar.gz && docker build -t {version_tag} . && docker tag {version_tag} rvops_app:latest"
        stdin, stdout, stderr = ssh.exec_command(cmd_build)
        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
            print("[ERRO] Falha no docker build:")
            print(stderr.read().decode('utf-8'))
            return False

        print("[5/5] Disparando Docker Stack Deploy com Traefik SSL...")
        cmd_deploy = f"cd {REMOTE_DIR} && sed -i 's|image: rvops_app:.*|image: {version_tag}|' docker-stack.yml && docker stack deploy -c docker-stack.yml rvops && docker service update --image {version_tag} --force rvops_app"
        stdin, stdout, stderr = ssh.exec_command(cmd_deploy)
        stdout.channel.recv_exit_status()
        print(stdout.read().decode('utf-8'))

        print("=================================================================")
        print(" ✅ DEPLOY CONCLUÍDO COM SUCESSO!")
        print(" - Aplicação & Frontend: https://revnaut.vpsconexao.org")
        print(" - Swagger Studio:       https://revnaut.vpsconexao.org/docs")
        print(" - Webhook Studio:       https://revnaut.vpsconexao.org/webhooks")
        print(" - MCP Studio (IA):      https://revnaut.vpsconexao.org/mcp")
        print(" - Guia do Usuário:      https://revnaut.vpsconexao.org/docs/guia")
        print("=================================================================")
        return True

    except Exception as e:
        print("[ERRO] Falha durante o deploy:", e)
        return False
    finally:
        if os.path.exists(tar_path):
            os.remove(tar_path)
        ssh.close()


if __name__ == "__main__":
    deploy()
