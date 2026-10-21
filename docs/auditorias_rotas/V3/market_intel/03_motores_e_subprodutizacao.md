# 03. Motores de Backend & Diagnóstico de Subprodutização — Rota: market_intel (Auditoria V3)

## 1. Aproveitamento dos Motores do Backend
A tela integra-se diretamente com os serviços FastAPI e tabelas SQLite WAL:
- `src/features/market_intel/router.py`
- `src/features/intelligence/router.py`

---

## 2. Capacidades Ociosas do Motor Identificadas (Anti-Subprodutização)
- **Análise de Sentimento Social:** Backend possui conector para monitorar menções em eventos, tela omite
- **Projeção de Elasticidade-Preço:** Modelo econométrico de sensibilidade a preço implementado no motor mas não na UI