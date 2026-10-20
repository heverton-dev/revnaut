# 03. Motores de Backend e Subprodutização — Rota: deals (Auditoria v2)

## 1. Motores Subjacentes do Ecossistema
A rota conecta-se diretamente às seguintes fatias verticais do backend:
- **Fatia de Backend:** `src/features/deals/router.py`
- **Fatia de Backend:** `src/features/pipelines/router.py`
- **Fatia de Backend:** `src/features/contracts/router.py`

---

## 2. Análise de Subprodutização do Motor (Capacidades Ociosas)

| Recurso / Capacidade do Motor | O Que o Backend Executa | O Que a Tela Consome Atualmente | Diagnóstico de Subprodutização & Potencial |
| :--- | :--- | :--- | :--- |
| **Histórico de Mudança de Probabilidade** | Recurso implementado no motor | Não exposto na interface do usuário | **Backend armazena log temporal de probabilidades, tela mostra só atual** |
| **Múltiplos Contatos por Negócio** | Recurso implementado no motor | Não exposto na interface do usuário | **Banco suporta múltiplos decisores N:N, UI foca no cirurgião primário** |
