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
    """Valida presença da tela de login, rodapé de usuário, gestão de usuários e importador universal no frontend."""
    res = client.get("/")
    assert res.status_code == 200
    html = res.text
    # 1. Modal e Form de Login
    assert 'id="auth-login-modal"' in html
    assert 'id="auth-login-form"' in html
    assert 'id="login-email"' in html
    assert 'id="login-password"' in html
    assert 'hevertoneduardoperes@gmail.com' in html
    assert 'fillSuperAdminCredentials()' in html
    # 2. Rodapé de usuário e botões de logout/troca
    assert 'id="sidebar-user-avatar"' in html
    assert 'id="sidebar-user-name"' in html
    assert 'Heverton Eduardo Peres' in html
    assert 'openLoginModal()' in html
    assert 'handleLogout()' in html
    # 3. Central de Gestão de Usuários & Credenciais
    assert 'id="users-view"' in html
    assert 'id="modal-new-collaborator"' in html
    assert 'id="modal-reset-collaborator-password"' in html
    assert 'fetchUsersList()' in html
    # 4. Importador Universal em Massa de Carteiras
    assert 'id="import-contacts-view"' in html
    assert 'id="import-csv-text"' in html
    assert 'handleBulkImportSubmit()' in html



def test_users_management_crud_and_security_invariants():
    """Valida gestão de colaboradores, reset de senha e invariante inquebrável de superadmin único."""
    # 1. Login do Super Admin
    login_res = client.post("/api/v1/auth/login", json={
        "email": "hevertoneduardoperes@gmail.com",
        "password": "@#Khen741963@#"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Listagem de usuários
    list_res = client.get("/api/v1/auth/users", headers=headers)
    assert list_res.status_code == 200
    users = list_res.json()
    assert len(users) >= 1
    # Verifica que apenas Heverton é superadmin
    superadmins = [u for u in users if u["is_superadmin"] is True]
    assert len(superadmins) == 1
    assert superadmins[0]["email"] == "hevertoneduardoperes@gmail.com"

    # 3. Criação de novo colaborador pelo Super Admin
    import uuid
    collab_email = f"dr.colaborador.{uuid.uuid4().hex[:6]}@revnaut.com"
    create_res = client.post("/api/v1/auth/users", json={
        "name": "Dr. Fernando Odonto",
        "email": collab_email,
        "password": "senhaInicial123",
        "role": "Consultor Comercial Odonto",
        "phone": "(11) 98765-4321"
    }, headers=headers)
    assert create_res.status_code == 200
    collab_data = create_res.json()
    assert collab_data["is_superadmin"] is False
    assert collab_data["email"] == collab_email
    new_user_id = collab_data["id"]

    # 4. Colaborador recém-criado consegue logar com sua senha
    collab_login = client.post("/api/v1/auth/login", json={
        "email": collab_email,
        "password": "senhaInicial123"
    })
    assert collab_login.status_code == 200
    collab_token = collab_login.json()["access_token"]
    collab_headers = {"Authorization": f"Bearer {collab_token}"}

    # 5. Colaborador comum NÃO PODE cadastrar novos usuários (403 Forbidden)
    forbidden_res = client.post("/api/v1/auth/users", json={
        "name": "Intruso",
        "email": "intruso@revnaut.com",
        "password": "123"
    }, headers=collab_headers)
    assert forbidden_res.status_code == 403

    # 6. Super Admin reseta a senha do colaborador
    reset_res = client.post(f"/api/v1/auth/users/{new_user_id}/reset-password", json={
        "new_password": "NovaSenhaSegura2026!"
    }, headers=headers)
    assert reset_res.status_code == 200
    assert reset_res.json()["success"] is True

    # 7. Colaborador loga com a NOVA senha com sucesso
    new_login = client.post("/api/v1/auth/login", json={
        "email": collab_email,
        "password": "NovaSenhaSegura2026!"
    })
    assert new_login.status_code == 200

    # 8. Desativação e Ativação do colaborador
    deact_res = client.put(f"/api/v1/auth/users/{new_user_id}/status", json={"is_active": False}, headers=headers)
    assert deact_res.status_code == 200

    # Login deve falhar com 403 para usuário desativado
    blocked_login = client.post("/api/v1/auth/login", json={
        "email": collab_email,
        "password": "NovaSenhaSegura2026!"
    })
    assert blocked_login.status_code == 403

    # Reativação
    react_res = client.put(f"/api/v1/auth/users/{new_user_id}/status", json={"is_active": True}, headers=headers)
    assert react_res.status_code == 200

    # 9. Invariante: Super Admin não pode ser desativado
    superadmin_user_id = superadmins[0]["id"]
    super_deact_res = client.put(f"/api/v1/auth/users/{superadmin_user_id}/status", json={"is_active": False}, headers=headers)
    assert super_deact_res.status_code == 400
    assert "Super Admin único não pode ser desativado" in super_deact_res.json()["detail"]


def test_login_rate_limiting_brute_force():
    """Testa bloqueio por rate limiting após 5 tentativas falhas de login."""
    test_email = "bruteforce.target@revnaut.com"
    # 5 tentativas com senha errada
    for i in range(5):
        res = client.post("/api/v1/auth/login", json={
            "email": test_email,
            "password": f"wrongpass{i}"
        })
        assert res.status_code == 401

    # 6ª tentativa deve ser bloqueada com 429 Too Many Requests
    blocked_res = client.post("/api/v1/auth/login", json={
        "email": test_email,
        "password": "wrongpass_blocked"
    })
    assert blocked_res.status_code == 429
    assert "Muitas tentativas" in blocked_res.json()["detail"]


def test_forgot_password_and_reset_token_flow():
    """Testa fluxo de recuperação de senha com token temporário."""
    # 1. Solicita link/token de recuperação
    req_res = client.post("/api/v1/auth/forgot-password", json={
        "email": "hevertoneduardoperes@gmail.com"
    })
    assert req_res.status_code == 200
    data = req_res.json()
    assert data["success"] is True
    assert data["reset_token"] is not None
    token = data["reset_token"]

    # 2. Reseta senha usando o token
    reset_res = client.post("/api/v1/auth/reset-password-with-token", json={
        "token": token,
        "new_password": "NovaSenhaSeguraHeverton2026!"
    })
    assert reset_res.status_code == 200
    assert reset_res.json()["success"] is True

    # 3. Loga com a nova senha
    login_res = client.post("/api/v1/auth/login", json={
        "email": "hevertoneduardoperes@gmail.com",
        "password": "NovaSenhaSeguraHeverton2026!"
    })
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()

    # 4. Restaura senha de teste original para não quebrar outros testes
    restore_res = client.post("/api/v1/auth/reset-password-with-token", json={
        "token": client.post("/api/v1/auth/forgot-password", json={"email": "hevertoneduardoperes@gmail.com"}).json()["reset_token"],
        "new_password": "superadmin_dental_2026"
    })
    assert restore_res.status_code == 200


