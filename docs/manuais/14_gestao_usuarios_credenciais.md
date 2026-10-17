# Manual da Rota: Central de Gestão de Usuários & Credenciais (`/#users`)

## 1. Objetivo da Rota
Prover o painel de governança exclusiva de acessos do Super Admin Único (`hevertoneduardoperes@gmail.com`, `is_superadmin = 1`). Permite cadastrar novos colaboradores associados a equipes e escopos da árvore RBAC (`SPEC_RBAC_DATA_SCOPING_HIERARQUICO.md`), gerenciar credenciais, ativar/suspender acessos e redefinir senhas mantendo a integridade criptográfica.

---

## 2. O Que o Usuário Consegue Realizar
* Consultar a lista completa de colaboradores com paginação dinâmica determinística (8 usuários por página).
* Filtrar colaboradores em tempo real por nome, e-mail institucional ou função/cargo.
* Acompanhar os KPIs da equipe: Total de Colaboradores, Usuários Ativos, Indicador do Super Admin Único e Regra de Segurança Inviolável.
* Cadastrar novo colaborador definindo: Nome, E-mail, Senha Provisória, Cargo/Papel (`role_id`), Equipe (`team_id`) e Escopo de Dados (`custom_data_scope`).
* Resetar a senha de qualquer colaborador (com modal de confirmação e exigência de nova senha segura).
* Ativar ou desativar o acesso de colaboradores com 1 clique (bloqueio imediato de autenticação na API).

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil | Acesso à Tela | Pode Criar Usuário | Pode Resetar Senhas | Pode Desativar Acessos |
|---|---|---|---|---|
| Colaboradores em Geral | Bloqueado (403 Proibido) | Não | Não | Não |
| Gerentes Regionais | Bloqueado (403 Proibido) | Não | Não | Não |
| Super Admin Único (Heverton) | Sim (Acesso Exclusivo) | Sim | Sim | Sim |

*Nota de Segurança Inviolável:* O Super Admin Heverton Eduardo Peres possui acesso máximo imutável (`is_superadmin = true`) e não pode ser desativado nem rebaixado no sistema por nenhuma operação de interface ou API.

---

## 4. Quais Ações Podem Ser Realizadas
* `SEARCH_USERS`: Busca instantânea nos campos de nome, e-mail e cargo via `handleUsersSearch`.
* `FILTER_ROLE`: Filtragem por cargo específico (Super Admin, Diretor, Gerente, Coordenador, Consultor).
* `CHANGE_PAGE`: Navegação de páginas (Anterior / Próxima) com recálculo determinístico de fatiamento.
* `CREATE_COLLABORATOR`: Modal de cadastro via `POST /api/v1/auth/users`.
* `RESET_USER_PASSWORD`: Redefinição de senha via `POST /api/v1/auth/users/{user_id}/reset-password`.
* `TOGGLE_USER_STATUS`: Ativação ou suspensão de conta via `POST /api/v1/auth/users/{user_id}/status`.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)

### Cadastro de um Novo Colaborador Comercial
1. Acesse **Gestão & Equipe > Gestão de Usuários** (apenas com sessão de Super Admin ativa).
2. Clique no botão "+ Novo Colaborador".
3. No formulário do modal, informe:
   * Nome Completo (ex: "Dr. Roberto Silveira").
   * E-mail Corporativo (ex: "roberto.silveira@revnaut.com").
   * Senha Inicial Segura.
   * Papel/Cargo e Equipe vinculada (`team_id`).
   * Escopo de Dados (padrão herdado do papel ou customizado).
4. Clique em "Cadastrar Colaborador".
5. O colaborador é inserido no SQLite WAL com senha criptografada em PBKDF2/bcrypt.

### Redefinição de Senha
1. Na lista de usuários, localize o colaborador desejado.
2. Clique no botão "Resetar Senha" na coluna de Ações.
3. No modal de reset, digite a nova senha provisória e confirme.
4. O hash criptográfico é atualizado imediatamente no banco de dados.

---

## 6. O Que Falta Implementar (Roadmap & Gaps)
* Envio automático da nova senha provisória por e-mail ou WhatsApp corporativo com solicitação de troca obrigatória no primeiro acesso.
* Registro de histórico de auditoria de quem redefiniu a senha e o timestamp exato da operação.
* Política de complexidade de senha configurável (mínimo de caracteres especiais, números e maiúsculas).

---

## ANOTAÇÕES DO HEVERTON

* **[INVARIANTE SUPER ADMIN]**: Apenas a conta `hevertoneduardoperes@gmail.com` possui a flag `is_superadmin = 1`. Tentativas de remover ou rebaixar este registro são abortadas no nível do banco e da API.
* **[VÍNCULO HIERÁRQUICO]**: Todo novo usuário recebe obrigatoriamente um vínculo de equipe (`team_id`), garantindo que seus negócios futuros caiam no escopo de seu gerente imediato.
