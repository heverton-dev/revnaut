# 03. Motores de Backend e Subprodutização — Rota: omnichannel (Auditoria v2)

## 1. Motores Subjacentes do Ecossistema
A rota conecta-se diretamente às seguintes fatias verticais do backend:
- **Fatia de Backend:** `src/features/integrations/omnichannel/router.py`
- **Fatia de Backend:** `src/features/communications/router.py`

---

## 2. Análise de Subprodutização do Motor (Capacidades Ociosas)

| Recurso / Capacidade do Motor | O Que o Backend Executa | O Que a Tela Consome Atualmente | Diagnóstico de Subprodutização & Potencial |
| :--- | :--- | :--- | :--- |
| **Diarização Faster-Whisper** | Recurso implementado no motor | Não exposto na interface do usuário | **Backend transcreve áudios com separação de vozes, tela mostra texto corrido** |
| **Webhooks de Entrega e Leitura** | Recurso implementado no motor | Não exposto na interface do usuário | **Status de leitura processado no backend mas sem check azul na UI** |
