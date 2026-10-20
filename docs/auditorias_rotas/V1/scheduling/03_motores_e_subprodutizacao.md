# 03. Motores de Backend e Subprodutização — Rota: scheduling

## 1. Motores Subjacentes do Ecossistema
A rota conecta-se diretamente às seguintes fatias verticais do backend:
- **Fatia de Backend:** `src/features/automations/router.py`
- **Fatia de Backend:** `src/features/tasks/router.py`

---

## 2. Análise de Subprodutização do Motor (Capacidades Ociosas)

| Recurso / Capacidade do Motor | O Que o Backend Executa | O Que a Tela Consome Atualmente | Diagnóstico de Subprodutização & Potencial |
| :--- | :--- | :--- | :--- |
| **Intervalo Clínico Personalizado por Procedimento** | Recurso implementado no motor | Não exposto na interface do usuário | **Backend sabe tempo de osseointegracao (90d vs 180d), mas UI usa 6 meses padrão** |
| **Cálculo de Receita Resgatada** | Recurso implementado no motor | Não exposto na interface do usuário | **Métrica de faturamento salvo por reativação calculada mas não exibida** |
