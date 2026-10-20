# 01. Visão Geral e Jornada do Usuário — Rota: analytics (Auditoria v2)

## 1. Identificação e Roteamento
- **Identificador / Slug:** `analytics`
- **Título Visual no Sistema:** Relatórios BI Superset & Text-to-SQL AST
- **Classificação:** Frontend SPA View (Single Page Application com Hashbang Router)
- **URL Canônica:** `https://revnault.vpsconexao.org/#!/analytics`
- **Componente React Raiz:** `frontend/src/features/bi/SupersetEmbeddedDashboard.tsx`
- **Ciclo de Auditoria:** v2 (Pós-implementação de gaps e tickets de produção)

---

## 2. Propósito e Objetivo de Negócio
A rota `analytics` atua no ecossistema RevOps proporcionando aos operadores clínicos e comerciais:
1. Controle determinístico dos fluxos de relatórios bi superset & text-to-sql ast.
2. Redução do tempo de atendimento operacional e eliminação de processos analógicos em campo.
3. Rastreabilidade regulatória ponta a ponta com persistência auditável em SQLite WAL.

---

## 3. Abas e Sub-rotas Mapeadas
- **Aba / Sub-aba `rls_studio`:** Estúdio BI com Apache Superset Embedded RLS
- **Aba / Sub-aba `text_to_sql`:** Console Analítico Text-to-SQL com Proteção AST

---

## 4. Jornada e Fluxo Operacional
O usuário autenticado acessa a rota `#!/analytics`. O sistema valida os privilégios do papel ativo no RBAC e carrega os dados específicos da fatia vertical de backend de forma reativa. O operador interage através dos controles dedicados sem recarregar a aplicação.
