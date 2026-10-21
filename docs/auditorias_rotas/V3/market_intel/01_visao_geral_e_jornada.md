# 01. Visão Geral e Jornada do Usuário — Rota: market_intel (Auditoria V3)

## 1. Identificação Técnica
- **Rota Visual:** `https://revnault.vpsconexao.org/#!/market_intel`
- **Título Oficial:** Radar de Mercado & Concorrência
- **Componente Front-end:** `frontend/src/features/market_intel/MarketIntelRadarWorkspace.tsx`
- **Motores Backend:** `src/features/market_intel/router.py`, `src/features/intelligence/router.py`
- **Suíte de Testes:** `tests/test_market_intel_service.py`, `tests/test_market_intel_api.py`, `tests/test_market_intel_concurrency.py`

---

## 2. Jornada do Usuário Real
O usuário acessa o módulo para executar operações cirúrgicas e comerciais sem atrito:
1. **Entrada na Tela:** Carregamento otimizado com dados reais via SQLite WAL.
2. **Navegação por Abas:** Alternância fluida entre as visões do módulo.
3. **Ações Primárias:** Interação com botões de alta densidade sem stubs ou toasts vazios.

---

## 3. Abas e Sub-Rotas Mapeadas
- **Aba `signals`:** Sinais de Mercado
- **Aba `competitors`:** Concorrentes Mapeados
- **Aba `opportunities`:** Oportunidades x Business Units
- **Aba `campaigns`:** Disparos Estratégicos & Trava 15d