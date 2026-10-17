# -*- coding: utf-8 -*-
"""
Handoff Automation Script — Antigravity Team Shift Handover
Gera e gerencia snapshots determinísticos de transição de contexto entre desenvolvedores.
"""

from __future__ import annotations
import os
import sys
import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
SECOES_DIR = ROOT_DIR / "secoes"
HANDOFF_FILE = SECOES_DIR / "HANDOFF_ATIVO.md"
HISTORICO_DIR = SECOES_DIR / "historico"


def _run_git_cmd(args: list[str]) -> str:
    try:
        res = subprocess.run(["git"] + args, cwd=str(ROOT_DIR), capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception:
        return ""


def get_active_dev() -> str:
    env_gemini = ROOT_DIR / ".env-gemini"
    active_marker = ROOT_DIR / ".gemini_active_dev"
    if active_marker.exists():
        return active_marker.read_text(encoding="utf-8").strip()
    return os.environ.get("CURRENT_DEV", "DEV_DESCONHECIDO")


def create_handoff(dev_name: str | None = None, mission: str | None = None, next_step: str | None = None):
    SECOES_DIR.mkdir(parents=True, exist_ok=True)
    
    dev = dev_name or get_active_dev()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    branch = _run_git_cmd(["branch", "--show-current"]) or "main"
    git_status = _run_git_cmd(["status", "-s"])
    last_commit = _run_git_cmd(["log", "-n", "1", "--oneline"])

    # Modificados
    modified_files = []
    if git_status:
        for line in git_status.splitlines():
            parts = line.strip().split()
            if len(parts) >= 2:
                modified_files.append(f"- `{parts[-1]}` ({parts[0]})")
    
    files_block = "\n".join(modified_files) if modified_files else "- *Nenhum arquivo modificado não commitado (Workspace limpo)*"

    content = f"""# 🤝 Snapshot de Transição de Contexto (Team Handoff)

- **Timestamp de Congelamento**: `{now_str}`
- **Desenvolvedor Cedente**: `{dev}`
- **Branch Ativa**: `{branch}`
- **Último Commit**: `{last_commit}`

---

## 1. Missão em Andamento
{mission or "Desenvolvimento contínuo da aplicação e refinamento de tickets no Antigravity."}

---

## 2. Estado Atual do Workspace (Git Status)
{files_block}

---

## 3. Próxima Ação Imediata (Next Step para o Próximo Dev)
> {next_step or "Executar 'pytest -q' para validar integridade e continuar a implementação do ponto onde foi pausado."}

---

## 4. Instruções para o Próximo Desenvolvedor
1. Alterne para o seu perfil: `python scripts/switch_dev.py --dev SEU_SLOT`
2. No chat do Antigravity, envie: `/retomar`
"""

    HANDOFF_FILE.write_text(content, encoding="utf-8")
    print(f"[OK] Snapshot de Handoff gerado com sucesso em: {HANDOFF_FILE}")
    print(f"Dev Cedente: {dev} | Timestamp: {now_str}")


def show_status():
    if not HANDOFF_FILE.exists():
        print("[INFO] Nenhum Handoff ativo pendente no momento. O workspace está pronto para novas tarefas.")
        return

    content = HANDOFF_FILE.read_text(encoding="utf-8")
    print("=================================================================")
    print(" 📋 SNAPSHOT DE HANDOFF ATIVO")
    print("=================================================================")
    print(content)


def clear_handoff():
    if not HANDOFF_FILE.exists():
        print("[INFO] Nenhum Handoff ativo para arquivar.")
        return

    HISTORICO_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_file = HISTORICO_DIR / f"handoff_{ts}.md"
    
    HANDOFF_FILE.rename(archive_file)
    print(f"[OK] Handoff arquivado em: {archive_file}")
    print("[OK] Workspace pronto e limpo para o novo turno.")


def main():
    parser = argparse.ArgumentParser(description="Automação de Handoff da Equipe Antigravity")
    subparsers = parser.add_subparsers(dest="command", help="Comando a executar")

    # create
    create_p = subparsers.add_parser("create", help="Gera um novo snapshot de Handoff")
    create_p.add_argument("--dev", type=str, help="Identificação do Dev (ex: DEV_01)")
    create_p.add_argument("--mission", type=str, help="Descrição do objetivo atual")
    create_p.add_argument("--next-step", type=str, help="Próxima ação imediata a executar")

    # status
    subparsers.add_parser("status", help="Exibe o snapshot de Handoff ativo")

    # clear
    subparsers.add_parser("clear", help="Arquiva o snapshot ativo para o histórico")

    args = parser.parse_args()

    if args.command == "create" or args.command is None:
        if args.command is None and len(sys.argv) > 1:
            parser.print_help()
            return
        create_handoff(
            dev_name=getattr(args, "dev", None),
            mission=getattr(args, "mission", None),
            next_step=getattr(args, "next_step", None)
        )
    elif args.command == "status":
        show_status()
    elif args.command == "clear":
        clear_handoff()


if __name__ == "__main__":
    main()
