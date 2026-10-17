# -*- coding: utf-8 -*-
"""
Dev Account Switcher — Antigravity Team Shift & Quota Manager
Alterna o desenvolvedor ativo a partir de .env-gemini sem perda de contexto ou retrabalho.
"""

from __future__ import annotations
import os
import sys
import argparse
from pathlib import Path


ROOT_DIR = Path.cwd()
GLOBAL_GEMINI_DIR = Path.home() / ".gemini"


def get_env_gemini_path() -> Path:
    local_p = ROOT_DIR / ".env-gemini"
    if local_p.exists():
        return local_p
    global_p = GLOBAL_GEMINI_DIR / ".env-gemini"
    if global_p.exists():
        return global_p
    return local_p


ACTIVE_DEV_FILE = ROOT_DIR / ".gemini_active_dev"
ACTIVE_ENV_FILE = ROOT_DIR / ".env.active"
HANDOFF_FILE = ROOT_DIR / "secoes" / "HANDOFF_ATIVO.md"


def parse_devs_from_env() -> dict[str, dict[str, str]]:
    env_file = get_env_gemini_path()
    if not env_file.exists():
        return {}

    lines = env_file.read_text(encoding="utf-8").splitlines()
    devs: dict[str, dict[str, str]] = {}

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip("'\"")
            
            # Formato DEV_XX_CAMPO
            if key.startswith("DEV_"):
                parts = key.split("_", 2)
                if len(parts) >= 3:
                    dev_id = f"{parts[0]}_{parts[1]}"  # ex: DEV_01
                    field = parts[2].lower()           # nome, email, senha, cargo, etc.
                    if dev_id not in devs:
                        devs[dev_id] = {}
                    devs[dev_id][field] = val

    return devs


def resolve_dynamic_project_id(configured_id: str | None = None) -> str:
    """Detecta deterministicamente o ID do projeto com base no repositório Git ou nome da pasta."""
    if configured_id and configured_id.strip() != "auto":
        return configured_id.strip()
    
    import subprocess
    try:
        res = subprocess.run(["git", "config", "--get", "remote.origin.url"], cwd=str(ROOT_DIR), capture_output=True, text=True, check=True)
        url = res.stdout.strip()
        if url:
            repo_name = url.split("/")[-1].replace(".git", "")
            if repo_name:
                return repo_name
    except Exception:
        pass
    return ROOT_DIR.name


def parse_global_config() -> dict[str, str]:
    env_file = get_env_gemini_path()
    if not env_file.exists():
        return {}
    lines = env_file.read_text(encoding="utf-8").splitlines()
    config = {}
    for line in lines:
        line = line.strip()
        if "=" in line and not line.startswith("#") and not line.startswith("DEV_"):
            k, v = line.split("=", 1)
            config[k.strip()] = v.strip().strip("'\"")
    return config


def get_current_dev() -> str:
    if ACTIVE_DEV_FILE.exists():
        return ACTIVE_DEV_FILE.read_text(encoding="utf-8").strip()
    return "DEV_01"


def sync_git_author(dev_data: dict[str, str]):
    """Sincroniza o autor local do Git para o desenvolvedor ativo."""
    nome = dev_data.get("nome", "").strip()
    email = dev_data.get("email", "").strip()
    if email:
        import subprocess
        try:
            if nome:
                subprocess.run(["git", "config", "user.name", nome], cwd=str(ROOT_DIR), check=False)
            subprocess.run(["git", "config", "user.email", email], cwd=str(ROOT_DIR), check=False)
            print(f" [GIT] Autor configurado no repositório: {nome or 'Dev'} <{email}>")
        except Exception as e:
            print(f" [GIT] Aviso ao atualizar git config: {e}")


def set_active_dev(target_dev: str, devs: dict[str, dict[str, str]]):
    target_dev = target_dev.upper().strip()
    if not target_dev.startswith("DEV_") and target_dev.isdigit():
        target_dev = f"DEV_{int(target_dev):02d}"

    if target_dev not in devs:
        print(f"[ERRO] Desenvolvedor '{target_dev}' não encontrado no arquivo .env-gemini.")
        print("Disponíveis:", ", ".join(sorted(devs.keys())))
        return False

    dev_data = devs[target_dev]
    global_cfg = parse_global_config()
    project_id = resolve_dynamic_project_id(global_cfg.get("GEMINI_PROJECT_ID"))

    ACTIVE_DEV_FILE.write_text(target_dev, encoding="utf-8")

    # Exporta variáveis para arquivo de ambiente ativo (.env.active)
    active_env_content = f"""# Perfil Ativo: {target_dev}
CURRENT_DEV={target_dev}
CURRENT_DEV_NOME="{dev_data.get('nome', '')}"
CURRENT_DEV_EMAIL="{dev_data.get('email', '')}"
CURRENT_DEV_CARGO="{dev_data.get('cargo', 'Desenvolvedor')}"
GEMINI_API_KEY="{dev_data.get('gemini_api_key', '')}"
GEMINI_PROJECT_ID="{project_id}"
GEMINI_ENVIRONMENT="{global_cfg.get('GEMINI_ENVIRONMENT', 'development')}"
"""
    ACTIVE_ENV_FILE.write_text(active_env_content, encoding="utf-8")

    # Sincroniza Git local
    sync_git_author(dev_data)

    print("=================================================================")
    print(f" 👤 DESENVOLVEDOR ATIVO ALTERADO PARA: {target_dev}")
    print("=================================================================")
    print(f" - Nome:    {dev_data.get('nome') or '(Nome não preenchido no .env-gemini)'}")
    print(f" - E-mail:  {dev_data.get('email') or '(E-mail não preenchido)'}")
    print(f" - Cargo:   {dev_data.get('cargo') or 'Desenvolvedor'}")
    print(f" - Projeto: {project_id} (Detecção Dinâmica)")
    print("-----------------------------------------------------------------")
    print(f" [OK] Perfil salvo em: {ACTIVE_DEV_FILE}")
    print(f" [OK] Variáveis exportadas em: {ACTIVE_ENV_FILE}")

    # Verifica se há handoff pendente
    if HANDOFF_FILE.exists():
        print("-----------------------------------------------------------------")
        print(" 🔔 ATENÇÃO: Há um snapshot de Handoff ativo deixado pelo dev anterior!")
        print(" Para assumir o trabalho do ponto exato, abra o Antigravity e envie:")
        print(" >>> /retomar")
        print("-----------------------------------------------------------------")
    else:
        print(" [INFO] Workspace livre e sem handoffs pendentes.")

    print("=================================================================")
    return True


def list_devs(devs: dict[str, dict[str, str]]):
    current = get_current_dev()
    print("=================================================================")
    print(" 👥 EQUIPE DE DESENVOLVIMENTO (15 SLOTS)")
    print("=================================================================")
    for dev_id in sorted(devs.keys()):
        d = devs[dev_id]
        mark = "👉 [ATIVO] " if dev_id == current else "          "
        nome = d.get("nome") or "(Não configurado)"
        cargo = d.get("cargo") or "Engineer"
        email = d.get("email") or "-"
        print(f"{mark}{dev_id}: {nome} | {cargo} ({email})")
    print("=================================================================")
    print(" Para trocar o dev ativo, use: python scripts/switch_dev.py --dev DEV_XX")
    print("=================================================================")


def show_status(devs: dict[str, dict[str, str]]):
    current = get_current_dev()
    dev_data = devs.get(current, {})
    print("=================================================================")
    print(f" 🟢 STATUS ATUAL DA SESSÃO ANTIGRAVITY")
    print("=================================================================")
    print(f" - Dev Ativo: {current} ({dev_data.get('nome') or 'Sem nome'})")
    print(f" - Cargo:     {dev_data.get('cargo') or 'Engineer'}")
    print(f" - E-mail:    {dev_data.get('email') or '-'}")
    print(f" - Handoff:   {'PENDENTE (use /retomar)' if HANDOFF_FILE.exists() else 'Nenhum snapshot ativo'}")
    print("=================================================================")


def switch_to_next_dev(devs: dict[str, dict[str, str]]):
    """Rotaciona automaticamente para o próximo desenvolvedor da lista (Round-Robin)."""
    current = get_current_dev()
    sorted_devs = sorted(devs.keys())
    if not sorted_devs:
        print("[ERRO] Nenhum desenvolvedor encontrado.")
        return False
    if current in sorted_devs:
        idx = sorted_devs.index(current)
        next_dev = sorted_devs[(idx + 1) % len(sorted_devs)]
    else:
        next_dev = sorted_devs[0]
    print(f"[AUTO-ROTAÇÃO] Alternando de {current} para {next_dev}...")
    return set_active_dev(next_dev, devs)


def auto_detect_from_git(devs: dict[str, dict[str, str]]):
    """Detecta automaticamente o desenvolvedor a partir do e-mail configurado no Git."""
    import subprocess
    git_email = ""
    try:
        res = subprocess.run(["git", "config", "user.email"], capture_output=True, text=True, check=True)
        git_email = res.stdout.strip().lower()
    except Exception:
        pass

    if git_email:
        for dev_id, d in devs.items():
            if d.get("email", "").strip().lower() == git_email:
                print(f"[AUTO-DETECÇÃO] E-mail do Git '{git_email}' corresponde ao {dev_id}!")
                return set_active_dev(dev_id, devs)

    print(f"[INFO] Nenhum slot corresponde exatamente ao e-mail do Git '{git_email}'. Mantendo {get_current_dev()}.")
    return False


def open_sso_login(target_dev: str | None, devs: dict[str, dict[str, str]]):
    """Executa a troca do dev, sincroniza o Git e abre o navegador oficial no Google Account Chooser com o email do dev pré-selecionado."""
    target = target_dev if target_dev else get_current_dev()
    target = target.upper().strip()
    if not target.startswith("DEV_") and target.isdigit():
        target = f"DEV_{int(target):02d}"

    if target not in devs:
        print(f"[ERRO] Desenvolvedor '{target}' não encontrado no .env-gemini.")
        return False

    dev_data = devs[target]
    set_active_dev(target, devs)

    email = dev_data.get("email", "").strip()
    login_url = f"https://accounts.google.com/AccountChooser?Email={email}" if email else "https://accounts.google.com/ServiceLogin"

    print("\n-----------------------------------------------------------------")
    print(" 🚀 INICIANDO LOGIN OFICIAL GOOGLE (Human-in-the-Loop)")
    print("-----------------------------------------------------------------")
    print(f" - Desenvolvedor: {target} ({dev_data.get('nome') or 'Sem nome'})")
    print(f" - E-mail Alvo:   {email or '(E-mail não preenchido)'}")
    print(" - Abrindo navegador padrão (Chrome/Edge) sem flags de automação...")
    print(" - O Google NÃO detectará bot e permitirá autenticação e 2FA normalmente.")
    print("-----------------------------------------------------------------")

    import webbrowser
    webbrowser.open(login_url)

    print(" 👉 Passos no Antigravity:")
    print("    1. Conclua o login e confirme o 2FA na janela do navegador aberta.")
    print("    2. No IDE, clique no ícone de Perfil/Contas (inferior esquerdo) -> 'Sign In with Google'.")
    print("    3. Envie '/retomar' no chat para restaurar o estado exato da tarefa.")
    print("=================================================================\n")
    return True


def main():
    devs = parse_devs_from_env()
    if not devs:
        print("[AVISO] O arquivo .env-gemini está vazio ou não existe. Criando template...")

    parser = argparse.ArgumentParser(description="Alternador de Desenvolvedor & Cota Antigravity")
    parser.add_argument("--dev", type=str, help="ID do desenvolvedor para ativar (ex: DEV_02 ou 2)")
    parser.add_argument("--login", "--sso", dest="login", action="store_true", help="Abrir janela de autenticação oficial Google (Human-in-the-Loop)")
    parser.add_argument("--next", action="store_true", help="Rotacionar automaticamente para a próxima conta (quando a cota estourar)")
    parser.add_argument("--auto", action="store_true", help="Detectar e ativar automaticamente com base no e-mail do Git")
    parser.add_argument("--list", action="store_true", help="Listar todos os desenvolvedores cadastrados")
    parser.add_argument("--status", action="store_true", help="Exibir desenvolvedor ativo no momento")

    args = parser.parse_args()

    if args.list:
        list_devs(devs)
    elif args.status:
        show_status(devs)
    elif args.login:
        open_sso_login(args.dev, devs)
    elif args.next:
        switch_to_next_dev(devs)
    elif args.auto:
        auto_detect_from_git(devs)
    elif args.dev:
        set_active_dev(args.dev, devs)
    else:
        show_status(devs)
        print("\nDica: Use '--login --dev DEV_XX' para autenticação oficial Google ou '--next' para rotacionar cota.")


if __name__ == "__main__":
    main()
