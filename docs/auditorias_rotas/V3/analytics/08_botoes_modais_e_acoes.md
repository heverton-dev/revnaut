# 08. Auditoria Anatômica de Botões, Modais & Ações — Rota: analytics (Auditoria V3)

## 1. Inventário Factual de Botões Existentes

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- |
| **Carregar Dashboard Superset** | Interação direta | Gera token de autenticação e injeta iframe seguro | **100% Funcional** |
| **Executar Pergunta Text-to-SQL** | Interação direta | Traduz pergunta natural em SQL auditado por AST parser | **100% Funcional** |
| **Exportar Resultados SQL em CSV** | Interação direta | Download instantâneo da tabela de dados resultante | **100% Funcional** |
| **Alternar Filtros de Tempo (7d, 30d, 90d)** | Interação direta | Atualiza parâmetros das visualizações analíticas | **100% Funcional** |

---

## 2. Gaps de Interação & Botões Sugeridos
- **Salvar Consulta no Favoritos** (`TICKET-ANA-01`): Botão para favoritar queries frequentes de Text-to-SQL
- **Agendamento de Envio por E-mail** (`TICKET-ANA-02`): Disparo automático do relatório consolidado semanal