# 08. Auditoria Anatômica de Botões, Modais & Ações de Interface — Rota: keypartners (Auditoria v2)

## 1. Inventário Factual de Botões Existentes na Rota

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | O Que Abre / Dispara | Por Que Existe (Propósito de Negócio) | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Cadastrar Nova Maleta** | Interação direta | Registra número de série e componentes do kit cirúrgico | Ação reativa | Suporte operacional | **100% Funcional** |
| **Emitir Remessa CFOP 5.113** | Interação direta | Gera documento fiscal de saída para consignação | Ação reativa | Suporte operacional | **100% Funcional** |
| **Despachar com Custódia** | Interação direta | Vincula entregador DENTGO com protocolo assinado | Ação reativa | Suporte operacional | **100% Funcional** |
| **Vincular Cirurgião KOL** | Interação direta | Registra speaker clínico e comissionamento acadêmico | Ação reativa | Suporte operacional | **100% Funcional** |

---

## 2. Modais e Gavetas (Drawers) na Rota
As ações de alta densidade disparam formulários em modais Dialog centralizados ou gavetas laterais Sheet, garantindo que o operador não perca o contexto de navegação.

---

## 3. Catálogo de Botões Faltantes (Gaps de Interação & UX)

| Botão Faltante | Localização Sugerida na Tela | O Que Deveria Abrir / Fazer | Por Que Está Faltando (Impacto na Jornada) | Micro-Ticket Vinculado |
| :--- | :--- | :--- | :--- | :--- |
| **Auditoria de Maleta via QR Code** | Barra de ações da rota | Scanner para conferência física de implantes na devolução | Lacuna identificada no fluxo | `TICKET-KEY-01` |
| **Renovação Automática de Termo** | Barra de ações da rota | Botão para estender comodato por mais 30 dias | Lacuna identificada no fluxo | `TICKET-KEY-02` |
