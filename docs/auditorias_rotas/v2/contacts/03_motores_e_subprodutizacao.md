# 03. Motores de Backend e Subprodutização — Rota: contacts (Auditoria v2)

## 1. Motores Subjacentes do Ecossistema
A rota conecta-se diretamente às seguintes fatias verticais do backend:
- **Fatia de Backend:** `src/features/contacts/router.py`
- **Fatia de Backend:** `src/features/institutions/router.py`

---

## 2. Análise de Subprodutização do Motor (Capacidades Ociosas)

| Recurso / Capacidade do Motor | O Que o Backend Executa | O Que a Tela Consome Atualmente | Diagnóstico de Subprodutização & Potencial |
| :--- | :--- | :--- | :--- |
| **Consulta CFO em Lote** | Recurso implementado no motor | Não exposto na interface do usuário | **Backend suporta validação de 50 CROs em paralelo, tela valida individual** |
| **Enriquecimento de CNPJ da Clínica** | Recurso implementado no motor | Não exposto na interface do usuário | **Backend possui conector com ReceitaWS, formulário usa entrada manual** |
| **Vínculo Multiclínica N:N** | Recurso implementado no motor | Não exposto na interface do usuário | **Tabelas suportam múltiplos vínculos clínicos, UI restringe a 1 hospital/clínica** |
