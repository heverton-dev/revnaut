# 08. Auditoria Anatômica de Botões, Modais & Ações de Interface — Rota: analytics

## 1. Inventário Factual de Botões Existentes na Rota

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | O Que Abre / Dispara | Por Que Existe (Propósito de Negócio) | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Executar Pergunta em Linguagem Natural** | Interação direta | Traduz pergunta para SQL com proteção AST | Ação reativa | Suporte operacional | **100% Funcional** |
| **Emitir Guest Token Superset** | Interação direta | Gera JWT de embed com restrição de tenant | Ação reativa | Suporte operacional | **100% Funcional** |
| **Exportar Dataset Parquet** | Interação direta | Salva arquivo colunar no Cloudflare R2 | Ação reativa | Suporte operacional | **100% Funcional** |
| **Visualizar SQL Gerado** | Interação direta | Expande query de banco para inspeção técnica | Ação reativa | Suporte operacional | **100% Funcional** |

---

## 2. Modais e Gavetas (Drawers) na Rota
As ações de alta complexidade disparam formulários em modais Dialog centralizados ou gavetas laterais Sheet, garantindo que o operador não perca o contexto de navegação.

---

## 3. Catálogo de Botões Faltantes (Gaps de Interação & UX)

| Botão Faltante | Localização Sugerida na Tela | O Que Deveria Abrir / Fazer | Por Que Está Faltando (Impacto na Jornada) | Micro-Ticket Vinculado |
| :--- | :--- | :--- | :--- | :--- |
| **Salvar Pergunta nos Favoritos** | Barra de ações da rota | Cria atalho para queries analíticas frequentes | Lacuna identificada no fluxo | `TICKET-ANA-01` |
| **Compartilhar Dashboard com a Equipe** | Barra de ações da rota | Gera link de visualização restrito por perfil | Lacuna identificada no fluxo | `TICKET-ANA-02` |
