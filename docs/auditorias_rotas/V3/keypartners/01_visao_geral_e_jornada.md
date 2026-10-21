# 01. Visão Geral e Jornada do Usuário — Rota: keypartners (Auditoria V3)

## 1. Identificação Técnica
- **Rota Visual:** `https://revnault.vpsconexao.org/#!/keypartners`
- **Título Oficial:** Malas em Consignação & KOL (KeyPartners)
- **Componente Front-end:** `frontend/src/features/keypartners/ConsignmentSurgicalBoard.tsx`
- **Motores Backend:** `src/features/keypartners/router.py`, `src/features/integrations/totvs/router.py`
- **Suíte de Testes:** `tests/test_erp_consignment_cfop_flow.py`, `tests/test_keypartners_dispatch_custody_route.py`, `tests/test_keypartners_kol_contracts.py`

---

## 2. Jornada do Usuário Real
O usuário acessa o módulo para executar operações cirúrgicas e comerciais sem atrito:
1. **Entrada na Tela:** Carregamento otimizado com dados reais via SQLite WAL.
2. **Navegação por Abas:** Alternância fluida entre as visões do módulo.
3. **Ações Primárias:** Interação com botões de alta densidade sem stubs ou toasts vazios.

---

## 3. Abas e Sub-Rotas Mapeadas
- **Aba `board`:** Quadro Cirúrgico 4 Estágios
- **Aba `agreements`:** Acordos & Maletas ANVISA
- **Aba `kol`:** Contratos de Parceria KOL & Speakers
- **Aba `loyalty`:** Programa de Fidelidade e Moeda Cirúrgica