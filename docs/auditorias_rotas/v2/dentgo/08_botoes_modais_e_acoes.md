# 08. Auditoria Anatômica de Botões, Modais & Ações de Interface — Rota: dentgo (Auditoria v2)

## 1. Inventário Factual de Botões Existentes na Rota

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | O Que Abre / Dispara | Por Que Existe (Propósito de Negócio) | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Solicitar Entrega SOS** | Interação direta | Abre formulário prioritário com entrega em até 45 minutos | Ação reativa | Suporte operacional | **100% Funcional** |
| **Localizar no Mapa** | Interação direta | Exibe rota de entrega e localização GPS do estafeta | Ação reativa | Suporte operacional | **100% Funcional** |
| **Ativar Oferta Flash FEFO** | Interação direta | Publica desconto agressivo em implantes com lote próximo ao vencimento | Ação reativa | Suporte operacional | **100% Funcional** |
| **Aprovar Split do Entregador** | Interação direta | Libera repasse da taxa de entrega para o motorista | Ação reativa | Suporte operacional | **100% Funcional** |

---

## 2. Modais e Gavetas (Drawers) na Rota
As ações de alta densidade disparam formulários em modais Dialog centralizados ou gavetas laterais Sheet, garantindo que o operador não perca o contexto de navegação.

---

## 3. Catálogo de Botões Faltantes (Gaps de Interação & UX)

| Botão Faltante | Localização Sugerida na Tela | O Que Deveria Abrir / Fazer | Por Que Está Faltando (Impacto na Jornada) | Micro-Ticket Vinculado |
| :--- | :--- | :--- | :--- | :--- |
| **Alocação Inteligente de Hub** | Barra de ações da rota | Botão para sugerir o hub mais próximo com base no trânsito | Lacuna identificada no fluxo | `TICKET-DENTGO-01` |
| **Notificar Cirurgião por SMS** | Barra de ações da rota | Gatilho manual de SMS para equipe cirúrgica em campo | Lacuna identificada no fluxo | `TICKET-DENTGO-02` |
