# Manual da Rota: Autenticação & Login (`/#login`)

## 1. Objetivo da Rota
Centralizar o controle de acesso seguro à plataforma Revnaut Dental, autenticando colaboradores e o Super Admin através de credenciais criptografadas (PBKDF2-HMAC-SHA256) e emitindo tokens de sessão assinados via HMAC-SHA256. Quando desautenticado ou após logout, a rota isola completamente a aplicação, ocultando dados comerciais e barras de navegação.

---

## 2. O Que o Usuário Consegue Realizar
* Autenticar-se no sistema com e-mail corporativo e senha cadastrada.
* Visualizar ou ocultar os caracteres da senha durante a digitação.
* Executar preenchimento automatizado de credenciais de teste para o Super Admin corporativo (Heverton Eduardo Peres).
* Receber feedback visual instantâneo em caso de falha de autenticação (e-mail inexistente, senha incorreta ou usuário inativo).
* Ser redirecionado imediatamente para o ambiente autenticado (`/#deals`) após a validação.

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil | Acesso à Tela | Pode Autenticar | Observação |
|---|---|---|---|
| Público / Anônimo | Sim | Sim (se tiver cadastro ativo) | Tela pública padrão de entrada |
| Consultor de Vendas | Sim | Sim | Visualiza dados do seu próprio escopo após login |
| Coordenador / Gerente | Sim | Sim | Visualiza dados da sua regional após login |
| Diretor Regional | Sim | Sim | Visualiza dados da sua Business Unit após login |
| Super Admin (User God) | Sim | Sim | Acesso total irrestrito a todos os tenants e dados |

---

## 4. Quais Ações Podem Ser Realizadas
* `SUBMIT_LOGIN`: Envio do formulário com e-mail e senha para validação em `/api/v1/auth/login`.
* `FAST_FILL_SUPERADMIN`: Preenchimento com 1 clique das credenciais oficiais do Super Admin.
* `TOGGLE_PASSWORD_VISIBILITY`: Alternância entre tipo password e texto puro no campo de senha.
* `REDIRECT_LOGOUT`: Redirecionamento forçado para esta rota quando qualquer sessão for finalizada no sistema.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)

### Autenticação Padrão
1. Acesse o endereço da aplicação no navegador (`https://revnaut.vpsconexao.org/#login`).
2. Digite o e-mail cadastrado no campo "E-mail Corporativo".
3. Digite a senha no campo "Senha de Acesso" (clique em "Mostrar Senha" se desejar conferir os caracteres).
4. Clique no botão "Entrar no Revnaut Dental".
5. O sistema valida as credenciais via API. Em caso de sucesso, armazena o token de sessão no navegador e carrega a tela principal de Vendas & Funis.

### Acesso Rápido para Validação e Testes
1. Na tela de login, clique no botão "Preencher Super Admin (Heverton)".
2. Os campos serão automaticamente preenchidos com `hevertoneduardoperes@gmail.com` e a credencial protegida.
3. Clique em "Entrar no Revnaut Dental".

### Fluxo de Encerramento (Logout)
1. Estando logado, clique no botão de deslogar no rodapé do menu lateral.
2. O sistema remove os tokens locais, revoga o token no backend e redireciona a interface automaticamente para `/#login`.

---

## 6. O Que Falta Implementar (Roadmap & Gaps)
* Autenticação de dois fatores (2FA / TOTP) via aplicativo autenticador.
* Fluxo de auto-recuperação de senha ("Esqueci minha senha") via envio de link temporário com token JWT por e-mail ou WhatsApp.
* Bloqueio temporário por rate-limiting após 5 tentativas consecutivas incorretas (proteção contra força bruta).
* Suporte a Single Sign-On (SSO) corporativo via OpenID Connect (Google Workspace / Microsoft Azure AD).
