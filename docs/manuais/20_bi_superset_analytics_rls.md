# Manual da Rota: BI Superset Executivo & Analytics RLS (`#bi-superset`)

## 1. Objetivo da Rota
Apresentar paineis analiticos executivos, relatorios de receita, predicoes de Share of Kit (SOK), calculo de margem liquida cirurgica real e monitoramento de Health Score Cirurgico (HSC), utilizando dashboards embarcados do Apache Superset protegidos por Row-Level Security (RLS).

---

## 2. O Que o Usuário Consegue Realizar
* Consultar paineis analiticos consolidados da operacao odontologica na rota `#bi-superset`:
  1. Margem Liquida Real por Tipo de Procedimento Clinico.
  2. Health Score Cirurgico (HSC) e Radar Anti-Churn.
  3. Previsao de Share of Kit (SOK) e Frequencia de Recompra.
  4. Performance de Despacho Logistico DENTGO (SLA 45 min).
* Filtrar analises por periodo, regiao, franquia ou linha de implantes.
* Exportar relatorios e graficos em PDF ou planilhas analiticas.
* Navegar por dados isolados deterministicamente pelo RLS de cada tenant.

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil | Acesso a Dashboards | Visualizacao de Margem | Filtro por Regiao | Exportacao de Relatorios |
|---|---|---|---|---|
| Consultor de Campo | Apenas seus numeros | Nao | Sua carteira | Nao |
| Gerente Regional | Numeros da sua regional | Sim (regional) | Sua regional | Sim |
| Diretor de BU | Visao consolidada da BU | Sim (global) | Todas as regioes | Sim |
| Super Admin | Acesso irrestrito a todos os dados | Sim | Global | Sim (Total) |

---

## 4. Quais Ações Podem Ser Realizadas
* `CHANGE_DASHBOARD`: Alternar entre painel financeiro, logistico ou cirurgico.
* `APPLY_FILTER`: Filtrar visualizacao por data ou regiao comercial.
* `DRILL_DOWN`: Clicar em metricas para detalhar clinicas ou cirurgioes especificos.
* `EXPORT_CHART`: Baixar imagem ou dados brutos de graficos selecionados.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)

### Consulta de Dashboards Analiticos
1. No menu lateral, clique em "BI Superset Analytics" na rota `#bi-superset`.
2. O sistema autentica automaticamente a sessao do usuario gerando um Guest Token JWT no Apache Superset.
3. O painel correspondente ao perfil de acesso do usuario e carregado de forma interativa.

---

## 6. O Que Falta Implementar
* Agendamento automatizado de envio de resumos semanais de BI diretamente no WhatsApp da diretoria executiva.
