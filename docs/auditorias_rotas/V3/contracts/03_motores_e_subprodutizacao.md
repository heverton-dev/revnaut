# 03. Motores de Backend & Diagnóstico de Subprodutização — Rota: contracts (Auditoria V3)

## 1. Aproveitamento dos Motores do Backend
A tela integra-se diretamente com os serviços FastAPI e tabelas SQLite WAL:
- `src/features/contracts/router.py`
- `src/features/integrations/totvs/router.py`

---

## 2. Capacidades Ociosas do Motor Identificadas (Anti-Subprodutização)
- **Campos Customizados Dinâmicos:** Documenso suporta tags variáveis infinitas, UI tem 4 campos fixos
- **Controle de Versões da Minuta:** Backend armazena diff de minutas, tela mostra apenas versão final