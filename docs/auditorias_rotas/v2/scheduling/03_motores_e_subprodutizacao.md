# 03. Motores de Backend e Subprodutização — Rota: scheduling (Auditoria v2)

## 1. Motores Subjacentes do Ecossistema
A rota conecta-se diretamente às seguintes fatias verticais do backend:
- **Fatia de Backend:** `src/features/scheduling/router.py`
- **Fatia de Backend:** `src/features/integrations/omnichannel/router.py`

---

## 2. Análise de Subprodutização do Motor (Capacidades Ociosas)

| Recurso / Capacidade do Motor | O Que o Backend Executa | O Que a Tela Consome Atualmente | Diagnóstico de Subprodutização & Potencial |
| :--- | :--- | :--- | :--- |
| **Alocação por Dentista Titular** | Recurso implementado no motor | Não exposto na interface do usuário | **Backend suporta rodízio entre especialistas da clínica, tela usa agenda única** |
| **Disparo via SMS / Flash Call** | Recurso implementado no motor | Não exposto na interface do usuário | **Conectores SIP de telefonia para lembrete automático não ativos na tela** |
