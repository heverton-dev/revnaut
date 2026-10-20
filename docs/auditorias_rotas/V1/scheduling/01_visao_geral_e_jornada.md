# 01. Visão Geral e Jornada do Usuário — Rota: scheduling

## 1. Identificação e Roteamento
- **Identificador / Slug:** `scheduling`
- **Título Visual no Sistema:** Retorno de Pacientes & Agendamentos
- **Classificação:** Frontend SPA View (Single Page Application com Hashbang Router)
- **URL de Produção:** `https://revnault.vpsconexao.org/#!/scheduling`
- **Componente React Raiz:** `frontend/src/features/scheduling/CalcomReactivationWorkspace.tsx`

---

## 2. Propósito e Objetivo de Negócio
A rota `scheduling` atua no ecossistema RevNault proporcionando aos operadores clínicos e comerciais:
1. Controle determinístico dos fluxos de retorno de pacientes & agendamentos.
2. Redução do tempo de atendimento e eliminação de processos analógicos na operação.
3. Rastreabilidade ponta a ponta com persistência auditável no SQLite WAL.

---

## 3. Abas e Sub-rotas Mapeadas
- **Aba `campaigns`:** Campanhas de Reativação Cal.com
- **Aba `appointments`:** Agenda de Consultas Confirmadas
- **Aba `templates`:** Modelos de Mensagens WhatsApp / SMS

---

## 4. Jornada e Fluxo Operacional
O usuário acessa `#!/scheduling`, o sistema valida as permissões de RBAC do perfil ativo e carrega os dados específicos da fatia vertical. O operador interage através dos controles dedicados sem recarregar a aplicação.
