# 01. Visão Geral e Jornada do Usuário — Rota: contacts (Auditoria V3)

## 1. Identificação Técnica
- **Rota Visual:** `https://revnault.vpsconexao.org/#!/contacts`
- **Título Oficial:** Dentistas e Clínicas (CRM Cirúrgico)
- **Componente Front-end:** `frontend/src/features/contacts/ContactsCrmWorkspace.tsx`
- **Motores Backend:** `src/features/contacts/router.py`, `src/features/institutions/router.py`
- **Suíte de Testes:** `tests/test_cro_cfo_compliance.py`, `tests/test_contacts_import.py`, `tests/test_contact_profile_timeline.py`

---

## 2. Jornada do Usuário Real
O usuário acessa o módulo para executar operações cirúrgicas e comerciais sem atrito:
1. **Entrada na Tela:** Carregamento otimizado com dados reais via SQLite WAL.
2. **Navegação por Abas:** Alternância fluida entre as visões do módulo.
3. **Ações Primárias:** Interação com botões de alta densidade sem stubs ou toasts vazios.

---

## 3. Abas e Sub-Rotas Mapeadas
- **Aba `crm_surgeons`:** Cirurgiões Dentistas Cadastrados
- **Aba `institutions`:** Clínicas, Hospitais e Polos
- **Aba `cfo_compliance`:** Validação de Registro CFO / CRO Ativo
- **Aba `icp_scoring`:** Qualificação e Enriquecimento ICP