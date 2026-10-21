# 01. Visão Geral e Jornada do Usuário — Rota: marketing (Auditoria V3)

## 1. Identificação Técnica
- **Rota Visual:** `https://revnault.vpsconexao.org/#!/marketing`
- **Título Oficial:** Campanhas e Indicações (Growth & Referral)
- **Componente Front-end:** `frontend/src/features/campaigns/LandingPageBuilder.tsx`
- **Motores Backend:** `src/features/campaigns/router.py`, `src/features/integrations/omnichannel/router.py`
- **Suíte de Testes:** `tests/test_landing_pages_grapesjs.py`, `tests/test_b2b_referral_mgm_loop.py`, `tests/test_listmonk_campaigns.py`

---

## 2. Jornada do Usuário Real
O usuário acessa o módulo para executar operações cirúrgicas e comerciais sem atrito:
1. **Entrada na Tela:** Carregamento otimizado com dados reais via SQLite WAL.
2. **Navegação por Abas:** Alternância fluida entre as visões do módulo.
3. **Ações Primárias:** Interação com botões de alta densidade sem stubs ou toasts vazios.

---

## 3. Abas e Sub-Rotas Mapeadas
- **Aba `analytics`:** Métricas de Mídia & ROAS
- **Aba `pages`:** Gestor de Landing Pages Publicadas
- **Aba `builder`:** Editor Visual Drag & Drop GrapesJS
- **Aba `referral_mgm`:** Loop de Indicação Membro-Gera-Membro