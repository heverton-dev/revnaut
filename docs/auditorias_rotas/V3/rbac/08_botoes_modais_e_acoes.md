# 08. Auditoria Anatômica de Botões, Modais & Ações — Rota: rbac (Auditoria V3)

## 1. Inventário Factual de Botões Existentes

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- |
| **Adicionar Nó na Hierarquia** | Interação direta | Cria regional, gerente ou consultor na estrutura | **100% Funcional** |
| **Salvar Matriz de Permissões** | Interação direta | Persiste escopos de leitura/escrita por perfil no SQLite | **100% Funcional** |
| **Definir Meta de Vendas** | Interação direta | Configura cota mensal de faturamento para o consultor | **100% Funcional** |
| **Calcular Comissões do Mês** | Interação direta | Executa motor de cálculo com faixas progressivas e aceleradores | **100% Funcional** |

---

## 2. Gaps de Interação & Botões Sugeridos
- **Simulador de Comissões para o Vendedor** (`TICKET-RBAC-01`): Calculadora interativa na tela do consultor comercial
- **Histórico de Alterações de Cargo** (`TICKET-RBAC-02`): Timeline de promoções e transferências de região