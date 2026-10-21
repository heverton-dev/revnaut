# 03. Motores de Backend & Diagnóstico de Subprodutização — Rota: settings (Auditoria V3)

## 1. Aproveitamento dos Motores do Backend
A tela integra-se diretamente com os serviços FastAPI e tabelas SQLite WAL:
- `src/features/settings/router.py`
- `src/features/integrations/totvs/router.py`
- `src/features/integrations/omnichannel/router.py`

---

## 2. Capacidades Ociosas do Motor Identificadas (Anti-Subprodutização)
- **Filtro Granular de Eventos de Webhook:** Backend suporta filtrar por 20 tópicos, UI assina todos os eventos
- **Sincronização de Pedidos de Compra TOTVS:** Conector Protheus lê ordens de compra, tela só sincroniza notas fiscais