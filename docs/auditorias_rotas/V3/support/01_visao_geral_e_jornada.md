# 01. Visão Geral e Jornada do Usuário — Rota: support (Auditoria V3)

## 1. Identificação Técnica
- **Rota Visual:** `https://revnault.vpsconexao.org/#!/support`
- **Título Oficial:** Suporte Clínico, RMA & Tecnovigilância ANVISA
- **Componente Front-end:** `frontend/src/features/support/SupportAnvisaWorkspace.tsx`
- **Motores Backend:** `src/features/support/router.py`, `src/features/integrations/omnichannel/router.py`
- **Suíte de Testes:** `tests/test_anvisa_technovigilance_rma.py`, `tests/test_postop_patient_care_b2c.py`

---

## 2. Jornada do Usuário Real
O usuário acessa o módulo para executar operações cirúrgicas e comerciais sem atrito:
1. **Entrada na Tela:** Carregamento otimizado com dados reais via SQLite WAL.
2. **Navegação por Abas:** Alternância fluida entre as visões do módulo.
3. **Ações Primárias:** Interação com botões de alta densidade sem stubs ou toasts vazios.

---

## 3. Abas e Sub-Rotas Mapeadas
- **Aba `anvisa_rma`:** Quarentena & Laudos de Tecnovigilância ANVISA
- **Aba `surgical_sos`:** Chamados de Emergência SOS Cirurgia
- **Aba `postop_b2c`:** Acompanhamento Pós-Operatório do Paciente