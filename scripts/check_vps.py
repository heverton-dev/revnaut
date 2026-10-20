import os
import paramiko
from pathlib import Path
from dotenv import load_dotenv

env_file = Path(".env")
if env_file.exists():
    load_dotenv(env_file)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(
    os.getenv("VPS_HOST"),
    port=int(os.getenv("VPS_PORT", 22)),
    username=os.getenv("VPS_USER"),
    password=os.getenv("VPS_PASSWORD"),
    timeout=10,
)
stdin, stdout, stderr = ssh.exec_command("docker service ls | grep revnault ; echo '---' ; docker ps --filter name=revnault | head -n 10")
print(stdout.read().decode())
err = stderr.read().decode()
if err:
    print("[STDERR]", err)
ssh.close()
