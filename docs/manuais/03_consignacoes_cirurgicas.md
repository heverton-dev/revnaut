# Manual da Rota: Consignações Cirúrgicas & Lotes ANVISA (`/#consignments`)

## 1. Objetivo da Rota
Rastrear e controlar caixas cirúrgicas, instrumentais e kits de implantes consignados em hospitais, clínicas e consultórios odontológicos. Garante o cumprimento das exigências regulatórias da ANVISA quanto ao controle de lotes, datas de esterilização e validade de componentes implantáveis.

---

## 2. O Que o Usuário Consegue Realizar
* Consultar todas as caixas cirúrgicas em campo com seus respectivos códigos de patrimônio e responsáveis.
* Acompanhar o status das caixas (Em Campo, Em Cirurgia, Aguardando Reposição, Em Trânsito).
* Registrar o envio de uma nova caixa consignada para um cirurgião ou hospital.
* Realizar acerto de cirurgia: registrar quais itens do lote foram consumidos no procedimento e gerar a ordem de faturamento correspondente.
* Monitorar alertas de validade de esterilização de caixas em posse de terceiros.

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil | Consulta de Caixas | Registro de Envio | Acerto Cirúrgico / Baixa | Edição de Lotes ANVISA |
|---|---|---|---|---|
| Consultor de Vendas | Apenas caixas de seus clientes atendidos | Sim (solicitação) | Sim | Não |
| Instrumentador Cirúrgico | Todas as caixas agendadas para cirurgias | Sim | Sim (baixa de itens) | Não |
| Gerente de Logística / Estoque | Controle integral de caixas da regional | Sim | Sim | Sim |
| Super Admin | Acesso irrestrito a todos os estoques e lotes | Sim | Sim | Sim |

---

## 4. Quais Ações Podem Ser Realizadas
* `DISPATCH_KIT`: Cadastrar envio de caixa cirúrgica para cirurgião parceiro.
* `SURGICAL_CONSUMPTION`: Informar itens e implantes consumidos durante a cirurgia para baixa no estoque.
* `TRACK_ANVISA_LOT`: Rastrear qual paciente/cirurgia recebeu determinado lote de implante.
* `RETURN_INSPECTION`: Registrar o retorno da caixa ao centro de distribuição para esterilização e reabastecimento.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)

### Registro de Acerto de Cirurgia (Consumo de Lote)
1. Acesse **Comercial & CRM > Consignações Cirúrgicas**.
2. Localize a caixa cirúrgica alocada ao cirurgião (ex: "Caixa Cone Morse #042 - Dr. Felipe").
3. Clique no botão "Registrar Cirurgia / Acerto".
4. Selecione os itens utilizados (ex: 2 Implantes 3.75x11.5 Lote #ANV-8841 e 1 Parafuso de Cobertura).
5. Confirme o cirurgião responsável e anexe o comprovante ou número de prontuário/registro.
6. Clique em "Concluir Acerto".
7. O sistema gera automaticamente o pedido de venda correspondente e atualiza o saldo do kit em campo.

---

## 6. O Que Falta Implementar (Roadmap & Gaps)
* Leitor de código de barras / DataMatrix via câmera do smartphone para conferência ultrarrápida de caixas cirúrgicas.
* Assinatura digital do cirurgião na tela do tablet/smartphone no momento da entrega e devolução da caixa.
* Alertas automáticos via WhatsApp notificando o consultor quando uma caixa estiver completando 30 dias sem procedimentos cirúrgicos registrados.
