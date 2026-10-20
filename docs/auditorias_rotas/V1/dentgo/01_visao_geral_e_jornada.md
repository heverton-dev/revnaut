# 01. Visão Geral e Jornada do Usuário — Rota: dentgo

## 1. Identificação e Roteamento
- **Identificador / Slug:** `dentgo`
- **Título Visual no Sistema:** Entregas Expressas (Logística Same-Day 45min)
- **Classificação:** Frontend SPA View (Single Page Application com Hashbang Router)
- **URL de Produção:** `https://revnault.vpsconexao.org/#!/dentgo`
- **Componente React Raiz:** `frontend/src/features/dentgo/DentgoExpressCockpit.tsx`

---

## 2. Propósito e Objetivo de Negócio
A rota `dentgo` atua no ecossistema RevNault proporcionando aos operadores clínicos e comerciais:
1. Controle determinístico dos fluxos de entregas expressas (logística same-day 45min).
2. Redução do tempo de atendimento e eliminação de processos analógicos na operação.
3. Rastreabilidade ponta a ponta com persistência auditável no SQLite WAL.

---

## 3. Abas e Sub-rotas Mapeadas
- **Aba `cockpit`:** Cockpit Same-Day 45min & Hubs
- **Aba `radar`:** Mapa de Rota & Rastreamento
- **Aba `fefo_deals`:** Ofertas Flash FEFO (Vencimento Próximo)
- **Aba `split`:** Split Financeiro e Taxa de Entrega

---

## 4. Jornada e Fluxo Operacional
O usuário acessa `#!/dentgo`, o sistema valida as permissões de RBAC do perfil ativo e carrega os dados específicos da fatia vertical. O operador interage através dos controles dedicados sem recarregar a aplicação.
