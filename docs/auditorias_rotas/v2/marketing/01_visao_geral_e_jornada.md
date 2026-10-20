# 01. Visão Geral e Jornada do Usuário — Rota: marketing (Auditoria v2)

## 1. Identificação e Roteamento
- **Identificador / Slug:** `marketing`
- **Título Visual no Sistema:** Campanhas e Indicações (Growth & Referral)
- **Classificação:** Frontend SPA View (Single Page Application com Hashbang Router)
- **URL Canônica:** `https://revnault.vpsconexao.org/#!/marketing`
- **Componente React Raiz:** `frontend/src/features/campaigns/LandingPageBuilder.tsx`
- **Ciclo de Auditoria:** v2 (Pós-implementação de gaps e tickets de produção)

---

## 2. Propósito e Objetivo de Negócio
A rota `marketing` atua no ecossistema RevOps proporcionando aos operadores clínicos e comerciais:
1. Controle determinístico dos fluxos de campanhas e indicações (growth & referral).
2. Redução do tempo de atendimento operacional e eliminação de processos analógicos em campo.
3. Rastreabilidade regulatória ponta a ponta com persistência auditável em SQLite WAL.

---

## 3. Abas e Sub-rotas Mapeadas
- **Aba / Sub-aba `analytics`:** Métricas de Mídia & ROAS
- **Aba / Sub-aba `pages`:** Gestor de Landing Pages Publicadas
- **Aba / Sub-aba `builder`:** Editor Visual Drag & Drop GrapesJS
- **Aba / Sub-aba `referral_mgm`:** Loop de Indicação Membro-Gera-Membro

---

## 4. Jornada e Fluxo Operacional
O usuário autenticado acessa a rota `#!/marketing`. O sistema valida os privilégios do papel ativo no RBAC e carrega os dados específicos da fatia vertical de backend de forma reativa. O operador interage através dos controles dedicados sem recarregar a aplicação.
