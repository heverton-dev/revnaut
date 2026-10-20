# 03. Motores de Backend e Subprodutização — Rota: contracts (Auditoria v2)

## 1. Motores Subjacentes do Ecossistema
A rota conecta-se diretamente às seguintes fatias verticais do backend:
- **Fatia de Backend:** `src/features/contracts/router.py`
- **Fatia de Backend:** `src/features/integrations/totvs/router.py`

---

## 2. Análise de Subprodutização do Motor (Capacidades Ociosas)

| Recurso / Capacidade do Motor | O Que o Backend Executa | O Que a Tela Consome Atualmente | Diagnóstico de Subprodutização & Potencial |
| :--- | :--- | :--- | :--- |
| **Campos Customizados Dinâmicos** | Recurso implementado no motor | Não exposto na interface do usuário | **Documenso suporta tags variáveis infinitas, UI tem 4 campos fixos** |
| **Controle de Versões da Minuta** | Recurso implementado no motor | Não exposto na interface do usuário | **Backend armazena diff de minutas, tela mostra apenas versão final** |
