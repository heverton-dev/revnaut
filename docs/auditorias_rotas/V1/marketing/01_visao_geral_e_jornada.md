# 01. Visão Geral e Jornada do Usuário — Rota: marketing

## 1. Identificação e Roteamento
- **Identificador / Slug:** `marketing`
- **Título Visual no Sistema:** Campanhas e Indicações (Growth & Referral)
- **Classificação:** Frontend SPA View (Single Page Application com Hashbang Router)
- **URL de Produção:** `https://revnault.vpsconexao.org/#!/marketing`
- **Componente React Raiz:** `frontend/src/features/campaigns/LandingPageBuilder.tsx`

---

## 2. Propósito e Objetivo de Negócio
A rota `marketing` atua no ecossistema RevNault proporcionando aos operadores clínicos e comerciais:
1. Controle determinístico dos fluxos de campanhas e indicações (growth & referral).
2. Redução do tempo de atendimento e eliminação de processos analógicos na operação.
3. Rastreabilidade ponta a ponta com persistência auditável no SQLite WAL.

---

## 3. Abas e Sub-rotas Mapeadas
- **Aba `analytics`:** Métricas de Mídia & ROAS
- **Aba `pages`:** Gestor de Landing Pages Publicadas
- **Aba `builder`:** Editor Visual Drag & Drop GrapesJS
- **Aba `referral_mgm`:** Loop de Indicação Membro-Gera-Membro

---

## 4. Jornada e Fluxo Operacional
O usuário acessa `#!/marketing`, o sistema valida as permissões de RBAC do perfil ativo e carrega os dados específicos da fatia vertical. O operador interage através dos controles dedicados sem recarregar a aplicação.
