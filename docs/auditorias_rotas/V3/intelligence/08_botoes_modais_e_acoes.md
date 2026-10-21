# 08. Auditoria Anatômica de Botões, Modais & Ações — Rota: intelligence (Auditoria V3)

## 1. Inventário Factual de Botões Existentes

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- |
| **Recalcular Risco de Evasão** | Interação direta | Executa modelo RFM determinístico sobre histórico de compras | **100% Funcional** |
| **Filtrar Grafo KOL por Especialidade** | Interação direta | Destaca polos acadêmicos e cirurgiões speakers | **100% Funcional** |
| **Consultar Assistente Clínico RAG** | Interação direta | Busca em embeddings vetoriais com citações do catálogo | **100% Funcional** |
| **Exportar Indicadores de Evasão** | Interação direta | Download de lista de cirurgiões em risco de churn | **100% Funcional** |

---

## 2. Gaps de Interação & Botões Sugeridos
- **Sugestão Automática de Ação no Chatwoot** (`TICKET-INT-01`): Botão no card de churn que já dispara mensagem no WhatsApp
- **Indexar Novo Manual Técnico no RAG** (`TICKET-INT-02`): Interface para upload direto de PDFs científicos no vector store