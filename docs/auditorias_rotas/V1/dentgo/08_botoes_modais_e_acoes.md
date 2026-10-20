# 08. Auditoria Anatômica de Botões, Modais & Ações de Interface — Rota: dentgo

## 1. Inventário Factual de Botões Existentes na Rota

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | O Que Abre / Dispara | Por Que Existe (Propósito de Negócio) | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Nova Solicitação Express** | Interação direta | Abre formulário para chamar motoboy para cirurgia | Ação reativa | Suporte operacional | **100% Funcional** |
| **Rastrear no Mapa** | Interação direta | Exibe rota e localização GPS do entregador | Ação reativa | Suporte operacional | **100% Funcional** |
| **Aprovar Oferta Flash FEFO** | Interação direta | Ativa desconto agressivo para itens próximos da validade | Ação reativa | Suporte operacional | **100% Funcional** |
| **Repassar Split Financeiro** | Interação direta | Dispara liquidação da taxa do operador logístico | Ação reativa | Suporte operacional | **100% Funcional** |

---

## 2. Modais e Gavetas (Drawers) na Rota
As ações de alta complexidade disparam formulários em modais Dialog centralizados ou gavetas laterais Sheet, garantindo que o operador não perca o contexto de navegação.

---

## 3. Catálogo de Botões Faltantes (Gaps de Interação & UX)

| Botão Faltante | Localização Sugerida na Tela | O Que Deveria Abrir / Fazer | Por Que Está Faltando (Impacto na Jornada) | Micro-Ticket Vinculado |
| :--- | :--- | :--- | :--- | :--- |
| **Assinatura Digital de Entrega** | Barra de ações da rota | Coleta de rubrica digital do cirurgião no ato do recebimento | Lacuna identificada no fluxo | `TICKET-DENTGO-01` |
| **Comprovante Fotográfico do Lote** | Barra de ações da rota | Upload de foto do implante entregue na sala cirúrgica | Lacuna identificada no fluxo | `TICKET-DENTGO-02` |
