# 01. Visão Geral e Jornada do Usuário — Rota: scoring (Auditoria V3)

## 1. Identificação Técnica
- **Rota Visual:** `https://revnault.vpsconexao.org/#!/scoring`
- **Título Oficial:** Qualificação de Clientes (ICP Scoring)
- **Componente Front-end:** `frontend/src/features/scoring/IcpScoringDashboard.tsx`
- **Motores Backend:** `src/features/scoring/router.py`, `src/features/intelligence/router.py`
- **Suíte de Testes:** `tests/test_lead_scoring_handoff.py`, `tests/test_lead_scoring_auto_handoff.py`

---

## 2. Jornada do Usuário Real
O usuário acessa o módulo para executar operações cirúrgicas e comerciais sem atrito:
1. **Entrada na Tela:** Carregamento otimizado com dados reais via SQLite WAL.
2. **Navegação por Abas:** Alternância fluida entre as visões do módulo.
3. **Ações Primárias:** Interação com botões de alta densidade sem stubs ou toasts vazios.

---

## 3. Abas e Sub-Rotas Mapeadas
- **Aba `overview`:** Score Geral da Carteira
- **Aba `matrix`:** Matriz ICP Odontológico
- **Aba `rules`:** Critérios e Pesos de Enquadramento