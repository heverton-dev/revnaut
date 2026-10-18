# Manual da Rota: KeyPartners Consignados & Lotes ANVISA (`#keypartners`, `#keypartners-kols`)

## 1. Objetivo da Rota
Gerenciar a custodia de caixas cirurgicas consignadas em clinicas e hospitais parceiros, com rastreabilidade unitaria de lotes ANVISA, controle de SLA de esterilizacao, conferencia de lacre de seguranca e gestao de bonificacoes de Key Opinion Leaders (KOLs) atraves da Moeda Cirurgica.

---

## 2. O Que o Usuário Consegue Realizar
* Monitorar o status de caixas cirurgicas consignadas nas sub-rotas `#keypartners` e `#keypartners-kols`:
  1. Em Transito para a Clinica.
  2. Custodia Ativa na Clinica / Hospital.
  3. Aberta em Procedimento Cirurgico.
  4. Aguardando Conferencia de Lacre.
  5. Faturada e Reposta.
* Visualizar o historico de lote ANVISA e data de validade de cada componente dentro da caixa.
* Realizar conferencia de lacre de seguranca apos cirurgia com registro de componentes consumidos.
* Calcular o Share of Kit (SOK) e disparar sugestao preditiva de reposicao automatica.
* Acompanhar o saldo de Moeda Cirurgica e bonificacoes de KOLs e docentes.

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil | Visualizacao de Caixas | Conferencia de Lacre | Disparo de Reposicao | Gestao de KOLs |
|---|---|---|---|---|
| Consultor de Campo | Apenas caixas de sua regiao | Sim (em campo) | Sim | Apenas leitura |
| Inside Sales | Todas as caixas da regiao | Sim (validacao) | Sim | Apenas leitura |
| Coordenador Regional | Todas as caixas da regional | Sim | Sim | Sim |
| Diretor / Super Admin | Acesso irrestrito a todas as caixas | Sim | Sim | Sim (Total) |

---

## 4. Quais Ações Podem Ser Realizadas
* `CHECK_IN_KIT`: Registrar entrada da caixa consignada na clinica parceira.
* `OPEN_SURGERY_KIT`: Registrar abertura do kit cirurgico para procedimento.
* `VERIFY_SEAL`: Conferir lacre de seguranca e itens consumidos no pos-operatorio.
* `TRIGGER_REPLENISHMENT`: Disparar pedido de reposicao expressa via DENTGO.
* `CREDIT_KOL_POINTS`: Creditar pontos de Moeda Cirurgica por cirurgia concluida.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)

### Conferencia de Lacre e Baixa Pos-Cirurgica
1. Acesse o menu lateral e clique em "KeyPartners Consignados".
2. Localize a caixa cirurgica pelo codigo ou nome do cirurgiao na rota `#keypartners`.
3. Clique em "Conferir Lacre & Consumo".
4. Selecione os componentes utilizados na cirurgia e informe o numero do prontuario.
5. Confirme a conferencia. O sistema gera a baixa de estoque e o faturamento no ERP.

---

## 6. O Que Falta Implementar
* Integracao via RFID com leitores fixos nas portas dos centros cirurgicos hospitalares para rastreamento sem fio automatizado.
