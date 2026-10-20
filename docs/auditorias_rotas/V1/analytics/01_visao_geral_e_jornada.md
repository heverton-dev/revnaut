# 01. Visão Geral e Jornada do Usuário — Rota: analytics

## 1. Identificação e Roteamento
- **Identificador / Slug:** `analytics`
- **Título Visual no Sistema:** Relatórios e Metas (Estúdio BI Superset & Text-to-SQL)
- **Classificação:** Frontend SPA View (Single Page Application com Hashbang Router)
- **URL de Produção:** `https://revnault.vpsconexao.org/#!/analytics`
- **Componente React Raiz:** `frontend/src/features/bi/SupersetEmbeddedDashboard.tsx`

---

## 2. Propósito e Objetivo de Negócio
A rota `analytics` atua no ecossistema RevOps proporcionando aos operadores clínicos e comerciais:
1. Controle determinístico dos fluxos de relatórios e metas (estúdio bi superset & text-to-sql).
2. Redução do tempo de atendimento e eliminação de processos analógicos na operação.
3. Rastreabilidade ponta a ponta com persistência auditável no SQLite WAL.

---

## 3. Abas e Sub-rotas Mapeadas
- **Aba `rls_studio`:** Estúdio BI com Apache Superset Embedded RLS
- **Aba `text_to_sql`:** Console Analítico Text-to-SQL com Proteção AST

---

## 4. Jornada e Fluxo Operacional
O usuário acessa `#!/analytics`, o sistema valida as permissões de RBAC do perfil ativo e carrega os dados específicos da fatia vertical. O operador interage através dos controles dedicados sem recarregar a aplicação.
