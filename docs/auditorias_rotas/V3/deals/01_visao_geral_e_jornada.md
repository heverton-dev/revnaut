# 01. Visão Geral e Jornada do Usuário — Rota: deals (Auditoria V3)

## 1. Identificação Técnica
- **Rota Visual:** `https://revnault.vpsconexao.org/#!/deals`
- **Título Oficial:** Negociações & Funil Comercial (CRM Cirúrgico)
- **Componente Front-end:** `frontend/src/features/deals/DealsWorkspace.tsx`
- **Motores Backend:** `src/features/deals/router.py`, `src/features/pipelines/router.py`, `src/features/contracts/router.py`
- **Suíte de Testes:** `tests/test_deals_advanced_features.py`, `tests/test_deals_contacts_scoping.py`, `tests/test_granola_copilot_zerotouch.py`

---

## 2. Jornada do Usuário Real
O usuário acessa o módulo para executar operações cirúrgicas e comerciais sem atrito:
1. **Entrada na Tela:** Carregamento otimizado com dados reais via SQLite WAL.
2. **Navegação por Abas:** Alternância fluida entre as visões do módulo.
3. **Ações Primárias:** Interação com botões de alta densidade sem stubs ou toasts vazios.

---

## 3. Abas e Sub-Rotas Mapeadas
- **Aba `kanban`:** Quadro Kanban Interativo Drag-and-Drop
- **Aba `table`:** Visão Tabela Densa e Paginada
- **Aba `stage_qualificacao`:** Estágio: Qualificação Técnica
- **Aba `stage_diagnostico_3d`:** Estágio: Diagnóstico 3D Tomográfico
- **Aba `stage_proposta`:** Estágio: Proposta Comercial
- **Aba `stage_contrato`:** Estágio: Minuta e Assinatura de Contrato
- **Aba `stage_fechado_ganho`:** Estágio: Negócio Fechado Ganho (MRR)