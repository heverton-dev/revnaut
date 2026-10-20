# 03. Motores de Backend e Subprodutização — Rota: settings (Auditoria v2)

## 1. Motores Subjacentes do Ecossistema
A rota conecta-se diretamente às seguintes fatias verticais do backend:
- **Fatia de Backend:** `src/features/settings/router.py`
- **Fatia de Backend:** `src/features/integrations/totvs/router.py`
- **Fatia de Backend:** `src/features/integrations/omnichannel/router.py`

---

## 2. Análise de Subprodutização do Motor (Capacidades Ociosas)

| Recurso / Capacidade do Motor | O Que o Backend Executa | O Que a Tela Consome Atualmente | Diagnóstico de Subprodutização & Potencial |
| :--- | :--- | :--- | :--- |
| **Filtro Granular de Eventos de Webhook** | Recurso implementado no motor | Não exposto na interface do usuário | **Backend suporta filtrar por 20 tópicos, UI assina todos os eventos** |
| **Sincronização de Pedidos de Compra TOTVS** | Recurso implementado no motor | Não exposto na interface do usuário | **Conector Protheus lê ordens de compra, tela só sincroniza notas fiscais** |
