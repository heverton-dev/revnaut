# 08. Auditoria Anatômica de Botões, Modais & Ações de Interface — Rota: contracts

## 1. Inventário Factual de Botões Existentes na Rota

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | O Que Abre / Dispara | Por Que Existe (Propósito de Negócio) | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Criar Novo Contrato** | Interação direta | Gera minuta a partir de template e dados do cirurgião | Ação reativa | Suporte operacional | **100% Funcional** |
| **Enviar para Assinatura** | Interação direta | Dispara envelope via Documenso para e-mail/WhatsApp | Ação reativa | Suporte operacional | **100% Funcional** |
| **Baixar PDF Assinado com Certificado** | Interação direta | Download de documento com carimbo de tempo | Ação reativa | Suporte operacional | **100% Funcional** |
| **Consultar Validade do Lote ANVISA** | Interação direta | Checa quarentena ou pendência regulatória | Ação reativa | Suporte operacional | **100% Funcional** |

---

## 2. Modais e Gavetas (Drawers) na Rota
As ações de alta complexidade disparam formulários em modais Dialog centralizados ou gavetas laterais Sheet, garantindo que o operador não perca o contexto de navegação.

---

## 3. Catálogo de Botões Faltantes (Gaps de Interação & UX)

| Botão Faltante | Localização Sugerida na Tela | O Que Deveria Abrir / Fazer | Por Que Está Faltando (Impacto na Jornada) | Micro-Ticket Vinculado |
| :--- | :--- | :--- | :--- | :--- |
| **Assinatura Presencial na Tela** | Barra de ações da rota | Coleta de assinatura manuscrita em tablet/touchscreen | Lacuna identificada no fluxo | `TICKET-DOC-01` |
| **Renovação Automática de Vigência** | Barra de ações da rota | Gatilho de prorrogação de contrato de comodato | Lacuna identificada no fluxo | `TICKET-DOC-02` |
