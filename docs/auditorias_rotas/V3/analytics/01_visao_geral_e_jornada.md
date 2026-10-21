# 01. Visão Geral e Jornada do Usuário — Rota: analytics (Auditoria V3)

## 1. Identificação Técnica
- **Rota Visual:** `https://revnault.vpsconexao.org/#!/analytics`
- **Título Oficial:** Relatórios BI Superset & Text-to-SQL AST
- **Componente Front-end:** `frontend/src/features/bi/SupersetEmbeddedDashboard.tsx`
- **Motores Backend:** `src/features/analytics/router.py`, `src/features/bi/router.py`
- **Suíte de Testes:** `tests/test_superset_rls_embedded.py`, `tests/test_text_to_sql_dynamic.py`, `tests/test_text_to_sql_security.py`

---

## 2. Jornada do Usuário Real
O usuário acessa o módulo para executar operações cirúrgicas e comerciais sem atrito:
1. **Entrada na Tela:** Carregamento otimizado com dados reais via SQLite WAL.
2. **Navegação por Abas:** Alternância fluida entre as visões do módulo.
3. **Ações Primárias:** Interação com botões de alta densidade sem stubs ou toasts vazios.

---

## 3. Abas e Sub-Rotas Mapeadas
- **Aba `rls_studio`:** Estúdio BI com Apache Superset Embedded RLS
- **Aba `text_to_sql`:** Console Analítico Text-to-SQL com Proteção AST