# 08. Auditoria Anatômica de Botões, Modais & Ações de Interface — Rota: settings (Auditoria v2)

## 1. Inventário Factual de Botões Existentes na Rota

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | O Que Abre / Dispara | Por Que Existe (Propósito de Negócio) | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Salvar Chave no Cofre** | Interação direta | Grava credencial com criptografia AES-256 no banco | Ação reativa | Suporte operacional | **100% Funcional** |
| **Testar Conexão com TOTVS ERP** | Interação direta | Valida comunicação SOAP/REST com o servidor ERP | Ação reativa | Suporte operacional | **100% Funcional** |
| **Disparar Webhook de Teste** | Interação direta | Envia payload simulado assinado com HMAC-SHA256 | Ação reativa | Suporte operacional | **100% Funcional** |
| **Convidar Novo Usuário** | Interação direta | Gera link de ativação com perfil RBAC predefinido | Ação reativa | Suporte operacional | **100% Funcional** |

---

## 2. Modais e Gavetas (Drawers) na Rota
As ações de alta densidade disparam formulários em modais Dialog centralizados ou gavetas laterais Sheet, garantindo que o operador não perca o contexto de navegação.

---

## 3. Catálogo de Botões Faltantes (Gaps de Interação & UX)

| Botão Faltante | Localização Sugerida na Tela | O Que Deveria Abrir / Fazer | Por Que Está Faltando (Impacto na Jornada) | Micro-Ticket Vinculado |
| :--- | :--- | :--- | :--- | :--- |
| **Rotação Automática de Chaves** | Barra de ações da rota | Botão para renovar tokens e chaves com prazo de validade | Lacuna identificada no fluxo | `TICKET-SET-01` |
| **Log de Acesso ao Cofre (Quem Acessou O Quê)** | Barra de ações da rota | Visualizador de auditoria de consultas aos segredos | Lacuna identificada no fluxo | `TICKET-SET-02` |
