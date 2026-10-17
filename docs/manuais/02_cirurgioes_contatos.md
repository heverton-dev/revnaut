# Manual da Rota: Cirurgiões & Contatos (`/#contacts`, `/#contacts-segments`)

## 1. Objetivo da Rota
Gerenciar a carteira de cirurgiões-dentistas, implantodontistas, clínicas e decisores institucionais. Centraliza dados regulatórios como número de CRO (Conselho Regional de Odontologia), UF de registro, especialidade cirúrgica, estimativa de consumo de implantes e o **Grafo Clínico Odontológico (Ecossistema KOL)** conectando profissionais a clínicas, hospitais, laboratórios CAD/CAM e faculdades.

---

## 2. O Que o Usuário Consegue Realizar
* **Subrota Base de Cirurgiões (`/#contacts`):**
  * Listar todos os cirurgiões com busca instantânea por nome, CRO, clínica, e-mail ou cidade.
  * Filtrar profissionais por especialidade cirúrgica (Implantodontia, Cirurgia Bucomaxilofacial, Periodontia, Prótese Dentária).
  * Cadastrar novos cirurgiões com validação de CRO, especialidade e volume cirúrgico mensal.
  * Visualizar a pontuação de Lead Scoring ICP (Tier A Hot Lead, Tier B, Tier C) e tag de prioridade.
  * Acionar contato rápido via WhatsApp oficial em um clique (`wa.me`).
  * Abrir modal completo de detalhes: dados cadastrais, score ICP, ecossistema de clínicas e histórico de oportunidades.
* **Grafo Clínico & Ecossistema KOL (`src/features/institutions/`):**
  * Mapeamento N:N de vínculos institucionais (`contact_institutions`): clínicas onde opera, radiologias parceiras, laboratórios protéticos e instituições de ensino onde atua como docente/palestrante.
  * Identificação de *Key Opinion Leaders (KOLs / Speakers)* para eventos e lançamentos científicos.
* **Subrota Segmentos & Especialidades (`/#contacts-segments`):**
  * Visualizar cards agregadores de distribuição por nicho clínico e volume cirúrgico (> 30 e > 50 implantes/mês).
  * Redirecionar diretamente do card de segmento para a lista filtrada de cirurgiões ou funil de vendas.

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil | Visualização | Cadastro de Contato | Edição de Contato | Vínculo no Grafo KOL | Atribuição Territorial |
|---|---|---|---|---|---|
| Consultor de Vendas | Apenas contatos da sua carteira (`owner_id`) | Sim | Sim (nos seus contatos) | Sim | Não |
| Coordenador / Gerente | Todos os contatos da sua equipe regional (`team_id`) | Sim | Sim | Sim | Sim (dentro da regional) |
| Diretor de BU | Todos os contatos da Business Unit | Sim | Sim | Sim | Sim |
| Super Admin (Heverton) | Carteira nacional completa de todas as regiões | Sim | Sim | Sim | Sim (qualquer território) |

---

## 4. Quais Ações Podem Ser Realizadas
* `SEARCH_CONTACT`: Filtrar contatos em tempo real por nome, CRO, UF ou clínica.
* `SPECIALTY_FILTER`: Selecionar a especialidade odontológica para isolar profissionais habilitados.
* `CREATE_CONTACT`: Adicionar novo cirurgião com metadados odontológicos e estimativa de implantes.
* `VIEW_CONTACT_DETAILS`: Abrir ficha completa com dados regulatórios, score e histórico de compras.
* `LINK_INSTITUTION`: Associar o cirurgião a hospitais, clínicas parceiras ou faculdades no Grafo Clínico.
* `QUICK_WHATSAPP`: Iniciar conversa direta via WhatsApp pelo botão de ação rápida da tabela.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)

### Cadastro de um Novo Cirurgião
1. No menu lateral, acesse **Comercial & CRM > Cirurgiões & Contatos**.
2. Clique no botão "+ Novo Cirurgião / Contato".
3. Preencha os campos estruturados:
   * Nome Completo (ex: "Dr. Marcelo Arantes").
   * CRO e UF (ex: "CRO-SP 89412").
   * Especialidade Cirúrgica Primária (ex: "Implantodontia").
   * Clínica / Hospital / Instituto de Atuação.
   * Telefone / WhatsApp com DDD.
   * Estimativa de Implantes/Mês (ex: 45 implantes).
4. Clique em "Salvar Contato". O registro é persistido no SQLite WAL e avaliado pelo motor de Lead Scoring.

### Busca e Filtragem Reativa de Profissionais
1. No campo de busca superior, digite qualquer fragmento de nome, CRO, clínica ou e-mail.
2. A tabela atualiza instantaneamente sem recarregar a página.
3. No seletor ao lado, escolha a especialidade desejada para refinar o público-alvo cirúrgico.
4. Clique no ícone de WhatsApp na coluna de ações para abrir o canal direto com o cirurgião.

### Associação ao Grafo Clínico & KOLs
1. Clique na linha do cirurgião para abrir o modal de detalhes do profissional.
2. Na seção "Ecossistema & Vínculos Institucionais", clique em "+ Vincular Instituição".
3. Selecione o tipo de vínculo (Clínica Privada, Hospital Cirúrgico, Laboratório CAD/CAM ou Faculdade/Pós-Graduação) e informe a instituição parceira.
4. Salve para atualizar a rede de influência do cirurgião.

---

## 6. O Que Falta Implementar (Roadmap & Gaps)
* Integração direta com a API pública do CFO (Conselho Federal de Odontologia) para checagem em lote da situação cadastral do registro profissional.
* Renderização de mapa com geolocalização dos consultórios para otimização de rotas de visita técnica dos consultores de campo.
* Mapeamento de preferências cirúrgicas de encaixe protético (Cone Morse, Hexágono Externo, Hexágono Interno) na ficha técnica do cirurgião.

---

## ANOTAÇÕES DO HEVERTON

* **[FILTROS IMPLEMENTADOS]**: A barra de ferramentas agora possui busca em tempo real por nome, CRO, clínica, e-mail e seletor por especialidade cirúrgica.
* **[ACESSO RÁPIDO WHATSAPP]**: Botão dedicado de WhatsApp ativo em cada linha da tabela de cirurgiões.
* **[MODAL DE DETALHES COMPLETO]**: Modal exibe todos os dados do cirurgião, pontuação ICP, volume mensal de implantes e ecossistema de instituições.
* **[GRAFO CLÍNICO ODONTOLÓGICO]**: Implementada a modelagem N:N (`contact_institutions`) para rastreamento de KOLs, radiologias, laboratórios CAD/CAM e faculdades parceiras.
