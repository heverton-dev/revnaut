# 01. Visão Geral e Jornada do Usuário — Rota: intelligence

## 1. Identificação e Roteamento
- **Identificador / Slug:** `intelligence`
- **Título Visual no Sistema:** Assistente Comercial & Inteligência de Carteira
- **Classificação:** Frontend SPA View (Single Page Application com Hashbang Router)
- **URL de Produção:** `https://revnault.vpsconexao.org/#!/intelligence`
- **Componente React Raiz:** `frontend/src/features/intelligence/IntelligenceSuiteWorkspace.tsx`

---

## 2. Propósito e Objetivo de Negócio
A rota `intelligence` atua no ecossistema RevNault proporcionando aos operadores clínicos e comerciais:
1. Controle determinístico dos fluxos de assistente comercial & inteligência de carteira.
2. Redução do tempo de atendimento e eliminação de processos analógicos na operação.
3. Rastreabilidade ponta a ponta com persistência auditável no SQLite WAL.

---

## 3. Abas e Sub-rotas Mapeadas
- **Aba `churn`:** Radar Preditivo de Evasão RFM
- **Aba `kol_graph`:** Topologia do Ecossistema Clínico KOL
- **Aba `rag_chat`:** Assistente RAG com Catálogo Técnico Cirúrgico

---

## 4. Jornada e Fluxo Operacional
O usuário acessa `#!/intelligence`, o sistema valida as permissões de RBAC do perfil ativo e carrega os dados específicos da fatia vertical. O operador interage através dos controles dedicados sem recarregar a aplicação.
