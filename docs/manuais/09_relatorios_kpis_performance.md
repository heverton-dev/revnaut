# Manual da Rota: Relatórios Executivos & KPIs (`/#reports`, `/#reports-performance`)

## 1. Objetivo da Rota
Disponibilizar painéis analíticos e indicadores de Business Intelligence (BI) para acompanhamento da receita industrial odontológica. Apresenta faturamento faturado versus projetado, volume de implantes/mês, margens brutas, ranking de performance por consultor e o **Índice de Risco Anti-Churn de Carteira**.

---

## 2. O Que o Usuário Consegue Realizar
* **Subrota Visão Geral & KPIs (`/#reports`):**
  * Visualizar MRR/ARR odontológico, receita faturada no mês, novos cirurgiões convertidos e caixas em campo.
  * Acompanhar o **Índice de Churn Preventivo (RFM)** indicando o volume financeiro em risco por cirurgiões em atraso de recompra.
  * Consolidar métricas filtradas pela subárvore do colaborador logado através de CTE recursiva SQLite WAL.
* **Subrota Performance de Vendas (`/#reports-performance`):**
  * Acompanhar o ranking da força de vendas em volume total faturado (R$) e quantidade de implantes comercializados.
  * Visualizar medalhas de colocação técnica (1º, 2º e 3º lugares) e percentual de batimento da meta individual do mês.

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil | Acesso aos Relatórios | Nível de Dados Visualizados |
|---|---|---|
| Consultor de Vendas | Sim | Apenas seus próprios números e sua posição no ranking |
| Coordenador de Equipe | Sim | Números consolidados da sua equipe de campo (`team_id`) |
| Gerente Regional | Sim | Números consolidados de toda a sua subárvore territorial (`subtree`) |
| Diretor de BU | Sim | Números consolidados da sua Business Unit |
| Super Admin (Heverton) / C-Level | Sim | DRE comercial e faturamento consolidado de todas as unidades |

---

## 4. Quais Ações Podem Ser Realizadas
* `FILTER_PERIOD`: Alternar entre períodos de visualização (Mensal, Trimestral, Anual).
* `INSPECT_CHURN_RISK`: Consultar o relatório de clientes com atraso no ciclo de reposição de implantes.
* `DRILL_DOWN_CONSULTANT`: Inspecionar os negócios ganhos, perdidos e comissões do vendedor.
* `EXPORT_REPORT`: Exportação de dados consolidados em planilha estruturada.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)
1. Acesse **Marketing & Scoring > Relatórios & KPIs**.
2. Na tela de visão geral, acompanhe os cards superiores com total faturado, caixas consignadas e valor sob risco de churn.
3. Para consultar o ranking individual da equipe, acesse a subrota **Performance de Vendas**.
4. Observe a tabela com volume total em R$, quantidade de cirurgias atendidas e percentual de batimento de meta.

---

## 6. O Que Falta Implementar (Roadmap & Gaps)
* Geração de relatórios executivos em formato PDF diagramado para apresentação a investidores e conselho de administração.
* Gráficos dinâmicos interativos com curvas de tendência temporal (usando biblioteca gráfica leve sem dependências pesadas de build).

---

## ANOTAÇÕES DO HEVERTON

* **[CÁLCULO RECURSIVO RBAC]**: As métricas de gerentes e diretores somam automaticamente todas as equipes descendentes via árvore de times (`WITH RECURSIVE`).
