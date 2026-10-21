# 08. Auditoria Anatômica de Botões, Modais & Ações — Rota: contacts (Auditoria V3)

## 1. Inventário Factual de Botões Existentes

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- |
| **Novo Contato / Cirurgião** | Interação direta | Abre modal de cadastro com CRO e clínica vinculada | **100% Funcional** |
| **Importar Base CSV** | Interação direta | Abre modal de importação em lote com deduplicação | **100% Funcional** |
| **Validar CRO no CFO** | Interação direta | Dispara consulta e validação contra API oficial do CFO | **100% Funcional** |
| **Exportar Lista CSV** | Interação direta | Download imediato da carteira de cirurgiões filtrada | **100% Funcional** |
| **Alternar Abas da Carteira** | Interação direta | Muda a visualização entre dentistas, clínicas e compliance | **100% Funcional** |

---

## 2. Gaps de Interação & Botões Sugeridos
- **Vincular Maleta em Consignação** (`TICKET-CONTACTS-01`): Atalho direto para destinar maleta KeyPartners ao cirurgião
- **Disparar Conversa WhatsApp** (`TICKET-CONTACTS-02`): Gatilho de abertura de chat instantâneo via Evolution API
- **Solicitar Entrega Expressa** (`TICKET-CONTACTS-03`): Botão para despachar reposição de implantes via DENTGO