# 08. Auditoria Anatômica de Botões, Modais & Ações de Interface — Rota: contacts

## 1. Inventário Factual de Botões Existentes na Rota

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | O Que Abre / Dispara | Por Que Existe (Propósito de Negócio) | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Novo Contato / Cirurgião** | Interação direta | Abre modal de cadastro com CRO e clínica | Ação reativa | Suporte operacional | **100% Funcional** |
| **Importar Base CSV** | Interação direta | Abre modal de importação em lote com deduplicação | Ação reativa | Suporte operacional | **100% Funcional** |
| **Validar CRO no CFO** | Interação direta | Dispara consulta e scraping da API oficial CFO | Ação reativa | Suporte operacional | **100% Funcional** |
| **Exportar Lista CSV** | Interação direta | Download imediato da carteira filtrada | Ação reativa | Suporte operacional | **100% Funcional** |
| **Alternar Abas** | Interação direta | Muda a visão reativa de cirurgiões para clínicas/compliance | Ação reativa | Suporte operacional | **100% Funcional** |

---

## 2. Modais e Gavetas (Drawers) na Rota
As ações de alta complexidade disparam formulários em modais Dialog centralizados ou gavetas laterais Sheet, garantindo que o operador não perca o contexto de navegação.

---

## 3. Catálogo de Botões Faltantes (Gaps de Interação & UX)

| Botão Faltante | Localização Sugerida na Tela | O Que Deveria Abrir / Fazer | Por Que Está Faltando (Impacto na Jornada) | Micro-Ticket Vinculado |
| :--- | :--- | :--- | :--- | :--- |
| **Vincular Maleta em Consignação** | Barra de ações da rota | Atalho direto para destinar maleta KeyPartners ao cirurgião | Lacuna identificada no fluxo | `TICKET-CONTACTS-01` |
| **Disparar Conversa WhatsApp** | Barra de ações da rota | Gatilho de abertura de chat instantâneo via Evolution API | Lacuna identificada no fluxo | `TICKET-CONTACTS-02` |
| **Solicitar Entrega Expressa** | Barra de ações da rota | Botão para despachar reposição de implantes via DENTGO | Lacuna identificada no fluxo | `TICKET-CONTACTS-03` |
