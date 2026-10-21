# 03. Motores de Backend & Diagnóstico de Subprodutização — Rota: support (Auditoria V3)

## 1. Aproveitamento dos Motores do Backend
A tela integra-se diretamente com os serviços FastAPI e tabelas SQLite WAL:
- `src/features/support/router.py`
- `src/features/integrations/omnichannel/router.py`

---

## 2. Capacidades Ociosas do Motor Identificadas (Anti-Subprodutização)
- **Integração Notivisa ANVISA:** Backend possui schema compatível com Notivisa, tela gera PDF manual
- **Painel de Taxa de Falha por Linha de Implante:** Agrupamento estatístico existe no banco mas não na UI