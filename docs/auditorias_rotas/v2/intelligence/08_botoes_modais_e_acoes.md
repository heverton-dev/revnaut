# 08. Auditoria Anatômica de Botões, Modais & Ações de Interface — Rota: intelligence (Auditoria v2)

## 1. Inventário Factual de Botões Existentes na Rota

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | O Que Abre / Dispara | Por Que Existe (Propósito de Negócio) | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Recalcular Risco de Evasão** | Interação direta | Executa modelo RFM determinístico sobre histórico de compras | Ação reativa | Suporte operacional | **100% Funcional** |
| **Filtrar Grafo KOL por Especialidade** | Interação direta | Destaca polos acadêmicos e cirurgiões speakers | Ação reativa | Suporte operacional | **100% Funcional** |
| **Consultar Assistente Clínico RAG** | Interação direta | Busca em embeddings vetoriais com citações do catálogo | Ação reativa | Suporte operacional | **100% Funcional** |
| **Exportar Indicadores de Evasão** | Interação direta | Download de lista de cirurgiões em risco de churn | Ação reativa | Suporte operacional | **100% Funcional** |

---

## 2. Modais e Gavetas (Drawers) na Rota
As ações de alta densidade disparam formulários em modais Dialog centralizados ou gavetas laterais Sheet, garantindo que o operador não perca o contexto de navegação.

---

## 3. Catálogo de Botões Faltantes (Gaps de Interação & UX)

| Botão Faltante | Localização Sugerida na Tela | O Que Deveria Abrir / Fazer | Por Que Está Faltando (Impacto na Jornada) | Micro-Ticket Vinculado |
| :--- | :--- | :--- | :--- | :--- |
| **Sugestão Automática de Ação no Chatwoot** | Barra de ações da rota | Botão no card de churn que já dispara mensagem no WhatsApp | Lacuna identificada no fluxo | `TICKET-INT-01` |
| **Indexar Novo Manual Técnico no RAG** | Barra de ações da rota | Interface para upload direto de PDFs científicos no vector store | Lacuna identificada no fluxo | `TICKET-INT-02` |
