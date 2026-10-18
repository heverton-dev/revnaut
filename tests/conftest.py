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

@pytest.fixture(scope="session", autouse=True)
def setup_isolated_test_database():
    temp_dir = tempfile.mkdtemp(prefix="revnaut_test_")
    test_db_path = os.path.join(temp_dir, "test_rvops.db")
    
    # Define caminhos de ambiente isolados
    os.environ["REVNAUT_DB_PATH"] = test_db_path
    os.environ["RVOPS_DB_PATH"] = test_db_path
    
    # Inicializa o schema e seeds limpos no banco de testes
    from src.core.database import init_db
    init_db()
    
    yield test_db_path
    
    # Teardown: limpa o diretório temporário após a suíte de testes
    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception:
        pass
