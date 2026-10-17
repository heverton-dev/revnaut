# Manual da Rota: Fluxos de Automação Cirúrgica (`/#automations`)

## 1. Objetivo da Rota
Mapear e operar fluxos lógicos e condicionais para disparo de eventos no ciclo cirúrgico e de receitas: acionamento do **Motor de Transbordo Automático (Tier A)**, emissão automática de pedidos no **TOTVS Protheus**, alertas de reposição de caixas de consignação e disparos de mensagens WhatsApp via Evolution API.

---

## 2. O Que o Usuário Consegue Realizar
* Consultar os gatilhos e automações ativas no sistema industrial odontológico.
* Ativar ou pausar regras automáticas de ciclo cirúrgico e faturamento.
* **Gatilhos de Receita e Transbordo (`revenue_triggers.py`):**
  * Detecção de cirurgião promovido a Tier A e alocação do Closer regional com SLA de 15 minutos.
  * Disparo automático do cabeçalho `SC5` e itens `SC6` no TOTVS Protheus ao fechar negócios.
  * Alertas preventivos do Radar Anti-Churn para cirurgiões com reposição de implantes atrasada.
* Visualizar o histórico de execuções das regras automáticas.

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil | Visualizar Automações | Criar / Pausar Fluxos | Disparar Teste Manual |
|---|---|---|---|
| Consultor de Vendas | Sim (apenas leitura das regras) | Não | Não |
| Gerente de Processos / RevOps | Sim | Sim | Sim |
| Super Admin (Heverton) | Sim | Sim | Sim |

---

## 4. Quais Ações Podem Ser Realizadas
* `TOGGLE_AUTOMATION`: Ativar ou desativar uma regra de automação no motor reativo.
* `TRIGGER_MANUAL`: Disparar teste manual de um fluxo específico (ex: simular transbordo Tier A).
* `VIEW_EXECUTION_LOGS`: Consultar logs de execução e retentativas da fila `integration_outbox`.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)
1. Acesse **Marketing & Scoring > Fluxos de Automação**.
2. Localize a automação desejada (ex: "Transbordo de Leads Hot Tier A para Closer Regional").
3. Utilize o botão liga/desliga para ativar ou suspender o fluxo.
4. Para simular a regra sem esperar o agendador, clique em "Testar Disparo".

---

## 6. O Que Falta Implementar (Roadmap & Gaps)
* Construtor visual drag-and-drop de nós de automação (Canvas com blocos: Gatilho ➔ Condição ➔ Ação).
* Integração configurável com conectores de saída para outros ERPs complementares (Bling, Tiny, Omie).

---

## ANOTAÇÕES DO HEVERTON

* **[AUTOMAÇÃO TOTVS PROTHEUS INTEGRADA]**: O fluxo de emissão de pedidos de venda no TOTVS agora é disparado nativamente por evento no fechamento do Kanban.
* **[REVENUE TRIGGERS ATIVOS]**: O transbordo de cirurgiões Tier A roda como serviço desacoplado com tolerância a falhas e fila de saída no SQLite WAL.
