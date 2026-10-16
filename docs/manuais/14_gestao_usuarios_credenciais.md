# Manual da Rota: Central de Gestão de Usuários & Credenciais (`/#users`)

## 1. Objetivo da Rota
Prover o painel de governança exclusiva de acessos do Super Admin (User God - Heverton Eduardo Peres). Permite cadastrar novos colaboradores com papéis e equipes bem definidos, ativar/desativar acessos e realizar o reset seguro de senhas mantendo a integridade criptográfica das credenciais corporativas.

---

## 2. O Que o Usuário Consegue Realizar
* Consultar a lista completa de colaboradores com paginação dinâmica determinística (8 usuários por página).
* Filtrar colaboradores em tempo real por nome, e-mail institucional ou função/cargo.
* Acompanhar os KPIs da equipe: Total de Colaboradores, Usuários Ativos, Indicador do Super Admin Único e Regra de Segurança Inviolável.
* Cadastrar novo colaborador definindo: Nome, E-mail, Senha Provisória, Cargo/Papel e Unidade/Equipe.
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
3. No modal que abrir, informe:
   * Nome Completo (ex: "Dr. Roberto Silveira").
   * E-mail Corporativo (ex: "roberto.silveira@revnaut.com").
   * Senha Inicial Segura.
   * Cargo (ex: "Consultor de Vendas").
   * Telefone / WhatsApp.
4. Clique em "Cadastrar Colaborador".
5. O novo colaborador é inserido no SQLite, a senha é criptografada e ele já poderá se autenticar.

### Redefinição de Senha de um Colaborador
1. Na lista de usuários, localize o colaborador desejado (utilize a barra de busca se necessário).
2. Clique no botão "Resetar Senha" na coluna de Ações.
3. No modal de reset, digite a nova senha provisória e confirme.
4. Clique em "Confirmar Nova Senha".
5. O hash criptográfico é atualizado imediatamente no banco e o colaborador poderá acessar com a nova credencial.

### Navegação de Páginas da Lista
1. Utilize os botões "Anterior" e "Próximo" localizados no rodapé da tabela.
2. O contador informa a faixa atual exibida (ex: "Mostrando 1-8 de 14 colaboradores").

---

## 6. O Que Falta Implementar (Roadmap & Gaps)
* Envio automático da nova senha provisória por e-mail ou WhatsApp corporativo com solicitação de troca obrigatória no primeiro acesso.
* Registro de histórico de auditoria de quem redefiniu a senha e o timestamp exato da operação.
* Política de complexidade de senha configurável (mínimo de caracteres especiais, números e maiúsculas).

---

## ANOTAÇÕES DO HEVERTON

