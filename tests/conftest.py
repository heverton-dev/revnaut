# -*- coding: utf-8 -*-
"""
Pytest Fixtures & Test DB Isolation
Garante que os testes executem estritamente em banco isolado temporário,
sem jamais poluir data/rvops.db ou data/revnaut.db.
"""

import os
import shutil
import tempfile
from pathlib import Path
import pytest

# ISOLAMENTO GLOBAL IMEDIATO: configurado antes de qualquer teste carregar módulos
_tmp_dir = Path("/tmp") if Path("/tmp").exists() else Path(tempfile.gettempdir())
try:
    _tmp_dir.mkdir(parents=True, exist_ok=True)
except Exception:
    pass

_test_db_path = str((_tmp_dir / "test_revnaut.db").resolve())
os.environ["REVNAUT_DB_PATH"] = _test_db_path

# Segredos exclusivos do ambiente de teste (webhooks são fail-closed sem segredo configurado)
TEST_WEBHOOK_SECRETS = {
    "OMNICHANNEL_WEBHOOK_SECRET": "test-omnichannel-webhook-secret-0001",
    "DOCUMENSO_WEBHOOK_SECRET": "test-documenso-webhook-secret-0001",
    "CALCOM_WEBHOOK_SECRET": "test-calcom-webhook-secret-0001",
    "LISTMONK_WEBHOOK_SECRET": "test-listmonk-webhook-secret-0001",
}
for _name, _value in TEST_WEBHOOK_SECRETS.items():
    os.environ[_name] = _value
# PBKDF2 mais leve apenas nos testes (produção usa 600000 iterações)
os.environ.setdefault("PASSWORD_PBKDF2_ITERATIONS", "1000")
os.environ["RVOPS_DB_PATH"] = _test_db_path

import src.core.config
src.core.config.DB_PATH = Path(_test_db_path)

# Remove banco de teste anterior se existir para garantir isolamento limpo
try:
    if os.path.exists(_test_db_path):
        os.remove(_test_db_path)
except Exception:
    pass

from src.core.database import init_db
init_db()

@pytest.fixture(scope="session", autouse=True)
def setup_isolated_test_database():
    yield _test_db_path
    try:
        if os.path.exists(_test_db_path):
            os.remove(_test_db_path)
    except Exception:
        pass
