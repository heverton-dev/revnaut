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
