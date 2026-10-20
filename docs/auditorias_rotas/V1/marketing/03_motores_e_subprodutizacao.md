# 03. Motores de Backend e Subprodutização — Rota: marketing

## 1. Motores Subjacentes do Ecossistema
A rota conecta-se diretamente às seguintes fatias verticais do backend:
- **Fatia de Backend:** `src/features/campaigns/router.py`
- **Fatia de Backend:** `src/features/integrations/omnichannel/router.py`

---

## 2. Análise de Subprodutização do Motor (Capacidades Ociosas)

| Recurso / Capacidade do Motor | O Que o Backend Executa | O Que a Tela Consome Atualmente | Diagnóstico de Subprodutização & Potencial |
| :--- | :--- | :--- | :--- |
| **Disparo de E-mail via Listmonk** | Recurso implementado no motor | Não exposto na interface do usuário | **Motor de e-mail marketing conectado mas sem disparador manual na UI** |
| **Pixel e Tags Customizadas** | Recurso implementado no motor | Não exposto na interface do usuário | **Campos de GTM/Meta Pixel existem no schema mas não no formulário básico** |
