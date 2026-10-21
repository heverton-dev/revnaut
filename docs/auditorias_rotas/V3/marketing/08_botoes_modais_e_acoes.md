# 08. Auditoria Anatômica de Botões, Modais & Ações — Rota: marketing (Auditoria V3)

## 1. Inventário Factual de Botões Existentes

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- |
| **Criar Nova Landing Page** | Interação direta | Abre formulário para criação de URL e seleção de tema | **100% Funcional** |
| **Abrir Editor GrapesJS** | Interação direta | Carrega o canvas drag-and-drop de blocos | **100% Funcional** |
| **Publicar Página** | Interação direta | Salva HTML/CSS no Cloudflare R2 e ativa rota pública | **100% Funcional** |
| **Gerar Link de Indicação MGM** | Interação direta | Emite link exclusivo com rastreamento UTM | **100% Funcional** |

---

## 2. Gaps de Interação & Botões Sugeridos
- **Teste A/B Automatizado** (`TICKET-MKT-01`): Botão para splitar tráfego entre 2 variantes de landing page
- **Pré-visualização Multi-Dispositivo** (`TICKET-MKT-02`): Alternador de viewport mobile/tablet direto no canvas