# Regras de Negócio & Fluxos Lógicos — Rvops

> **Fonte:** Decompilação de plugins do frontend (`deals-plugin.js`, `lead-plugin.js`, `tickets-plugin.js`, `state-plugin.js`) e interceptação de rotas.

---

## 1. Fluxo de Autenticação & Multi-Tenancy

1. **Autenticação em Dois Níveis:**
   * Nível 1: Credenciais globais do usuário (`/api/v1/auth/login`) retornam o perfil e contas associadas.
   * Nível 2: Seleção de Tenant/Conta (`POST /0f14ffff/config/users/login`) emite o token JWT com escopo de tenant (`bW9kQmFja2VuZFRva2Vu-0f14ffff`).
2. **Matriz RBAC (Role-Based Access Control):**
   * Cada usuário possui uma lista de roles para 28 objetos do sistema (ex: `deal`, `lead`, `campaign`, `ticket`, etc.).
   * Flags booleanas de permissão: `objectCreate`, `objectRead`, `objectEdit`, `objectDelete`, `mktPublish`.
3. **MFA Dinâmico:**
   * Suporta WhatsApp, Email e App TOTP. Pode ser configurado como obrigatório (`mfa_required`) ou adiável temporariamente.

---

## 2. Negócios & Gestão de Funil (Pipelines)

1. **Estrutura de Pipeline:**
   * Cada pipeline é composto por 1..N estágios ordenados sequencialmente.
   * Cada estágio possui uma probabilidade percentual de fechamento (0% a 100%) e cor identificadora.
2. **Cálculo de Totalizadores:**
   * O valor do estágio é a soma aritmética simples dos deals ativos naquele estágio (`∑ deal.value`).
   * O valor ponderado da pipeline aplica o multiplicador de probabilidade do estágio.
3. **Regras de Movimentação no Kanban:**
   * Ao mover um negócio para estágios finais (Ganha / Perdida), o sistema exige o preenchimento opcional do motivo da perda ou data real de fechamento.
   * Efeito comemorativo (confetti) acionado via `confetti.browser.min.js` ao marcar negócio como ganho.

---

## 3. Contatos & Leads

1. **Campos Obrigatórios:** Nome e (Email ou Telefone).
2. **Associações Cruzadas:**
   * 1 Contato pode pertencer a 1 Empresa principal.
   * 1 Contato pode possuir N Negócios vinculados ao longo do tempo.
   * Histórico de Timeline unificado (ligações Twilio, e-mails disparados, notas internas, tarefas e visitas a landing pages).
3. **Scoring de Engajamento:**
   * Pontuação acumulativa incrementada por abertura de email, clique em link ou preenchimento de formulário.

---

## 4. Caixa de Entrada Multi-Canal (Omnichannel)

1. **Roteamento de Conversas:**
   * Conversas novas entram no status `novo/aberto` e podem ser distribuídas automaticamente para atendentes via Round-Robin por equipe (`operators`).
2. **Canais Suportados:**
   * WhatsApp Business API (provedores oficiais e parceiros).
   * Webchat / Widget embutível.
   * SMS transacional e promocional.
3. **Respostas Rápidas & Snippets:**
   * Suporte a macros e snippets (`/atalho`) para preenchimento de respostas frequentes com placeholders dinâmicos (`{nome}`, `{empresa}`).
