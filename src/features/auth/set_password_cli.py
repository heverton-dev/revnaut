# -*- coding: utf-8 -*-
"""
Troca de senha pelo servidor (uso do Super Admin quando a senha atual está bloqueada).

Uso dentro do container do app:
    python -m src.features.auth.set_password_cli <e-mail>

A senha é lida por getpass (não aparece na tela nem no histórico do shell), exige no mínimo
12 caracteres, recusa senhas padrão/vazadas e é gravada com PBKDF2-SHA256.
"""

from __future__ import annotations

import getpass
import sys
from typing import Callable, List, Optional

from fastapi import HTTPException

from src.core.database import get_connection, init_db
from src.features.auth.service import set_user_password


def run(argv: List[str], prompt: Callable[[str], str] = getpass.getpass, out=print) -> int:
    if len(argv) != 1 or "@" not in argv[0]:
        out("Uso: python -m src.features.auth.set_password_cli <e-mail>")
        return 2
    email = argv[0].strip().lower()
    init_db()
    conn = get_connection()
    try:
        row = conn.execute("SELECT id, name FROM users WHERE lower(email) = ?", (email,)).fetchone()
    finally:
        conn.close()
    if not row:
        out(f"Usuário não encontrado: {email}")
        return 1

    first = prompt("Nova senha: ")
    second = prompt("Confirme a nova senha: ")
    if first != second:
        out("As senhas não conferem. Nada foi alterado.")
        return 1
    try:
        set_user_password(row["id"], first)
    except HTTPException as exc:
        out(f"Senha recusada: {exc.detail}")
        return 1
    out(f"Senha de {row['name']} ({email}) alterada com sucesso.")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    return run(sys.argv[1:] if argv is None else argv)


if __name__ == "__main__":
    sys.exit(main())
