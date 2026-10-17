# Manual da Rota: Tarefas Operacionais & Checklist (`/#tasks`)

## 1. Objetivo da Rota
Organizar as atividades de campo e de retaguarda dos consultores de vendas e assessores técnicos: visitas a consultórios, reposição de caixas de consignação, cobrança de faturamento e **Tarefas Automáticas de Transbordo (SLA 15min)** para cirurgiões Tier A e alertas do Radar Anti-Churn.

---

## 2. O Que o Usuário Consegue Realizar
* Visualizar lista de tarefas do dia com status, prioridade e prazo de expiração.
* Concluir tarefas com 1 clique (checkbox interativo sincronizado via API).
* Criar novas tarefas associadas a cirurgiões, clínicas ou negócios do funil.
* **Tarefas Automáticas Geradas pelo Sistema:**
  * **Transbordo de Lead Tier A:** Quando um cirurgião atinge alta qualificação de compra, uma tarefa prioritária com SLA de 15 minutos é atribuída ao Closer do estado/UF correspondente.
  * **Alerta Anti-Churn (RFM):** Tarefa de contato preventivo gerada automaticamente quando a clínica ultrapassa a cadência habitual de compra de implantes.
* Visualizar barra de progresso diário da equipe.

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil | Visualizar Tarefas | Criar Tarefas | Delegar Tarefas |
|---|---|---|---|
| Consultor de Vendas | Apenas as suas próprias tarefas (`owner_id`) | Sim | Não |
| Coordenador / Gerente | Tarefas de toda a equipe de campo (`team_id`) | Sim | Sim (atribui para consultores) |
| Super Admin (Heverton) | Acesso irrestrito a todas as tarefas da organização | Sim | Sim |

---

## 4. Quais Ações Podem Ser Realizadas
* `CHECK_TASK`: Concluir tarefa (atualização imediata de status no SQLite).
* `CREATE_TASK`: Cadastrar nova ação com título, cirurgião relacionado, data limite e prioridade.
* `AUTO_TASK_INFLOW`: Recepção de tarefas disparadas pelos motores de transbordo e inteligência.
* `DELETE_TASK`: Excluir ou arquivar tarefas.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)
1. Acesse **Operações & Carteira > Tarefas & Checklist**.
2. Tarefas geradas pelo sistema com a etiqueta "SLA 15min • Hot Lead" devem ser atendidas com prioridade máxima.
3. Para concluir uma tarefa realizada, clique na caixa de seleção ao lado do título.
4. Para criar uma nova tarefa manual, clique em "+ Nova Tarefa", selecione o cirurgião vinculado e defina o prazo de execução.

---

## 6. O Que Falta Implementar (Roadmap & Gaps)
* Sincronização bidirecional com Google Calendar e Microsoft Outlook via CalDAV/OAuth.
* Disparo de notificação push no celular do consultor no exato horário do agendamento da cirurgia ou visita técnica.

---

## ANOTAÇÕES DO HEVERTON

* **[TAREFAS AUTOMÁTICAS DE RECEITA]**: Tarefas prioritárias agora são geradas automaticamente pelo motor de transbordo Tier A (`revenue_triggers.py`), garantindo que nenhum cirurgião de alto volume fique sem retorno imediato.
