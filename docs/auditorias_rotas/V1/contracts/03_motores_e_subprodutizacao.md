# 03. Motores de Backend e Subprodutização — Rota: contracts

## 1. Motores Subjacentes do Ecossistema
A rota conecta-se diretamente às seguintes fatias verticais do backend:
- **Fatia de Backend:** `src/features/deals/router.py`
- **Fatia de Backend:** `src/features/storage/router.py`

---

## 2. Análise de Subprodutização do Motor (Capacidades Ociosas)

| Recurso / Capacidade do Motor | O Que o Backend Executa | O Que a Tela Consome Atualmente | Diagnóstico de Subprodutização & Potencial |
| :--- | :--- | :--- | :--- |
| **Webhooks de Status de Assinatura** | Recurso implementado no motor | Não exposto na interface do usuário | **Documenso notifica quando cirurgião abre o e-mail, mas UI só mostra assinado/pendente** |
| **Hash SHA-256 no R2** | Recurso implementado no motor | Não exposto na interface do usuário | **Todos os PDFs possuem hash imutável de custódia, mas UI não expõe o verificador público** |
