# 03. Motores de Backend e Subprodutização — Rota: dashboard (Auditoria v2)

## 1. Motores Subjacentes do Ecossistema
A rota conecta-se diretamente às seguintes fatias verticais do backend:
- **Fatia de Backend:** `src/features/deals/router.py`
- **Fatia de Backend:** `src/features/campaigns/router.py`
- **Fatia de Backend:** `src/features/intelligence/router.py`

---

## 2. Análise de Subprodutização do Motor (Capacidades Ociosas)

| Recurso / Capacidade do Motor | O Que o Backend Executa | O Que a Tela Consome Atualmente | Diagnóstico de Subprodutização & Potencial |
| :--- | :--- | :--- | :--- |
| **Agrupamento Multi-Moeda** | Recurso implementado no motor | Não exposto na interface do usuário | **Backend calcula taxas cambiais, mas tela exibe exclusivamente BRL** |
| **Projeção Preditiva Trimestral** | Recurso implementado no motor | Não exposto na interface do usuário | **Motor ARIMA/Regressão disponível no backend mas não exposto nos cards** |
