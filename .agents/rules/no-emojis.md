# Regra Inviolável: Proibição Absoluta de Emojis em Código e Interfaces (UI/UX)

> **Severidade:** P0 / Quality Gate Bloqueante (Exit 1)  
> **Escopo:** Todo o código de frontend (HTML, CSS, JS, JSX, TSX), strings de interface, botões, badges, modais, alertas e toasts.

---

## 1. Diretriz Inviolável

**É TERMINANTEMENTE PROIBIDO o uso de emojis Unicode em qualquer elemento de interface do usuário.**

Isso inclui, mas não se limita a:
- Emojis de tema/modo: `🌙`, `☀️`, `⚡`, `🎨`, `💡`
- Emojis de busca e filtros: `🔍`, setas unicode como `↓`, `↑`, `➡️`
- Emojis de status/feedback: `✅`, `❌`, `⚠️`, `🚨`, `ℹ️`, `🟢`, `🔴`
- Emojis decorativos ou de categorias: `🚀`, `🔥`, `✨`, `📈`, `🏥`, `🦷`

---

## 2. Padrão Obrigatório de Substituição (Padrão shadcn / Lucide)

1. **Iconografia Vetorial SVG (shadcn / Lucide)**:
   Toda representação gráfica de status, ações, buscas ou ferramentas deve utilizar **estritamente SVGs vetoriais inline no padrão shadcn / Lucide** com dimensões controladas (ex: 13x13px, 14x14px), `viewBox="0 0 24 24"`, `fill="none"`, `stroke="currentColor"`, `stroke-width="2"`, `stroke-linecap="round"`, `stroke-linejoin="round"`.
   - Busca padrão: `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>`

2. **Rótulos Semânticos em Texto Limpo**:
   - Em vez de `🌙 Escuro` ➔ usar `Escuro` com SVG de lua (se necessário) ou apenas o rótulo limpo `Escuro`.
   - Em vez de `☀️ Claro` ➔ usar `Claro` ou `Claro (Alto Contraste)`.
   - Em vez de `✅ Sucesso` ➔ usar `Sucesso` ou badge semântico com cor de status.
   - Em vez de `⚡ Transbordar` ➔ usar `Transbordar para Closer`.

3. **Toasts e Notificações**:
   Toasts devem conter apenas texto claro e sóbrio em PT-BR corporativo, sem emojis no corpo da mensagem.
