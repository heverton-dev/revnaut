# Manuais Operacionais e Catálogo de Rotas • Revnaut Dental

Este diretório contém a documentação exaustiva e padronizada de todas as telas, rotas e subrotas da plataforma Revnaut Dental (Revenue Operations e CRM B2B Odontológico).

## Estrutura dos Manuais
Cada manual segue rigorosamente a estrutura canônica de governança:
1. Objetivo da Rota / Subrota
2. O que o Usuário Consegue Realizar
3. Matriz de Visualização e Permissões (RBAC / Escopos)
4. Ações Disponíveis
5. Passo a Passo Operacional (Como o Usuário Opera)
6. O Que Falta Implementar (Gaps Técnicos & Roadmap)

---

## Catálogo Geral de Módulos e Rotas

| Código | Módulo / Rota | Identificador / Hash | Público-Alvo Principal |
|---|---|---|---|
| 00 | [Autenticação & Login](00_autenticacao_login.md) | `/#login` | Todos os Usuários / Super Admin |
| 01 | [Comercial, Vendas & Funis](01_comercial_vendas_funis.md) | `/#deals` | Consultores, Gerentes e Diretores |
| 02 | [Cirurgiões & Base de Contatos](02_cirurgioes_contatos.md) | `/#contacts`, `/#contacts-segments` | Força de Vendas e SDRs |
| 05 | [Importador Universal de Carteiras](05_importador_carteiras_clientes.md) | `/#import-contacts` | Super Admin e Operações Comerciais |
| 06 | [Inbox de Mensagens WhatsApp](06_comunicacao_inbox_whatsapp.md) | `/#inbox` | Atendimento, SDRs e Consultores |
| 07 | [Central de Tickets & Suporte](07_tickets_suporte_cirurgico.md) | `/#tickets` | SAC Cirúrgico e Pós-Venda |
| 08 | [Tarefas Operacionais & Checklist](08_tarefas_operacionais.md) | `/#tasks` | Consultores e Gerentes de Contas |
| 09 | [Relatórios Executivos & KPIs](09_relatorios_kpis_performance.md) | `/#reports`, `/#reports-performance` | C-Level, Diretores e Gerentes |
| 10 | [Marketing & Campanhas Mautic](10_marketing_campanhas_mautic.md) | `/#marketing`, `/#marketing-mautic` | Marketing e Inteligência de Mercado |
| 11 | [Lead Scoring & ICP Odontológico](11_lead_scoring_icp_odontologico.md) | `/#scoring`, `/#scoring-icp` | RevOps e Inteligência Comercial |
| 12 | [Fluxos de Automação Cirúrgica](12_fluxos_automacao_cirurgica.md) | `/#automations` | RevOps e Gestores de Processos |
| 13 | [Organograma, RBAC, Metas & Comissões](13_organograma_rbac_metas_comissoes.md) | `/#hierarchy` | Super Admin, RH e Diretoria |
| 14 | [Central de Gestão de Usuários](14_gestao_usuarios_credenciais.md) | `/#users` | Super Admin Único (Heverton) |
| 15 | [Governança AIDD & Quarteto Sine Qua Non](15_governanca_studios_quarteto.md) | `/docs`, `/webhooks`, `/mcp`, `/docs/guia` | Desenvolvedores, IAs e Arquitetos |
