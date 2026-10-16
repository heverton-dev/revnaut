# Status de Retomada — Próxima Sessão (Revnaut Dental Ops)

**Data do Ponto de Restauração:** 16/10/2026 10:05 BRT  
**ID da Conversa:** `f1bbcd99-64df-4a50-a2e8-1a221672f2dd`  
**Repositório GitHub:** `https://github.com/heverton-dev/revnaut` (Privado)  
**Ambiente Ativo:** Local Monolith / VPS Swarm (`https://revnaut.vpsconexao.org`)  
**Backend:** FastAPI + SQLite WAL (`data/revops.db` / `data/rvops.db`)  
**Frontend:** `docs/reconstruct_rvops/05_reconstructed_app/index.html` (Servido na raiz `/`)  
**Testes Automatizados:** 59/59 passaram com 100% de sucesso (`pytest -v`)  
**Quality Gates AIDD:** 12/12 gates aprovados em exit code 0 (`G_TESTES_REAIS`, `G_BLOQUEAR_SEGREDOS`, `G_CYBERSECURITY_OWASP`, `G_QUARTETO_SINE_QUA_NON`, `G_CONTRACTS`, `G_STACK_PADRAO_OURO`, `G_SAIDA_BINARIA`, `G_DETERMINISMO_LEI_1`, `G_ESTRUTURA_AST`, `G_HARNESS_COMPAT`, `G_INJECT`, `G_PERFORMANCE`)

---

## 1. O que foi Entregue e Homologado (RevOps Puro: CRM Odontológico, Autenticação, Metas & Comissões)

- [x] **Módulo de Autenticação, Tela de Login & Gestão de Sessão (100% Concluído):**
  - Fatia vertical modular `src/features/auth/` (`schemas.py`, `service.py`, `router.py`).
  - Endpoints canônicos: `POST /api/v1/auth/login`, `GET /api/v1/auth/me`, `POST /api/v1/auth/logout`.
  - Assinatura segura de sessão via HMAC-SHA256 (`Bearer Token`) e validação de hash determinístico de senhas.
  - Tela de Login com atalho de 1 clique: `⚡ Entrar com Super Admin (Heverton)`.
  - Botões explícitos no menu lateral (`.sidebar-nav`): "Alternar Credencial / Login" e "Sair da Sessão (Logout)".
  - Proteção proativa: se não autenticado, abre imediatamente a tela de login.

- [x] **Central de Gestão de Usuários & Credenciais (Backend & Frontend):**
  - Endpoints administrativos: `GET /api/v1/auth/users`, `POST /api/v1/auth/users`, `PUT /api/v1/auth/users/{user_id}/status`, `POST /api/v1/auth/users/{user_id}/reset-password`.
  - Invariante de Segurança Inviolável: Apenas `hevertoneduardoperes@gmail.com` é Super Admin (`is_superadmin = 1`). Novos colaboradores cadastrados têm `is_superadmin = 0` obrigatoriamente.
  - View `#users-view` completa no SPA com listagem de colaboradores, badges RBAC, métricas de status e modais `#modal-new-collaborator` e `#modal-reset-collaborator-password`.

- [x] **Importador Universal em Massa de Carteiras de Clientes Odontológicos (CSV / XLSX / JSON):**
  - Endpoint `POST /api/v1/contacts/import` com processamento em lote e sanitização.
  - Parsing de colunas odontológicas: `Nome`, `CRO`, `UF`, `Especialidade`, `Telefone`, `Clínica`, `Cidade/Estado`, `Volume Implantes/Mês`.
  - 3 Estratégias Determinísticas de Distribuição:
    1. *Territorial por UF:* Mapeia cirurgiões conforme estado/região da equipe comercial.
    2. *Por Especialidade Odontológica:* Direciona perfis cirúrgicos (Buco/Implante) para consultores técnicos.
    3. *Round-Robin Equilibrado:* Divisão equitativa 1-a-1 entre os consultores ativos da equipe.
  - Deduplicação determinística: atualização idempotente caso CRO + UF ou e-mail já existam na conta.
  - View `#import-contacts-view` com textarea CSV, botão para carregar dados demo reais, prévia dinâmica de dados e relatório de alocação por consultor.

- [x] **Motor de Lead Scoring ICP Odontológico & Tiers Customizáveis:**
  - Presets setoriais e recálculo dinâmico da base.

- [x] **Metas Top-Down & Comissionamento Hierárquico:**
  - Gestão de cotas com acelerador de supermeta e extrato consolidado.

- [x] **Suíte de Testes Automatizados:**
  - 59/59 testes reais passando com exit code 0 (`pytest -v`). Testes adicionados em `tests/test_auth.py` e `tests/test_contacts_import.py`.

---

## 2. O que Iniciar Imediatamente a Seguir

1. **Conector Plug & Play de ERP Odontológico (TOTVS Protheus Adapter):**
   - Módulo `src/features/integrations/totvs.py` para sincronização bidirecional de clientes e emissão de pedidos de venda (`SC5/SC6`).
2. **Construtor de Fluxos e Gatilhos de Receita:**
   - Automação de transbordo de leads Hot (Tier A) diretamente para os Closers regionais conforme o escopo de cada território.


---

## 3. Prompt de Retomada Rápida

Basta colar o comando abaixo na nova sessão:

```text
Continuar o projeto Revnaut Dental Ops a partir de docs/STATUS_RETOMADA_PROXIMA_SESSAO.md. O motor de Metas, Comissões Hierárquicas e Lead Scoring ICP Odontológico está 100% implementado e testado com 49 testes reais e 12 Quality Gates aprovados. Sincronizar em produção no VPS Swarm ou avançar nos gatilhos automáticos de transbordo para Closers.
```
