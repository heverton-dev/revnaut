# 08. Auditoria Anatômica de Botões, Modais & Ações de Interface — Rota: keypartners

## 1. Inventário Factual de Botões Existentes na Rota

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | O Que Abre / Dispara | Por Que Existe (Propósito de Negócio) | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Nova Maleta Cirúrgica** | Interação direta | Cadastra kit com serial e lote de implantes | Ação reativa | Suporte operacional | **100% Funcional** |
| **Gerar Nota de Remessa CFOP 5.113** | Interação direta | Sincroniza com TOTVS para faturamento fiscal | Ação reativa | Suporte operacional | **100% Funcional** |
| **Registrar Consumo Cirúrgico** | Interação direta | Dá baixa nos implantes utilizados e fatura CFOP 5.114 | Ação reativa | Suporte operacional | **100% Funcional** |
| **Auditar Saldo de Custódia** | Interação direta | Emite relatório de conferência física hospitalar | Ação reativa | Suporte operacional | **100% Funcional** |

---

## 2. Modais e Gavetas (Drawers) na Rota
As ações de alta complexidade disparam formulários em modais Dialog centralizados ou gavetas laterais Sheet, garantindo que o operador não perca o contexto de navegação.

---

## 3. Catálogo de Botões Faltantes (Gaps de Interação & UX)

| Botão Faltante | Localização Sugerida na Tela | O Que Deveria Abrir / Fazer | Por Que Está Faltando (Impacto na Jornada) | Micro-Ticket Vinculado |
| :--- | :--- | :--- | :--- | :--- |
| **Leitor de Código de Barras / DataMatrix** | Barra de ações da rota | Abertura de câmera para bipar lotes ANVISA na maleta | Lacuna identificada no fluxo | `TICKET-KEY-01` |
| **Reposição Rápida via DENTGO** | Barra de ações da rota | Gatilho de reposição automática de itens consumidos | Lacuna identificada no fluxo | `TICKET-KEY-02` |
