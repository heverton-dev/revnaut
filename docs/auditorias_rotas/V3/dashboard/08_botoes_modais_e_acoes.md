# 08. Auditoria Anatômica de Botões, Modais & Ações — Rota: dashboard (Auditoria V3)

## 1. Inventário Factual de Botões Existentes

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- |
| **Visualizar por Estágio** | Interação direta | Alterna o gráfico central para visão por estágio de funil | **100% Funcional** |
| **Visualizar por Tendência** | Interação direta | Alterna o gráfico central para série temporal de MRR | **100% Funcional** |
| **Visualizar Consignação** | Interação direta | Alterna o gráfico central para giro de maletas e CFOP 5.113 | **100% Funcional** |
| **Card Pipeline Total** | Interação direta | Exibe valor total negociado e taxa de conversão | **100% Funcional** |
| **Card MRR / Fechado Ganho** | Interação direta | Exibe receita recorrente e novos contratos | **100% Funcional** |
| **Card Performance Mídia** | Interação direta | Exibe ROAS consolidado e CAC médio | **100% Funcional** |
| **Card Alertas de Churn** | Interação direta | Exibe contagem de cirurgiões em risco crítico | **100% Funcional** |

---

## 2. Gaps de Interação & Botões Sugeridos
- **Exportar Relatório Executivo PDF** (`TICKET-DASH-01`): Disparo direto de download do snapshot do cockpit
- **Filtro Global por Regional** (`TICKET-DASH-02`): Dropdown para filtrar KPIs por divisão geográfica