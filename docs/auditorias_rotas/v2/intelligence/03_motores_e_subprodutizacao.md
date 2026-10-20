# 03. Motores de Backend e Subprodutização — Rota: intelligence (Auditoria v2)

## 1. Motores Subjacentes do Ecossistema
A rota conecta-se diretamente às seguintes fatias verticais do backend:
- **Fatia de Backend:** `src/features/intelligence/router.py`
- **Fatia de Backend:** `src/features/search/router.py`

---

## 2. Análise de Subprodutização do Motor (Capacidades Ociosas)

| Recurso / Capacidade do Motor | O Que o Backend Executa | O Que a Tela Consome Atualmente | Diagnóstico de Subprodutização & Potencial |
| :--- | :--- | :--- | :--- |
| **Similaridade por Cosseno Híbrida** | Recurso implementado no motor | Não exposto na interface do usuário | **Backend suporta busca híbrida (BM25 + Vetores), tela usa busca densa** |
| **Previsão de Próxima Cirurgia** | Recurso implementado no motor | Não exposto na interface do usuário | **Modelo calcula probabilidade de data da próxima cirurgia, tela omite** |
