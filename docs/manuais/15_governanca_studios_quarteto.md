# Manual da Rota: Governança AIDD & Quarteto Sine Qua Non (`/docs`, `/webhooks`, `/mcp`, `/docs/guia`)

## 1. Objetivo das Rotas
Cumprir a Lei Canônica #10 de Governança AIDD, que exige que toda aplicação em produção exponha de forma dinâmica, viva e sem stubs os 4 pilares essenciais para operação por humanos, sistemas legados e agentes de Inteligência Artificial autônomos, com sincronização contínua de contratos tipados (`api_contracts.ts`).

---

## 2. O Que o Usuário Consegue Realizar
* **Pilar I: Swagger Studio (`/docs`):**
  * Explorar e testar todas as rotas e contratos da API OpenAPI 3.1 com schemas Pydantic tipados e autenticação interativa Bearer Token.
* **Pilar II: Webhook Studio (`/webhooks`):**
  * Auditar payloads de eventos comerciais, disparar requisições de teste em tempo real e inspecionar assinaturas HMAC-SHA256 para Evolution API, Chatwoot e Mautic.
* **Pilar III: MCP Studio (`/mcp`):**
  * Interface e discovery de endpoints para Model Context Protocol (MCP), permitindo que agentes LLM e ferramentas operem o CRM de forma controlada.
* **Pilar IV: Guia do Usuário (`/docs/guia`):**
  * Catálogo operacional vivo e navegável da plataforma acessível a toda a equipe comercial e diretoria.
* **Central de Conectores & Integrações (`integrations`):**
  * Painel visual para monitoramento dos conectores TOTVS Protheus (tabelas SA1, SC5, SC6), WhatsApp Evolution API, Mautic VPS e Meta CAPI, com auditoria em tempo real da fila Outbox.
* **Sincronizador Tipado de Contratos (`api_contracts.ts`):**
  * Sincronização automática entre os schemas FastAPI/Pydantic e os contratos TypeScript do Frontend, auditados pelo teste de regressão `test_api_contracts_sync.py`.

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Ferramenta | Rota | Público | Permissão Necessária |
|---|---|---|---|
| Swagger Studio | `/docs` | Desenvolvedores e Integradores | Pública para consulta; requer token Bearer para execução de rotas protegidas |
| Webhook Studio | `/webhooks` | Equipe de TI e Engenharia | Autenticação de Operações |
| MCP Studio | `/mcp` | Agentes de IA e Automação | Token de API de Sistema |
| Guia do Usuário | `/docs/guia` | Colaboradores Comerciais | Aberto para leitura corporativa |
| Central de Conectores | `integrations` | Gestores e Administradores | Visualização e Operação de Integrações |

---

## 4. Quais Ações Podem Ser Realizadas
* `API_TESTING`: Disparar requisições diretamente pela interface interativa do Swagger.
* `WEBHOOK_SIMULATION`: Enviar webhooks de teste com payload de simulação de venda para URLs configuradas.
* `MCP_TOOL_DISCOVERY`: Listagem dinâmica de ferramentas e schemas para modelos de linguagem.
* `VERIFY_CONTRACTS`: Validação de 100% dos response models Pydantic via Quality Gate `G_CONTRACTS`.
* `INTEGRATION_MANAGEMENT`: Testar conectores ERP TOTVS Protheus, auditar sessão WhatsApp e inspecionar a fila transacional Outbox.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)
1. No menu lateral, role até o bloco **Governança AIDD** ou clique em **Central de Integrações**.
2. Clique no link desejado (ex: "Swagger Studio" ou "Central de Integrações").
3. As ferramentas de estúdio serão abertas em nova aba; a Central de Integrações carrega os cards dos conectores e a tabela da fila Outbox diretamente na aplicação.
4. Para testar a comunicação com o ERP, clique em "Testar Ping ERP" ou "Sincronizar Cliente SA1 (TOTVS)".
5. Para autenticar no Swagger, clique em "Authorize" e informe o token Bearer gerado na tela de login.

---

## 6. O Que Falta Implementar (Roadmap & Gaps)
* Simulador visual interativo de webhook payloads diretamente no Webhook Studio com replay de requisições que falharam.
* Exportação de SDK em Python para clientes externos que consomem a API de forma programática.

---

## ANOTAÇÕES DO HEVERTON

* **[CONTRATOS TIPADOS EM TEMPO REAL]**: O arquivo `api_contracts.ts` é mantido rigorosamente sincronizado com os modelos Pydantic de `src/features/`, garantindo tipagem fim-a-fim sem a lentidão de um build pesado de Node.js.
