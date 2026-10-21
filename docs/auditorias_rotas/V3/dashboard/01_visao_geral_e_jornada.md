# 01. Visão Geral e Jornada do Usuário — Rota: dashboard (Auditoria V3)

## 1. Identificação Técnica
- **Rota Visual:** `https://revnault.vpsconexao.org/#!/dashboard`
- **Título Oficial:** Visão do Dia (Cockpit Executivo)
- **Componente Front-end:** `frontend/src/features/dashboard/ExecutiveCockpitView.tsx`
- **Motores Backend:** `src/features/deals/router.py`, `src/features/campaigns/router.py`, `src/features/intelligence/router.py`
- **Suíte de Testes:** `tests/test_predictive_sok_pr_math.py`, `tests/test_clinical_graph_churn.py`, `tests/test_revenue_triggers.py`

---

## 2. Jornada do Usuário Real
O usuário acessa o módulo para executar operações cirúrgicas e comerciais sem atrito:
1. **Entrada na Tela:** Carregamento otimizado com dados reais via SQLite WAL.
2. **Navegação por Abas:** Alternância fluida entre as visões do módulo.
3. **Ações Primárias:** Interação com botões de alta densidade sem stubs ou toasts vazios.

---

## 3. Abas e Sub-Rotas Mapeadas
- **Aba `stage`:** Funil de Receita Comercial por Estágio
- **Aba `trend`:** Série Temporal de MRR e Tendência
- **Aba `consignment`:** Giro de Maletas e Faturamento CFOP 5.113
- **Aba `churn_radar`:** Radar Anti-Churn RFM Preditivo
- **Aba `kol_graph`:** Ecossistema Clínico e Topologia KOL