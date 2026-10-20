# 03. Motores de Backend e Subprodutização — Rota: analytics (Auditoria v2)

## 1. Motores Subjacentes do Ecossistema
A rota conecta-se diretamente às seguintes fatias verticais do backend:
- **Fatia de Backend:** `src/features/analytics/router.py`
- **Fatia de Backend:** `src/features/bi/router.py`

---

## 2. Análise de Subprodutização do Motor (Capacidades Ociosas)

| Recurso / Capacidade do Motor | O Que o Backend Executa | O Que a Tela Consome Atualmente | Diagnóstico de Subprodutização & Potencial |
| :--- | :--- | :--- | :--- |
| **Validação de AST para INSERT/DELETE** | Recurso implementado no motor | Não exposto na interface do usuário | **Parser bloqueia mutações, backend suporta explain query plan** |
| **Cache de Resultados Text-to-SQL** | Recurso implementado no motor | Não exposto na interface do usuário | **Armazenamento em cache Redis implementado mas não exposto na UI** |
