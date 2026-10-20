# 03. Motores de Backend e Subprodutização — Rota: scoring (Auditoria v2)

## 1. Motores Subjacentes do Ecossistema
A rota conecta-se diretamente às seguintes fatias verticais do backend:
- **Fatia de Backend:** `src/features/scoring/router.py`
- **Fatia de Backend:** `src/features/intelligence/router.py`

---

## 2. Análise de Subprodutização do Motor (Capacidades Ociosas)

| Recurso / Capacidade do Motor | O Que o Backend Executa | O Que a Tela Consome Atualmente | Diagnóstico de Subprodutização & Potencial |
| :--- | :--- | :--- | :--- |
| **Regras Dinâmicas de ICP** | Recurso implementado no motor | Não exposto na interface do usuário | **Motor permite expressões aritméticas customizadas, UI usa fórmula fixa** |
| **Previsão de Ticket Anual** | Recurso implementado no motor | Não exposto na interface do usuário | **Backend estima faturamento potencial baseado em cadeiras, tela omite** |
