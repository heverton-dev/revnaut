# 03. Motores de Backend e Subprodutização — Rota: dentgo

## 1. Motores Subjacentes do Ecossistema
A rota conecta-se diretamente às seguintes fatias verticais do backend:
- **Fatia de Backend:** `src/features/dentgo/router.py`

---

## 2. Análise de Subprodutização do Motor (Capacidades Ociosas)

| Recurso / Capacidade do Motor | O Que o Backend Executa | O Que a Tela Consome Atualmente | Diagnóstico de Subprodutização & Potencial |
| :--- | :--- | :--- | :--- |
| **Geofencing de Chegada** | Recurso implementado no motor | Não exposto na interface do usuário | **Backend calcula raio de 500m do hospital, mas UI não dispara alerta sonoro** |
| **Roteirização Multiparada** | Recurso implementado no motor | Não exposto na interface do usuário | **Algoritmo suporta entregar em 3 clínicas na mesma viagem, mas tela cadastra 1 por vez** |
