# 03. Motores de Backend & Diagnóstico de Subprodutização — Rota: dashboard (Auditoria V3)

## 1. Aproveitamento dos Motores do Backend
A tela integra-se diretamente com os serviços FastAPI e tabelas SQLite WAL:
- `src/features/deals/router.py`
- `src/features/campaigns/router.py`
- `src/features/intelligence/router.py`

---

## 2. Capacidades Ociosas do Motor Identificadas (Anti-Subprodutização)
- **Agrupamento Multi-Moeda:** Backend calcula taxas cambiais, tela exibe prioritariamente BRL
- **Projeção Preditiva Trimestral:** Motor ARIMA/Regressão disponível no backend mas não exposto nos cards