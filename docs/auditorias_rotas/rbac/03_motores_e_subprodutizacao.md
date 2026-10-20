# 03. Motores de Backend e Subprodutização — Rota: rbac

## 1. Motores Subjacentes do Ecossistema
A rota conecta-se diretamente às seguintes fatias verticais do backend:
- **Fatia de Backend:** `src/features/hierarchy/router.py`
- **Fatia de Backend:** `src/features/auth/router.py`

---

## 2. Análise de Subprodutização do Motor (Capacidades Ociosas)

| Recurso / Capacidade do Motor | O Que o Backend Executa | O Que a Tela Consome Atualmente | Diagnóstico de Subprodutização & Potencial |
| :--- | :--- | :--- | :--- |
| **Comissão Diferenciada por Linha de Produto** | Recurso implementado no motor | Não exposto na interface do usuário | **Backend calcula margem maior para implantes premium, UI usa alíquota linear** |
| **Multi-território Compartilhado** | Recurso implementado no motor | Não exposto na interface do usuário | **Estrutura suporta consultor atendendo 2 regionais, mas UI vincula a 1 nó** |
