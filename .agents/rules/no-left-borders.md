# Quality Gate de Design System AIDD: Proibição Estrita de Bordas Laterais Coloridas (Anti-Flop Invariant)

> **Invariante P0:** Fica formalmente e categoricamente proibido em todo o repositório o uso de `border-left`, `border-right`, `border-top` ou qualquer variação de bordas laterais assimétricas coloridas decorativas em itens de menu, cartões (cards), botões, tabelas, modais, alertas ou toasts.

---

### Diretrizes de Substituição Mandatórias

1. **Menu Lateral (Sidebar Links Ativos e em Hover):**
   - **PROIBIDO:** `border-left: 3px solid var(--color-brand);` ou qualquer borda lateral.
   - **PADRÃO OBRIGATÓRIO (Design Raycast / Linear):**
     - O item ativo deve ser destacado com preenchimento sutil de fundo (`background: var(--color-brand-light)` ou tonalidade neutra com alto contraste no light mode).
     - Tipografia e ícone com a cor semântica ou de destaque (`color: var(--color-brand)`).
     - Arredondamento harmônico nos 4 cantos (`border-radius: var(--radius-sm)`).
     - Borda transparente ou inexistente (`border: none`).

2. **Cartões de Métricas (KPI Cards) e Alertas:**
   - **PROIBIDO:** `border-left: 3px solid #cor;` simulando "tarja lateral de status".
   - **PADRÃO OBRIGATÓRIO:**
     - Borda sutil e uniforme nos 4 cantos (`border: 1px solid var(--border-card)`).
     - Diferenciação semântica realizada via ícone vetorial, tag/badge pill interna ou subtexto colorido de alto contraste.

3. **Toasts e Notificações:**
   - **PROIBIDO:** `border-left: 3px solid var(--color-emerald);`
   - **PADRÃO OBRIGATÓRIO:** Caixa fechada moderna com sombra suave, borda 360° tênue e ícone semântico indicativo.

4. **Rodapé de Usuário da Barra Lateral:**
   - Quando recolhida (`.sidebar.collapsed`), deve exibir estritamente um único elemento centralizado (o avatar do usuário), ocultando botões duplicados ou redundantes de navegação.
