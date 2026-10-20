# 07. Plano de Ação em Micro-Tickets Cirúrgicos — Rota: dashboard

## Catálogo de Micro-Tickets Executáveis

---

### TICKET-DASH-01: Desacoplamento Arquitetural VSA do Cockpit Executivo
- **O Que Fazer:** Separar o Cockpit Executivo da rota `/dashboard` do Estúdio BI Superset da rota `/analytics`, que atualmente compartilham o mesmo arquivo monolítico de 1.008 linhas.
- **Como Fazer:** Criar `frontend/src/features/dashboard/ExecutiveCockpitView.tsx`, migrando as funções `fetchExecutiveCockpit`, `computedChartBars` e os cards de KPI executivos para esse novo componente limpo. Atualizar `frontend/src/router.tsx` para importar diretamente o novo componente no case `"dashboard"`.
- **Onde Fazer:** 
  - Criar: `frontend/src/features/dashboard/ExecutiveCockpitView.tsx`
  - Modificar: `frontend/src/router.tsx` (linhas 63-69)
  - Limpar: `frontend/src/features/bi/SupersetEmbeddedDashboard.tsx`
- **Critério Binário de Aceitação:** `npm run build` ou `tsc --noEmit` executando com código `exit 0` e o Cockpit renderizando de forma idêntica.

---

### TICKET-DASH-02: Ativação do Motor Ocioso de Exportação em Formato Parquet
- **O Que Fazer:** Expor no botão de exportação da interface a opção de download em formato Apache Parquet colunar, recurso já implementado e testado no motor de backend (`src/features/intelligence/router.py`).
- **Como Fazer:** Adicionar um menu dropdown ou botões segmentados no cabeçalho permitindo ao usuário selecionar `CSV` ou `PARQUET`. Passar o parâmetro selecionado na chamada `handleExportDataset(format)`.
- **Onde Fazer:** 
  - Arquivo: `frontend/src/features/bi/SupersetEmbeddedDashboard.tsx` (linhas 413-423)
- **Critério Binário de Aceitação:** Teste E2E ou manual disparando requisição com `{"format": "parquet"}` e recebendo resposta HTTP 200 com chave de arquivo `.parquet` no R2.

---

### TICKET-DASH-03: Filtro Dinâmico de Janela Temporal no Radar Anti-Churn
- **O Que Fazer:** Permitir filtrar a visualização do radar de cirurgiões em risco de churn por faixas de dias sem pedido (30d, 45d, 60d, 90d+).
- **Como Fazer:** Adicionar um componente `Select` no cabeçalho do card "Radar Anti-Churn RFM Odontológico" e injetar o parâmetro `?days_threshold=...` na requisição `fetch('/api/v1/intelligence/churn-risk?days_threshold=...')`.
- **Onde Fazer:**
  - Arquivo: `frontend/src/features/bi/SupersetEmbeddedDashboard.tsx` (linhas 234 e 500-511)
- **Critério Binário de Aceitação:** A alteração do seletor na interface re-dispara a busca e atualiza o estado `churnData` sem recarregar a tela inteira.

---

### TICKET-DASH-04: Blindagem Rigorosa contra IDOR nos Endpoints de Métricas
- **O Que Fazer:** Assegurar que nenhum parâmetro `account_id` enviado pelo cliente possa sobrepor o tenant real do usuário autenticado no token JWT.
- **Como Fazer:** No backend (`src/features/intelligence/router.py`), adicionar a dependência `current_user = Depends(get_current_active_user)` nos endpoints `/churn-risk`, `/clinical-graph` e `/bi/guest-token`, forçando `account_id = current_user.organization_id`.
- **Onde Fazer:**
  - Arquivo: `src/features/intelligence/router.py` (linhas 51-60, 64-70, 196-205)
- **Critério Binário de Aceitação:** Executar `pytest tests/test_clinical_graph_churn.py tests/test_superset_rls_embedded.py` com retorno `exit 0`.
