# 03. Motores de Backend e Subprodutização — Rota: rbac (Auditoria v2)

## 1. Motores Subjacentes do Ecossistema
A rota conecta-se diretamente às seguintes fatias verticais do backend:
- **Fatia de Backend:** `src/features/rbac/router.py`
- **Fatia de Backend:** `src/features/hierarchy/router.py`

---

## 2. Análise de Subprodutização do Motor (Capacidades Ociosas)

| Recurso / Capacidade do Motor | O Que o Backend Executa | O Que a Tela Consome Atualmente | Diagnóstico de Subprodutização & Potencial |
| :--- | :--- | :--- | :--- |
| **Herança Recursiva de Permissões** | Recurso implementado no motor | Não exposto na interface do usuário | **Backend resolve permissões em cascata N-níveis, UI exibe tabela estática** |
| **Split de Comissão Entre Vendedores** | Recurso implementado no motor | Não exposto na interface do usuário | **Cálculo suporta divisão da comissão em vendas conjuntas, tela usa 1 recebedor** |
