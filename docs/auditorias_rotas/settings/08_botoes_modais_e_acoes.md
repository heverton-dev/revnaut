# 08. Auditoria Anatômica de Botões, Modais & Ações de Interface — Rota: settings

## 1. Inventário Factual de Botões Existentes na Rota

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | O Que Abre / Dispara | Por Que Existe (Propósito de Negócio) | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Salvar Chaves no Cofre** | Interação direta | Grava credenciais criptografadas no banco seguro | Ação reativa | Suporte operacional | **100% Funcional** |
| **Testar Conexão TOTVS** | Interação direta | Executa ping no web service Protheus e valida token | Ação reativa | Suporte operacional | **100% Funcional** |
| **Criar Novo Webhook Endpoint** | Interação direta | Cadastra URL de destino para eventos de domínio | Ação reativa | Suporte operacional | **100% Funcional** |
| **Disparar Teste de Ping HMAC** | Interação direta | Envia payload simulado assinado com segredo HMAC | Ação reativa | Suporte operacional | **100% Funcional** |

---

## 2. Modais e Gavetas (Drawers) na Rota
As ações de alta complexidade disparam formulários em modais Dialog centralizados ou gavetas laterais Sheet, garantindo que o operador não perca o contexto de navegação.

---

## 3. Catálogo de Botões Faltantes (Gaps de Interação & UX)

| Botão Faltante | Localização Sugerida na Tela | O Que Deveria Abrir / Fazer | Por Que Está Faltando (Impacto na Jornada) | Micro-Ticket Vinculado |
| :--- | :--- | :--- | :--- | :--- |
| **Rotação Automática de Chaves** | Barra de ações da rota | Revoga segredo antigo e gera nova chave de API | Lacuna identificada no fluxo | `TICKET-SETT-01` |
| **Re-tentativa Manual de Webhooks com Falha** | Barra de ações da rota | Botão de replay para eventos com status 500 | Lacuna identificada no fluxo | `TICKET-SETT-02` |
