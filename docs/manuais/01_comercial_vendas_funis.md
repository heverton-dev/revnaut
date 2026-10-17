# Manual da Rota: Vendas & Funis Setoriais (`/#deals`)

## 1. Objetivo da Rota
Operar o pipeline comercial e o funil de receitas da indústria de implantes e biomateriais odontológicos. Permite acompanhar as etapas de negociação desde a qualificação inicial de cirurgiões até o fechamento de pedidos de caixas cirúrgicas, contratos institucionais e vendas no atacado, com integração automática ao ERP TOTVS Protheus e Radar Anti-Churn de recompra.

---

## 2. O Que o Usuário Consegue Realizar
* Alternar entre 4 funis setoriais odontológicos:
  1. Cirurgiões & Venda Direta / Consignação de Caixas.
  2. Instituições de Ensino & Kits Acadêmicos (Faculdades Mandic, ABO, etc.).
  3. Distribuidores & Contratos de Atacado.
  4. Key Opinion Leaders (KOLs) & Eventos CIOSP.
* Alternar a visualização dos negócios entre Pipeline Kanban (colunas arrastáveis) e Tabela Analítica.
* Filtrar negociações por escopo de usuário simulado (RBAC hierárquico em tempo real via CTE recursiva SQLite WAL).
* Criar novas oportunidades comerciais informando título, cirurgião/decisor, clínica, valor estimado e estágio inicial.
* Mover negócios entre estágios (Qualificação, Demonstração Técnica, Proposta/Consignação, Fechamento).
* **Integração Automática ERP TOTVS Protheus:** Geração imediata de Pedido de Venda (`SC5` / `SC6`) e validação de crédito (`SA1`) ao mover o negócio para "Fechado & Ganho", com fila de retentativa idempotente (`integration_outbox`).
* **Radar Anti-Churn Odontológico (RFM):** Identificação e destaque visual de cirurgiões e clínicas com ciclo de recompra de implantes em atraso na rota `/api/v1/intelligence/churn-risk`.
* Acompanhar os KPIs da topbar: Valor Total em Pipeline, Ticket Médio Odontológico, Taxa de Conversão e Negócios Ativos.

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil | Visualização de Negócios | Criação de Negócios | Edição / Movimentação de Estágio | Emissão de Pedido ERP | Exclusão de Oportunidades |
|---|---|---|---|---|---|
| Consultor de Vendas | Apenas negócios onde é o responsável (`owner_id`) | Sim (atribuído a si mesmo) | Sim (apenas nos seus negócios) | Automático via Fechamento | Não |
| Coordenador de Equipe | Todos os negócios da sua equipe de campo (`team_id`) | Sim | Sim (para membros da sua equipe) | Automático via Fechamento | Não |
| Gerente Regional | Todos os negócios do seu território/regional (`subtree`) | Sim | Sim (dentro da regional) | Homologação de crédito | Com autorização |
| Diretor de BU | Todos os negócios da sua Business Unit | Sim | Sim | Sim | Sim |
| Super Admin (Heverton) | Todos os negócios de todas as BUs sem restrição | Sim | Sim | Sim (Total) | Sim |

---

## 4. Quais Ações Podem Ser Realizadas
* `CHANGE_PIPELINE`: Selecionar o funil setorial odontológico no seletor da interface.
* `TOGGLE_VIEW_MODE`: Alternar entre visualização Kanban e Tabela Analítica de Negócios.
* `CREATE_DEAL`: Abrir o modal de nova oportunidade, preencher parâmetros e persistir em `/api/v1/deals/`.
* `DRAG_DROP_STAGE`: Arrastar o card de negociação entre etapas, atualizando o status no backend.
* `SYNC_TOTVS_ORDER`: Disparar a emissão do pedido de faturamento no TOTVS Protheus (`/api/v1/integrations/totvs/orders`).
* `VIEW_CHURN_RADAR`: Visualizar o alerta de risco de churn por atraso no ciclo de reposição de implantes.
* `EXPORT_CSV`: Exportar os negócios filtrados da tela em formato CSV estruturado.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)

### Criação de um Novo Negócio
1. Na visualização de Vendas, clique no botão "+ Novo Negócio" na barra superior.
2. No formulário do modal, preencha:
   * Título da oportunidade (Ex: "Kit 50 Implantes Cônico Cone Morse - Dr. Roberto").
   * Nome do Cirurgião / Decisor.
   * Clínica / Hospital / Instituto.
   * Valor Estimado (R$).
   * Estágio do Funil (ex: Demonstração Técnica de Caixa).
3. Clique em "Salvar Negócio".
4. O card é imediatamente inserido na coluna correspondente e persistido no SQLite WAL.

### Movimentação de Estágio e Faturamento no TOTVS Protheus
1. Localize o card da oportunidade desejada.
2. Clique e arraste o card para a coluna de destino (ex: de "Proposta Enviada" para "Fechado / Ganho").
3. Ao atingir o estágio de fechamento:
   * O sistema aciona o conector TOTVS Protheus (`src/features/integrations/totvs/`).
   * Gera o pedido de venda com cabeçalho `SC5` e itens `SC6`.
   * Registra o payload na fila idempotente `integration_outbox` do SQLite WAL.
4. Caso a oportunidade possua valor superior a R$ 150.000,00 e envolva consignação de caixas cirúrgicas, a trava de crédito entra em ação exigindo homologação pela Gerência/Controladoria.

### Acompanhamento do Radar Anti-Churn (RFM Odontológico)
1. Negócios e clientes com ciclo de recompra extrapolado exibem o selo vermelho de alerta "Alerta de Churn • Reposição Vencida".
2. Passe o mouse sobre o selo para visualizar a quantidade de dias desde o último pedido faturado versus o intervalo médio de consumo do cirurgião.
3. Clique no botão de ação rápida para agendar uma visita técnica ou abrir mensagem pré-formatada de reposição no WhatsApp.

### Edição Inline de Valores e Prazos (Modo Tabela)
1. No topo da tela de negócios, alterne para o modo "Tabela".
2. Localize a oportunidade desejada e edite diretamente o valor em Reais ou a data prevista de fechamento.
3. A alteração é persistida imediatamente via API com registro auditado na timeline.

---

## 6. O Que Falta Implementar (Roadmap & Gaps)
* Aplicativo complementar PWA/Mobile offline-first otimizado para consultores cirúrgicos em trânsito dentro de centros cirúrgicos sem conectividade de rede.
* Suporte a seleção visual simultânea em grade de múltiplos pipelines no mesmo dashboard.
* Vinculação granular de regras de comissionamento híbrido para negócios sob escopo de múltiplos gerentes de carteira e SDRs compartilhados.

---

## ANOTAÇÕES DO HEVERTON

* **[PIPELINES SETORIAIS]**: Implementado com suporte a múltiplos pipelines setoriais odontológicos (venda direta, kits acadêmicos, atacado distribuidor e KOLs).
* **[TOTVS PROTHEUS INTEGRADO]**: O conector REST gera pedidos `SC5/SC6` automaticamente com chave de idempotência e retentativa em background.
* **[RADAR CHURN RFM]**: O motor calcula a cadência média de compra de implantes e sinaliza atrasos antes da perda da carteira para a concorrência.
* **[DATA SCOPING RBAC]**: Todo negócio herda `owner_id` e `team_id`. Gerentes e diretores visualizam automaticamente as oportunidades da sua subárvore hierárquica via CTE recursiva no SQLite WAL.
