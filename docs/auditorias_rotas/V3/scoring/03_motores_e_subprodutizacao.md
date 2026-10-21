# 03. Motores de Backend & Diagnóstico de Subprodutização — Rota: scoring (Auditoria V3)

## 1. Aproveitamento dos Motores do Backend
A tela integra-se diretamente com os serviços FastAPI e tabelas SQLite WAL:
- `src/features/scoring/router.py`
- `src/features/intelligence/router.py`

---

## 2. Capacidades Ociosas do Motor Identificadas (Anti-Subprodutização)
- **Regras Dinâmicas de ICP:** Motor permite expressões aritméticas customizadas, UI usa fórmula fixa
- **Previsão de Ticket Anual:** Backend estima faturamento potencial baseado em cadeiras, tela omite