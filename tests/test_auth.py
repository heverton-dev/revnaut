# -*- coding: utf-8 -*-
"""
Testes automatizados da fatia de Autenticação e Sessão de Usuários (FastAPI + SQLite WAL).
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_login_superadmin_success():
    """Valida login do Super Admin único (User God) Heverton Eduardo Peres com sucesso."""
    payload = {
        "email": "hevertoneduardoperes@gmail.com",
        "password": "@#Khen741963@#"
    }
    res = client.post("/api/v1/auth/login", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "hevertoneduardoperes@gmail.com"
    assert "Heverton Eduardo Peres" in data["user"]["name"]
    assert data["user"]["is_superadmin"] is True
    assert data["user"]["role"] == "Super Admin"


def test_login_invalid_password_fails():
    """Valida que senha incorreta para o Super Admin é rejeitada com 401 Unauthorized."""
    payload = {
        "email": "hevertoneduardoperes@gmail.com",
        "password": "senha_totalmente_errada"
    }
    res = client.post("/api/v1/auth/login", json=payload)
    assert res.status_code == 401
    assert "E-mail ou senha incorretos" in res.json()["detail"]


def test_login_nonexistent_user_fails():
    """Valida que usuário inexistente é rejeitado com 401."""
    payload = {
        "email": "desconhecido@revnaut.com",
        "password": "qualquer_senha"
    }
    res = client.post("/api/v1/auth/login", json=payload)
    assert res.status_code == 401


def test_auth_me_with_valid_bearer_token():
    """Valida recuperação do perfil ativo através do endpoint /api/v1/auth/me."""
    # 1. Faz login para obter token
    login_res = client.post("/api/v1/auth/login", json={
        "email": "hevertoneduardoperes@gmail.com",
        "password": "@#Khen741963@#"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    # 2. Chama /me passando o Bearer Token
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == "hevertoneduardoperes@gmail.com"
    assert me_data["is_superadmin"] is True


def test_auth_logout():
    """Valida endpoint de encerramento de sessão."""
    res = client.post("/api/v1/auth/logout")
    assert res.status_code == 200
    assert res.json()["success"] is True


def test_frontend_auth_elements():
    """Valida presença da tela de login, rodapé de usuário e botões de alternar/sair no frontend."""
    res = client.get("/")
    assert res.status_code == 200
    html = res.text
    # 1. Modal e Form de Login
    assert 'id="auth-login-modal"' in html
    assert 'id="auth-login-form"' in html
    assert 'id="login-email"' in html
    assert 'id="login-password"' in html
    assert 'hevertoneduardoperes@gmail.com' in html
    # 2. Rodapé de usuário e botões de logout/troca
    assert 'id="sidebar-user-avatar"' in html
    assert 'id="sidebar-user-name"' in html
    assert 'Heverton Eduardo Peres' in html
    assert 'openLoginModal()' in html
    assert 'handleLogout()' in html

