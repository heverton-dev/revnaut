# Manual da Rota: Central de Tickets & Suporte Cirúrgico (`/#tickets`)

## 1. Objetivo da Rota
Gerenciar chamados técnicos, dúvidas de intercorrências cirúrgicas, solicitações de troca de peças em garantia, reposição de instrumentais quebrados e dúvidas sobre protocolos de torque de implantes.

---

## 2. O Que o Usuário Consegue Realizar
* Listar todos os chamados técnicos com indicadores visuais de severidade (Baixa, Média, Alta, Crítica).
* Filtrar chamados por status (Aberto, Em Andamento, Resolvido).
* Abrir novos tickets informando o cirurgião, o código do instrumental e a descrição da ocorrência.
* Assumir chamados e registrar respostas técnicas fundamentadas nos manuais de engenharia da fábrica.

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil | Abertura de Ticket | Atendimento / Resposta | Fechamento de Chamado |
|---|---|---|---|
| Cirurgião / Cliente | Sim (via canal de entrada) | Não | Não |
| Consultor de Vendas | Sim (em nome do cirurgião) | Sim (comentários) | Não |
| Engenheiro / Suporte Técnico | Sim | Sim | Sim |
| Gerente de Qualidade | Sim | Sim | Sim |
| Super Admin | Sim | Sim | Sim |

---

## 4. Quais Ações Podem Ser Realizadas
* `CREATE_TICKET`: Formulário de criação com seleção de urgência e categoria (Garantia, Torque, Troca).
* `ASSIGN_AGENT`: Atribuição de responsável técnico pelo chamado.
* `UPDATE_TICKET_STATUS`: Mudança de status para Em Andamento ou Resolvido.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)
1. Acesse **Operações & Carteira > Tickets & Suporte**.
2. Clique no botão "+ Novo Ticket".
3. Preencha o cirurgião solicitante, a gravidade e o motivo técnico (ex: "Travamento de chave de contra-ângulo").
4. Clique em "Salvar Ticket".
5. A equipe de engenharia e qualidade receberá notificação imediata para atendimento em SLA de 4 horas.

---

## 6. O Que Falta Implementar (Roadmap & Gaps)
* Gestão formal de SLA com contagem regressiva visual e alertas de estouro de prazo.
* Integração com o módulo de qualidade para abertura automática de Não-Conformidade (RNC) quando o chamado envolver quebra em boca do paciente.
