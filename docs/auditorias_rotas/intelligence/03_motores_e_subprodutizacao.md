# 03. Motores de Backend e Subprodutização — Rota: intelligence

## 1. Motores Subjacentes do Ecossistema
A rota conecta-se diretamente às seguintes fatias verticais do backend:
- **Fatia de Backend:** `src/features/intelligence/router.py`

---

## 2. Análise de Subprodutização do Motor (Capacidades Ociosas)

| Recurso / Capacidade do Motor | O Que o Backend Executa | O Que a Tela Consome Atualmente | Diagnóstico de Subprodutização & Potencial |
| :--- | :--- | :--- | :--- |
| **Embeddings no pgvector** | Recurso implementado no motor | Não exposto na interface do usuário | **Base vetorial de manuais indexada mas sem visualização de fontes citadas** |
| **Score de Afinidade Cirúrgica** | Recurso implementado no motor | Não exposto na interface do usuário | **Cálculo de probabilidade de adoção de novo implante não exposto na UI** |
