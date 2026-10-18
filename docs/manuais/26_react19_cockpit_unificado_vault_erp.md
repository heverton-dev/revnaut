# Manual da Rota: Cockpit Unificado React 19, Cofre AES-256 & Hub Fiscal ERP (`#settings`)

## 1. Objetivo da Rota / Sub-rota
Centralizar a governança do Cockpit Odontológico 360° (React 19 + TypeScript SPA), o Cofre de Credenciais cifradas em repouso (AES-256-GCM), o Hub Fiscal Windmill/ERP (CFOP 5.917, 1.918 e 5.113) e o despachante de Webhooks Outbound assinados com HMAC-SHA256.

---

## 2. O Que o Usuário Consegue Realizar
* Gerenciar chaves de integração (Evolution API v2, TOTVS Protheus, SAP B1, Sankhya, Documenso, LiveKit SIP) com criptografia simétrica autenticada AES-256-GCM.
* Auditar emissões fiscais de remessa em consignação (`5917`), retorno simbólico (`1918`) e faturamento de consumo cirúrgico (`5113`) com XML e DANFE PDF arquivados no Cloudflare R2.
* Configurar assinaturas de Webhooks Outbound com proteção Anti-SSRF e disjuntor automático (Circuit Breaker).
* Navegar pelas 17 rotas unificadas do SPA React 19 conectadas em tempo real ao FastAPI via TanStack Query v5.

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil de Usuário | Visualizar | Criar / Submeter | Disparar Testes | Configuração Avançada |
|---|---|---|---|---|
| Consultor de Campo (Field) | Não | Não | Não | Não |
| Analista Inside Sales | Leitura Parcial | Não | Não | Não |
| Diretor de BU | Leitura de Logs | Não | Sim | Leitura |
| Super Admin | Acesso Total | Sim | Sim | Sim (Total) |

---

## 4. Quais Ações Podem Ser Realizadas
* `CREATE_VAULT_CREDENTIAL`: Criptografa e armazena um novo segredo em `tenant_credentials`.
* `DELETE_VAULT_CREDENTIAL`: Revoga e remove credencial cifrada do tenant.
* `EMIT_ERP_NFE`: Dispara job no Windmill para emissão de NF-e de remessa ou faturamento com guarda no Cloudflare R2.
* `RESET_WEBHOOK_CIRCUIT`: Rearma o disjuntor de uma inscrição de webhook após normalização do endpoint de destino.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)
1. Acesse o menu lateral em **Governança & Inteligência** e selecione **Configurações & ERP** (`#settings`).
2. Clique em **Nova Credencial Cifrada** para abrir o modal do cofre seguro.
3. Selecione o serviço alvo (`evolution_api_v2`, `totvs_protheus`, `documenso_api`, `livekit_sip`) e informe o segredo em texto puro.
4. Clique em **Cifrar e Salvar** para gravar com AES-256-GCM e visualizar apenas os últimos 4 caracteres mascarados.

---

## 6. Catálogo Anatômico de Botões & Ações do DOM

| Rótulo do Botão / Elemento | Classe CSS | Evento (`onclick`) | Ação Operacional Realizada |
|---|---|---|---|
| `Nova Credencial Cifrada` | `bg-brand-primary text-text-inverse` | `setIsDialogOpen(true)` | Abre o modal de adição de segredo no cofre |
| `Cifrar e Salvar` | `bg-brand-primary` | `handleSave()` | Envia `POST /api/v1/auth/credentials` |
| `Atualizar` | `bg-surface-card border-border` | `fetchCredentials()` | Sincroniza lista via `GET /api/v1/auth/credentials` |
| `Excluir credencial` | `text-status-danger` | `handleDelete(id)` | Remove registro via `DELETE /api/v1/auth/credentials/{id}` |

---

## 7. Catálogo de Modais & Gavetas Operacionais
* **Modal Cadastrar Credencial no Cofre Cifrado**: Solicita `service_name`, `credential_type` e `secret_value`, aplicando derivação PBKDF2-HMAC-SHA256 antes da persistência.

---

## 8. Motores de Backend & Arquitetura Subjacente
* **Endpoints REST Vinculados**: `/api/v1/auth/credentials`, `/api/v1/integrations/erp/remittance/emit`, `/api/v1/integrations/erp/settlement/emit`, `/api/v1/webhooks/subscriptions`.
* **O Que o Motor Executa**: Derivação criptográfica AES-256-GCM, orquestração de jobs fiscais via Windmill, upload S3v4 no Cloudflare R2 e disparo assíncrono via Redis Streams (`XREADGROUP`).
* **O Que o Motor Não Executa**: Jamais retorna segredos descriptografados em respostas HTTP públicas.
* **Garantia de Resiliência**: Isolamento multi-tenant estrito e auditoria imutável.

---

## 9. O Que Falta Implementar & Plano de Micro-Tickets
* `[TICKET-41]` e `[TICKET-42]`: Concluídos integralmente com sincronização 1:1 de contratos e cobertura dos 14 Quality Gates AIDD.
