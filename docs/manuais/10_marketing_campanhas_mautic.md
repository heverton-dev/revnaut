# Manual da Rota: Marketing & Campanhas Mautic (`/#marketing`, `/#marketing-mautic`)

## 1. Objetivo da Rota
Coordenar as ações de atração e nutrição de cirurgiões-dentistas via réguas de relacionamento automatizadas e integração com a instância open-source do Mautic rodando em VPS. Abrange divulgação de lançamentos de implantes, convites para o congresso CIOSP e cursos de pós-graduação.

---

## 2. O Que o Usuário Consegue Realizar
* **Subrota Campanhas de Marketing (`/#marketing`):**
  * Listar campanhas ativas com público-alvo, canal de disparo e taxa de conversão.
  * Acompanhar métricas de e-mail marketing (abertura, clique, descadastro).
* **Subrota Painel Mautic VPS (`/#marketing-mautic`):**
  * Monitorar a sincronização dos contatos locais do SQLite com o banco do Mautic.
  * Forçar sincronização manual de novos cirurgiões cadastrados.

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil | Visualizar Campanhas | Disparar E-mails | Gerenciar Integração Mautic |
|---|---|---|---|
| Consultor de Vendas | Apenas campanhas ativas para divulgar | Não | Não |
| Analista de Marketing | Sim | Sim | Sim (segmentos e campanhas) |
| Gerente de Marketing | Sim | Sim | Sim |
| Super Admin | Sim | Sim | Sim (configuração de credenciais VPS) |

---

## 4. Quais Ações Podem Ser Realizadas
* `SYNC_MAUTIC`: Disparar sincronização bidirecional de cirurgiões e tags com o Mautic.
* `CREATE_CAMPAIGN`: Criar nova campanha de nutrição para cirurgiões com perfil ICP A.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)
1. Acesse **Marketing & Scoring > Campanhas Mautic**.
2. Visualize as campanhas em andamento (ex: "Lançamento Nova Linha Biomateriais CIOSP 2026").
3. Para validar o status da integração técnica com o Mautic, clique na sub-opção **Mautic VPS & E-mails**.
4. Verifique a quantidade de contatos sincronizados e a latência da API.

---

## 6. O Que Falta Implementar (Roadmap & Gaps)
* Editor visual de templates de e-mail diretamente no dashboard.
* Disparo de sequências automatizadas por gatilhos de WhatsApp integrado ao fluxo do Mautic.

---

## ANOTAÇÕES DO HEVERTON

