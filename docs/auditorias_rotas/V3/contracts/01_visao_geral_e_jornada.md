# 01. Visão Geral e Jornada do Usuário — Rota: contracts (Auditoria V3)

## 1. Identificação Técnica
- **Rota Visual:** `https://revnault.vpsconexao.org/#!/contracts`
- **Título Oficial:** Propostas e Contratos (Documenso & ANVISA)
- **Componente Front-end:** `frontend/src/features/contracts/ContractsDocumensoWorkspace.tsx`
- **Motores Backend:** `src/features/contracts/router.py`, `src/features/integrations/totvs/router.py`
- **Suíte de Testes:** `tests/test_documenso_contract_flow.py`, `tests/test_r2_storage.py`, `tests/test_catalog_pricing_approval.py`

---

## 2. Jornada do Usuário Real
O usuário acessa o módulo para executar operações cirúrgicas e comerciais sem atrito:
1. **Entrada na Tela:** Carregamento otimizado com dados reais via SQLite WAL.
2. **Navegação por Abas:** Alternância fluida entre as visões do módulo.
3. **Ações Primárias:** Interação com botões de alta densidade sem stubs ou toasts vazios.

---

## 3. Abas e Sub-Rotas Mapeadas
- **Aba `documenso_list`:** Contratos e Assinaturas Eletrônicas
- **Aba `anvisa_catalog`:** Catálogo Regulatório ANVISA e Lotes
- **Aba `r2_custody`:** Custódia Segura no Cloudflare R2