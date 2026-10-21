# 03. Motores de Backend & Diagnóstico de Subprodutização — Rota: deals (Auditoria V3)

## 1. Aproveitamento dos Motores do Backend
A tela integra-se diretamente com os serviços FastAPI e tabelas SQLite WAL:
- `src/features/deals/router.py`
- `src/features/pipelines/router.py`
- `src/features/contracts/router.py`

---

## 2. Capacidades Ociosas do Motor Identificadas (Anti-Subprodutização)
- **Histórico de Mudança de Probabilidade:** Backend armazena log temporal de probabilidades, tela mostra só atual
- **Múltiplos Contatos por Negócio:** Banco suporta múltiplos decisores N:N, UI foca no cirurgião primário