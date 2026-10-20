# Manuais Operacionais e Catálogo de Rotas & Sub-rotas • RevNault Dental

Este diretório contém a documentação canônica, padronizada e sincronizada de todas as telas, rotas e sub-rotas operacionais da plataforma **RevNault Dental Ops** (Revenue Operations, CRM B2B Industrial Odontológico, KeyPartners & DENTGO).

## Estrutura Canônica dos Manuais (Seções Anatômicas Obrigatórias & Zero Emojis)
Cada manual segue a estrutura anatômica estrita de governança (Lei #12 — *Anti-Docs Rot* e Lei #14 — *Zero Emojis*), cobrindo obrigatoriamente as 6 dimensões fundamentais de operação e governança (e estendida até 9 seções anatômicas auditadas por `G_MANUAIS_ROTAS.py`):
1. **Objetivo da Rota / Sub-rota**: Propósito de negócio no nicho odontológico industrial.
2. **O Que o Usuário Consegue Realizar**: Funcionalidades ativas, integrações ERP e motores de IA.
3. **Quem Pode Ver e Realizar Ações (Matriz RBAC)**: Controle granular de acesso por cargo e subárvore dual (Field Sales + Inside Sales).
4. **Quais Ações Podem Ser Realizadas**: Eventos, despachos e ações transacionais do controlador.
5. **Como o Usuário Realiza as Ações (Passo a Passo)**: Guia operacional de uso pelo operador da tela.
6. **Catálogo Anatômico de Botões & Ações do DOM**: Inventário factual de cada botão, classe, `onclick` e impacto no sistema.
7. **Catálogo de Modais & Gavetas Operacionais**: Relação de modais, finalidades, campos obrigatórios e validações.
8. **Motores de Backend & Arquitetura Subjacente**: Endpoints REST, garantias transacionais (PostgreSQL 16 + pgvector / SQLite WAL), Redis Streams, Cloudflare R2 e resiliência.
9. **O Que Falta Implementar & Plano de Micro-Tickets**: Roadmap técnico e status de conclusão dos micro-tickets (`TICKET-00` a `TICKET-42`).

---

## Catálogo Geral de Rotas, Sub-rotas e Módulos React 19 SPA (Relação 1-para-1 Estrita)

| Cód | Rota / Sub-rota | Identificador / Hash / Rota SPA | Tipo | Destaques da Arquitetura & Implementação |
|---|---|---|---|---|
| 00 | [Acesso & Autenticação](00_login.md) | `/#login` | Rota | Cliente modular `api-client.js`, Bearer JWT e Super Admin único. |
| 01 | [Comercial, Vendas & Funis](01_deals.md) | `/#deals` / `deals` | Rota | Pedidos TOTVS Protheus (`SC5/SC6`), Copiloto Granola LiteLLM, Documenso e múltiplos pipelines. |
| 02 | [Cirurgiões & Base de Contatos](02_contacts.md) | `/#contacts` / `contacts` | Rota | Grafo Clínico KOL, validador CRO/UF com cache Redis 7d (`CroVerifiedInput`) e WhatsApp em 1 clique. |
| 03 | [Segmentos Inteligentes](03_contacts_segments.md) | `/#contacts-segments` | Sub-rota | Filtros dinâmicos por especialidade e sincronização em tempo real com Mautic VPS e Listmonk. |
| 04 | [Inbox Omnichannel WhatsApp](04_inbox.md) | `/#inbox` / `omnichannel` | Rota | Sharding Evolution API v2 + Chatwoot + Sidebar Contextual 360° (`OmnichannelContextSidebar`). |
| 05 | [Central de Tickets & Suporte](05_tickets.md) | `/#tickets` / `support` | Rota | Tecnovigilância ANVISA, RMA de osseointegração, quarentena automática de lotes (>2.5%) e SLA cirúrgico. |
| 06 | [Tarefas Operacionais & Checklist](06_tasks.md) | `/#tasks` | Rota | Gatilhos de receita, SLA de 15min para leads Tier A e alertas de ociosidade $SOK \ge 1.0$. |
| 07 | [Relatórios Executivos & KPIs](07_reports.md) | `/#reports` | Rota | BI com consolidação hierárquica por subárvore recursiva, margem clínica líquida e radar anti-churn. |
| 08 | [Performance por Consultor](08_reports_performance.md) | `/#reports-performance` | Sub-rota | Comissionamento bipartido (70% Field Sales / 30% Inside Sales) e taxa de conversão cirúrgica. |
| 09 | [Campanhas de Marketing & CIOSP](09_marketing.md) | `/#marketing` / `marketing` | Rota | Construtor de Landing Pages GrapesJS (`LandingPageBuilder`) com compliance CFO Art. 43 e publicação no R2. |
| 10 | [Sincronização Mautic VPS](10_marketing_mautic.md) | `/#marketing-mautic` | Sub-rota | Arquitetura híbrida Mautic 5 + Listmonk + loop viral de indicação B2B (MGM Cirúrgico). |
| 11 | [Lead Scoring de Cirurgiões](11_scoring.md) | `/#scoring` / `scoring` | Rota | Painel `IcpScoringDashboard`, histórico `scoring_history` e handoff automático Tier A para o Closer regional. |
| 12 | [Critérios ICP & Prescrição](12_scoring_icp.md) | `/#scoring-icp` | Sub-rota | Matriz de pontuação por volume de implantes/mês, clínica própria, especialidade CRO e afinidade vetorial. |
| 13 | [Fluxos de Automação Cirúrgica](13_automations.md) | `/#automations` / `scheduling` | Rota | Agendamento inteligente Cal.com (reativação 6/12/18m) e régua pós-operatória B2C (24h/48h/72h/7d). |
| 14 | [Organograma & RBAC Setorial](14_hierarchy.md) | `/#hierarchy` / `rbac` | Rota | Árvore Dual Field/Inside (`RbacHierarchyTree`), 4 Presets Odontológicos e resolução DAG sem ciclos. |
| 15 | [Central de Usuários & Acessos](15_users.md) | `/#users` | Rota | Governança exclusiva do Super Admin Único com paginação determinística e escopo de visibilidade. |
| 16 | [Importador Universal de Carteiras](16_import_contacts.md) | `/#import-contacts` | Rota | Deduplicação por chave composta (`cro` + `uf`) e recálculo automático de scoring. |
| 17 | [Central de Conectores Enterprise](17_integrations.md) | `/#integrations` | Rota | Hub Fiscal Windmill (TOTVS Protheus, SAP B1, Sankhya) com NF-e CFOP 5.917/1.918/5.113 no R2. |
| 18 | [KeyPartners Consignados & Lotes](18_keypartners.md) | `/#keypartners` / `keypartners` | Rota | Quadro `ConsignmentSurgicalBoard`, custódia líquida ANVISA, conferência de lacre no R2 e programa Moeda Cirúrgica. |
| 19 | [KeyPartners KOLs & Custódia](19_keypartners_kols.md) | `/#keypartners-kols` | Sub-rota | Contratos de comodato de KOLs, evidências clínicas no R2, cálculo preditivo $SOK$/$PR$ e Health Score $HSC$. |
| 20 | [DENTGO Express Despacho 45min](20_dentgo.md) | `/#dentgo` / `dentgo` | Rota | Cockpit `DentgoExpressCockpit`, roteamento Haversine, lacre térmico, validação de PIN e split financeiro. |
| 21 | [DENTGO Rastreabilidade FEFO & PIN](21_dentgo_fefo.md) | `/#dentgo-fefo` | Sub-rota | Liquidação inteligente FEFO (6 a 9 meses) via Flash Deals geolocalizados (50 km) e reserva atômica. |
| 22 | [Vídeo Suporte SOS Mesa Cirúrgica](22_video_sos.md) | `/#video-sos` / `video_sos` | Rota | Sala LiveKit WebRTC/SIP (`LiveKitDealRoomModal`) com Egress R2, transcrição `faster-whisper` e RAG cirúrgico. |
| 23 | [Tomografias DICOM & STL 3D](23_dicom_viewer.md) | `/#dicom-viewer` / `imaging` | Rota | Visualizador `DicomStl3DViewer` integrado ao Orthanc PACS v24.3, presigned URLs R2 e anonimização LGPD. |
| 24 | [BI Executivo Superset](24_bi_superset.md) | `/#bi-superset` / `analytics` | Rota | `SupersetEmbeddedDashboard` com Guest Tokens JWT, RLS por escopo, Text-to-SQL seguro e exportação R2. |
| 25 | [Governança AIDD & Quarteto](25_governanca_studios_quarteto.md) | `/docs`, `/webhooks`, `/mcp`, `/docs/guia` | Governança | Swagger Studio, Webhook Studio, Servidor Nativo MCP e Guia do Usuário da Lei #10. |
| 26 | [Cockpit React 19, Cofre AES-256 & ERP](26_react19_cockpit_unificado_vault_erp.md) | `/#settings` / `settings` / `contracts` / `intelligence` | Rota | `CredentialsVaultPage` (AES-256-GCM), `R2DirectUploader`, `GranolaCopilotCard` e contratos 1:1 `API_V1_ROUTES`. |
| 27 | [Inteligência de Mercado & Radar de Concorrência](27_market_intel_radar.md) | `/#market_intel` / `market_intel` | Rota | `MarketIntelRadarWorkspace` com RBAC territorial, crawler passivo (janela 01:00-05:00 UTC, jitter 7-22s, dedup SHA-256), matcher vetorial de SKUs e trava anti-spam de 15 dias. |
