# 08. Auditoria Anatômica de Botões, Modais & Ações — Rota: scoring (Auditoria V3)

## 1. Inventário Factual de Botões Existentes

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- |
| **Recalcular Scores** | Interação direta | Dispara recálculo determinístico em lote de toda a base | **100% Funcional** |
| **Filtrar por Tier (A/B/C)** | Interação direta | Filtra cards de cirurgiões pelo potencial cirúrgico | **100% Funcional** |
| **Exportar Matriz** | Interação direta | Gera snapshot das regras e clientes classificados | **100% Funcional** |

---

## 2. Gaps de Interação & Botões Sugeridos
- **Ajuste Interativo de Pesos (Sliders)** (`TICKET-SCORING-01`): Calibração dinâmica de pesos na UI pelo gestor
- **Handoff Automático para Vendedor** (`TICKET-SCORING-02`): Botão para atribuição automática de leads Tier A a consultores seniores