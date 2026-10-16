# Manual da Rota: Fluxos de Automação Cirúrgica (`/#automations`)

## 1. Objetivo da Rota
Mapear e construir fluxos lógicos de regras condicionais automatizadas para disparo de eventos no ciclo de vida de uma venda ou procedimento cirúrgico (ex: envio de alerta quando uma caixa cirúrgica completa 15 dias sem consumo; notificação de cobrança após acerto cirúrgico).

---

## 2. O Que o Usuário Consegue Realizar
* Consultar os gatilhos e automações ativas no sistema.
* Ativar ou pausar fluxos automáticos de pós-operatório e faturamento.
* Visualizar o histórico de execuções das regras automáticas.

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil | Visualizar Automações | Criar / Pausar Fluxos |
|---|---|---|
| Consultor de Vendas | Sim (apenas leitura) | Não |
| Gerente de Processos / RevOps | Sim | Sim |
| Super Admin | Sim | Sim |

---

## 4. Quais Ações Podem Ser Realizadas
* `TOGGLE_AUTOMATION`: Ativar ou desativar uma regra de automação no motor reativo.
* `TRIGGER_MANUAL`: Disparar teste manual de um fluxo específico.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)
1. Acesse **Marketing & Scoring > Fluxos de Automação**.
2. Localize a automação desejada (ex: "Alerta de Reposição de Brocas Cirúrgicas").
3. Utilize o botão liga/desliga para ativar ou suspender o fluxo.

---

## 6. O Que Falta Implementar (Roadmap & Gaps)
* Construtor visual drag-and-drop de nós de automação (Canvas com blocos: Gatilho -> Condição -> Ação).
* Integração com webhooks de saída configuráveis para terceiros (ERP Protheus, Bling, Tiny).
