# Manual da Rota: Governança AIDD & Studios do Quarteto Sine Qua Non (`#governanca`)

## 1. Objetivo da Rota / Sub-rota
Expor e governar os 4 pilares do Quarteto Sine Qua Non dinâmico da Lei Canônica #10: Swagger Studio (`/docs`), Webhook Studio (`/webhooks`), Servidor Nativo MCP (`/mcp`) e Guia do Usuário (`/docs/guia`).

---

## 2. O Que o Usuário Consegue Realizar
* Inspecionar e testar interativamente todos os contratos de API REST no Swagger Studio (`/docs`).
* Monitorar entregas de webhooks, retentativas e payloads no Webhook Studio (`/webhooks`).
* Conectar agentes de inteligência artificial de forma padronizada via MCP Studio (`/mcp`).
* Consultar os manuais operacionais unificados e guias técnicos no Guia do Utilizador (`/docs/guia`).

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil de Usuário | Visualizar | Criar / Submeter | Disparar Testes | Configuração Avançada |
|---|---|---|---|---|
| Consultor de Campo | Apenas Guia do Usuário | Não | Não | Não |
| Gerente Regional | Guia do Usuário e Webhooks | Não | Não | Não |
| Diretor de BU | Todos os Studios | Sim | Sim | Leitura |
| Super Admin | Acesso irrestrito a todos os 4 pilares | Sim | Sim | Sim (Total) |

---

## 4. Quais Ações Podem Ser Realizadas
* `OPEN_SWAGGER`: Abertura da interface OpenAPI interativa para testes de endpoints.
* `INSPECT_WEBHOOKS`: Consulta de logs de disparo e status de entrega de webhooks.
* `MCP_INTEGRATION`: Conexão de ferramentas agênticas via Model Context Protocol.
* `VIEW_USER_GUIDE`: Navegação pelos manuais canônicos de todas as rotas e sub-rotas.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)
1. Localize a seção **Governança AIDD** no rodapé do menu lateral.
2. Clique no link do pilar desejado: Swagger Studio, Webhook Studio, Servidor MCP ou Guia do Usuário.
3. O pilar selecionado abre em uma aba dedicada ou painel embutido de alta fidelidade.
4. Execute as inspeções, testes ou leituras de conformidade de governança.

---

## 6. Catálogo Anatômico de Botões & Ações do DOM

| Rótulo do Botão / Elemento | Classe CSS | Evento (`onclick`) | Ação Operacional Realizada |
|---|---|---|---|
| `Swagger Studio` | `.nav-link .aidd-link` | `href="/docs"` | Abre documentação interativa OpenAPI 3.1 em nova aba |
| `Webhook Studio` | `.nav-link .aidd-link` | `href="/webhooks"` | Abre console de auditoria de webhooks |
| `Servidor MCP` | `.nav-link .aidd-link` | `href="/mcp"` | Abre manifesto de ferramentas e recursos MCP para IA |
| `Guia do Usuário` | `.nav-link .aidd-link` | `href="/docs/guia"` | Abre portal centralizado de documentação canônica |

---

## 7. Catálogo de Modais & Gavetas Operacionais
* Os 4 pilares do Quarteto utilizam páginas e consoles dedicados independentes com isolamento sandbox.

---

## 8. Motores de Backend & Arquitetura Subjacente
* **Endpoints REST Vinculados**: `/docs`, `/openapi.json`, `/webhooks`, `/mcp`, `/docs/guia`.
* **O Que o Motor Executa**: Geração de esquemas OpenAPI 3.1 com tipagem Pydantic estrita, renderização de dashboard Swagger UI, captura de eventos de webhooks e disponibilização de SSE/JSON-RPC para clientes MCP.
* **O Que o Motor Não Executa**: Não expõe segredos nem credenciais sensíveis nos manifestos públicos.
* **Garantia de Resiliência**: Endpoints estáticos servidos com cache imutável e compressão gzip.

---

## 9. O Que Falta Implementar & Plano de Micro-Tickets
* `[TICKET-GOV-01]`: Painel de visualização de traces OpenTelemetry integrado ao Webhook Studio.
* `[TICKET-GOV-02]`: Simulador de payloads de webhook com assinatura HMAC em tempo real.
