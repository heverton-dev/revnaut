# Manuais Operacionais e Catálogo de Rotas • Revnaut Dental

Este diretório contém a documentação canônica, padronizada e sincronizada de todas as telas, rotas e módulos operacionais da plataforma **Revnaut Dental Ops** (Revenue Operations e CRM B2B Industrial Odontológico), alinhada ao [Plano de Ação Argon (Caminho A + Caminho B)](file:///c:/Users/trcnologia/Desktop/_inbox/proj_revops/docs/plano-acao-revnault-argon.md).

## Estrutura Padronizada dos Manuais
Cada manual segue a estrutura canônica de governança (Lei #12 — *Anti-Docs Rot*):
1. **Objetivo da Rota / Subrota** (Propósito de negócio no nicho odontológico).
2. **O Que o Usuário Consegue Realizar** (Funcionalidades ativas, integrações ERP e motores de IA).
3. **Matriz de Visualização e Permissões (RBAC / Escopos)** (Controle de acesso por cargo e subárvore de times).
4. **Quais Ações Podem Ser Realizadas** (Eventos e despachos de API).
5. **Passo a Passo Operacional** (Guia prático de uso pelo colaborador).
6. **O Que Falta Implementar (Roadmap & Gaps)** (Itens planejados para próximas iterações).
7. **Anotações do Heverton** (Decisões arquiteturais e invariantes do Super Admin).

---

## Catálogo Geral de Módulos e Rotas Atualizadas

| Código | Módulo / Rota | Identificador / Hash | Destaques da Arquitetura & Implementação |
|---|---|---|---|
| 00 | [Autenticação & Login](00_autenticacao_login.md) | `/#login` | Cliente modular `api-client.js`, Bearer JWT e Super Admin único (`hevertoneduardoperes@gmail.com`). |
| 01 | [Comercial, Vendas & Funis](01_comercial_vendas_funis.md) | `/#deals` | Integração automática com pedidos TOTVS Protheus (`SC5/SC6`), Radar Anti-Churn RFM e múltiplos pipelines setoriais. |
| 02 | [Cirurgiões & Base de Contatos](02_cirurgioes_contatos.md) | `/#contacts`, `/#contacts-segments` | Grafo Clínico KOL (`contact_institutions`), busca instantânea por CRO/Especialidade e contato via WhatsApp em 1 clique. |
| 05 | [Importador Universal de Carteiras](05_importador_carteiras_clientes.md) | `/#import-contacts` | Deduplicação por chave composta (`cro` + `uf`), distribuição territorial e recálculo automático de scoring ICP. |
| 06 | [Inbox de Mensagens WhatsApp](06_comunicacao_inbox_whatsapp.md) | `/#inbox` | Gateway Omnichannel Evolution API v2 + Chatwoot com arquitetura Ports & Adapters e webhooks HMAC. |
| 07 | [Central de Tickets & Suporte](07_tickets_suporte_cirurgico.md) | `/#tickets` | Módulo Fluxo Digital CAD/CAM, ingestão de malhas 3D de scanners intraorais (`.STL`/`.PLY`) e SLA de fabricação. |
| 08 | [Tarefas Operacionais & Checklist](08_tarefas_operacionais.md) | `/#tasks` | Tarefas automáticas geradas por gatilhos de receita (SLA 15min para Leads Tier A e visitas preventivas anti-churn). |
| 09 | [Relatórios Executivos & KPIs](09_relatorios_kpis_performance.md) | `/#reports`, `/#reports-performance` | BI com consolidação hierárquica por subárvore (`WITH RECURSIVE`) e monitoramento de MRR sob risco de churn. |
| 10 | [Marketing & Campanhas Mautic](10_marketing_campanhas_mautic.md) | `/#marketing`, `/#marketing-mautic` | Integração Mautic 5 via webhooks em tempo real e incremento dinâmico de pontuação por engajamento digital. |
| 11 | [Lead Scoring & ICP Odontológico](11_lead_scoring_icp_odontologico.md) | `/#scoring`, `/#scoring-icp` | Motor de Transbordo Automático de Leads Hot (Tier A) com notificação para o Closer regional da UF. |
| 12 | [Fluxos de Automação Cirúrgica](12_fluxos_automacao_cirurgica.md) | `/#automations` | Gatilhos de receita (`revenue_triggers.py`), faturamento no Protheus e fila de saída resiliente no SQLite WAL. |
| 13 | [Organograma, RBAC, Metas & Comissões](13_organograma_rbac_metas_comissoes.md) | `/#hierarchy` | 4 Presets Odontológicos Plug & Play, resolução de escopo em < 0.2ms via CTE recursiva e cálculo de override. |
| 14 | [Central de Gestão de Usuários](14_gestao_usuarios_credenciais.md) | `/#users` | Governança exclusiva do Super Admin Único com paginação determinística e vínculo hierárquico obrigatório de equipe. |
| 15 | [Governança AIDD & Quarteto Sine Qua Non](15_governanca_studios_quarteto.md) | `/docs`, `/webhooks`, `/mcp`, `/docs/guia` | Swagger Studio, Webhook Studio, MCP Studio, Guia Vivo e sincronizador tipado de contratos (`api_contracts.ts`). |
