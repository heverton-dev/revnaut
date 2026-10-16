# Manual da Rota: Tarefas Operacionais & Checklist (`/#tasks`)

## 1. Objetivo da Rota
Organizar as atividades diárias de campo dos consultores comerciais e assistentes cirúrgicos: visitas a consultórios, recolhimento de caixas de consignação, agendamento de treinamentos de secretárias e cobrança de faturas pendentes.

---

## 2. O Que o Usuário Consegue Realizar
* Visualizar sua lista individual de tarefas do dia com data de vencimento e prioridade.
* Marcar tarefas como concluídas com 1 clique (checkbox interativo).
* Criar novas tarefas associadas a cirurgiões ou negócios em andamento.
* Visualizar o progresso de conclusão da rotina semanal.

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil | Visualizar Tarefas | Criar Tarefas | Delegar Tarefas |
|---|---|---|---|
| Consultor de Vendas | Apenas as suas próprias tarefas | Sim | Não |
| Coordenador / Gerente | Tarefas de toda a equipe de campo | Sim | Sim (atribui para consultores) |
| Super Admin | Acesso a todas as tarefas de todos os colaboradores | Sim | Sim |

---

## 4. Quais Ações Podem Ser Realizadas
* `CHECK_TASK`: Concluir tarefa (alteração de estado reativo).
* `CREATE_TASK`: Cadastrar nova ação com título, cirurgião relacionado, data limite e prioridade.
* `DELETE_TASK`: Excluir tarefas não mais necessárias.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)
1. Acesse **Operações & Carteira > Tarefas Operacionais**.
2. Para concluir uma tarefa realizada, clique na caixa de seleção ao lado do título (ex: "Visita pós-cirúrgica - Dr. Paulo").
3. Para criar uma nova tarefa, clique em "+ Nova Tarefa", preencha a descrição e defina a data limite.

---

## 6. O Que Falta Implementar (Roadmap & Gaps)
* Sincronização bidirecional com Google Calendar e Microsoft Outlook.
* Notificações push no smartphone no horário agendado da visita ao consultório.

---

## ANOTAÇÕES DO HEVERTON

