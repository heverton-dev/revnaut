# Manual da Rota: Relatórios Executivos & KPIs (`/#reports`, `/#reports-performance`)

## 1. Objetivo da Rota
Disponibilizar painéis analíticos e indicadores de Business Intelligence (BI) para acompanhamento da saúde financeira e comercial da empresa. Apresenta faturamento consolidado, margens brutas, evolução de ticket médio e o ranking de performance por consultor cirúrgico.

---

## 2. O Que o Usuário Consegue Realizar
* **Subrota Visão Geral & KPIs (`/#reports`):**
  * Visualizar MRR/ARR odontológico, receita total do mês, novos cirurgiões ativados e caixas em campo.
  * Analisar gráfico de tendência de vendas e taxa de churn de clínicas.
* **Subrota Performance de Vendas (`/#reports-performance`):**
  * Acompanhar o ranking dos consultores de maior volume de vendas diretas e consignadas.
  * Verificar medalhas de colocação técnica (1º, 2º e 3º lugares) e percentual de atingimento de cota individual.

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil | Acesso aos Relatórios | Nível de Dados Visualizados |
|---|---|---|
| Consultor de Vendas | Sim | Apenas seus próprios números e sua posição no ranking |
| Gerente Regional | Sim | Números consolidados da sua regional de vendas |
| Diretor de BU | Sim | Números consolidados da sua Business Unit |
| Super Admin / C-Level | Sim | DRE comercial e faturamento de toda a operação |

---

## 4. Quais Ações Podem Ser Realizadas
* `FILTER_PERIOD`: Alternar entre períodos de visualização (Mensal, Trimestral, Anual).
* `DRILL_DOWN_CONSULTANT`: Clicar no consultor do ranking para inspecionar seus negócios ganhos e perdidos.
* `EXPORT_REPORT`: Exportação de dados consolidados em formatos estruturados.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)
1. Acesse **Marketing & Scoring > Relatórios & KPIs**.
2. Na tela de visão geral, acompanhe os cards executivos superiores.
3. Para consultar o ranking individual da equipe, acesse a subrota **Performance de Vendas**.
4. Observe a tabela com volume total em R$, quantidade de cirurgias atendidas e percentual de batimento de meta.

---

## 6. O Que Falta Implementar (Roadmap & Gaps)
* Geração de relatórios executivos em formato PDF diagramado para apresentação a investidores e conselho.
* Gráficos dinâmicos interativos com curvas de tendência temporal (usando biblioteca gráfica leve sem dependências pesadas).
