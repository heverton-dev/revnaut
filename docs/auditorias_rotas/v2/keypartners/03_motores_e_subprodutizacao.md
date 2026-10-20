# 03. Motores de Backend e Subprodutização — Rota: keypartners (Auditoria v2)

## 1. Motores Subjacentes do Ecossistema
A rota conecta-se diretamente às seguintes fatias verticais do backend:
- **Fatia de Backend:** `src/features/keypartners/router.py`
- **Fatia de Backend:** `src/features/integrations/totvs/router.py`

---

## 2. Análise de Subprodutização do Motor (Capacidades Ociosas)

| Recurso / Capacidade do Motor | O Que o Backend Executa | O Que a Tela Consome Atualmente | Diagnóstico de Subprodutização & Potencial |
| :--- | :--- | :--- | :--- |
| **Alerta de Giro Ocioso** | Recurso implementado no motor | Não exposto na interface do usuário | **Backend identifica maletas sem uso por > 45 dias, tela não prioriza** |
| **Cálculo Automático de Depreciação** | Recurso implementado no motor | Não exposto na interface do usuário | **Motor calcula desgaste de instrumentais, tela omite dados contábeis** |
