# 01. Visão Geral e Jornada do Usuário — Rota: dentgo (Auditoria V3)

## 1. Identificação Técnica
- **Rota Visual:** `https://revnault.vpsconexao.org/#!/dentgo`
- **Título Oficial:** Entregas Expressas Same-Day (DENTGO)
- **Componente Front-end:** `frontend/src/features/dentgo/DentgoExpressCockpit.tsx`
- **Motores Backend:** `src/features/dentgo/router.py`, `src/features/inventory/router.py`
- **Suíte de Testes:** `tests/test_dentgo_express_route.py`, `tests/test_dentgo_fefo_flash_deals.py`, `tests/test_dentgo_financial_split.py`

---

## 2. Jornada do Usuário Real
O usuário acessa o módulo para executar operações cirúrgicas e comerciais sem atrito:
1. **Entrada na Tela:** Carregamento otimizado com dados reais via SQLite WAL.
2. **Navegação por Abas:** Alternância fluida entre as visões do módulo.
3. **Ações Primárias:** Interação com botões de alta densidade sem stubs ou toasts vazios.

---

## 3. Abas e Sub-Rotas Mapeadas
- **Aba `orders`:** Despacho Rápido (45 min)
- **Aba `hubs`:** Busca de Estoque Mais Próximo
- **Aba `fefo`:** Ofertas de Lotes Próximos do Vencimento
- **Aba `split`:** Repasses e Custos de Entrega