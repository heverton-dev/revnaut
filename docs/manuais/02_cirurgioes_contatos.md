# Manual da Rota: Cirurgiões & Contatos (`/#contacts`, `/#contacts-segments`)

## 1. Objetivo da Rota
Gerenciar a carteira central de cirurgiões-dentistas, implantodontistas, clínicas e compradores institucionais. Contém dados regulatórios como número de CRO (Conselho Regional de Odontologia), UF de registro, especialidade clínica e volume médio mensal de procedimentos cirúrgicos.

---

## 2. O Que o Usuário Consegue Realizar
* **Subrota Base de Cirurgiões (`/#contacts`):**
  * Listar todos os cirurgiões e clínicas com filtro por nome, CRO, cidade ou UF.
  * Cadastrar novos cirurgiões com validação de CRO e duplicidade de dados.
  * Visualizar a pontuação de Lead Scoring (ICP) de cada cirurgião.
  * Acessar contato rápido via WhatsApp ou ligação direta.
* **Subrota Segmentos & Especialidades (`/#contacts-segments`):**
  * Visualizar a distribuição dos profissionais por nicho clínico (Implantodontia, Prótese Dentária, Bucomaxilofacial, Periodontia, Ortodontia).
  * Filtrar e agrupar cirurgiões de alto volume (> 50 implantes/mês) para campanhas direcionadas.

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil | Visualização | Cadastro de Contato | Edição de Contato | Atribuição Territorial |
|---|---|---|---|---|
| Consultor de Vendas | Apenas contatos da sua carteira ou território | Sim | Sim (nos seus contatos) | Não |
| Coordenador / Gerente | Todos os contatos da sua equipe regional | Sim | Sim | Sim (dentro da regional) |
| Diretor de BU | Todos os contatos da Business Unit | Sim | Sim | Sim |
| Super Admin | Carteira nacional completa de todas as regiões | Sim | Sim | Sim (qualquer território) |

---

## 4. Quais Ações Podem Ser Realizadas
* `SEARCH_CONTACT`: Filtrar contatos em tempo real por nome, CRO ou cidade.
* `CREATE_CONTACT`: Adicionar novo cirurgião com nome, CRO, UF, telefone, clínica e potencial cirúrgico.
* `VIEW_CONTACT_DETAILS`: Abrir ficha completa com histórico de pedidos e caixas consignadas.
* `SEGMENT_FILTER`: Agrupar profissionais por especialidade e tier de consumo (Tier A, Tier B, Tier C).

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)

### Cadastro de um Novo Cirurgião
1. No menu lateral, acesse **Comercial & CRM > Cirurgiões & Contatos**.
2. Clique no botão "+ Novo Contato / Cirurgião".
3. Preencha os campos obrigatórios:
   * Nome Completo (ex: "Dr. Marcelo Arantes").
   * CRO e UF (ex: "CRO-SP 89412").
   * Especialidade Primária (ex: "Implantodontia Avançada").
   * Telefone / WhatsApp com DDD.
   * Volume Estimado de Implantes/Mês.
4. Clique em "Salvar Contato".
5. O sistema grava o registro no banco SQLite WAL e executa o cálculo de scoring inicial.

### Consulta por Segmento Clínico
1. No submenu de contatos, clique em **Segmentos & Especialidades**.
2. Selecione a especialidade desejada no card de segmentos (ex: "Implantodontia").
3. A listagem é automaticamente filtrada exibindo apenas profissionais habilitados para cirurgias com kits de fixação rígida e biomateriais.

---

## 6. O Que Falta Implementar (Roadmap & Gaps)
* Integração com a API do CFO (Conselho Federal de Odontologia) para validação cadastral automática da situação da inscrição do CRO.
* Geolocalização de consultórios no mapa para planejamento de rotas de visitas dos consultores.
* Histórico clínico de preferências de instrumentais (tipos de chaves cirúrgicas, conexões protéticas preferidas).

---

## ANOTAÇÕES DO HEVERTON

[FILTROS: Nao existe implementacao de filtro por nome, CRO, cidade ou UF]

[ACESSAR CONTATO: Nao existe implementacao para acessar contato rápido via WhatsApp ou ligação direta]

[DADOS: Clicar no registro deveria abrir modal com todos os dados, score, histórico de compras e oportunidades de cada cirurgião]

[DUVIDA: Subrota Segmentos & Especialidades podem ser criadas dinamicamente ou sao fixas? sao individuais por BU ou por perfil/usuario?]

[REDIRECIONAMENTO: clicar no card de segmento direciona para um funil de oportunidades com status e etapa]
