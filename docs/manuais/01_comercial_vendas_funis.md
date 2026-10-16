# Manual da Rota: Vendas & Funis Setoriais (`/#deals`)

## 1. Objetivo da Rota
Operar o pipeline comercial e o funil de receitas da indústria de implantes e biomateriais odontológicos. Permite acompanhar as etapas de negociação desde a qualificação inicial de cirurgiões até o fechamento de pedidos de caixas cirúrgicas, contratos institucionais e vendas no atacado.

---

## 2. O Que o Usuário Consegue Realizar
* Alternar entre 4 funis setoriais odontológicos:
  1. Cirurgiões & Venda Direta / Consignação.
  2. Instituições de Ensino & Kits Acadêmicos (Faculdades Mandic, ABO, etc.).
  3. Distribuidores & Contratos Atacado.
  4. Key Opinion Leaders (KOLs) & Eventos CIOSP.
* Alternar a visualização dos negócios entre Pipeline Kanban (colunas arrastáveis) e Tabela Analítica.
* Filtrar negociações por escopo de usuário simulado (RBAC hierárquico em tempo real).
* Criar novas oportunidades comerciais informando título, cirurgião/decisor, clínica, valor estimado e estágio inicial.
* Mover negócios entre os estágios do funil comercial (Qualificação, Demonstração Técnica, Proposta/Consignação, Fechamento).
* Acompanhar os KPIs da topbar: Valor Total em Pipeline, Ticket Médio Odontológico, Taxa de Conversão e Negócios Ativos.

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil | Visualização de Negócios | Criação de Negócios | Edição / Movimentação de Estágio | Exclusão de Oportunidades |
|---|---|---|---|---|
| Consultor de Vendas | Apenas negócios onde é o responsável (`user_id`) | Sim (atribuído a si mesmo) | Sim (apenas nos seus negócios) | Não |
| Coordenador de Equipe | Todos os negócios da sua equipe de campo | Sim | Sim (para membros da sua equipe) | Não |
| Gerente Regional | Todos os negócios do seu distrito/regional | Sim | Sim (dentro da regional) | Com autorização |
| Diretor de BU | Todos os negócios da sua Business Unit | Sim | Sim | Sim |
| Super Admin | Todos os negócios de todas as BUs sem restrição | Sim | Sim | Sim |

---

## 4. Quais Ações Podem Ser Realizadas
* `CHANGE_PIPELINE`: Selecionar o funil específico no dropdown da topbar (`handlePipelineChange`).
* `TOGGLE_VIEW_MODE`: Alternar entre Kanban (`setDealView('kanban')`) e Lista em Tabela (`setDealView('table')`).
* `CREATE_DEAL`: Abrir o modal de novo negócio, preencher dados e enviar para `/api/v1/deals/`.
* `DRAG_DROP_STAGE`: Arrastar o card de um cirurgião de uma etapa para outra atualizando o status no SQLite.
* `FILTER_USER_SCOPE`: Alternar a simulação de visualização por consultor no seletor da barra superior.

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
4. O card é imediatamente inserido na coluna correspondente e persistido no banco SQLite WAL.

### Movimentação de Estágio no Kanban
1. Localize o card da oportunidade desejada.
2. Clique e arraste o card para a coluna de destino (ex: de "Proposta Enviada" para "Fechado / Ganho").
3. O sistema calcula automaticamente o recalculo de comissões e dispara o webhook correspondente.
4. Caso a oportunidade possua valor superior a R$ 150.000,00 e o destino seja Consignação/Fechamento, a Trava de Limite de Crédito entra em ação exigindo parecer e homologação pela Controladoria.

### Edição Inline de Valores e Prazos (Modo Tabela)
1. No canto superior direito da tela de negócios, clique no botão "Tabela".
2. Localize a oportunidade desejada nas linhas da tabela.
3. Edite diretamente o campo de valor numérico em Reais ou o seletor de data de previsão de fechamento.
4. A alteração é persistida imediatamente via API com registro auditado na linha do tempo.

### Linha do Tempo e Histórico de Auditoria
1. Na visualização Kanban ou Tabela, clique no botão "Timeline" associado à oportunidade.
2. O modal exibe todos os eventos cronológicos: movimentações de estágio, reajustes de valores, aprovações de crédito e notas de consultores.
3. Utilize o campo no rodapé do modal para registrar uma nova nota formal de auditoria.

### Exportação do Pipeline Comercial em CSV
1. No canto superior direito da tabela de negócios, clique no botão "Exportar CSV".
2. O sistema gera e descarrega a planilha estruturada contendo todos os negócios, cirurgiões, estágios, valores e previsões.

---

## 6. O Que Falta Implementar (Roadmap & Gaps)
* Suporte nativo a múltiplos pipelines simultâneos dinâmicos por categoria odontológica (implantes, próteses, ortodontia e equipamentos cirúrgicos pesados).
* Aplicativo complementar PWA/Mobile offline-first otimizado para consultores cirúrgicos em trânsito e hospitais.
* Vinculação granular de regras de comissionamento híbrido para negócios sob escopo de múltiplos gerentes de carteira e SDRs compartilhados.

---

## ANOTAÇÕES DO HEVERTON

* [CHANGE_PIPELINE 4 funis setoriais odontológicos]: Atualmente o motor suporta funil unificado com estágios customizados. A expansão para seleção ativa de múltiplos pipelines por divisão de negócios está mapeada para a próxima iteração arquitetural.
* [DUVIDA MOBILE FIRST]: A aplicação possui layout responsivo via media-queries CSS com drawer retrátil da barra lateral para smartphones. Contudo, em centros cirúrgicos sem conectividade de rede, recomenda-se a extensão offline-first via Service Workers PWA.
* [DUVIDA PWA]: O manifesto PWA e service workers de cache offline ainda não foram instanciados no build estático; a arquitetura atual opera como SPA web altamente otimizada.
* [DUVIDA PIPELINE]: Na matriz RBAC atual, a criação e reordenação de estágios de pipeline é restrita ao Super Admin e Gerente Comercial para preservar a consistência analítica das métricas de conversão.
* [DUVIDA CARTEIRA]: Todo novo negócio criado herda o vínculo do consultor logado (`owner_id` / `user_id`). Gerentes de equipe visualizam automaticamente todas as oportunidades dos consultores sob sua hierarquia (Data Scoping RBAC). Leads sem carteira atribuída permanecem no pool geral de prospecção SDR até a distribuição territorial formal.
