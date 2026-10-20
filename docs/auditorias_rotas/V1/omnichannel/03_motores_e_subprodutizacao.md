# 03. Motores de Backend e Subprodutização — Rota: omnichannel

## 1. Motores Subjacentes do Ecossistema
A rota conecta-se diretamente às seguintes fatias verticais do backend:
- **Fatia de Backend:** `src/features/communications/router.py`
- **Fatia de Backend:** `src/features/integrations/omnichannel/evolution_webhook_router.py`

---

## 2. Análise de Subprodutização do Motor (Capacidades Ociosas)

| Recurso / Capacidade do Motor | O Que o Backend Executa | O Que a Tela Consome Atualmente | Diagnóstico de Subprodutização & Potencial |
| :--- | :--- | :--- | :--- |
| **Transcrições Automáticas Whisper** | Recurso implementado no motor | Não exposto na interface do usuário | **Backend transcreve áudios recebidos, mas UI não exibe a transcrição inline** |
| **Roteamento Inteligente por Regional** | Recurso implementado no motor | Não exposto na interface do usuário | **Evolution Cluster suporta múltiplas instâncias por DDD, mas UI exibe fila única** |
