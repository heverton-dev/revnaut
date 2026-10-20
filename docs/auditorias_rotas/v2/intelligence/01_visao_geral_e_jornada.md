# 01. Visão Geral e Jornada do Usuário — Rota: intelligence (Auditoria v2)

## 1. Identificação e Roteamento
- **Identificador / Slug:** `intelligence`
- **Título Visual no Sistema:** Assistente Comercial & RAG Clínico
- **Classificação:** Frontend SPA View (Single Page Application com Hashbang Router)
- **URL Canônica:** `https://revnault.vpsconexao.org/#!/intelligence`
- **Componente React Raiz:** `frontend/src/features/intelligence/IntelligenceSuiteWorkspace.tsx`
- **Ciclo de Auditoria:** v2 (Pós-implementação de gaps e tickets de produção)

---

## 2. Propósito e Objetivo de Negócio
A rota `intelligence` atua no ecossistema RevOps proporcionando aos operadores clínicos e comerciais:
1. Controle determinístico dos fluxos de assistente comercial & rag clínico.
2. Redução do tempo de atendimento operacional e eliminação de processos analógicos em campo.
3. Rastreabilidade regulatória ponta a ponta com persistência auditável em SQLite WAL.

---

## 3. Abas e Sub-rotas Mapeadas
- **Aba / Sub-aba `churn`:** Radar Preditivo de Evasão RFM
- **Aba / Sub-aba `kol_graph`:** Topologia do Ecossistema Clínico e KOL
- **Aba / Sub-aba `rag_chat`:** Assistente RAG com Catálogo Técnico Cirúrgico

---

## 4. Jornada e Fluxo Operacional
O usuário autenticado acessa a rota `#!/intelligence`. O sistema valida os privilégios do papel ativo no RBAC e carrega os dados específicos da fatia vertical de backend de forma reativa. O operador interage através dos controles dedicados sem recarregar a aplicação.
