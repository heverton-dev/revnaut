# Manual da Rota: DENTGO Express Same-Day & Liquidacao FEFO (`#dentgo`, `#dentgo-fefo`)

## 1. Objetivo da Rota
Operar a malha de logistica express intraoperatoria com SLA de 45 minutos para entrega de implantes e componentes em carater de urgencia cirurgica, gestao de couriers, split de corridas e liquidacao inteligente First-Expired, First-Out (FEFO) de lotes com validade curta.

---

## 2. O Que o Usuário Consegue Realizar
* Acompanhar chamados de entrega emergencial em tempo real com contador regressivo de SLA nas sub-rotas `#dentgo` e `#dentgo-fefo`:
  1. Pedido Emergencial Recebido.
  2. Courier Alocado via Raio Haversine.
  3. Lacre Termico R2 Aplicado no Hub.
  4. Em Transito para o Centro Cirurgico.
  5. Entregue e Homologado pelo Cirurgiao.
* Visualizar o comprovante fotografico de entrega com lacre no Cloudflare R2.
* Acessar a prateleira de liquidacao FEFO com desconto progressivo para produtos de validade curta.
* Consultar o split financeiro de taxas de entrega por corrida.

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil | Visualizacao de Entregas | Despacho de Corridas | Confirmacao de Lacre | Liquidacao FEFO |
|---|---|---|---|---|
| Courier / Motorista | Apenas suas corridas ativas | Nao | Sim (upload de foto) | Nao |
| Consultor de Campo | Entregas de seus clientes | Sim | Sim | Sim (reserva) |
| Operador do Hub | Todas as entregas do hub | Sim | Sim | Sim |
| Diretor / Super Admin | Acesso irrestrito ao marketplace | Sim | Sim | Sim (Total) |

---

## 4. Quais Ações Podem Ser Realizadas
* `CREATE_DISPATCH`: Criar pedido de entrega express com coordenadas geograficas.
* `ASSIGN_COURIER`: Alocar courier mais proximo automaticamente.
* `UPLOAD_SEAL_PROOF`: Enviar foto do lacre termico para Cloudflare R2.
* `CONFIRM_DELIVERY`: Confirmar entrega na recepcao da clinica.
* `BUY_FEFO_DEAL`: Adquirir componente em promocao FEFO de validade curta.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)

### Abertura de Chamado Emergencial DENTGO
1. Acesse o menu lateral e clique em "DENTGO Express (45m)".
2. Na rota `#dentgo`, clique em "Novo Despacho Emergencial".
3. Selecione o cirurgiao, o hospital e os componentes de implante solicitados.
4. O sistema calcula a distancia e o hub mais proximo e aloca o courier com SLA de 45 minutos.

---

## 6. O Que Falta Implementar
* Rastreamento telemetrico em tempo real via GPS continuo de couriers em mapa vetorial interativo.
