# 03. Motores de Backend e Subprodutização — Rota: keypartners

## 1. Motores Subjacentes do Ecossistema
A rota conecta-se diretamente às seguintes fatias verticais do backend:
- **Fatia de Backend:** `src/features/keypartners/router.py`
- **Fatia de Backend:** `src/features/integrations/totvs/router.py`

---

## 2. Análise de Subprodutização do Motor (Capacidades Ociosas)

| Recurso / Capacidade do Motor | O Que o Backend Executa | O Que a Tela Consome Atualmente | Diagnóstico de Subprodutização & Potencial |
| :--- | :--- | :--- | :--- |
| **Alerta de Validade FEFO das Maletas** | Recurso implementado no motor | Não exposto na interface do usuário | **Backend calcula itens próximos do vencimento, mas tela não destaca com badges de urgência** |
| **Assinatura do Termo de Recebimento** | Recurso implementado no motor | Não exposto na interface do usuário | **Documenso pode colher assinatura do responsável do hospital, mas fluxo é manual** |
