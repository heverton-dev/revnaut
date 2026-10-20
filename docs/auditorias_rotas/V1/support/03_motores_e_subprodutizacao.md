# 03. Motores de Backend e Subprodutização — Rota: support

## 1. Motores Subjacentes do Ecossistema
A rota conecta-se diretamente às seguintes fatias verticais do backend:
- **Fatia de Backend:** `src/features/tickets/router.py`
- **Fatia de Backend:** `src/features/tasks/router.py`

---

## 2. Análise de Subprodutização do Motor (Capacidades Ociosas)

| Recurso / Capacidade do Motor | O Que o Backend Executa | O Que a Tela Consome Atualmente | Diagnóstico de Subprodutização & Potencial |
| :--- | :--- | :--- | :--- |
| **Controle de Lote em Quarentena** | Recurso implementado no motor | Não exposto na interface do usuário | **Backend bloqueia faturamento de lote em RMA, mas UI não alerta na hora da venda** |
| **Protocolo Automático de Dor Pós-Op** | Recurso implementado no motor | Não exposto na interface do usuário | **Algoritmo classifica paciente febril em risco, mas sem push notification** |
