# Manuais Operacionais e Catálogo de Rotas & Sub-rotas • Revnaut Dental

Este diretório contém a documentação canônica, padronizada e sincronizada de todas as telas, rotas e sub-rotas operacionais da plataforma **Revnaut Dental Ops** (Revenue Operations e CRM B2B Industrial Odontológico).

## Estrutura Canônica dos Manuais (9 Seções Anatômicas)
Cada manual segue a estrutura anatômica estrita de governança (Lei #12 — *Anti-Docs Rot* e Lei #14 — *Zero Emojis*):
1. **Objetivo da Rota / Sub-rota**: Propósito de negócio no nicho odontológico industrial.
2. **O Que o Usuário Consegue Realizar**: Funcionalidades ativas, integrações ERP e motores de IA.
3. **Quem Pode Ver e Realizar Ações (Matriz RBAC)**: Controle granular de acesso por cargo e subárvore de times.
4. **Quais Ações Podem Ser Realizadas**: Eventos, despachos e ações transacionais do controlador.
5. **Como o Usuário Realiza as Ações (Passo a Passo)**: Guia operacional de uso pelo operador da tela.
6. **Catálogo Anatômico de Botões & Ações do DOM**: Inventário factual de cada botão, classe, `onclick` e impacto no sistema.
7. **Catálogo de Modais & Gavetas Operacionais**: Relação de modais, finalidades, campos obrigatórios e validações.
8. **Motores de Backend & Arquitetura Subjacente**: Endpoints REST, garantias transacionais (SQLite WAL), outbox e resiliência.
9. **O Que Falta Implementar & Plano de Micro-Tickets**: Roadmap técnico e tickets atômicos TDD com critérios binários.

---

## Catálogo Geral de Rotas e Sub-rotas (Relação 1-para-1 Estrita)

| Cód | Rota / Sub-rota | Identificador / Hash | Tipo | Destaques da Arquitetura & Implementação |
|---|---|---|---|---|
| 00 | [Acesso & Autenticação](00_login.md) | `/#login` | Rota | Cliente modular `api-client.js`, Bearer JWT e Super Admin único. |
| 01 | [Comercial, Vendas & Funis](01_deals.md) | `/#deals` | Rota | Pedidos TOTVS Protheus (`SC5/SC6`), Radar Anti-Churn e múltiplos pipelines. |
| 02 | [Cirurgiões & Base de Contatos](02_contacts.md) | `/#contacts` | Rota | Grafo Clínico KOL, busca por CRO/Especialidade e WhatsApp em 1 clique. |
| 03 | [Segmentos Inteligentes](03_contacts_segments.md) | `/#contacts-segments` | Sub-rota | Filtros dinâmicos por especialidade e sincronização em tempo real com Mautic VPS. |
| 04 | [Inbox Omnichannel WhatsApp](04_inbox.md) | `/#inbox` | Rota | Evolution API v2 + Chatwoot com arquitetura Ports & Adapters e webhooks HMAC. |
| 05 | [Central de Tickets & Suporte](05_tickets.md) | `/#tickets` | Rota | Fluxo Digital CAD/CAM, ingestão de malhas 3D de scanners intraorais e SLA cirúrgico. |
| 06 | [Tarefas Operacionais & Checklist](06_tasks.md) | `/#tasks` | Rota | Gatilhos de receita, SLA de 15min para leads Tier A e visitas preventivas. |
| 07 | [Relatórios Executivos & KPIs](07_reports.md) | `/#reports` | Rota | BI com consolidação hierárquica por subárvore recursiva e monitoramento anti-churn. |
| 08 | [Performance por Consultor](08_reports_performance.md) | `/#reports-performance` | Sub-rota | Ranking de produtividade, metas progressivas e taxa de conversão cirúrgica individual. |
| 09 | [Campanhas de Marketing & CIOSP](09_marketing.md) | `/#marketing` | Rota | Gestão de campanhas digitais e eventos de congressos odontológicos nacionais. |
| 10 | [Sincronização Mautic VPS](10_marketing_mautic.md) | `/#marketing-mautic` | Sub-rota | Painel de monitoramento do Mautic 5 via webhooks em tempo real e telemetria de leads. |
| 11 | [Lead Scoring de Cirurgiões](11_scoring.md) | `/#scoring` | Rota | Transbordo automático de Leads Hot (Tier A) com notificação para o Closer regional. |
| 12 | [Critérios ICP & Prescrição](12_scoring_icp.md) | `/#scoring-icp` | Sub-rota | Matriz de pontuação por volume de implantes/mês, clínica própria e especialidade CRO. |
| 13 | [Fluxos de Automação Cirúrgica](13_automations.md) | `/#automations` | Rota | Gatilhos de receita (`revenue_triggers.py`), faturamento Protheus e fila outbox. |
| 14 | [Organograma & RBAC Setorial](14_hierarchy.md) | `/#hierarchy` | Rota | 4 Presets Odontológicos Plug & Play, resolução de escopo em < 0.2ms via CTE. |
| 15 | [Central de Usuários & Acessos](15_users.md) | `/#users` | Rota | Governança exclusiva do Super Admin Único com paginação determinística. |
| 16 | [Importador Universal de Carteiras](16_import_contacts.md) | `/#import-contacts` | Rota | Deduplicação por chave composta (`cro` + `uf`) e recálculo automático de scoring. |
| 17 | [Central de Conectores Enterprise](17_integrations.md) | `/#integrations` | Rota | Conectores TOTVS Protheus, Evolution API WhatsApp, Mautic e Outbox transacional. |
| 18 | [KeyPartners Consignados & Lotes](18_keypartners.md) | `/#keypartners` | Rota | Custódia hospitalar de caixas cirúrgicas e rastreabilidade unitária de lotes ANVISA. |
| 19 | [KeyPartners KOLs & Custódia](19_keypartners_kols.md) | `/#keypartners-kols` | Sub-rota | Gestão de contratos de consignação, limites de crédito e demanda mensal de KOLs. |
| 20 | [DENTGO Express Despacho 45min](20_dentgo.md) | `/#dentgo` | Rota | Logística express intraoperatória com SLA 45min, lacre térmico no R2 e telemetria. |
| 21 | [DENTGO Rastreabilidade FEFO & PIN](21_dentgo_fefo.md) | `/#dentgo-fefo` | Sub-rota | Bipagem óptica de lotes ANVISA e validação sanitária de entrega por PIN do cirurgião. |
| 22 | [Vídeo SOS Mesa Cirúrgica](22_video_sos.md) | `/#video-sos` | Rota | Suporte crítico em 1 clique via LiveKit WebRTC e discagem VoIP SIP para o campo operatório. |
| 23 | [Tomografias DICOM & STL 3D](23_dicom_viewer.md) | `/#dicom-viewer` | Rota | Visualizador 3D WebGL para tomografias periapicais cone-beam e guias protéticos STL. |
| 24 | [BI Executivo Superset](24_bi_superset.md) | `/#bi-superset` | Rota | Dashboards analíticos Apache Superset 3.1 com Row-Level Security (RLS) governado. |
| 25 | [Governança AIDD & Quarteto](25_governanca_studios_quarteto.md) | `/docs`, `/webhooks`, `/mcp`, `/docs/guia` | Governança | Swagger Studio, Webhook Studio, Servidor Nativo MCP e Guia do Usuário da Lei #10. |
