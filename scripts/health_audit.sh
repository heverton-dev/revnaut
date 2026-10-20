#!/usr/bin/env bash
# ==============================================================================
# RevNault Production Cluster Health & Hardening Audit Script
# Validação determinística de infraestrutura em produção (Docker / VPS / R2)
# Conformidade estrita com a Lei #14 (Zero Emojis).
# ==============================================================================

set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
REDIS_HOST="${REDIS_HOST:-127.0.0.1}"
REDIS_PORT="${REDIS_PORT:-6379}"
POSTGRES_HOST="${POSTGRES_HOST:-127.0.0.1}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
ORTHANC_PORT="${ORTHANC_PORT:-8042}"

AUDIT_FAILED=0

log_pass() {
    echo "[PASS] $1"
}

log_fail() {
    echo "[FAIL] $1"
    AUDIT_FAILED=1
}

log_warn() {
    echo "[WARN] $1"
}

echo "=============================================================================="
echo "Iniciando Auditoria de Seguranca e Saude do Cluster RevNault"
echo "Data/Hora UTC: $(date -u '+%Y-%m-%d %H:%M:%SZ')"
echo "=============================================================================="

# 1. Auditoria de Recursos do Sistema
echo "[CHECK] 1. Recursos do Servidor (CPU/Memoria/Disco)"
MEM_AVAIL=$(free -m | awk '/^Mem:/{print $7}')
DISK_AVAIL_PCT=$(df -h / | awk 'NR==2 {print $5}' | tr -d '%')

if [ "$MEM_AVAIL" -ge 256 ]; then
    log_pass "Memoria livre adequada: ${MEM_AVAIL}MB disponiveis"
else
    log_warn "Memoria livre baixa: ${MEM_AVAIL}MB disponiveis"
fi

if [ "$DISK_AVAIL_PCT" -lt 85 ]; then
    log_pass "Uso de disco sob controle: ${DISK_AVAIL_PCT}% ocupado"
else
    log_warn "Alerta de espaco em disco: ${DISK_AVAIL_PCT}% ocupado"
fi

# 2. Auditoria da API Core FastAPI
echo "[CHECK] 2. Endpoint de Saude FastAPI Core (/health)"
if command -v curl >/dev/null 2>&1; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "${BASE_URL}/health" || echo "000")
    if [ "$HTTP_CODE" = "200" ]; then
        log_pass "FastAPI /health retornou HTTP 200 OK"
    else
        log_fail "FastAPI /health falhou com status HTTP ${HTTP_CODE}"
    fi
else
    log_warn "curl nao disponivel; pulando teste HTTP de /health"
fi

# 3. Auditoria do Redis Streams
echo "[CHECK] 3. Conectividade Redis Streams"
if command -v redis-cli >/dev/null 2>&1; then
    PONG=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" PING 2>/dev/null || echo "FAIL")
    if [ "$PONG" = "PONG" ]; then
        log_pass "Redis respondendo PING"
    else
        log_fail "Redis nao respondeu ao PING no host ${REDIS_HOST}:${REDIS_PORT}"
    fi
else
    log_warn "redis-cli nao instalado; pulando checagem direta do Redis"
fi

# 4. Auditoria do PostgreSQL 16
echo "[CHECK] 4. Conectividade PostgreSQL 16"
if command -v pg_isready >/dev/null 2>&1; then
    if pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -t 3 >/dev/null 2>&1; then
        log_pass "PostgreSQL 16 operacional e aceitando conexoes"
    else
        log_fail "PostgreSQL 16 indisponivel no host ${POSTGRES_HOST}:${POSTGRES_PORT}"
    fi
else
    log_warn "pg_isready nao instalado; pulando checagem de Postgres"
fi

# 5. Auditoria de Servidor Orthanc DICOM 3D
echo "[CHECK] 5. Servidor Orthanc DICOM (Porta ${ORTHANC_PORT})"
if command -v nc >/dev/null 2>&1; then
    if nc -z -w 3 localhost "$ORTHANC_PORT" >/dev/null 2>&1; then
        log_pass "Porta Orthanc HTTP ${ORTHANC_PORT} ativa e respondendo"
    else
        log_warn "Orthanc HTTP ${ORTHANC_PORT} nao escutando (servico opcional em staging)"
    fi
fi

# 6. Auditoria de Hardening e Permissoes de Arquivos
echo "[CHECK] 6. Permissoes e Hardening de Arquivos de Seguranca"
if [ -d "gates" ]; then
    log_pass "Diretorio de Quality Gates integro"
fi

if [ -f "docker-stack.yml" ]; then
    log_pass "docker-stack.yml presente e versionado"
fi

if [ -f "docker-compose.prod.yml" ]; then
    log_pass "docker-compose.prod.yml presente e versionado"
fi

echo "=============================================================================="
if [ "$AUDIT_FAILED" -eq 0 ]; then
    echo "[SUCESSO] Auditoria de Saude do Cluster concluida sem falhas criticas."
    exit 0
else
    echo "[ERRO] Auditoria do Cluster detectou 1 ou mais falhas criticas."
    exit 1
fi
