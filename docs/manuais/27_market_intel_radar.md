# Manual da Rota: Inteligência de Mercado & Radar de Concorrência (`/#market_intel`)

## 1. Objetivo da Rota / Sub-rota
Concentrar em uma única tela (`/#market_intel`, componente `MarketIntelRadarWorkspace`) a leitura de sinais do mercado odontológico (ANVISA, FDA, congressos e periódicos científicos), o monitoramento passivo de concorrentes e o disparo determinístico de campanhas táticas por praça. Cada oportunidade é cruzada com SKUs reais do catálogo (`products_catalog`) e nenhum cirurgião recebe mais de uma campanha automatizada a cada 15 dias.

---

## 2. O Que o Usuário Consegue Realizar
* Filtrar sinais de mercado por escopo geográfico (`GLOBAL`, `BR-SP`, `BR-PR`, `BR-PE`, `US-FL`, `LATAM`), especialidade e tipo de fonte, com tópicos, tendências e link da fonte original.
* Acompanhar os concorrentes monitorados, a timeline de capturas com hash SHA-256 e as ofertas detectadas (produto, preço e desconto).
* Consultar o relatório de contra-ataque B2B, que compara a oferta do concorrente com o SKU equivalente do catálogo e a diferença percentual de preço.
* Filtrar oportunidades por Unidade de Negócio (`Implantodontia`, `Prótese Digital`, `Biomateriais`), praça e status, e gerar a minuta da campanha tática.
* Revisar a minuta validada pela Resolução CFO 196/2019 e aprovar o disparo, com contadores de enviados e de bloqueados pela trava de 15 dias.
* Simular no cabeçalho cada perfil da matriz RBAC (Diretor, Gerente Regional, Consultor Interno e Consultor Externo) e a praça do perfil.

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil | Sinais | Concorrentes | Gerar Minuta | Aprovar/Disparar |
|---|---|---|---|---|
| Diretor Nacional / Admin (`director`) | Global (todas as praças) | Leitura + cadastro de concorrentes | Sim (qualquer praça) | Sim (qualquer praça) |
| Gerente Regional (`regional_manager`) | Sua praça + `GLOBAL` | Somente leitura | Sim (sua praça) | Sim (sua praça) |
| Consultor Interno SDR/Inside (`inside_sales`) | Sua carteira/praça + `GLOBAL` | Somente leitura de insights | Sim (rascunho) | Não (HTTP 403) |
| Consultor Externo de Campo (`field_sales`) | Alertas da praça + `GLOBAL` (visão mobile) | Cards de contra-ataque | Não (HTTP 403) | Não (HTTP 403) |

Todas as rotas exigem o token de sessão emitido no login (`Authorization: Bearer <token>`); sem token válido ou com usuário inativo a resposta é HTTP 401. Perfil, praça e tenant vêm do cadastro do usuário (`users.role`, `users.is_superadmin`, `users.region_code`, `users.account_id`), nunca de headers livres. O cabeçalho `X-User-Role` só rebaixa o perfil (simulação de perfis menores) e `X-User-Region` só é aceito quando o usuário real é Diretoria. O perfil efetivo pode ser consultado em `GET /api/v1/market-intel/me`.

---

## 4. Quais Ações Podem Ser Realizadas
* `WHOAMI`: `GET /api/v1/market-intel/me` (perfil efetivo, praça e permissões do usuário autenticado).
* `LIST_SIGNALS`: `GET /api/v1/market-intel/signals` com `scope`, `specialty`, `source_type`, `limit` e `offset`.
* `LIST_OPPORTUNITIES`: `GET /api/v1/market-intel/opportunities` com `region_code`, `bu_target` e `status`.
* `MATCH_OPPORTUNITY`: `POST /api/v1/market-intel/opportunities/match` (sinal ou snapshot contra o catálogo).
* `GENERATE_DRAFT`: `POST /api/v1/market-intel/campaigns/generate-draft` (minuta `DRAFT` com validação ética CFO).
* `LIST_CAMPAIGNS`: `GET /api/v1/market-intel/campaigns`.
* `DISPATCH_CAMPAIGN`: `POST /api/v1/campaigns/{campaign_id}/dispatch` ou `POST /api/v1/market-intel/campaigns/{campaign_id}/dispatch`.
* `LIST_COMPETITORS` / `REGISTER_COMPETITOR`: `GET` e `POST /api/v1/competitors`.
* `COMPETITOR_TIMELINE`: `GET /api/v1/competitors/{competitor_id}/snapshots`.
* `TACTICAL_INSIGHTS`: `GET /api/v1/competitors/tactical-insights`.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)
1. No menu lateral, abra **Radar de Mercado e Concorrência** (atalho `N`) ou use o botão **Radar de Mercado** na tela Assistente Comercial.
2. O cartão de perfil mostra o seu perfil e a sua praça, lidos do cadastro. Somente a Diretoria pode simular perfis menores e outras praças. Os selos mostram o que o perfil efetivo pode fazer.
3. Na aba **Sinais de Mercado**, combine escopo, especialidade e tipo de fonte. Cada cartão mostra tópicos, tendências e o link da fonte.
4. Na aba **Concorrentes**, selecione um concorrente para ver a timeline de capturas. O Diretor pode usar **Registrar Concorrente** para incluir um domínio na fila noturna.
5. Na aba **Oportunidades x BUs**, filtre por BU, praça e status, escolha o canal (WhatsApp ou e-mail) e clique em **Gerar Minuta de Campanha Tatica**.
6. Na aba **Disparos & Trava 15d**, revise a minuta e clique em **Aprovar & Disparar Campanha (Trava 15d)**. Os contadores mostram quantos contatos receberam a mensagem e quantos foram bloqueados pela trava.

---

## 6. Catálogo Anatômico de Botões & Ações do DOM

| Botão / Controle | Localização | Ação | Regra |
|---|---|---|---|
| Perfil (select) | Cartão de perfil | Define `X-User-Role` das chamadas (somente rebaixa o perfil) | Habilitado só para Diretoria |
| Praça do perfil (select) | Cartão de perfil | Define `X-User-Region` | Habilitado só para Diretoria simulando perfil regional |
| Atualizar | Cabeçalho da rota | Recarrega a aba ativa | Todos os perfis |
| Registrar Concorrente | Banner da fila passiva | Abre o modal de cadastro | Habilitado só para Diretor |
| Item de concorrente | Lista lateral da aba Concorrentes | Carrega a timeline de snapshots | Todos os perfis |
| Gerar Minuta de Campanha Tatica | Cartão de oportunidade | `POST .../campaigns/generate-draft` | Desabilitado para Consultor Externo |
| Item de campanha | Lista lateral da aba Disparos | Seleciona a minuta para revisão | Todos os perfis |
| Aprovar & Disparar Campanha (Trava 15d) | Painel da minuta | `POST /api/v1/campaigns/{id}/dispatch` | Somente Diretor e Gerente Regional, campanhas em `DRAFT` |
| Fonte original | Cartão de sinal | Abre a URL da fonte em nova aba | Todos os perfis |

---

## 7. Catálogo de Modais & Gavetas Operacionais
* **Registrar concorrente na fila passiva** (`Dialog`): campos Nome, Domínio público e Frequência de coleta (24h, 72h ou semanal). Ao confirmar, o domínio é normalizado, gravado em `competitors` e recebe a próxima coleta dentro da janela 01:00-05:00 UTC. Nenhuma página é coletada no momento do cadastro. Domínio duplicado retorna HTTP 409.

---

## 8. Motores de Backend & Arquitetura Subjacente
* `src/features/market_intel/crawler_engine.py`: janela morta de 01:00 a 05:00 UTC (`is_within_dead_window_utc`), jitter de 7 a 22 segundos por domínio (`compute_domain_jitter_seconds`), headers desktop rotacionados com script stealth do Playwright (`navigator.webdriver = false`), limpeza do DOM com SHA-256 (`normalize_and_hash_dom`) e deduplicação: conteúdo inalterado retorna `SKIPPED_UNCHANGED_HASH` sem chamar o LLM.
* `src/features/market_intel/llm_classifier.py`: usa Ollama (`/api/generate`, `format=json`, `qwen2.5:7b`) ou LiteLLM quando `OLLAMA_BASE_URL` ou `LITELLM_API_KEY` estiver configurado. Na falta deles, usa um classificador odontológico determinístico por regras. Extrai ofertas com preço em reais e desconto.
* `src/features/market_intel/opportunity_matcher.py`: indexa produtos e sinais no `VectorStoreService` (`compute_semantic_embedding`), define BU e tipo de oportunidade e recomenda SKUs reais por similaridade de cosseno, filtrados pela categoria da BU.
* `src/features/market_intel/campaign_dispatcher.py`: aplica a matriz RBAC, valida a minuta com `cro_validator.validate_cfo_marketing_compliance` e aplica a trava de 15 dias em `campaign_recipient_locks`. Envia por `omnichannel_messages` (WhatsApp) ou `ListmonkClient.send_transactional` (e-mail).
* Worker: o stream `stream:market_intel` (`handle_market_intel_stream` em `src/workers/runner.py`) processa `market_intel.batch.tick`, `competitor.snapshot.ingested` e `market_signal.ingested`.
* Agendador do lote noturno (`src/workers/market_intel_scheduler.py`): o processo do worker publica `market_intel.batch.tick` uma vez por slot horário da janela 01:00-05:00 UTC (01h, 02h, 03h e 04h) para cada tenant com concorrente ativo. A tabela `market_intel_batch_ticks` (chave slot + tenant) impede tick duplicado entre réplicas e reinícios. Pode ser desligado com `MARKET_INTEL_SCHEDULER_ENABLED=0`.
* Persistência: tabelas `market_signals`, `competitors`, `competitor_snapshots`, `market_opportunities`, `targeted_campaigns` e `campaign_recipient_locks`, criadas em `init_db()` e na migração Alembic `0002_add_market_intel_and_competitor_radar`.

---

## 9. O Que Falta Implementar & Plano de Micro-Tickets
* `MKTINTEL-NEXT-01`: ingestão automática de feeds RSS (CFO, revistas e portais de eventos) para `market_signals`. Hoje os sinais vêm do seed ou da publicação do evento `market_signal.ingested`.
* `MKTINTEL-NEXT-02`: edição da minuta na própria tela antes da aprovação, com revalidação CFO. Hoje a minuta é gerada pelo backend e exibida somente para leitura.
* `MKTINTEL-NEXT-03`: ação de descartar oportunidade (`DISMISSED`) pela interface.
