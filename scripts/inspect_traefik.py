import os
import paramiko

host = os.environ.get("VPS_HOST", "127.0.0.1")
password = os.environ.get("VPS_PASSWORD", "")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port=int(os.environ.get("VPS_PORT", 22)), username=os.environ.get("VPS_USER", "root"), password=password, timeout=10)

cmd = """
CID=$(docker ps -q -f name=rvops_app.1)
docker exec $CID grep -F "uvicorn.run" /app/run_server.py
"""
stdin, stdout, stderr = ssh.exec_command(cmd)
print("=== GREP NO CONTAINER ===")
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

ssh.close()
