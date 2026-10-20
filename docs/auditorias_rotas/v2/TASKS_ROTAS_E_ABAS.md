# Tasks — Catálogo Completo de Rotas, Sub-rotas e Abas para Auditoria (v2)

> **Padrão de Execução:** Orquestrador Filarmônico `aidd-route-analyze` (Ciclo v2)
> **Framework:** AIDD Canary v4.0 (Zero Stubs / Zero Emojis / Lei #14)
> **Status:** `17/17` rotas concluídas e homologadas

---

## Matriz Geral de Rastreabilidade v2

| Código | Rota Hashbang | Título Visual | Fatias Backend | Componente React | Status v2 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TASK-ROUTE-01** | `#!/dashboard` | Visão do Dia (Cockpit Executivo) | `deals`, `campaigns`, `intelligence` | `ExecutiveCockpitView.tsx` | `[X] HOMOLOGADO v2` |
| **TASK-ROUTE-02** | `#!/deals` | Negociações & Funil Comercial (CRM Cirúrgico) | `deals`, `pipelines`, `contracts` | `DealsWorkspace.tsx` | `[X] HOMOLOGADO v2` |
| **TASK-ROUTE-03** | `#!/contacts` | Dentistas e Clínicas (CRM Cirúrgico) | `contacts`, `institutions` | `ContactsCrmWorkspace.tsx` | `[X] HOMOLOGADO v2` |
| **TASK-ROUTE-04** | `#!/scoring` | Qualificação de Clientes (ICP Scoring) | `scoring`, `intelligence` | `IcpScoringDashboard.tsx` | `[X] HOMOLOGADO v2` |
| **TASK-ROUTE-05** | `#!/marketing` | Campanhas e Indicações (Growth & Referral) | `campaigns`, `integrations` | `LandingPageBuilder.tsx` | `[X] HOMOLOGADO v2` |
| **TASK-ROUTE-06** | `#!/omnichannel` | Atendimento Clínico WhatsApp (Omnichannel) | `integrations`, `communications` | `OmnichannelWorkspace.tsx` | `[X] HOMOLOGADO v2` |
| **TASK-ROUTE-07** | `#!/keypartners` | Malas em Consignação & KOL (KeyPartners) | `keypartners`, `integrations` | `ConsignmentSurgicalBoard.tsx` | `[X] HOMOLOGADO v2` |
| **TASK-ROUTE-08** | `#!/dentgo` | Entregas Expressas Same-Day (DENTGO) | `dentgo`, `inventory` | `DentgoExpressCockpit.tsx` | `[X] HOMOLOGADO v2` |
| **TASK-ROUTE-09** | `#!/video_sos` | Chamadas e Vídeo SOS Mesa Cirúrgica (LiveKit) | `communications`, `intelligence` | `LiveKitDealRoomModal.tsx` | `[X] HOMOLOGADO v2` |
| **TASK-ROUTE-10** | `#!/contracts` | Propostas e Contratos (Documenso & ANVISA) | `contracts`, `integrations` | `ContractsDocumensoWorkspace.tsx` | `[X] HOMOLOGADO v2` |
| **TASK-ROUTE-11** | `#!/imaging` | Exames 3D e Tomografias (DICOM / STL Viewer) | `imaging`, `contracts` | `DicomStl3DViewer.tsx` | `[X] HOMOLOGADO v2` |
| **TASK-ROUTE-12** | `#!/support` | Suporte Clínico, RMA & Tecnovigilância ANVISA | `support`, `integrations` | `SupportAnvisaWorkspace.tsx` | `[X] HOMOLOGADO v2` |
| **TASK-ROUTE-13** | `#!/intelligence` | Assistente Comercial & RAG Clínico | `intelligence`, `search` | `IntelligenceSuiteWorkspace.tsx` | `[X] HOMOLOGADO v2` |
| **TASK-ROUTE-14** | `#!/analytics` | Relatórios BI Superset & Text-to-SQL AST | `analytics`, `bi` | `SupersetEmbeddedDashboard.tsx` | `[X] HOMOLOGADO v2` |
| **TASK-ROUTE-15** | `#!/scheduling` | Reativação de Pacientes (Cal.com) | `scheduling`, `integrations` | `CalcomReactivationWorkspace.tsx` | `[X] HOMOLOGADO v2` |
| **TASK-ROUTE-16** | `#!/rbac` | Equipes, Metas & Comissionamento (RBAC) | `rbac`, `hierarchy` | `RbacHierarchyTree.tsx` | `[X] HOMOLOGADO v2` |
| **TASK-ROUTE-17** | `#!/settings` | Configurações, Vault & Conexão TOTVS ERP | `settings`, `integrations`, `integrations` | `CredentialsVaultPage.tsx` | `[X] HOMOLOGADO v2` |

---

## 1. Suíte Comercial & Relacionamento (CRM)

- [X] **TASK-ROUTE-01: Rota `#!/dashboard` (Visão do Dia (Cockpit Executivo))**
  - [X] Aba / Sub-módulo: `stage` (Funil de Receita Comercial por Estágio)
  - [X] Aba / Sub-módulo: `trend` (Série Temporal de MRR e Tendência)
  - [X] Aba / Sub-módulo: `consignment` (Giro de Maletas e Faturamento CFOP 5.113)
  - [X] Aba / Sub-módulo: `churn_radar` (Radar Anti-Churn RFM Preditivo)
  - [X] Aba / Sub-módulo: `kol_graph` (Ecossistema Clínico e Topologia KOL)

- [X] **TASK-ROUTE-02: Rota `#!/deals` (Negociações & Funil Comercial (CRM Cirúrgico))**
  - [X] Aba / Sub-módulo: `kanban` (Quadro Kanban Interativo Drag-and-Drop)
  - [X] Aba / Sub-módulo: `table` (Visão Tabela Densa e Paginada)
  - [X] Aba / Sub-módulo: `stage_qualificacao` (Estágio: Qualificação Técnica)
  - [X] Aba / Sub-módulo: `stage_diagnostico_3d` (Estágio: Diagnóstico 3D Tomográfico)
  - [X] Aba / Sub-módulo: `stage_proposta` (Estágio: Proposta Comercial)
  - [X] Aba / Sub-módulo: `stage_contrato` (Estágio: Minuta e Assinatura de Contrato)
  - [X] Aba / Sub-módulo: `stage_fechado_ganho` (Estágio: Negócio Fechado Ganho (MRR))

- [X] **TASK-ROUTE-03: Rota `#!/contacts` (Dentistas e Clínicas (CRM Cirúrgico))**
  - [X] Aba / Sub-módulo: `crm_surgeons` (Cirurgiões Dentistas Cadastrados)
  - [X] Aba / Sub-módulo: `institutions` (Clínicas, Hospitais e Polos)
  - [X] Aba / Sub-módulo: `cfo_compliance` (Validação de Registro CFO / CRO Ativo)
  - [X] Aba / Sub-módulo: `icp_scoring` (Qualificação e Enriquecimento ICP)

- [X] **TASK-ROUTE-04: Rota `#!/scoring` (Qualificação de Clientes (ICP Scoring))**
  - [X] Aba / Sub-módulo: `overview` (Score Geral da Carteira)
  - [X] Aba / Sub-módulo: `matrix` (Matriz ICP Odontológico)
  - [X] Aba / Sub-módulo: `rules` (Critérios e Pesos de Enquadramento)

- [X] **TASK-ROUTE-05: Rota `#!/marketing` (Campanhas e Indicações (Growth & Referral))**
  - [X] Aba / Sub-módulo: `analytics` (Métricas de Mídia & ROAS)
  - [X] Aba / Sub-módulo: `pages` (Gestor de Landing Pages Publicadas)
  - [X] Aba / Sub-módulo: `builder` (Editor Visual Drag & Drop GrapesJS)
  - [X] Aba / Sub-módulo: `referral_mgm` (Loop de Indicação Membro-Gera-Membro)

- [X] **TASK-ROUTE-06: Rota `#!/omnichannel` (Atendimento Clínico WhatsApp (Omnichannel))**
  - [X] Aba / Sub-módulo: `inbox` (Fila de Conversas Inbox (Chatwoot))
  - [X] Aba / Sub-módulo: `chat` (Chat em Tempo Real e Envio de Mídia)
  - [X] Aba / Sub-módulo: `context` (Barra Lateral de Contexto do Cirurgião)
  - [X] Aba / Sub-módulo: `sos_call` (Disparador de Chamada SOS Mesa Cirúrgica)

---

## 2. Suíte Cirúrgica, Logística & Regulamentar

- [X] **TASK-ROUTE-07: Rota `#!/keypartners` (Malas em Consignação & KOL (KeyPartners))**
  - [X] Aba / Sub-módulo: `kits` (Inventário de Maletas & Rastreabilidade ANVISA)
  - [X] Aba / Sub-módulo: `agreements` (Termos de Consignação & Notas CFOP 5.113)
  - [X] Aba / Sub-módulo: `kol` (Contratos de Parceria KOL & Speakers)
  - [X] Aba / Sub-módulo: `loyalty` (Programa de Fidelidade e Pontos de Consumo)

- [X] **TASK-ROUTE-08: Rota `#!/dentgo` (Entregas Expressas Same-Day (DENTGO))**
  - [X] Aba / Sub-módulo: `cockpit` (Cockpit Same-Day 45min & Status de Hubs)
  - [X] Aba / Sub-módulo: `radar` (Mapa de Rota & Rastreamento em Tempo Real)
  - [X] Aba / Sub-módulo: `fefo_deals` (Ofertas Flash FEFO (Vencimento Próximo))
  - [X] Aba / Sub-módulo: `split` (Split Financeiro e Taxa do Entregador)

- [X] **TASK-ROUTE-09: Rota `#!/video_sos` (Chamadas e Vídeo SOS Mesa Cirúrgica (LiveKit))**
  - [X] Aba / Sub-módulo: `video` (Videoconferência WebRTC LiveKit em Tempo Real)
  - [X] Aba / Sub-módulo: `voip` (Telefonia SIP Direta com Especialista)
  - [X] Aba / Sub-módulo: `recording` (Histórico de Gravações & Transcrições Whisper)

- [X] **TASK-ROUTE-10: Rota `#!/contracts` (Propostas e Contratos (Documenso & ANVISA))**
  - [X] Aba / Sub-módulo: `documenso_list` (Contratos e Assinaturas Eletrônicas)
  - [X] Aba / Sub-módulo: `anvisa_catalog` (Catálogo Regulatório ANVISA e Lotes)
  - [X] Aba / Sub-módulo: `r2_custody` (Custódia Segura no Cloudflare R2)

- [X] **TASK-ROUTE-11: Rota `#!/imaging` (Exames 3D e Tomografias (DICOM / STL Viewer))**
  - [X] Aba / Sub-módulo: `dicom_cone_beam` (Tomografia Computadorizada Cone Beam)
  - [X] Aba / Sub-módulo: `stl_3d` (Malhas STL 3D de Guias Cirúrgicos)
  - [X] Aba / Sub-módulo: `mpr_slices` (Cortes Multiplanares (Axial, Sagital, Coronal))

- [X] **TASK-ROUTE-12: Rota `#!/support` (Suporte Clínico, RMA & Tecnovigilância ANVISA)**
  - [X] Aba / Sub-módulo: `anvisa_rma` (Quarentena & Laudos de Tecnovigilância ANVISA)
  - [X] Aba / Sub-módulo: `surgical_sos` (Chamados de Emergência SOS Cirurgia)
  - [X] Aba / Sub-módulo: `postop_b2c` (Acompanhamento Pós-Operatório do Paciente)

---

## 3. Suíte de Inteligência, Governança & Configurações

- [X] **TASK-ROUTE-13: Rota `#!/intelligence` (Assistente Comercial & RAG Clínico)**
  - [X] Aba / Sub-módulo: `churn` (Radar Preditivo de Evasão RFM)
  - [X] Aba / Sub-módulo: `kol_graph` (Topologia do Ecossistema Clínico e KOL)
  - [X] Aba / Sub-módulo: `rag_chat` (Assistente RAG com Catálogo Técnico Cirúrgico)

- [X] **TASK-ROUTE-14: Rota `#!/analytics` (Relatórios BI Superset & Text-to-SQL AST)**
  - [X] Aba / Sub-módulo: `rls_studio` (Estúdio BI com Apache Superset Embedded RLS)
  - [X] Aba / Sub-módulo: `text_to_sql` (Console Analítico Text-to-SQL com Proteção AST)

- [X] **TASK-ROUTE-15: Rota `#!/scheduling` (Reativação de Pacientes (Cal.com))**
  - [X] Aba / Sub-módulo: `campaigns` (Campanhas de Reativação Cal.com)
  - [X] Aba / Sub-módulo: `appointments` (Agenda de Consultas Confirmadas)
  - [X] Aba / Sub-módulo: `templates` (Modelos de Mensagens WhatsApp / SMS)

- [X] **TASK-ROUTE-16: Rota `#!/rbac` (Equipes, Metas & Comissionamento (RBAC))**
  - [X] Aba / Sub-módulo: `tree` (Árvore Hierárquica Nacional / Regional / Consultor)
  - [X] Aba / Sub-módulo: `permissions` (Matriz de Permissões Granulares por Papel)
  - [X] Aba / Sub-módulo: `targets` (Gestor de Metas Comerciais por Equipe)
  - [X] Aba / Sub-módulo: `commissions` (Regras e Cálculos de Comissionamento)

- [X] **TASK-ROUTE-17: Rota `#!/settings` (Configurações, Vault & Conexão TOTVS ERP)**
  - [X] Aba / Sub-módulo: `vault` (Cofre Seguro de Chaves de API e Segredos)
  - [X] Aba / Sub-módulo: `erp` (Conexão TOTVS Protheus & Sincronização de Notas)
  - [X] Aba / Sub-módulo: `webhooks` (Webhooks Studio & Assinaturas HMAC)
  - [X] Aba / Sub-módulo: `users` (Gestão de Usuários e Perfis de Acesso)
