# 03. Motores de Backend e Subprodutização — Rota: support (Auditoria v2)

## 1. Motores Subjacentes do Ecossistema
A rota conecta-se diretamente às seguintes fatias verticais do backend:
- **Fatia de Backend:** `src/features/support/router.py`
- **Fatia de Backend:** `src/features/integrations/omnichannel/router.py`

---

## 2. Análise de Subprodutização do Motor (Capacidades Ociosas)

| Recurso / Capacidade do Motor | O Que o Backend Executa | O Que a Tela Consome Atualmente | Diagnóstico de Subprodutização & Potencial |
| :--- | :--- | :--- | :--- |
| **Integração Notivisa ANVISA** | Recurso implementado no motor | Não exposto na interface do usuário | **Backend possui schema compatível com Notivisa, tela gera PDF manual** |
| **Painel de Taxa de Falha por Linha de Implante** | Recurso implementado no motor | Não exposto na interface do usuário | **Agrupamento estatístico existe no banco mas não na UI** |
