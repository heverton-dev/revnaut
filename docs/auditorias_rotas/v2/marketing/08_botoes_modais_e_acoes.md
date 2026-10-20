# 08. Auditoria Anatômica de Botões, Modais & Ações de Interface — Rota: marketing (Auditoria v2)

## 1. Inventário Factual de Botões Existentes na Rota

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | O Que Abre / Dispara | Por Que Existe (Propósito de Negócio) | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Criar Nova Landing Page** | Interação direta | Abre formulário para criação de URL e seleção de tema | Ação reativa | Suporte operacional | **100% Funcional** |
| **Abrir Editor GrapesJS** | Interação direta | Carrega o canvas drag-and-drop de blocos | Ação reativa | Suporte operacional | **100% Funcional** |
| **Publicar Página** | Interação direta | Salva HTML/CSS no Cloudflare R2 e ativa rota pública | Ação reativa | Suporte operacional | **100% Funcional** |
| **Gerar Link de Indicação MGM** | Interação direta | Emite link exclusivo com rastreamento UTM | Ação reativa | Suporte operacional | **100% Funcional** |

---

## 2. Modais e Gavetas (Drawers) na Rota
As ações de alta densidade disparam formulários em modais Dialog centralizados ou gavetas laterais Sheet, garantindo que o operador não perca o contexto de navegação.

---

## 3. Catálogo de Botões Faltantes (Gaps de Interação & UX)

| Botão Faltante | Localização Sugerida na Tela | O Que Deveria Abrir / Fazer | Por Que Está Faltando (Impacto na Jornada) | Micro-Ticket Vinculado |
| :--- | :--- | :--- | :--- | :--- |
| **Teste A/B Automatizado** | Barra de ações da rota | Botão para splitar tráfego entre 2 variantes de landing page | Lacuna identificada no fluxo | `TICKET-MKT-01` |
| **Pré-visualização Multi-Dispositivo** | Barra de ações da rota | Alternador de viewport mobile/tablet direto no canvas | Lacuna identificada no fluxo | `TICKET-MKT-02` |
