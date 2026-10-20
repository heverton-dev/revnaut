# Dossiê Executivo de Engenharia Reversa Profunda & Reconstrução Factual — RevNault

> **Alvo:** RevNault CRM (`https://app.revnault.com`)  
> **Tenant Mapeado:** Sales Rocket (`0f14ffff`)  
> **Operador:** Thiago Hortolan (`thiago@salesrocketbrasil.com.br`)  
> **Data:** 15 de Outubro de 2026  
> **Governança:** AIDD Standard (Leis #1, #2, #5, #6, #8, #10, #11 e #13)

---

## 1. Descoberta Arquitetural Factual (O "Motor Oculto")

A engenharia reversa profunda nos arquivos JavaScript do runtime (`window.Mautic`) revelou a verdadeira arquitetura da RevNault:
1. **Core de Automação & Marketing:** A RevNault é construída sobre um fork do **Mautic** (motor Open Source líder de automação).
2. **Camada de CRM:** Plugins proprietários sobre o Mautic (`DealsBundle`, `TicketsBundle`, `TasksBundle`).
3. **Camada de Mensageria:** Central de atendimento omnichannel integrada a provedores de WhatsApp (`spread_operator_id`, Baileys e Meta Cloud API).

Essa descoberta factual viabilizou a substituição de 100% dos módulos por **motores Open Source de elite (Mautic 5.x + Chatwoot + Evolution API + Twenty CRM)**, sem qualquer necessidade de reinventar a roda do zero.

---

## 2. Inventário Completo de Módulos & Telas Mapeadas (Mais de 30 Telas)

### A. Módulos Centrais (Pasta `01_evidence/screens/`)
* `00_login.png`: Tela de autenticação global.
* `01_mfa_setup.png`: Configuração de 2FA e opções de WhatsApp / Email / TOTP.
* `02_accounts.png`: Seleção de Tenant (Multi-Tenancy `0f14ffff`).
* `03_contacts.png`: Tabela de Contatos & Leads com filtros rápidos.
* `04_deals_list.png`: Listagem tabular de negócios.
* `05_deals_kanban.png`: Funil Kanban com Drag & Drop e totalizadores.
* `06_inbox.png`: Caixa de entrada multi-canal.
* `07_dashboards.png`: Painéis e gráficos de receita consolidada.
* `08_tickets.png`: Central de tickets e atendimento de suporte.
* `09_tasks.png`: Gestão de tarefas e follow-ups de vendedores.
* `10_campaigns.png`: Listagem de fluxos de automação.
* `11_settings_users.png`: Gestão de usuários e permissões RBAC de 28 objetos.
* `12_mobile_deals.png` e `13_mobile_contacts.png`: Versões mobile responsivas (393x852).

### B. Módulos Avançados, Construtores & Modais (Pasta `06_profundidade_total/screens_full/`)
* `01_modal_criar_contato.png`: Formulário completo de cadastro de leads.
* `02_campaigns_list.png`: Painel geral de campanhas ativas.
* `03_campaign_builder.png`: Configurações de fluxo (Baseado em contatos vs. Negócios).
* `04_campaign_canvas_open.png` e `05_campaign_canvas_active.png`: **O Canvas Gráfico de Automação**.
* `06_campaign_trigger_selected.png`: Gatilhos de inscrição por segmento/formulário.
* `07_whatsapp_templates.png`: Gestor de templates de WhatsApp (HSM).
* `08_operators_list.png`: Gestão de filas e operadores de chat.
* `09_companies.png`: Cadastro e visão 360º de empresas.
* `10_products.png`: Catálogo de produtos, SKU e tabelas de preço.
* `11_forms.png`: Construtor de formulários embutíveis.
* `12_landing_pages.png`: Construtor de páginas de alta conversão.
* `13_emails.png`: Templates de e-mail marketing drag-and-drop.
* `14_segments.png`: Construtor de filtros booleanos de base de contatos.
* `15_points_lead_scoring.png` e `16_points_triggers.png`: Sistema de pontuação e gatilhos de pontuação.
* `17_assets.png`: Gestor de downloads de arquivos rastreáveis.
* `18_snippets.png`: Macros de respostas rápidas para atendimento.
* `19_analysis_chats.png`: Métricas e relatórios de tempo de resposta do chat.

---

## 3. Schemas Fatuais Extraídos em Extrema Profundidade

1. **Schema de Contato & Rastreamento (50+ Campos):**
   * Documentado em [contact_lead_schema.json](file:///c:/Users/trcnologia/Desktop/_inbox/proj_revops/docs/reconstruct_revnault/06_profundidade_total/forms_schemas/contact_lead_schema.json).
   * Cobertura: Dados Pessoais, Endereço, UTMs de Primeiro Toque, UTMs de Último Toque, Ad IDs, Facebook Click ID (`fbclid`), Google Click ID (`gclid`), Click-to-WhatsApp ID (`ctwa_clid`), Meta Lead ID e Lead Scoring.
2. **Motor de Automação (Campaign Builder DAG):**
   * Documentado em [campaign_builder_spec.md](file:///c:/Users/trcnologia/Desktop/_inbox/proj_revops/docs/reconstruct_revnault/06_profundidade_total/campaign_builder_spec.md).
   * 18 Ações: Disparo WhatsApp, E-mail, Alerta interno, Mudança de estágio de negócio, CAPI Meta, Webhook, Pausas e Roleta de Vendedores.
   * 7 Condições: Propriedades, tags, segmentos, validação de e-mail e teste A/B.
   * 8 Decisões Comportamentais: Leitura de WhatsApp, Resposta WhatsApp, Abertura de e-mail, Clique em link, Visita de página, Envio de form.

---

## 4. Arquitetura de Produção com Motores Open Source

* Documentada em [open_source_architecture.md](file:///c:/Users/trcnologia/Desktop/_inbox/proj_revops/docs/reconstruct_revnault/06_profundidade_total/open_source_architecture.md).
* **Mautic 5.x** para Automações, Formulários, Segmentos e Scoring.
* **Evolution API + Chatwoot** para WhatsApp Oficial e Chat Omnichannel.
* **FastAPI + SQLite WAL** para o motor central de CRM, Pipelines e o **Quarteto Sine Qua Non Dinâmico**:
  * Swagger Studio: `http://localhost:8000/docs`
  * Webhook Studio: `http://localhost:8000/webhooks`
  * MCP Studio: `http://localhost:8000/mcp`
  * Guia do Usuário: `http://localhost:8000/docs/guia`

---

## 5. Homologação & Quality Gates

* **Zero Stubs / Zero Mocks (Lei #5):** Suíte automatizada com 11 testes reais em [test_backend.py](file:///c:/Users/trcnologia/Desktop/_inbox/proj_revops/tests/test_backend.py).
* **Quality Gate `G_TESTES_REAIS.py`:** Aprovado (Exit 0).
* **Quality Gate `G_aidd_forge.py`:** Aprovado (Exit 0).
