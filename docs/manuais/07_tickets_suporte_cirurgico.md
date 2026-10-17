# Manual da Rota: Central de Tickets & Suporte Cirúrgico (`/#tickets`)

## 1. Objetivo da Rota
Gerenciar chamados técnicos, dúvidas de intercorrências cirúrgicas, solicitações de garantia de implantes, reposição de brocas/instrumentais e o **Fluxo Digital CAD/CAM** (recebimento de arquivos de scanner intraoral `.STL`/`.PLY`, aprovação de guias cirúrgicos e fresagem de componentes protéticos).

---

## 2. O Que o Usuário Consegue Realizar
* Listar todos os chamados técnicos com tags de severidade (Baixa, Média, Alta, Crítica).
* Filtrar chamados por status (Aberto, Em Andamento, Aguardando Fabricação, Resolvido).
* Abrir novos tickets informando o cirurgião, o código do instrumental e o relato da ocorrência.
* **Módulo Fluxo Digital CAD/CAM:**
  * Ingestão de pedidos de guias cirúrgicos guiados e próteses fresadas.
  * Upload e validação de arquivos de escaneamento intraoral (`.STL`, `.PLY`, `.OBJ`).
  * Controle de SLA de desenho protético e envio para fresadora/impressora 3D.
* Assumir chamados e registrar pareceres técnicos fundamentados nas normas da fábrica.

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil | Abertura de Ticket | Atendimento / Resposta | Fechamento de Chamado |
|---|---|---|---|
| Cirurgião / Cliente | Sim (via canal de entrada) | Não | Não |
| Consultor de Vendas | Sim (em nome do cirurgião) | Sim (comentários) | Não |
| Especialista Digital / CAD/CAM | Sim | Sim (desenho e aprovação) | Sim |
| Engenheiro / Suporte Técnico | Sim | Sim (laudo de garantia) | Sim |
| Gerente de Qualidade | Sim | Sim | Sim |
| Super Admin (Heverton) | Sim | Sim | Sim |

---

## 4. Quais Ações Podem Ser Realizadas
* `CREATE_TICKET`: Abertura de chamado com seleção de gravidade e categoria (Garantia, Torque, Troca, CAD/CAM).
* `UPLOAD_SCAN_FILE`: Anexar malha 3D de escaneamento odontológico (`.STL`/`.PLY`).
* `ASSIGN_AGENT`: Atribuição de responsável técnico pelo chamado.
* `UPDATE_TICKET_STATUS`: Mudança de status para Em Andamento, Desenho Aprovado ou Resolvido.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)
1. Acesse **Operações & Carteira > Central de Tickets**.
2. Clique no botão "+ Novo Ticket".
3. Preencha o cirurgião solicitante, a gravidade e o motivo técnico (ex: "Aprovação de Guia Cirúrgico Guiado - Mandíbula Total").
4. Se envolver prótese digital, anexe o arquivo `.STL` de escaneamento.
5. Clique em "Salvar Ticket". O chamado entra na fila da equipe de Engenharia/CAD-CAM com contagem regressiva de SLA.

---

## 6. O Que Falta Implementar (Roadmap & Gaps)
* Gestão formal de SLA com contadores regressivos visuais dinâmicos e disparo de alerta via WhatsApp em caso de estouro de prazo.
* Integração com o módulo de qualidade para abertura automática de Relatório de Não-Conformidade (RNC) quando envolver quebra em boca do paciente.

---

## ANOTAÇÕES DO HEVERTON

* **[FLUXO DIGITAL ODONTOLÓGICO]**: Categoria exclusiva adicionada para atendimento de clínicas com scanner intraoral e necessidades de planejamento virtual guiado.
