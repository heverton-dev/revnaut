# 01. Visão Geral e Jornada do Usuário — Rota: dashboard (Auditoria v2)

## 1. Identificação e Roteamento
- **Identificador / Slug:** `dashboard`
- **Título Visual no Sistema:** Visão do Dia (Cockpit Executivo)
- **Classificação:** Frontend SPA View (Single Page Application com Hashbang Router)
- **URL Canônica:** `https://revnault.vpsconexao.org/#!/dashboard`
- **Componente React Raiz:** `frontend/src/features/dashboard/ExecutiveCockpitView.tsx`
- **Ciclo de Auditoria:** v2 (Pós-implementação de gaps e tickets de produção)

---

## 2. Propósito e Objetivo de Negócio
A rota `dashboard` atua no ecossistema RevNault proporcionando aos operadores clínicos e comerciais:
1. Controle determinístico dos fluxos de visão do dia (cockpit executivo).
2. Redução do tempo de atendimento operacional e eliminação de processos analógicos em campo.
3. Rastreabilidade regulatória ponta a ponta com persistência auditável em SQLite WAL.

---

## 3. Abas e Sub-rotas Mapeadas
- **Aba / Sub-aba `stage`:** Funil de Receita Comercial por Estágio
- **Aba / Sub-aba `trend`:** Série Temporal de MRR e Tendência
- **Aba / Sub-aba `consignment`:** Giro de Maletas e Faturamento CFOP 5.113
- **Aba / Sub-aba `churn_radar`:** Radar Anti-Churn RFM Preditivo
- **Aba / Sub-aba `kol_graph`:** Ecossistema Clínico e Topologia KOL

---

## 4. Jornada e Fluxo Operacional
O usuário autenticado acessa a rota `#!/dashboard`. O sistema valida os privilégios do papel ativo no RBAC e carrega os dados específicos da fatia vertical de backend de forma reativa. O operador interage através dos controles dedicados sem recarregar a aplicação.
