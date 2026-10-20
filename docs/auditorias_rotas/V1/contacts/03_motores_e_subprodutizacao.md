# 03. Motores de Backend e Subprodutização — Rota: contacts

## 1. Motores Subjacentes do Ecossistema
A rota conecta-se diretamente às seguintes fatias verticais do backend:
- **Fatia de Backend:** `src/features/contacts/router.py`
- **Fatia de Backend:** `src/features/institutions/router.py`

---

## 2. Análise de Subprodutização do Motor (Capacidades Ociosas)

| Recurso / Capacidade do Motor | O Que o Backend Executa | O Que a Tela Consome Atualmente | Diagnóstico de Subprodutização & Potencial |
| :--- | :--- | :--- | :--- |
| **Consulta CFO em Lote** | Recurso implementado no motor | Não exposto na interface do usuário | **Backend suporta validação de 50 CROs em paralelo, mas UI valida 1 por vez** |
| **Enriquecimento de CNPJ da Clínica** | Recurso implementado no motor | Não exposto na interface do usuário | **Backend possui integração com Receita, mas tela usa campos manuais** |
| **Vínculo Multiclínica N:N** | Recurso implementado no motor | Não exposto na interface do usuário | **Tabelas suportam cirurgião em múltiplas clínicas, mas UI só permite 1 clínica principal** |
