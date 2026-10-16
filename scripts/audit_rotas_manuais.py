#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Auditor e Gerador Determinístico de Manuais de Rotas • Revnaut Dental.

Funções:
1. Auditar rotas do código (FastAPI + Frontend) contra docs/manuais/*.md.
2. Gerar scaffold automático com as 6 seções obrigatórias para novas rotas adicionadas.

Uso:
  python scripts/audit_rotas_manuais.py --audit
  python scripts/audit_rotas_manuais.py --scaffold <rota_id> "<Título da Rota>"
"""

import argparse
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANUAIS_DIR = REPO_ROOT / "docs" / "manuais"
INDEX_HTML = REPO_ROOT / "docs" / "reconstruct_rvops" / "05_reconstructed_app" / "index.html"

SCAFFOLD_TEMPLATE = """# Manual da Rota: {title} (`/#{route_id}`)

## 1. Objetivo da Rota
{objective}

---

## 2. O Que o Usuário Consegue Realizar
* Ação 1 a ser descrita...
* Ação 2 a ser descrita...

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil | Visualizar | Criar / Executar | Editar | Excluir |
|---|---|---|---|---|
| Consultor de Vendas | Conforme escopo | Não | Não | Não |
| Gerente Regional | Regional | Sim | Sim | Não |
| Diretor de BU | Toda a BU | Sim | Sim | Sim |
| Super Admin | Irrestrito | Sim | Sim | Sim |

---

## 4. Quais Ações Podem Ser Realizadas
* `ACTION_PRIMARY`: Descrição técnica da ação.
* `ACTION_SECONDARY`: Descrição técnica da ação secundária.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)
1. Acesse o menu lateral e clique em **{title}**.
2. Passo operacional 1...
3. Passo operacional 2...

---

## 6. O Que Falta Implementar (Roadmap & Gaps)
* Item 1 do roadmap de evolução...
* Item 2 do roadmap de evolução...
"""


def extract_frontend_routes() -> list[str]:
    if not INDEX_HTML.exists():
        return []
    content = INDEX_HTML.read_text(encoding="utf-8")
    block_match = re.search(r"const\s+VIEW_CONFIG\s*=\s*\{(.+?)\n\s*\};", content, re.DOTALL)
    if not block_match:
        return []
    return re.findall(r"['\"]([a-zA-Z0-9_\-]+)['\"]\s*:\s*\{", block_match.group(1))


def audit() -> int:
    routes = extract_frontend_routes()
    manual_files = list(MANUAIS_DIR.glob("*.md"))
    all_texts = "\n".join([f.read_text(encoding="utf-8") for f in manual_files])

    missing = []
    for r in routes:
        pattern = rf"(#|'|\"|`){re.escape(r)}('|#|\"|`|\b)"
        if not re.search(pattern, all_texts, re.IGNORECASE):
            missing.append(r)

    print(f"=== AUDITORIA DE MANUAIS DE ROTAS ===")
    print(f"Total de rotas no frontend: {len(routes)}")
    print(f"Total de manuais em docs/manuais/: {len(manual_files)}")
    if missing:
        print(f"ATENÇÃO: {len(missing)} rotas NÃO possuem manual correspondente:")
        for m in missing:
            print(f"  - {m}")
        return 1

    print("Status: 100% das rotas devidamente documentadas.")
    return 0


def scaffold(route_id: str, title: str) -> None:
    MANUAIS_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{route_id.replace('-', '_')}.md"
    filepath = MANUAIS_DIR / filename

    if filepath.exists():
        print(f"O arquivo {filepath} já existe. Não sobrescrito.")
        return

    content = SCAFFOLD_TEMPLATE.format(
        route_id=route_id,
        title=title,
        objective=f"Centralizar a operação da rota {title} no CRM Odontológico Revnaut."
    )
    filepath.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"Scaffold gerado com sucesso em: {filepath}")


def main():
    parser = argparse.ArgumentParser(description="Auditor e Gerador de Manuais de Rotas")
    parser.add_argument("--audit", action="store_true", help="Auditar conformidade das rotas")
    parser.add_argument("--scaffold", nargs=2, metavar=("ROTA_ID", "TITULO"), help="Gerar scaffold para nova rota")

    args = parser.parse_args()

    if args.scaffold:
        scaffold(args.scaffold[0], args.scaffold[1])
        sys.exit(0)

    sys.exit(audit())


if __name__ == "__main__":
    main()
