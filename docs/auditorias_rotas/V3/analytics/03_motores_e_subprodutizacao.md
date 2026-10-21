# 03. Motores de Backend & Diagnóstico de Subprodutização — Rota: analytics (Auditoria V3)

## 1. Aproveitamento dos Motores do Backend
A tela integra-se diretamente com os serviços FastAPI e tabelas SQLite WAL:
- `src/features/analytics/router.py`
- `src/features/bi/router.py`

---

## 2. Capacidades Ociosas do Motor Identificadas (Anti-Subprodutização)
- **Validação de AST para INSERT/DELETE:** Parser bloqueia mutações, backend suporta explain query plan
- **Cache de Resultados Text-to-SQL:** Armazenamento em cache Redis implementado mas não exposto na UI