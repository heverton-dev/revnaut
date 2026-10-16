# Manual da Rota: Governança AIDD & Quarteto Sine Qua Non (`/docs`, `/webhooks`, `/mcp`, `/docs/guia`)

## 1. Objetivo das Rotas
Cumprir a Lei Canônica #10 de Governança AIDD, que exige que toda aplicação em produção exponha de forma dinâmica, viva e sem stubs os 4 pilares essenciais para operação por humanos, sistemas legados e agentes de Inteligência Artificial autônomos.

---

## 2. O Que o Usuário Consegue Realizar
* **Pilar I: Swagger Studio (`/docs`):**
  * Explorar e testar todas as rotas e contratos da API OpenAPI 3.1 com schemas tipados e autenticação interativa.
* **Pilar II: Webhook Studio (`/webhooks`):**
  * Disparar eventos de teste em tempo real, testar assinaturas HMAC-SHA256 e auditar entregas de eventos comerciais.
* **Pilar III: MCP Studio (`/mcp`):**
  * Interface dedicada para conexões de Model Context Protocol (MCP) que permite que assistentes e IAs interajam com o CRM de forma controlada.
* **Pilar IV: Guia do Usuário (`/docs/guia`):**
  * Visualizador e documentação viva da plataforma acessível a colaboradores e gestores.

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Ferramenta | Rota | Público | Permissão Necessária |
|---|---|---|---|
| Swagger Studio | `/docs` | Desenvolvedores e Integradores | Pública para consulta; requer token Bearer para execução de rotas protegidas |
| Webhook Studio | `/webhooks` | Equipe de TI e Engenharia | Autenticação de Operações |
| MCP Studio | `/mcp` | Agentes de IA e Automação | Token de API de Sistema |
| Guia do Usuário | `/docs/guia` | Colaboradores Comerciais | Aberto para leitura corporativa |

---

## 4. Quais Ações Podem Ser Realizadas
* `API_TESTING`: Disparar requisições diretamente pela interface interativa do Swagger.
* `WEBHOOK_SIMULATION`: Enviar webhooks de teste com payload de simulação de venda para URLs configuradas.
* `MCP_TOOL_DISCOVERY`: Listagem dinâmica de ferramentas e schemas para modelos de linguagem.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)
1. No menu lateral, role até o bloco **Governança AIDD**.
2. Clique no link desejado (ex: "Swagger Studio").
3. A ferramenta será aberta em uma nova aba do navegador sem interromper o trabalho no CRM.
4. Para autenticar no Swagger, clique em "Authorize" e informe o token Bearer gerado na tela de login.

---

## 6. O Que Falta Implementar (Roadmap & Gaps)
* Simulador visual interativo de webhook payloads diretamente no Webhook Studio com replay de requisições que falharam.
* Exportação de SDKs tipados em TypeScript e Python gerados automaticamente a partir da especificação OpenAPI ativa.
