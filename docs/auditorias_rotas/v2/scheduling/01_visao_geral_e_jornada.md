# 01. Visão Geral e Jornada do Usuário — Rota: scheduling (Auditoria v2)

## 1. Identificação e Roteamento
- **Identificador / Slug:** `scheduling`
- **Título Visual no Sistema:** Reativação de Pacientes (Cal.com)
- **Classificação:** Frontend SPA View (Single Page Application com Hashbang Router)
- **URL Canônica:** `https://revnault.vpsconexao.org/#!/scheduling`
- **Componente React Raiz:** `frontend/src/features/scheduling/CalcomReactivationWorkspace.tsx`
- **Ciclo de Auditoria:** v2 (Pós-implementação de gaps e tickets de produção)

---

## 2. Propósito e Objetivo de Negócio
A rota `scheduling` atua no ecossistema RevNault proporcionando aos operadores clínicos e comerciais:
1. Controle determinístico dos fluxos de reativação de pacientes (cal.com).
2. Redução do tempo de atendimento operacional e eliminação de processos analógicos em campo.
3. Rastreabilidade regulatória ponta a ponta com persistência auditável em SQLite WAL.

---

## 3. Abas e Sub-rotas Mapeadas
- **Aba / Sub-aba `campaigns`:** Campanhas de Reativação Cal.com
- **Aba / Sub-aba `appointments`:** Agenda de Consultas Confirmadas
- **Aba / Sub-aba `templates`:** Modelos de Mensagens WhatsApp / SMS

---

## 4. Jornada e Fluxo Operacional
O usuário autenticado acessa a rota `#!/scheduling`. O sistema valida os privilégios do papel ativo no RBAC e carrega os dados específicos da fatia vertical de backend de forma reativa. O operador interage através dos controles dedicados sem recarregar a aplicação.
