# 03. Motores de Backend e Subprodutização — Rota: analytics

## 1. Motores Subjacentes do Ecossistema
A rota conecta-se diretamente às seguintes fatias verticais do backend:
- **Fatia de Backend:** `src/features/intelligence/router.py`

---

## 2. Análise de Subprodutização do Motor (Capacidades Ociosas)

| Recurso / Capacidade do Motor | O Que o Backend Executa | O Que a Tela Consome Atualmente | Diagnóstico de Subprodutização & Potencial |
| :--- | :--- | :--- | :--- |
| **Suporte a Múltiplos Datasets** | Recurso implementado no motor | Não exposto na interface do usuário | **Backend tem 4 datasets analíticos configurados, mas UI foca em 1 por vez** |
| **Cache de Resultados SQL** | Recurso implementado no motor | Não exposto na interface do usuário | **Mecanismo de TTL no Redis Streams mas sem indicador de frescor na tela** |
