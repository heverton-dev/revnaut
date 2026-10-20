# 01. Visão Geral e Jornada do Usuário — Rota: dentgo (Auditoria v2)

## 1. Identificação e Roteamento
- **Identificador / Slug:** `dentgo`
- **Título Visual no Sistema:** Entregas Expressas Same-Day (DENTGO)
- **Classificação:** Frontend SPA View (Single Page Application com Hashbang Router)
- **URL Canônica:** `https://revnault.vpsconexao.org/#!/dentgo`
- **Componente React Raiz:** `frontend/src/features/dentgo/DentgoExpressCockpit.tsx`
- **Ciclo de Auditoria:** v2 (Pós-implementação de gaps e tickets de produção)

---

## 2. Propósito e Objetivo de Negócio
A rota `dentgo` atua no ecossistema RevNault proporcionando aos operadores clínicos e comerciais:
1. Controle determinístico dos fluxos de entregas expressas same-day (dentgo).
2. Redução do tempo de atendimento operacional e eliminação de processos analógicos em campo.
3. Rastreabilidade regulatória ponta a ponta com persistência auditável em SQLite WAL.

---

## 3. Abas e Sub-rotas Mapeadas
- **Aba / Sub-aba `cockpit`:** Cockpit Same-Day 45min & Status de Hubs
- **Aba / Sub-aba `radar`:** Mapa de Rota & Rastreamento em Tempo Real
- **Aba / Sub-aba `fefo_deals`:** Ofertas Flash FEFO (Vencimento Próximo)
- **Aba / Sub-aba `split`:** Split Financeiro e Taxa do Entregador

---

## 4. Jornada e Fluxo Operacional
O usuário autenticado acessa a rota `#!/dentgo`. O sistema valida os privilégios do papel ativo no RBAC e carrega os dados específicos da fatia vertical de backend de forma reativa. O operador interage através dos controles dedicados sem recarregar a aplicação.
