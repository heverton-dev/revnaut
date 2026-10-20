# 03. Motores de Backend e Subprodutização — Rota: dentgo (Auditoria v2)

## 1. Motores Subjacentes do Ecossistema
A rota conecta-se diretamente às seguintes fatias verticais do backend:
- **Fatia de Backend:** `src/features/dentgo/router.py`
- **Fatia de Backend:** `src/features/inventory/router.py`

---

## 2. Análise de Subprodutização do Motor (Capacidades Ociosas)

| Recurso / Capacidade do Motor | O Que o Backend Executa | O Que a Tela Consome Atualmente | Diagnóstico de Subprodutização & Potencial |
| :--- | :--- | :--- | :--- |
| **Algoritmo de Roteirização Multi-Ponto** | Recurso implementado no motor | Não exposto na interface do usuário | **Backend calcula rotas de entrega para 5 clínicas, tela suporta 1 destino** |
| **Previsão de Tráfego em Tempo Real** | Recurso implementado no motor | Não exposto na interface do usuário | **Conector com dados de trânsito existente no backend mas não plotado no mapa** |
