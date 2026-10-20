# 08. Auditoria Anatômica de Botões, Modais & Ações de Interface — Rota: deals

## 1. Inventário Factual de Botões Existentes na Rota

A rota de negociações expõe 11 botões e controles acionáveis mapeados diretamente no DOM:

| Elemento / Rótulo Visual | Gatilho Técnico (`onClick`) | O Que Faz | O Que Abre / Dispara | Por Que Existe (Propósito de Negócio) | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Botão "Novo Negócio"** | `setIsNewDealOpen(true)` | Abre o formulário de cadastro de oportunidade. | Abre modal **Dialog** centralizado (`Dialog isOpen={isNewDealOpen}`). | Permitir aos consultores criar novas oportunidades cirúrgicas no funil. | **FUNCIONA 100%:** Valida título, valor, prioridade e estágio inicial, persistindo via `POST /api/v1/deals`. |
| **Botão "Exportar CSV"** | `handleExportCsv()` | Dispara download do arquivo CSV com as negociações ativas. | Não abre modal. Realiza requisição para `GET /api/v1/deals/export/csv` e inicia o download do arquivo no navegador. | Permitir conciliação externa e relatórios para a diretoria. | **FUNCIONA 100%:** Gera arquivo formatado e aciona blob download no browser. |
| **Botão Alternador "Tabela"** | `setViewMode("table")` | Alterna a visualização para a tabela densa paginada. | Não abre modal. Re-renderiza o corpo central com o componente `DataTable`. | Prover visualização compacta de alta densidade de dados para análise rápida. | **FUNCIONA 100%:** Aplica classe ativa `bg-brand-primary text-white`. |
| **Botão Alternador "Kanban"** | `setViewMode("kanban")` | Alterna a visualização para o quadro visual de colunas. | Não abre modal. Re-renderiza o corpo central com o componente `KanbanBoard`. | Facilitar a gestão visual do funil comercial e visão do avanço de estágios. | **FUNCIONA 100%:** Aplica classe ativa e renderiza colunas com contadores. |
| **Botão "Atualizar" (Ícone Refresh)**| `dealsQuery.refetch()` | Re-executa as queries de negócios e métricas. | Não abre modal. Atualiza a lista em tela sem recarregar a aplicação. | Obter alterações mais recentes feitas por outros consultores em tempo real. | **FUNCIONA 100%:** Re-sincroniza o React Query com o backend. |
| **Card / Linha da Tabela** | `handleOpenDealDrawer(deal)` | Seleciona o negócio ativo e carrega dados complementares. | Abre **Drawer Lateral (Sheet)** da direita com o cockpit completo da oportunidade. | Exibir detalhes profundos, histórico, contratos e ações de fechamento do negócio. | **FUNCIONA 100%:** Dispara busca de timeline e abre gaveta sem travamentos. |
| **Botão "Salvar Alterações" (Drawer)**| `handleUpdateDeal()` | Envia dados modificados (valor, estágio, probabilidade) para a API. | Não abre modal. Executa `PUT /api/v1/deals/{deal_id}` e atualiza a lista em tempo real. | Permitir ajuste ágil de dados durante a conversa com o cirurgião. | **FUNCIONA 100%:** Registra entrada automática na linha do tempo de auditoria. |
| **Botão "Aprovar Limite Excedido"** | `handleApproveCredit()` | Envia liberação gerencial de crédito para o negócio. | Não abre modal. Executa `POST /api/v1/deals/{deal_id}/approve-credit` e remove a trava de crédito. | Evitar que cirurgias urgentes sejam canceladas por excesso temporário de limite. | **FUNCIONA 100%:** Exibe badge de aprovação com ID do gerente aprovador. |
| **Botão "Copilot Granola (IA)"** | `applyCopilotNotes()` | Analisa transcrição de áudio e extrai notas da cirurgia. | Atualiza campos do negócio automaticamente (*Zero-Touch CRM*). | Eliminar o preenchimento manual de relatórios de visita pelo consultor. | **FUNCIONA 100%:** Extrai valor, produto e estágio sugerido com IA. |
| **Botão "SOS Mesa Cirúrgica (Vídeo)"**| `openLiveKitRoom()` | Inicia chamada de emergência em tempo real. | Abre modal de videoconferência WebRTC LiveKit deal room. | Permitir suporte técnico imediato ao cirurgião durante o ato operatório. | **FUNCIONA 100%:** Conecta à sala WebRTC. |
| **Botão "Fechar Gaveta" (Ícone X)** | `setIsDrawerOpen(false)` | Fecha a gaveta lateral de detalhes. | Desmonta o Drawer e retorna a visualização limpa do funil. | Voltar à navegação geral do funil. | **FUNCIONA 100%:** Fecha com animação fluida sem perder o estado da tabela. |

---

## 2. Modais e Gavetas (Drawers) na Rota

- **Modal Dialog "Novo Negócio":** Centralizado na tela, com campos de Título, Valor (R$), Estágio, Prioridade e Seleção de Cirurgião/Clínica. Possui escape via tecla `Esc`, clique no backdrop ou botão Cancelar.
- **Gaveta Lateral (Sheet Drawer):** Desliza da direita para a esquerda ao clicar em qualquer oportunidade. Agrupa a inteligência do negócio em abas verticais sem sobrecarregar a tela principal.
- **Modal LiveKit Deal Room:** Renderizado sob demanda dentro do Drawer para chamadas de suporte ao vivo.

---

## 3. Catálogo de Botões Faltantes (Gaps de Interação & UX)

| Botão Faltante | Localização Sugerida na Tela | O Que Deveria Abrir / Fazer | Por Que Está Faltando (Impacto na Jornada) | Micro-Ticket Vinculado |
| :--- | :--- | :--- | :--- | :--- |
| **"Gerar Proposta Comercial PDF"** | No topo do Drawer lateral do negócio. | Disparar geração e download imediato da proposta diagramada com produtos selecionados. | Atualmente o consultor precisa alternar manualmente para a rota `/#!/contracts` para gerar o contrato formal. | `TICKET-DEALS-01` |
| **"Solicitar Entrega Expressa (DENTGO)"**| Dentro do Drawer lateral em negócios no estágio "Contrato" ou "Fechado Ganho". | Abrir modal com pré-preenchimento dos implantes do negócio para despacho via motoboy em 45 min. | O consultor precisa sair do deal, ir para `/#!/dentgo` e redigitar o pedido de entrega. | `TICKET-DEALS-02` |
| **"Adicionar Produto do Catálogo"** | No formulário de edição inline do Drawer. | Abrir seletor com a lista de implantes e tabelas de preço odontológicas cadastradas no backend. | O campo de valor aceita apenas digitação manual de número, sem vínculo com os itens do catálogo técnico. | `TICKET-DEALS-03` |
