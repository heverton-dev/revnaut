# 08. Auditoria Anatômica de Botões, Modais & Ações — Rota: contracts (Auditoria V3)

## 1. Inventário Factual de Botões Existentes

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- |
| **Novo Contrato** | Interação direta | Gera documento a partir de template e envia para Documenso | **100% Funcional** |
| **Verificar Status da Assinatura** | Interação direta | Consulta webhook e polling da assinatura de partes | **100% Funcional** |
| **Download PDF Assinado** | Interação direta | Recupera versão imutável armazenada no Cloudflare R2 | **100% Funcional** |
| **Vincular Lote ANVISA** | Interação direta | Adiciona número de registro regulatório da peça no termo | **100% Funcional** |

---

## 2. Gaps de Interação & Botões Sugeridos
- **Assinatura com Certificado ICP-Brasil** (`TICKET-DOC-01`): Suporte a token A1/A3 para contratos de alto valor
- **Lembrete de Assinatura por WhatsApp** (`TICKET-DOC-02`): Botão para reenviar link de assinatura via WhatsApp