# 08. Auditoria Anatômica de Botões, Modais & Ações — Rota: settings (Auditoria V3)

## 1. Inventário Factual de Botões Existentes

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- |
| **Salvar Chave no Cofre** | Interação direta | Grava credencial com criptografia AES-256 no banco | **100% Funcional** |
| **Testar Conexão com TOTVS ERP** | Interação direta | Valida comunicação SOAP/REST com o servidor ERP | **100% Funcional** |
| **Disparar Webhook de Teste** | Interação direta | Envia payload simulado assinado com HMAC-SHA256 | **100% Funcional** |
| **Convidar Novo Usuário** | Interação direta | Gera link de ativação com perfil RBAC predefinido | **100% Funcional** |

---

## 2. Gaps de Interação & Botões Sugeridos
- **Rotação Automática de Chaves** (`TICKET-SET-01`): Botão para renovar tokens e chaves com prazo de validade
- **Log de Acesso ao Cofre (Quem Acessou O Quê)** (`TICKET-SET-02`): Visualizador de auditoria de consultas aos segredos