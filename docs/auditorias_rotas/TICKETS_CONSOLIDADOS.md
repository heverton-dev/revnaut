# Catálogo Consolidado de Tickets — Auditoria de Rotas

> Extraído de `V1/LIVRO_MESTRE_AUDITORIA_ROTAS_COMPLETO.pdf` e `v2/LIVRO_MESTRE_AUDITORIA_ROTAS_COMPLETO.pdf` (seção 07, *Plano de Ação em Micro-Tickets Cirúrgicos*, de cada rota).

- **V1:** 38 tickets · **v2:** 35 tickets · **Total:** 73 · **Rotas:** 17
- Os IDs se repetem entre versões (ex.: `TICKET-DASH-01`) com escopos diferentes; o sufixo `[V1]`/`[v2]` identifica a origem. A v2 reflete o estado após o ciclo de correções da V1.

## Cotejo com a aplicação (somente leitura)

- **Data/hora:** 2026-10-20 07:05 · **Base:** commit `4b3b453` (`HEAD`, branch `main`)
- **Método:** leitura estática do código (grep + leitura de trechos) e `git show HEAD:<arquivo>`. Nada foi executado, testado ou alterado na aplicação.
- **Critério do sufixo `[FEITO]`:** a funcionalidade descrita no título está implementada de ponta a ponta (UI e, quando aplicável, backend) e **commitada no `HEAD`**.
- **Status possíveis:** `FEITO` · `PARCIAL` (existe parte, com a lacuna descrita) · `NÃO FEITO` (sem evidência no código) · `WIP` (existe só como alteração não commitada, em edição por outros agentes; não conta como feito).
- **Aviso:** outros agentes estão editando arquivos agora (`SupersetEmbeddedDashboard.tsx` mudou de tamanho três vezes durante a análise, além de `DealsWorkspace.tsx`, `KanbanBoard.tsx`, `ConsignmentSurgicalBoard.tsx` e rotas de `auth`, `hierarchy`, `keypartners`, `automations`). Itens `WIP` podem virar `FEITO` após o commit; reexecutar o cotejo depois.
- **Limite:** o critério de aceitação de cada ticket (testes `exit 0`) não foi executado.

| Status | Tickets |
|---|---|
| FEITO | 34 |
| PARCIAL | 21 |
| WIP (não commitado) | 8 |
| NÃO FEITO | 10 |
| **Total** | **73** |

## Índice por rota

| Rota | V1 | v2 |
|---|---|---|
| [`dashboard`](#rota-dashboard) | 4 | 2 |
| [`deals`](#rota-deals) | 3 | 2 |
| [`contacts`](#rota-contacts) | 3 | 3 |
| [`scoring`](#rota-scoring) | 2 | 2 |
| [`marketing`](#rota-marketing) | 2 | 2 |
| [`omnichannel`](#rota-omnichannel) | 2 | 2 |
| [`keypartners`](#rota-keypartners) | 2 | 2 |
| [`dentgo`](#rota-dentgo) | 2 | 2 |
| [`video_sos`](#rota-video_sos) | 2 | 2 |
| [`contracts`](#rota-contracts) | 2 | 2 |
| [`imaging`](#rota-imaging) | 2 | 2 |
| [`support`](#rota-support) | 2 | 2 |
| [`intelligence`](#rota-intelligence) | 2 | 2 |
| [`analytics`](#rota-analytics) | 2 | 2 |
| [`scheduling`](#rota-scheduling) | 2 | 2 |
| [`rbac`](#rota-rbac) | 2 | 2 |
| [`settings`](#rota-settings) | 2 | 2 |

## Rota: dashboard

<a id="rota-dashboard"></a>

### V1 (4 tickets)

#### TICKET-DASH-01 — Desacoplamento Arquitetural VSA do Cockpit Executivo  `[V1]`

- **Status:** PARCIAL
- **Evidência:** `dashboard/ExecutiveCockpitView.tsx` existe (59 linhas) e `router.tsx` o importa, mas é só wrapper de `SupersetEmbeddedDashboard mode=executive_cockpit`; `fetchExecutiveCockpit`/`computedChartBars` continuam em `bi/SupersetEmbeddedDashboard.tsx` (limpeza não feita).
- **O que fazer:** Separar o Cockpit Executivo da rota /dashboard do Estúdio BI Superset da rota /analytics , que atualmente compartilham o mesmo arquivo monolítico de 1.008 linhas.
- **Como fazer:** Criar frontend/src/features/dashboard/ExecutiveCockpitView.tsx , migrando as funções fetchExecutiveCockpit , computedChartBars e os cards de KPI executivos para esse novo componente limpo. Atualizar frontend/src/router.tsx para importar diretamente o novo componente no case "dashboard" .
- **Onde fazer:**
  - Criar: frontend/src/features/dashboard/ExecutiveCockpitView.tsx
  - Modificar: frontend/src/router.tsx (linhas 63-69)
  - Limpar: frontend/src/features/bi/SupersetEmbeddedDashboard.tsx
- **Critério binário de aceitação:** npm run build ou tsc --noEmit executando com código exit 0 e o Cockpit renderizando de forma idêntica.

#### TICKET-DASH-02 — Ativação do Motor Ocioso de Exportação em Formato Parquet [FEITO]  `[V1]`

- **Status:** FEITO
- **Evidência:** `bi/SupersetEmbeddedDashboard.tsx`: `<option value="parquet">` + `handleExportDataset(format)`.
- **O que fazer:** Expor no botão de exportação da interface a opção de download em formato Apache Parquet colunar, recurso já implementado e testado no motor de backend ( src/features/intelligence/router.py ).
- **Como fazer:** Adicionar um menu dropdown ou botões segmentados no cabeçalho permitindo ao usuário selecionar CSV ou PARQUET . Passar o parâmetro selecionado na chamada handleExportDataset(format) .
- **Onde fazer:** Arquivo: frontend/src/features/bi/SupersetEmbeddedDashboard.tsx (linhas 413-423)
- **Critério binário de aceitação:** Teste E2E ou manual disparando requisição com {"format": "parquet"} e recebendo resposta HTTP 200 com chave de arquivo .parquet no R2.

#### TICKET-DASH-03 — Filtro Dinâmico de Janela Temporal no Radar Anti-Churn [FEITO]  `[V1]`

- **Status:** FEITO
- **Evidência:** `bi/SupersetEmbeddedDashboard.tsx`: `churnDaysThreshold` injeta `?days_threshold=` em `/intelligence/churn-risk`.
- **O que fazer:** Permitir filtrar a visualização do radar de cirurgiões em risco de churn por faixas de dias sem pedido (30d, 45d, 60d, 90d+).
- **Como fazer:** Adicionar um componente Select no cabeçalho do card "Radar Anti-Churn RFM Odontológico" e injetar o parâmetro ?days_threshold=... na requisição fetch('/api/v1/intelligence/churn-risk?days_threshold=...') .
- **Onde fazer:** Arquivo: frontend/src/features/bi/SupersetEmbeddedDashboard.tsx (linhas 234 e 500-511)
- **Critério binário de aceitação:** A alteração do seletor na interface re-dispara a busca e atualiza o estado churnData sem recarregar a tela inteira.

#### TICKET-DASH-04 — Blindagem Rigorosa contra IDOR nos Endpoints de Métricas [FEITO]  `[V1]`

- **Status:** FEITO
- **Evidência:** `src/features/intelligence/router.py`: `churn-risk`, `clinical-graph` e `bi/guest-token` usam `Depends(get_current_user)` e `current_user.account_id`. Outras rotas do mesmo router ainda aceitam `account_id` do cliente (fora do escopo do ticket).
- **O que fazer:** Assegurar que nenhum parâmetro account_id enviado pelo cliente possa sobrepor o tenant real do usuário autenticado no token JWT.
- **Como fazer:** No backend ( src/features/intelligence/router.py ), adicionar a dependência current_user = Depends(get_current_active_user) nos endpoints /churn-risk , /clinical-graph e /bi/guest-token , forçando account_id = current_user.organization_id .
- **Onde fazer:** Arquivo: src/features/intelligence/router.py (linhas 51-60, 64-70, 196-205)
- **Critério binário de aceitação:** Executar pytest tests/test_clinical_graph_churn.py tests/test_superset_rls_embedded.py com retorno exit 0 .

### v2 (2 tickets)

#### TICKET-DASH-01 — Implementar Exportar Relatório Executivo PDF  `[v2]`

- **Status:** WIP
- **Evidência:** Não está no `HEAD`. `bi/SupersetEmbeddedDashboard.tsx` está sendo editado por outro agente (imports `FileDown`/`Mail` e botão com `FileDown` no working tree, sem commit).
- **O que fazer:** Adicionar exportar relatório executivo pdf na interface da rota dashboard .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/dashboard/ExecutiveCockpitView.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

#### TICKET-DASH-02 — Implementar Filtro Global por Regional  `[v2]`

- **Status:** WIP
- **Evidência:** Não está no `HEAD`. Working tree de `SupersetEmbeddedDashboard.tsx` tem `regionalMultiplier` em edição por outro agente; `ExecutiveCockpitView.tsx` sem alteração.
- **O que fazer:** Adicionar filtro global por regional na interface da rota dashboard .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/dashboard/ExecutiveCockpitView.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

## Rota: deals

<a id="rota-deals"></a>

### V1 (3 tickets)

#### TICKET-DEALS-01 — Extração Arquitetural VSA de DealsWorkspace.tsx [FEITO]  `[V1]`

- **Status:** FEITO
- **Evidência:** `deals/DealsWorkspace.tsx` autônomo; `router.tsx` instancia `<DealsWorkspace/>`; `App.tsx` reduzido a 114 linhas.
- **O que fazer:** Desacoplar a rota de negociações de frontend/src/App.tsx , movendo todo o código de Kanban, DataTable e Drawer para frontend/src/features/deals/DealsWorkspace.tsx .
- **Como fazer:** Criar o componente autônomo com suas props e tipagens, e atualizar frontend/src/router.tsx no case "deals" para instanciar <DealsWorkspace /> .
- **Onde fazer:**
  - Criar: frontend/src/features/deals/DealsWorkspace.tsx
  - Limpar: frontend/src/App.tsx (linhas 148-1120)
- **Critério binário de aceitação:** npm run build ou tsc --noEmit executando com código exit 0 .

#### TICKET-DEALS-02 — Integração do Catálogo Odontológico no Drawer de Oportunidades [FEITO]  `[V1]`

- **Status:** FEITO
- **Evidência:** `DealsWorkspace.tsx`: GET `/api/v1/deals/catalog/products`, Select de SKU + quantidade, carrinho com `cartTotal` e aplicação ao valor do negócio.
- **O que fazer:** Substituir o input numérico solto de valor por um seletor de itens do catálogo de produtos odontológicos ( /api/v1/deals/catalog/products ), calculando o valor do negócio automaticamente com base na quantidade de implantes e kit protético selecionados.
- **Como fazer:** Adicionar chamada useQuery(["catalog_products"]) no Drawer lateral e renderizar um componente Select com busca de implantes.
- **Onde fazer:** Arquivo: frontend/src/App.tsx (ou novo DealsWorkspace.tsx , seção do Drawer)
- **Critério binário de aceitação:** Ao selecionar produtos, o valor total do negócio é calculado e exibido em BRL de forma determinística.

#### TICKET-DEALS-03 — Ação Rápida de Despacho DENTGO a Partir de Negócios Ganhos [FEITO]  `[V1]`

- **Status:** FEITO
- **Evidência:** `DealsWorkspace.tsx`: botão "Despachar com DENTGO (45 min)" condicionado a `isContractOrWon`, POST `/api/v1/dentgo/orders/express`.
- **O que fazer:** Incluir um botão "Despachar com DENTGO (45 min)" no Drawer lateral para negócios no estágio "Contrato" ou "Fechado Ganho".
- **Como fazer:** Ao clicar, navegar para #!/dentgo?deal_id=... ou abrir modal pré-preenchido para solicitar motoboy express com os implantes da oportunidade.
- **Onde fazer:** Arquivo: Drawer lateral de Deals
- **Critério binário de aceitação:** Redirecionamento ou abertura de modal transferindo o ID do negócio e produtos para o formulário de entrega rápida.

### v2 (2 tickets)

#### TICKET-DEALS-01 — Implementar Aprovação Rápida de Desconto  `[v2]`

- **Status:** WIP
- **Evidência:** Somente no working tree (não commitado): `handleQuickApproveDiscount` em `DealsWorkspace.tsx` → POST `/api/v1/deals/catalog/approve-discount`; a rota backend já existe em `deals/router.py`.
- **O que fazer:** Adicionar aprovação rápida de desconto na interface da rota deals .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/deals/DealsWorkspace.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

#### TICKET-DEALS-02 — Implementar Reordenar Estágios do Funil  `[v2]`

- **Status:** WIP
- **Evidência:** Somente no working tree (não commitado): `handleReorderStage`/`customStageOrder` em `DealsWorkspace.tsx` e `KanbanBoard.tsx`. A ordem fica em estado local, sem persistência no backend.
- **O que fazer:** Adicionar reordenar estágios do funil na interface da rota deals .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/deals/DealsWorkspace.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

## Rota: contacts

<a id="rota-contacts"></a>

### V1 (3 tickets)

#### TICKET-CONTACTS-01 — Implementar Vincular Maleta em Consignação  `[V1]`

- **Status:** PARCIAL
- **Evidência:** Botão existe, mas só faz `location.hash = "#!/keypartners"`; não vincula maleta ao contato nem chama endpoint.
- **O que fazer:** Adicionar vincular maleta em consignação na interface da rota contacts .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/contacts/ContactsCrmWorkspace.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

#### TICKET-CONTACTS-02 — Implementar Disparar Conversa WhatsApp [FEITO]  `[V1]`

- **Status:** FEITO
- **Evidência:** Botão abre `https://wa.me/<fone>` com texto pré-preenchido. Ressalva: deep link externo, não passa pelo omnichannel/backend.
- **O que fazer:** Adicionar disparar conversa whatsapp na interface da rota contacts .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/contacts/ContactsCrmWorkspace.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

#### TICKET-CONTACTS-03 — Implementar Solicitar Entrega Expressa  `[V1]`

- **Status:** PARCIAL
- **Evidência:** Botão só navega para `#!/dentgo`, sem passar contato/endereço ao formulário.
- **O que fazer:** Adicionar solicitar entrega expressa na interface da rota contacts .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/contacts/ContactsCrmWorkspace.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

### v2 (3 tickets)

#### TICKET-CONTACTS-01 — Implementar Vincular Maleta em Consignação  `[v2]`

- **Status:** PARCIAL
- **Evidência:** Botão existe, mas só faz `location.hash = "#!/keypartners"`; não vincula maleta ao contato nem chama endpoint.
- **O que fazer:** Adicionar vincular maleta em consignação na interface da rota contacts .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/contacts/ContactsCrmWorkspace.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

#### TICKET-CONTACTS-02 — Implementar Disparar Conversa WhatsApp [FEITO]  `[v2]`

- **Status:** FEITO
- **Evidência:** Botão abre `https://wa.me/<fone>` com texto pré-preenchido. Ressalva: deep link externo, não passa pelo omnichannel/backend.
- **O que fazer:** Adicionar disparar conversa whatsapp na interface da rota contacts .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/contacts/ContactsCrmWorkspace.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

#### TICKET-CONTACTS-03 — Implementar Solicitar Entrega Expressa  `[v2]`

- **Status:** PARCIAL
- **Evidência:** Botão só navega para `#!/dentgo`, sem passar contato/endereço ao formulário.
- **O que fazer:** Adicionar solicitar entrega expressa na interface da rota contacts .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/contacts/ContactsCrmWorkspace.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

## Rota: scoring

<a id="rota-scoring"></a>

### V1 (2 tickets)

#### TICKET-SCORING-01 — Implementar Ajuste Interativo de Pesos (Sliders)  `[V1]`

- **Status:** PARCIAL
- **Evidência:** `scoring/IcpScoringDashboard.tsx`: 4 sliders `type=range` existem, mas os pesos só alteram o estado local; não são enviados ao backend nem recalculam o ranking (score exibido usa fallback fixo `95 - idx*7`).
- **O que fazer:** Adicionar ajuste interativo de pesos (sliders) na interface da rota scoring .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/scoring/IcpScoringDashboard.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

#### TICKET-SCORING-02 — Implementar Handoff Automático para Vendedor [FEITO]  `[V1]`

- **Status:** FEITO
- **Evidência:** `IcpScoringDashboard.tsx`: `handleEvaluateHandoff` → POST `/api/v1/scoring/evaluate-handoff`; backend em `src/features/scoring/router.py`.
- **O que fazer:** Adicionar handoff automático para vendedor na interface da rota scoring .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/scoring/IcpScoringDashboard.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

### v2 (2 tickets)

#### TICKET-SCORING-01 — Implementar Ajuste Interativo de Pesos (Sliders)  `[v2]`

- **Status:** PARCIAL
- **Evidência:** `scoring/IcpScoringDashboard.tsx`: 4 sliders `type=range` existem, mas os pesos só alteram o estado local; não são enviados ao backend nem recalculam o ranking (score exibido usa fallback fixo `95 - idx*7`).
- **O que fazer:** Adicionar ajuste interativo de pesos (sliders) na interface da rota scoring .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/scoring/IcpScoringDashboard.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

#### TICKET-SCORING-02 — Implementar Handoff Automático para Vendedor [FEITO]  `[v2]`

- **Status:** FEITO
- **Evidência:** `IcpScoringDashboard.tsx`: `handleEvaluateHandoff` → POST `/api/v1/scoring/evaluate-handoff`; backend em `src/features/scoring/router.py`.
- **O que fazer:** Adicionar handoff automático para vendedor na interface da rota scoring .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/scoring/IcpScoringDashboard.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

## Rota: marketing

<a id="rota-marketing"></a>

### V1 (2 tickets)

#### TICKET-MKT-01 — Implementar Teste A/B Automatizado  `[V1]`

- **Status:** PARCIAL
- **Evidência:** `campaigns/LandingPageBuilder.tsx`: botão + modal A/B (variantes A/B, "Ativar Split 50/50"), mas apenas estado local (`abTestEnabled`); sem endpoint, divisão de tráfego ou promoção automática.
- **O que fazer:** Adicionar teste a/b automatizado na interface da rota marketing .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/campaigns/LandingPageBuilder.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

#### TICKET-MKT-02 — Implementar Pré-visualização Mobile/Tablet [FEITO]  `[V1]`

- **Status:** FEITO
- **Evidência:** `LandingPageBuilder.tsx`: seletor Desktop/Tablet 768px/Mobile 375px redimensiona o iframe de preview.
- **O que fazer:** Adicionar pré-visualização mobile/tablet na interface da rota marketing .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/campaigns/LandingPageBuilder.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

### v2 (2 tickets)

#### TICKET-MKT-01 — Implementar Teste A/B Automatizado  `[v2]`

- **Status:** PARCIAL
- **Evidência:** `campaigns/LandingPageBuilder.tsx`: botão + modal A/B (variantes A/B, "Ativar Split 50/50"), mas apenas estado local (`abTestEnabled`); sem endpoint, divisão de tráfego ou promoção automática.
- **O que fazer:** Adicionar teste a/b automatizado na interface da rota marketing .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/campaigns/LandingPageBuilder.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

#### TICKET-MKT-02 — Implementar Pré-visualização Multi-Dispositivo [FEITO]  `[v2]`

- **Status:** FEITO
- **Evidência:** Mesma evidência de MKT-02 (V1): seletor Desktop/Tablet/Mobile no preview do `LandingPageBuilder.tsx`.
- **O que fazer:** Adicionar pré-visualização multi-dispositivo na interface da rota marketing .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/campaigns/LandingPageBuilder.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

## Rota: omnichannel

<a id="rota-omnichannel"></a>

### V1 (2 tickets)

#### TICKET-OMNI-01 — Implementar Gravar Áudio Direto do Navegador [FEITO]  `[V1]`

- **Status:** FEITO
- **Evidência:** `inbox/OmnichannelWorkspace.tsx`: `getUserMedia` + `MediaRecorder`, upload via `uploadMedia` (pasta `voice`), player `<audio>`.
- **O que fazer:** Adicionar gravar áudio direto do navegador na interface da rota omnichannel .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/inbox/OmnichannelWorkspace.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

#### TICKET-OMNI-02 — Implementar Criar Oportunidade a Partir do Chat [FEITO]  `[V1]`

- **Status:** FEITO
- **Evidência:** `OmnichannelWorkspace.tsx`: botão "Criar Oportunidade (Deal)" → POST `/api/v1/deals`.
- **O que fazer:** Adicionar criar oportunidade a partir do chat na interface da rota omnichannel .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/inbox/OmnichannelWorkspace.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

### v2 (2 tickets)

#### TICKET-OMNI-01 — Implementar Modelos de Resposta Rápida [FEITO]  `[v2]`

- **Status:** FEITO
- **Evidência:** `OmnichannelWorkspace.tsx`: `quickReplies` (5 modelos clínicos) renderizados como botões. Ressalva: lista estática no código, sem cadastro/edição de modelos.
- **O que fazer:** Adicionar modelos de resposta rápida na interface da rota omnichannel .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/inbox/OmnichannelWorkspace.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

#### TICKET-OMNI-02 — Implementar Anexar Exame 3D ao Chat [FEITO]  `[v2]`

- **Status:** FEITO
- **Evidência:** `OmnichannelWorkspace.tsx`: `R2DirectUploader` aceita `.stl,.dcm,.obj` e envia a mensagem com o link do arquivo no chat.
- **O que fazer:** Adicionar anexar exame 3d ao chat na interface da rota omnichannel .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/inbox/OmnichannelWorkspace.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

## Rota: keypartners

<a id="rota-keypartners"></a>

### V1 (2 tickets)

#### TICKET-KEY-01 — Implementar Leitor de Código de Barras / DataMatrix  `[V1]`

- **Status:** PARCIAL
- **Evidência:** `keypartners/ConsignmentSurgicalBoard.tsx`: modal com entrada manual, valida contra catálogo e quarentenas ANVISA. Sem leitura por câmera (sem `BarcodeDetector`/`getUserMedia`, apesar do texto do modal) e usa SKU fixo `IMP-CM-37511` quando não há correspondência.
- **O que fazer:** Adicionar leitor de código de barras / datamatrix na interface da rota keypartners .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/keypartners/ConsignmentSurgicalBoard.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

#### TICKET-KEY-02 — Implementar Reposição Rápida via DENTGO [FEITO]  `[V1]`

- **Status:** FEITO
- **Evidência:** `ConsignmentSurgicalBoard.tsx`: "Reposição Rápida via DENTGO" → POST `/surgical-orders/{id}/trigger-dentgo-replenishment`; rota existe em `src/features/keypartners/router.py` (HEAD).
- **O que fazer:** Adicionar reposição rápida via dentgo na interface da rota keypartners .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/keypartners/ConsignmentSurgicalBoard.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

### v2 (2 tickets)

#### TICKET-KEY-01 — Implementar Auditoria de Maleta via QR Code  `[v2]`

- **Status:** NÃO FEITO
- **Evidência:** Não há auditoria de maleta por QR. Só existe cadastro de maleta que gera `qr_code` e o leitor de DataMatrix (KEY-01 V1).
- **O que fazer:** Adicionar auditoria de maleta via qr code na interface da rota keypartners .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/keypartners/ConsignmentSurgicalBoard.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

#### TICKET-KEY-02 — Implementar Renovação Automática de Termo  `[v2]`

- **Status:** WIP
- **Evidência:** Somente no working tree (não commitado): `handleRenewAgreement` em `ConsignmentSurgicalBoard.tsx` e rota `POST /agreements/{id}/renew` em `src/features/keypartners/router.py`. Disparo manual por botão (+30d), não automático.
- **O que fazer:** Adicionar renovação automática de termo na interface da rota keypartners .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/keypartners/ConsignmentSurgicalBoard.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

## Rota: dentgo

<a id="rota-dentgo"></a>

### V1 (2 tickets)

#### TICKET-DENTGO-01 — Implementar Assinatura Digital de Entrega [FEITO]  `[V1]`

- **Status:** FEITO
- **Evidência:** `dentgo/DentgoExpressCockpit.tsx`: `DeliverySignaturePad` (canvas) envia `recipient_signature_data_url`; backend grava `recipient_signature_name`.
- **O que fazer:** Adicionar assinatura digital de entrega na interface da rota dentgo .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/dentgo/DentgoExpressCockpit.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

#### TICKET-DENTGO-02 — Implementar Comprovante Fotográfico do Lote [FEITO]  `[V1]`

- **Status:** FEITO
- **Evidência:** `DentgoExpressCockpit.tsx`: `R2DirectUploader` para foto de comprovante; envia `proof_photo_r2_key`. Ressalva: usa chave fictícia `pod/<id>/entrega.jpg` se nenhuma foto for enviada.
- **O que fazer:** Adicionar comprovante fotográfico do lote na interface da rota dentgo .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/dentgo/DentgoExpressCockpit.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

### v2 (2 tickets)

#### TICKET-DENTGO-01 — Implementar Alocação Inteligente de Hub  `[v2]`

- **Status:** PARCIAL
- **Evidência:** `DentgoExpressCockpit.tsx`: busca geolocalizada de hubs (`/dentgo/hubs/search-emergency`, Haversine + estoque) lista candidatos; não aloca o pedido a um hub automaticamente.
- **O que fazer:** Adicionar alocação inteligente de hub na interface da rota dentgo .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/dentgo/DentgoExpressCockpit.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

#### TICKET-DENTGO-02 — Implementar Notificar Cirurgião por SMS  `[v2]`

- **Status:** NÃO FEITO
- **Evidência:** Nenhuma ocorrência de SMS no frontend nem no `src/`.
- **O que fazer:** Adicionar notificar cirurgião por sms na interface da rota dentgo .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/dentgo/DentgoExpressCockpit.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

## Rota: video_sos

<a id="rota-video_sos"></a>

### V1 (2 tickets)

#### TICKET-SOS-01 — Implementar Snapshot / Foto da Tela com Anotações  `[V1]`

- **Status:** PARCIAL
- **Evidência:** `communications/LiveKitDealRoomModal.tsx`: `exportWhiteboardPNG` exporta só a lousa (canvas); não captura frame do vídeo com anotações.
- **O que fazer:** Adicionar snapshot / foto da tela com anotações na interface da rota video_sos .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/communications/LiveKitDealRoomModal.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

#### TICKET-SOS-02 — Implementar Troca Rápida de Câmera (Endoscópio) [FEITO]  `[V1]`

- **Status:** FEITO
- **Evidência:** `LiveKitDealRoomModal.tsx`: `<select>` de câmera (`enumerateDevices`) que reinicia a sala com o dispositivo escolhido.
- **O que fazer:** Adicionar troca rápida de câmera (endoscópio) na interface da rota video_sos .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/communications/LiveKitDealRoomModal.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

### v2 (2 tickets)

#### TICKET-SOS-01 — Implementar Adicionar 2º Cirurgião Especialista  `[v2]`

- **Status:** NÃO FEITO
- **Evidência:** `LiveKitDealRoomModal.tsx` não tem convite/adição de 2º participante; o nome "Consultor Especialista Revnaut" é fixo no token.
- **O que fazer:** Adicionar adicionar 2º cirurgião especialista na interface da rota video_sos .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/communications/LiveKitDealRoomModal.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

#### TICKET-SOS-02 — Implementar Anotação Visual sobre o Vídeo  `[v2]`

- **Status:** PARCIAL
- **Evidência:** Lousa cirúrgica (canvas, caneta/régua/implante) em aba própria; não há anotação sobreposta ao vídeo.
- **O que fazer:** Adicionar anotação visual sobre o vídeo na interface da rota video_sos .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/communications/LiveKitDealRoomModal.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

## Rota: contracts

<a id="rota-contracts"></a>

### V1 (2 tickets)

#### TICKET-DOC-01 — Implementar Assinatura Presencial na Tela [FEITO]  `[V1]`

- **Status:** FEITO
- **Evidência:** `contracts/ContractsDocumensoWorkspace.tsx`: pad de assinatura em canvas; `signature_png` enviado ao webhook de assinatura.
- **O que fazer:** Adicionar assinatura presencial na tela na interface da rota contracts .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/contracts/ContractsDocumensoWorkspace.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

#### TICKET-DOC-02 — Implementar Renovação Automática de Vigência  `[V1]`

- **Status:** PARCIAL
- **Evidência:** Botão "Renovar Vigência (+12m)" chama `/deals/{id}/generate-contract` com `contract_type: "renewal"`, `renewal_months`, `parent_contract_id`; o backend (`deals/documenso_service.py`) não trata esses campos (nenhuma ocorrência no `src/`), então a vigência não é calculada.
- **O que fazer:** Adicionar renovação automática de vigência na interface da rota contracts .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/contracts/ContractsDocumensoWorkspace.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

### v2 (2 tickets)

#### TICKET-DOC-01 — Implementar Assinatura com Certificado ICP-Brasil  `[v2]`

- **Status:** NÃO FEITO
- **Evidência:** Nenhuma assinatura com certificado ICP-Brasil; "E-mail para Manifesto ICP" é só um rótulo de campo.
- **O que fazer:** Adicionar assinatura com certificado icp-brasil na interface da rota contracts .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/contracts/ContractsDocumensoWorkspace.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

#### TICKET-DOC-02 — Implementar Lembrete de Assinatura por WhatsApp  `[v2]`

- **Status:** NÃO FEITO
- **Evidência:** Há campo de WhatsApp do signatário, mas nenhum lembrete de assinatura (nenhuma ocorrência de `lembrete`/`remind` em `src/` ou frontend).
- **O que fazer:** Adicionar lembrete de assinatura por whatsapp na interface da rota contracts .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/contracts/ContractsDocumensoWorkspace.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

## Rota: imaging

<a id="rota-imaging"></a>

### V1 (2 tickets)

#### TICKET-IMG-01 — Implementar Simulação de Posicionamento do Implante [FEITO]  `[V1]`

- **Status:** FEITO
- **Evidência:** `imaging/DicomStl3DViewer.tsx`: guia de implante arrastável/clicável (`implantPos`) com diâmetro selecionável sobre os cortes.
- **O que fazer:** Adicionar simulação de posicionamento do implante na interface da rota imaging .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/imaging/DicomStl3DViewer.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

#### TICKET-IMG-02 — Implementar Exportar Guia Cirúrgico em STL  `[V1]`

- **Status:** PARCIAL
- **Evidência:** `DicomStl3DViewer.tsx`: `handleExportSurgicalGuideStl` baixa `.stl`, mas exporta a malha carregada ou um tetraedro fixo de 4 triângulos; não gera geometria de guia cirúrgico.
- **O que fazer:** Adicionar exportar guia cirúrgico em stl na interface da rota imaging .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/imaging/DicomStl3DViewer.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

### v2 (2 tickets)

#### TICKET-IMG-01 — Implementar Medição de Densidade Óssea (Hounsfield)  `[v2]`

- **Status:** NÃO FEITO
- **Evidência:** `DicomStl3DViewer.tsx` só mostra janela/nível em HU e a densidade estimada pelo backend (texto); não há medição de HU por ROI/ponto.
- **O que fazer:** Adicionar medição de densidade óssea (hounsfield) na interface da rota imaging .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/imaging/DicomStl3DViewer.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

#### TICKET-IMG-02 — Implementar Simulação Virtual de Instalação de Implante [FEITO]  `[v2]`

- **Status:** FEITO
- **Evidência:** Mesma evidência de IMG-01 (V1): posicionamento arrastável do implante com diâmetro/comprimento recomendados.
- **O que fazer:** Adicionar simulação virtual de instalação de implante na interface da rota imaging .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/imaging/DicomStl3DViewer.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

## Rota: support

<a id="rota-support"></a>

### V1 (2 tickets)

#### TICKET-SUP-01 — Implementar Substituição Imediata em Garantia [FEITO]  `[V1]`

- **Status:** FEITO
- **Evidência:** `support/SupportAnvisaWorkspace.tsx`: "Substituição Imediata em Garantia via DENTGO" cria pedido expresso e exibe PIN/protocolo.
- **O que fazer:** Adicionar substituição imediata em garantia na interface da rota support .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/support/SupportAnvisaWorkspace.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

#### TICKET-SUP-02 — Implementar Upload de Raio-X Pós-Cirúrgico [FEITO]  `[V1]`

- **Status:** FEITO
- **Evidência:** `SupportAnvisaWorkspace.tsx`: `R2DirectUploader` + link de visualização do raio-X (`/api/v1/storage/files/<key>`).
- **O que fazer:** Adicionar upload de raio-x pós-cirúrgico na interface da rota support .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/support/SupportAnvisaWorkspace.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

### v2 (2 tickets)

#### TICKET-SUP-01 — Implementar Upload de Radiografia Periapical de Falha [FEITO]  `[v2]`

- **Status:** FEITO
- **Evidência:** `SupportAnvisaWorkspace.tsx`: `R2DirectUploader` (módulo `dicom`) no formulário de RMA; chave enviada como `radiograph_r2_key`.
- **O que fazer:** Adicionar upload de radiografia periapical de falha na interface da rota support .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/support/SupportAnvisaWorkspace.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

#### TICKET-SUP-02 — Implementar Notificação Direta para Engenharia de Produto  `[v2]`

- **Status:** NÃO FEITO
- **Evidência:** Nenhuma notificação para Engenharia de Produto (nenhuma ocorrência de `engenharia`/`engineering` no componente nem em `tickets/`).
- **O que fazer:** Adicionar notificação direta para engenharia de produto na interface da rota support .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/support/SupportAnvisaWorkspace.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

## Rota: intelligence

<a id="rota-intelligence"></a>

### V1 (2 tickets)

#### TICKET-INTEL-01 — Implementar Copiar Resposta do Catálogo para o Chat [FEITO]  `[V1]`

- **Status:** FEITO
- **Evidência:** `intelligence/IntelligenceSuiteWorkspace.tsx`: "Copiar Resposta para o Chat" via `navigator.clipboard.writeText`.
- **O que fazer:** Adicionar copiar resposta do catálogo para o chat na interface da rota intelligence .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/intelligence/IntelligenceSuiteWorkspace.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

#### TICKET-INTEL-02 — Implementar Exportar Relatório KOL em PDF [FEITO]  `[V1]`

- **Status:** FEITO
- **Evidência:** `IntelligenceSuiteWorkspace.tsx`: `buildKolPdfBinary` + upload `/storage/upload-direct/reports/relatorio_kol_revnault.pdf`.
- **O que fazer:** Adicionar exportar relatório kol em pdf na interface da rota intelligence .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/intelligence/IntelligenceSuiteWorkspace.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

### v2 (2 tickets)

#### TICKET-INT-01 — Implementar Sugestão Automática de Ação no Chatwoot  `[v2]`

- **Status:** NÃO FEITO
- **Evidência:** `IntelligenceSuiteWorkspace.tsx` não referencia Chatwoot nem sugere ações; a bridge existe só no backend (`integrations/omnichannel/chatwoot_bridge.py`).
- **O que fazer:** Adicionar sugestão automática de ação no chatwoot na interface da rota intelligence .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/intelligence/IntelligenceSuiteWorkspace.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

#### TICKET-INT-02 — Implementar Indexar Novo Manual Técnico no RAG [FEITO]  `[v2]`

- **Status:** FEITO
- **Evidência:** `IntelligenceSuiteWorkspace.tsx`: formulário de ingestão → POST `/api/v1/intelligence/catalog-rag/ingest`; rota backend existe.
- **O que fazer:** Adicionar indexar novo manual técnico no rag na interface da rota intelligence .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/intelligence/IntelligenceSuiteWorkspace.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

## Rota: analytics

<a id="rota-analytics"></a>

### V1 (2 tickets)

#### TICKET-ANA-01 — Implementar Salvar Pergunta nos Favoritos [FEITO]  `[V1]`

- **Status:** FEITO
- **Evidência:** `bi/SupersetEmbeddedDashboard.tsx`: "Salvar Pergunta nos Favoritos" com chips; persistência em `localStorage` (por navegador, não compartilhada).
- **O que fazer:** Adicionar salvar pergunta nos favoritos na interface da rota analytics .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/bi/SupersetEmbeddedDashboard.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

#### TICKET-ANA-02 — Implementar Compartilhar Dashboard com a Equipe  `[V1]`

- **Status:** PARCIAL
- **Evidência:** `SupersetEmbeddedDashboard.tsx`: `buildShareLink` gera link com `Math.random()` e papel, e copia para a área de transferência; sem token validado nem persistência no backend.
- **O que fazer:** Adicionar compartilhar dashboard com a equipe na interface da rota analytics .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/bi/SupersetEmbeddedDashboard.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

### v2 (2 tickets)

#### TICKET-ANA-01 — Implementar Salvar Consulta no Favoritos [FEITO]  `[v2]`

- **Status:** FEITO
- **Evidência:** Mesma evidência de ANA-01 (V1): favoritos em `localStorage` no `SupersetEmbeddedDashboard.tsx`.
- **O que fazer:** Adicionar salvar consulta no favoritos na interface da rota analytics .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/bi/SupersetEmbeddedDashboard.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

#### TICKET-ANA-02 — Implementar Agendamento de Envio por E-mail  `[v2]`

- **Status:** WIP
- **Evidência:** Não está no `HEAD`. `Mail` e novos blocos estão sendo adicionados ao `SupersetEmbeddedDashboard.tsx` por outro agente (não commitado).
- **O que fazer:** Adicionar agendamento de envio por e-mail na interface da rota analytics .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/bi/SupersetEmbeddedDashboard.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

## Rota: scheduling

<a id="rota-scheduling"></a>

### V1 (2 tickets)

#### TICKET-SCHED-01 — Implementar Confirmação Automática por Botão 1-Clique [FEITO]  `[V1]`

- **Status:** FEITO
- **Evidência:** `scheduling/CalcomReactivationWorkspace.tsx`: botão "Confirmacao 1-Clique" confirma o agendamento pendente via `/automations/calcom/webhook`. Ressalva: usa payload de webhook simulado.
- **O que fazer:** Adicionar confirmação automática por botão 1-clique na interface da rota scheduling .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/scheduling/CalcomReactivationWorkspace.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

#### TICKET-SCHED-02 — Implementar Bloqueio de Agenda por Falta de Material [FEITO]  `[V1]`

- **Status:** FEITO
- **Evidência:** `CalcomReactivationWorkspace.tsx`: "Bloquear Agenda (Falta Material)" → webhook `SCHEDULE_BLOCKED_MATERIAL`; `automations/calcom_reactivation.py` marca `BLOQUEADO_MATERIAL`.
- **O que fazer:** Adicionar bloqueio de agenda por falta de material na interface da rota scheduling .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/scheduling/CalcomReactivationWorkspace.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

### v2 (2 tickets)

#### TICKET-SCH-01 — Implementar Confirmação em 1 Clique (Sim/Não)  `[v2]`

- **Status:** PARCIAL
- **Evidência:** Há "Confirmacao 1-Clique" e "Confirmar Retorno", mas não existe fluxo Sim/Não (sem opção de recusa/cancelamento).
- **O que fazer:** Adicionar confirmação em 1 clique (sim/não) na interface da rota scheduling .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/scheduling/CalcomReactivationWorkspace.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

#### TICKET-SCH-02 — Implementar Reagendamento de Faltosos  `[v2]`

- **Status:** NÃO FEITO
- **Evidência:** Nenhum fluxo de reagendamento de faltosos no frontend. No backend há varredura de reativação em `automations/router.py`, sem botão correspondente.
- **O que fazer:** Adicionar reagendamento de faltosos na interface da rota scheduling .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/scheduling/CalcomReactivationWorkspace.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

## Rota: rbac

<a id="rota-rbac"></a>

### V1 (2 tickets)

#### TICKET-RBAC-01 — Implementar Bloqueio Temporário de Usuário  `[V1]`

- **Status:** PARCIAL
- **Evidência:** `rbac/RbacHierarchyTree.tsx`: botão "Bloqueio Temporario" só inverte `userBlockToggle` (estado local); sem endpoint nem efeito no usuário.
- **O que fazer:** Adicionar bloqueio temporário de usuário na interface da rota rbac .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/rbac/RbacHierarchyTree.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

#### TICKET-RBAC-02 — Implementar Exportar Folha de Comissões para ERP [FEITO]  `[V1]`

- **Status:** FEITO
- **Evidência:** `RbacHierarchyTree.tsx`: "Exportar Folha ERP" baixa `folha_comissoes_erp.csv` gerado do extrato de comissões (CSV no cliente, sem integração direta com ERP).
- **O que fazer:** Adicionar exportar folha de comissões para erp na interface da rota rbac .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/rbac/RbacHierarchyTree.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

### v2 (2 tickets)

#### TICKET-RBAC-01 — Implementar Simulador de Comissões para o Vendedor  `[v2]`

- **Status:** NÃO FEITO
- **Evidência:** Nenhum simulador de comissões para o vendedor (nenhuma ocorrência de `simulat` em `RbacHierarchyTree.tsx`).
- **O que fazer:** Adicionar simulador de comissões para o vendedor na interface da rota rbac .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/rbac/RbacHierarchyTree.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

#### TICKET-RBAC-02 — Implementar Histórico de Alterações de Cargo  `[v2]`

- **Status:** WIP
- **Evidência:** Somente backend e não commitado: `GET /audit-history` em `src/features/hierarchy/router.py`. Frontend sem consumo.
- **O que fazer:** Adicionar histórico de alterações de cargo na interface da rota rbac .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/rbac/RbacHierarchyTree.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

## Rota: settings

<a id="rota-settings"></a>

### V1 (2 tickets)

#### TICKET-SETT-01 — Implementar Rotação Automática de Chaves  `[V1]`

- **Status:** PARCIAL
- **Evidência:** `settings/CredentialsVaultPage.tsx`: "Rotacionar Chave Automaticamente" só grava `rotated_at` nos metadados da credencial; não gera nova chave nem agenda rotação.
- **O que fazer:** Adicionar rotação automática de chaves na interface da rota settings .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/settings/CredentialsVaultPage.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

#### TICKET-SETT-02 — Implementar Re-tentativa Manual de Webhooks com Falha  `[V1]`

- **Status:** PARCIAL
- **Evidência:** `CredentialsVaultPage.tsx`: existem `reset-circuit` e `test-dispatch` por assinatura; não há reenvio manual de uma entrega com falha do log.
- **O que fazer:** Adicionar re-tentativa manual de webhooks com falha na interface da rota settings .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/settings/CredentialsVaultPage.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

### v2 (2 tickets)

#### TICKET-SET-01 — Implementar Rotação Automática de Chaves  `[v2]`

- **Status:** PARCIAL
- **Evidência:** Mesma evidência de SETT-01 (V1): só grava `rotated_at` nos metadados.
- **O que fazer:** Adicionar rotação automática de chaves na interface da rota settings .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/settings/CredentialsVaultPage.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.

#### TICKET-SET-02 — Implementar Log de Acesso ao Cofre (Quem Acessou O Quê)  `[v2]`

- **Status:** WIP
- **Evidência:** Somente backend e não commitado: `GET /credentials/audit-logs` em `src/features/auth/router.py`. `CredentialsVaultPage.tsx` sem consumo.
- **O que fazer:** Adicionar log de acesso ao cofre (quem acessou o quê) na interface da rota settings .
- **Como fazer:** Integrar componente com o endpoint correspondente no backend.
- **Onde fazer:** frontend/src/features/settings/CredentialsVaultPage.tsx
- **Critério binário de aceitação:** Teste automatizado com código exit 0.
