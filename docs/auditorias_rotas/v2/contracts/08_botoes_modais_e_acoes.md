# 08. Auditoria Anatômica de Botões, Modais & Ações de Interface — Rota: contracts (Auditoria v2)

## 1. Inventário Factual de Botões Existentes na Rota

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | O Que Abre / Dispara | Por Que Existe (Propósito de Negócio) | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Novo Contrato** | Interação direta | Gera documento a partir de template e envia para Documenso | Ação reativa | Suporte operacional | **100% Funcional** |
| **Verificar Status da Assinatura** | Interação direta | Consulta webhook e polling da assinatura de partes | Ação reativa | Suporte operacional | **100% Funcional** |
| **Download PDF Assinado** | Interação direta | Recupera versão imutável armazenada no Cloudflare R2 | Ação reativa | Suporte operacional | **100% Funcional** |
| **Vincular Lote ANVISA** | Interação direta | Adiciona número de registro regulatório da peça no termo | Ação reativa | Suporte operacional | **100% Funcional** |

---

## 2. Modais e Gavetas (Drawers) na Rota
As ações de alta densidade disparam formulários em modais Dialog centralizados ou gavetas laterais Sheet, garantindo que o operador não perca o contexto de navegação.

---

## 3. Catálogo de Botões Faltantes (Gaps de Interação & UX)

| Botão Faltante | Localização Sugerida na Tela | O Que Deveria Abrir / Fazer | Por Que Está Faltando (Impacto na Jornada) | Micro-Ticket Vinculado |
| :--- | :--- | :--- | :--- | :--- |
| **Assinatura com Certificado ICP-Brasil** | Barra de ações da rota | Suporte a token A1/A3 para contratos de alto valor | Lacuna identificada no fluxo | `TICKET-DOC-01` |
| **Lembrete de Assinatura por WhatsApp** | Barra de ações da rota | Botão para reenviar link de assinatura via WhatsApp | Lacuna identificada no fluxo | `TICKET-DOC-02` |
