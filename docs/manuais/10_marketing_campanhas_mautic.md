# Manual da Rota: Marketing & Campanhas Mautic (`/#marketing`, `/#marketing-mautic`)

## 1. Objetivo da Rota
Coordenar as ações de atração e nutrição de cirurgiões-dentistas via réguas de relacionamento automatizadas e integração com a instância open-source do Mautic 5 rodando em VPS. Abrange divulgação de lançamentos de implantes, convites para o congresso CIOSP, workshops práticos e sincronização bidirecional de pontuação de engajamento via webhooks.

---

## 2. O Que o Usuário Consegue Realizar
* **Subrota Campanhas de Marketing (`/#marketing`):**
  * Listar campanhas ativas com público-alvo cirúrgico, canais de disparo e taxas de conversão.
  * Acompanhar métricas de e-mail marketing (taxa de abertura de catálogos técnicos, cliques e descadastros).
* **Subrota Painel Mautic VPS (`/#marketing-mautic`):**
  * Monitorar a sincronização dos contatos do SQLite WAL com os segmentos do Mautic.
  * **Ingestão de Webhooks do Mautic (`/api/v1/webhooks/mautic`):** Recepção de eventos em tempo real (`lead.changepoints`) com assinatura HMAC. Quando o cirurgião baixa um catálogo ou abre e-mails, sua pontuação no Lead Scoring ICP é incrementada instantaneamente.
  * Forçar sincronização manual de novos cirurgiões cadastrados.

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil | Visualizar Campanhas | Disparar E-mails | Gerenciar Integração Mautic |
|---|---|---|---|
| Consultor de Vendas | Apenas campanhas ativas para divulgar | Não | Não |
| Analista de Marketing | Sim | Sim | Sim (segmentos e campanhas) |
| Gerente de Marketing | Sim | Sim | Sim |
| Super Admin (Heverton) | Sim | Sim | Sim (credenciais e webhooks VPS) |

---

## 4. Quais Ações Podem Ser Realizadas
* `SYNC_MAUTIC`: Disparar sincronização bidirecional de cirurgiões e tags com o Mautic.
* `INGEST_MAUTIC_WEBHOOK`: Recepção de eventos de alteração de pontos e engajamento.
* `CREATE_CAMPAIGN`: Criar nova campanha de nutrição para cirurgiões com perfil ICP Tier A.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)
1. Acesse **Marketing & Scoring > Campanhas Mautic**.
2. Visualize as campanhas em andamento (ex: "Lançamento Linha Biomateriais CIOSP 2026").
3. Para validar o status da integração técnica com o Mautic, clique na sub-opção **Mautic VPS & E-mails**.
4. Verifique a quantidade de contatos sincronizados, latência e logs de webhooks recebidos.

---

## 6. O Que Falta Implementar (Roadmap & Gaps)
* Editor visual drag-and-drop de templates de e-mail integrado diretamente dentro do dashboard do Revnaut.
* Disparo de fluxos mistos (E-mail Mautic + Mensagem WhatsApp Evolution API) em sequência cadenciada.

---

## ANOTAÇÕES DO HEVERTON

* **[WEBHOOKS HMAC MAUTIC]**: O endpoint `/api/v1/webhooks/mautic` valida a assinatura do payload e recalcula o score do cirurgião em tempo real a cada interação digital.
