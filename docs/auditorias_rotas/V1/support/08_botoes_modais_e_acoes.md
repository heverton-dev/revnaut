# 08. Auditoria Anatômica de Botões, Modais & Ações de Interface — Rota: support

## 1. Inventário Factual de Botões Existentes na Rota

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | O Que Abre / Dispara | Por Que Existe (Propósito de Negócio) | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Abrir Laudo RMA / Devolução** | Interação direta | Inicia protocolo de quarentena de implante fraturado | Ação reativa | Suporte operacional | **100% Funcional** |
| **Enviar para Análise Metalúrgica** | Interação direta | Atualiza status do lote com parecer laboratorial | Ação reativa | Suporte operacional | **100% Funcional** |
| **Emitir Alerta de Tecnovigilância ANVISA** | Interação direta | Prepara notificação sanitária obrigatória | Ação reativa | Suporte operacional | **100% Funcional** |
| **Enviar Questionário Pós-Operatório** | Interação direta | Dispara WhatsApp com escala visual de dor (EVA) | Ação reativa | Suporte operacional | **100% Funcional** |

---

## 2. Modais e Gavetas (Drawers) na Rota
As ações de alta complexidade disparam formulários em modais Dialog centralizados ou gavetas laterais Sheet, garantindo que o operador não perca o contexto de navegação.

---

## 3. Catálogo de Botões Faltantes (Gaps de Interação & UX)

| Botão Faltante | Localização Sugerida na Tela | O Que Deveria Abrir / Fazer | Por Que Está Faltando (Impacto na Jornada) | Micro-Ticket Vinculado |
| :--- | :--- | :--- | :--- | :--- |
| **Substituição Imediata em Garantia** | Barra de ações da rota | Atalho para despachar implante novo sem custo via DENTGO | Lacuna identificada no fluxo | `TICKET-SUP-01` |
| **Upload de Raio-X Pós-Cirúrgico** | Barra de ações da rota | Anexo de comprovação de osteointegração no chamado | Lacuna identificada no fluxo | `TICKET-SUP-02` |
