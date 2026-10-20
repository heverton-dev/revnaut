# 08. Auditoria Anatômica de Botões, Modais & Ações de Interface — Rota: dashboard

## 1. Inventário Factual de Botões Existentes na Rota

O modo ativo da rota (`mode="executive_cockpit"`) expõe exatamente 5 elementos acionáveis no DOM:

| Elemento / Rótulo Visual | Gatilho Técnico (`onClick`) | O Que Faz | O Que Abre / Dispara | Por Que Existe (Propósito de Negócio) | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Botão "Atualizar Cockpit"** | `fetchExecutiveCockpit()` e `fetchGuestToken()` | Re-executa as 5 requisições de telemetria em paralelo via `Promise.all` e renova o token RLS. | Não abre modal. Atualiza os estados reativos em memória (`pipelineMetrics`, `campaignMetrics`, `churnData`, `clinicalGraph`, `dealsData`). | Permitir ao gestor obter os números mais recentes de vendas sem dar F5 / reload na página inteira. | **FUNCIONA 100%:** Desabilita durante o carregamento (`disabled={loadingExecutive}`) e exibe ícone giratório `RefreshCw`. |
| **Botão "Exportar Snapshot R2"** | `handleExportDataset("csv")` | Submete requisição `POST /api/v1/intelligence/bi/export-dataset` para gerar snapshot analítico. | Não abre modal. Grava o arquivo no bucket Cloudflare R2 e exibe um alerta verde no topo da tela com a chave gerada. | Atender exigências de auditoria corporativa e extração de dados para relatórios offline. | **FUNCIONA 100%:** Bloqueia cliques múltiplos (`disabled={exporting}`) e renderiza toast de sucesso com `r2_storage_key`. |
| **Pílula/Tab "Estágio"** | `setChartViewMode("stage")` | Altera a variável de estado `chartViewMode` para `"stage"`. | Não abre modal. Re-renderiza o gráfico SVG para exibir barras de receita por fase do funil de vendas (Qualificação, Diagnóstico, Proposta, etc.). | Permitir ao diretor enxergar onde a receita está acumulada no funil comercial. | **FUNCIONA 100%:** Alterna a classe de estilo para estado ativo (`bg-brand-primary text-white`). |
| **Pílula/Tab "Tendência"** | `setChartViewMode("trend")` | Altera a variável de estado `chartViewMode` para `"trend"`. | Não abre modal. Re-renderiza o gráfico SVG em série temporal simulada dos últimos 6 meses (Mai a Out). | Dar visibilidade de crescimento mês a mês do faturamento faturado. | **FUNCIONA PARCIAL:** Usa dados proporcionais derivados da métrica global em vez de histórico real de faturamento do banco. |
| **Pílula/Tab "Consignação"** | `setChartViewMode("consignment")` | Altera a variável de estado `chartViewMode` para `"consignment"`. | Não abre modal. Re-renderiza o gráfico com a decomposição de maletas cirúrgicas custodiadas vs consumo faturado. | Permitir o acompanhamento do modelo de negócio KeyPartners de consignação de implantes em hospitais. | **FUNCIONA 100%:** Aplica classes semânticas `fill-brand-navy` e `fill-status-success`. |

---

## 2. Modais e Gavetas (Drawers) na Rota

- **Modais Existentes:** Nenhum modal nativo é disparado diretamente pelo Cockpit Executivo na rota `/#!/dashboard`. Todas as interações ocorrem *in-place* por atualização de cards reativos.
- **Risco Operacional:** A ausência de modais impede que o gestor tome ações imediatas a partir dos alertas exibidos (ex: abrir ficha do cirurgião ao clicar no alerta de churn).

---

## 3. Catálogo de Botões Faltantes (Gaps de Interação & UX)

A auditoria factual identificou a ausência de 4 botões críticos para o fluxo de trabalho de RevOps:

| Botão Faltante | Localização Sugerida na Tela | O Que Deveria Abrir / Fazer | Por Que Está Faltando (Impacto na Jornada) | Micro-Ticket Vinculado |
| :--- | :--- | :--- | :--- | :--- |
| **"Atuar no Lead / Reativar"** (por cirurgião no Radar Churn) | Ao lado de cada barra de cirurgião em risco crítico no card de Churn RFM. | Abrir modal ou redirecionar para `/#!/contacts?id=...` ou disparar WhatsApp pré-configurado via Evolution API. | Atualmente o card mostra o alerta e a ação recomendada, mas **não oferece botão de execução**. O consultor é forçado a sair da tela, ir em Contatos e procurar manualmente o médico. | `TICKET-DASH-05` |
| **"Seletor de Formato de Exportação (CSV / Parquet)"** | Integrado ao botão de exportação no topo direito. | Abrir dropdown com opções "CSV (.csv)" e "Apache Parquet (.parquet)". | O motor já suporta Parquet colunar no backend, mas o usuário não tem botão para escolher esse formato. | `TICKET-DASH-02` |
| **"Drill-down do Estágio Comercial"** | Ao clicar em qualquer barra do gráfico de funil de vendas. | Redirecionar para `/#!/deals?stage=...` com filtro aplicado do estágio selecionado. | O gráfico é puramente estático para visualização. Clicar na barra não filtra nem leva às oportunidades reais daquele estágio. | `TICKET-DASH-06` |
| **"Expandir Topologia do Grafo"** | Cabeçalho do card "Ecossistema Clínico KOL". | Abrir modal com visualizador interativo completo de teia de relacionamentos (cirurgião <-> clínica <-> CAD/CAM). | O card atual trunca a lista nos primeiros 8 itens e não permite explorar a malha de conexões entre os profissionais. | `TICKET-DASH-07` |
