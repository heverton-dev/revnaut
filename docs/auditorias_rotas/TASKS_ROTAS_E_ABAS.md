# Tasks — Catálogo Completo de Rotas, Sub-rotas e Abas para Auditoria

> **Padrão de Execução:** Orquestrador Filarmônico `aidd-route-analyze`  
> **Status:** `[X]` Concluído | `[ ]` Pendente

---

## 1. Suíte Comercial & Relacionamento (CRM)

- [X] **TASK-ROUTE-01: Rota `#!/dashboard` (Visão do Dia)**
  - [X] Sub-aba / Pílula: `Estágio` (Funil de Receita Comercial)
  - [X] Sub-aba / Pílula: `Tendência` (Série Temporal de MRR)
  - [X] Sub-aba / Pílula: `Consignação` (Giro de Maletas e CFOP 5.113)
  - [X] Painel: `Radar Anti-Churn RFM` (Preditivo de Cirurgiões)
  - [X] Painel: `Ecossistema Clínico KOL` (Grafo de Vínculos)

- [X] **TASK-ROUTE-02: Rota `#!/deals` (Negociações & Funil)**
  - [X] Sub-rota / Modo: `Quadro Kanban`
  - [X] Sub-rota / Modo: `Visão Tabela / Lista`
  - [X] Sub-aba: Estágio `Qualificação`
  - [X] Sub-aba: Estágio `Diagnóstico 3D`
  - [X] Sub-aba: Estágio `Proposta Comercial`
  - [X] Sub-aba: Estágio `Contrato`
  - [X] Sub-aba: Estágio `Fechado Ganho`
  - [X] Gaveta Lateral: `Linha do Tempo de Auditoria`
  - [X] Gaveta Lateral: `Contratos Documenso Vinculados`
  - [X] Gaveta Lateral: `Copilot Comercial Granola`

- [X] **TASK-ROUTE-03: Rota `#!/contacts` (Dentistas e Clínicas)**
  - [X] Aba 1: `crm_surgeons` (Cirurgiões Dentistas)
  - [X] Aba 2: `institutions` (Clínicas e Polos Credenciados)
  - [X] Aba 3: `cfo_compliance` (Validação CFO / CRO Ativo)
  - [X] Aba 4: `icp_scoring` (Enriquecimento e Qualificação ICP)

- [X] **TASK-ROUTE-04: Rota `#!/scoring` (Qualificação de Clientes)**
  - [X] Aba 1: `Score Geral da Carteira`
  - [X] Aba 2: `Matriz ICP Odontológico`
  - [X] Aba 3: `Critérios e Pesos de Enquadramento`

- [X] **TASK-ROUTE-05: Rota `#!/marketing` (Campanhas e Indicações)**
  - [X] Aba 1: `analytics` (Métricas de Mídia & ROAS)
  - [X] Aba 2: `pages` (Gestor de Landing Pages Publicadas)
  - [X] Aba 3: `builder` (Editor Visual GrapesJS Drag & Drop)
  - [X] Aba 4: `referral_mgm` (Loop de Indicação Membro-Gera-Membro)

- [X] **TASK-ROUTE-06: Rota `#!/omnichannel` (Atendimento WhatsApp)**
  - [X] Sub-painel: `Fila de Conversas Inbox (Chatwoot)`
  - [X] Sub-painel: `Chat em Tempo Real & Envio de Mídia`
  - [X] Sub-painel: `Barra Lateral de Contexto do Cirurgião`
  - [X] Ação Rápida: `Botão SOS Mesa Cirúrgica`

---

## 2. Suíte Cirúrgica, Logística & Regulamentar

- [X] **TASK-ROUTE-07: Rota `#!/keypartners` (Malas em Consignação)**
  - [X] Aba 1: `kits` (Inventário de Maletas & Rastreabilidade ANVISA)
  - [X] Aba 2: `agreements` (Termos de Consignação & Notas CFOP 5.113)
  - [X] Aba 3: `kol` (Contratos de Parceria KOL & Speakers Clínicos)
  - [X] Aba 4: `loyalty` (Programa de Fidelidade e Pontos de Consumo)

- [X] **TASK-ROUTE-08: Rota `#!/dentgo` (Entregas Expressas)**
  - [X] Aba 1: `cockpit` (Cockpit Same-Day 45min & Status de Hubs)
  - [X] Aba 2: `radar` (Mapa de Rota & Rastreamento em Tempo Real)
  - [X] Aba 3: `fefo_deals` (Ofertas Flash FEFO - Vencimento Próximo)
  - [X] Aba 4: `split` (Split Financeiro de Custódia e Taxa do Entregador)

- [X] **TASK-ROUTE-09: Rota `#!/video_sos` (Chamadas e Vídeo SOS)**
  - [X] Aba 1: `video` (Videoconferência WebRTC LiveKit em Tempo Real)
  - [X] Aba 2: `voip` (Telefonia SIP Direta com Consultor Técnico)
  - [X] Aba 3: `recording` (Histórico de Gravações & Transcrições Faster-Whisper)

- [X] **TASK-ROUTE-10: Rota `#!/contracts` (Propostas e Contratos)**
  - [X] Aba 1: `documenso_list` (Contratos & Assinaturas Documenso)
  - [X] Aba 2: `anvisa_catalog` (Catálogo Regulatório ANVISA & Lotes)
  - [X] Aba 3: `r2_custody` (Custódia de Documentos no Cloudflare R2)

- [X] **TASK-ROUTE-11: Rota `#!/imaging` (Exames 3D e Tomografias)**
  - [X] Sub-módulo: `Visualizador DICOM (Tomografias Cone Beam)`
  - [X] Sub-módulo: `Malhas STL 3D (Próteses CAD/CAM)`
  - [X] Sub-módulo: `Planos de Corte Multiplanar (MPR)`

- [X] **TASK-ROUTE-12: Rota `#!/support` (Suporte Clínico e Garantias)**
  - [X] Aba 1: `anvisa_rma` (Quarentena & Laudos de Tecnovigilância ANVISA)
  - [X] Aba 2: `surgical_sos` (Chamados de Emergência SOS Cirurgia)
  - [X] Aba 3: `postop_b2c` (Acompanhamento Pós-Operatório do Paciente)

---

## 3. Suíte de Inteligência, Governança & Configurações

- [X] **TASK-ROUTE-13: Rota `#!/intelligence` (Assistente Comercial)**
  - [X] Aba 1: `churn` (Radar Preditivo de Evasão RFM)
  - [X] Aba 2: `kol_graph` (Topologia do Ecossistema Clínico)
  - [X] Aba 3: `rag_chat` (Assistente RAG com Catálogo Técnico Cirúrgico)

- [X] **TASK-ROUTE-14: Rota `#!/analytics` (Relatórios e Metas)**
  - [X] Aba 1: `rls_studio` (Estúdio BI com Apache Superset Embedded RLS)
  - [X] Aba 2: `text_to_sql` (Console Analítico Text-to-SQL com Proteção AST)

- [X] **TASK-ROUTE-15: Rota `#!/scheduling` (Retorno de Pacientes)**
  - [X] Aba 1: `campaigns` (Campanhas de Reativação Cal.com)
  - [X] Aba 2: `appointments` (Agenda de Consultas Confirmadas)
  - [X] Aba 3: `templates` (Modelos de Mensagens WhatsApp / SMS)

- [X] **TASK-ROUTE-16: Rota `#!/rbac` (Equipes e Acessos)**
  - [X] Aba 1: `tree` (Árvore Hierárquica Nacional / Regional / Consultor)
  - [X] Aba 2: `permissions` (Matriz de Permissões Granulares)
  - [X] Aba 3: `targets` (Gestor de Metas Comerciais por Equipe)
  - [X] Aba 4: `commissions` (Regras de Cálculo de Comissionamento)

- [X] **TASK-ROUTE-17: Rota `#!/settings` (Configurações e Notas Fiscais)**
  - [X] Aba 1: `vault` (Cofre Seguro de Chaves de API e Segredos)
  - [X] Aba 2: `erp` (Conexão TOTVS Protheus & Sincronização de Notas)
  - [X] Aba 3: `webhooks` (Webhooks Studio & Assinaturas HMAC)
  - [X] Aba 4: `users` (Gestão de Usuários e Perfis)