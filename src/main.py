# -*- coding: utf-8 -*-
"""
Revnaut Canonical VSA Monolith (AIDD Master Standard)
Agregador de fatias verticais autônomas com SQLite WAL e Quarteto Dinâmico.
"""

from __future__ import annotations
import time
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from src.core.database import get_connection, init_db
from src.features.deals.router import router as deals_router
from src.features.contacts.router import router as contacts_router
from src.features.communications.router import router as comms_router
from src.features.tickets.router import router as tickets_router
from src.features.tasks.router import router as tasks_router
from src.features.campaigns.router import router as campaigns_router
from src.features.scoring.router import router as scoring_router
from src.features.institutions.router import router as institutions_router
from src.features.webhooks.router import router as webhooks_router
from src.features.quarteto.router import router as quarteto_router
from src.features.hierarchy.router import router as hierarchy_router
from src.features.auth import auth_router
from src.features.integrations.totvs.router import router as totvs_router
from src.features.integrations.omnichannel.router import router as omnichannel_router
from src.features.automations.router import router as automations_router
from src.features.intelligence.router import router as intelligence_router
from src.features.storage.router import router as storage_router

# Inicializa schema e seed SQLite WAL




init_db()

app = FastAPI(
    title="Revnaut Enterprise API & Engine",
    description="Motor oficial de Revenue Operations, Funil de Vendas e CRM Omnichannel com Quarteto Sine Qua Non Dinâmico.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from pydantic import BaseModel

class HealthResponse(BaseModel):
    model_config = {"extra": "allow"}
    status: str
    sqlite_journal_mode: str
    accounts_online: int
    timestamp: float | None = None

# Health Check do Monólito
@app.get("/api/v1/health", response_model=HealthResponse, tags=["Sistema"])
def health_check():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("PRAGMA journal_mode;")
    mode = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM accounts")
    acc_count = cur.fetchone()[0]
    conn.close()
    return {
        "status": "healthy",
        "sqlite_journal_mode": mode,
        "accounts_online": acc_count,
        "timestamp": time.time()
    }

# Registro das Fatias Verticais (Vertical Slices)
app.include_router(deals_router)
app.include_router(contacts_router)
app.include_router(comms_router)
app.include_router(tickets_router)
app.include_router(tasks_router)
app.include_router(campaigns_router)
app.include_router(scoring_router)
app.include_router(institutions_router)
app.include_router(webhooks_router)
app.include_router(quarteto_router)
app.include_router(hierarchy_router)
app.include_router(auth_router)
app.include_router(totvs_router)
app.include_router(omnichannel_router)
app.include_router(automations_router)
app.include_router(intelligence_router)
app.include_router(storage_router)

# Montagem de Estáticos e Frontend Root
_possible_static_paths = [
    Path(__file__).resolve().parent.parent / "docs" / "reconstruct_rvops" / "05_reconstructed_app",
    Path("/app/static"),
    Path(__file__).resolve().parent / "static"
]

_active_static_dir = None
for p in _possible_static_paths:
    if p.exists() and (p / "index.html").exists():
        _active_static_dir = p
        break

if _active_static_dir:
    @app.get("/", response_class=HTMLResponse, tags=["Frontend"])
    def serve_frontend_root():
        index_file = _active_static_dir / "index.html"
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))

    css_path = _active_static_dir / "css"
    if css_path.exists():
        app.mount("/css", StaticFiles(directory=str(css_path)), name="css")

    js_path = _active_static_dir / "js"
    if js_path.exists():
        app.mount("/js", StaticFiles(directory=str(js_path)), name="js")

    @app.get("/favicon.ico", include_in_schema=False)
    @app.get("/favicon.svg", include_in_schema=False)
    def serve_favicon():
        fav_path = _active_static_dir / "favicon.svg"
        if not fav_path.exists():
            fav_path = Path(__file__).resolve().parent / "static" / "favicon.svg"
        if fav_path.exists():
            return Response(content=fav_path.read_bytes(), media_type="image/svg+xml")
        return Response(status_code=404)

    app.mount("/static", StaticFiles(directory=str(_active_static_dir)), name="static")
    app.mount("/app-assets", StaticFiles(directory=str(_active_static_dir)), name="app_assets")
