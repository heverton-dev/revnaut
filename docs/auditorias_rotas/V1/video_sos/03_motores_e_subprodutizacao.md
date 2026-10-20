# 03. Motores de Backend e Subprodutização — Rota: video_sos

## 1. Motores Subjacentes do Ecossistema
A rota conecta-se diretamente às seguintes fatias verticais do backend:
- **Fatia de Backend:** `src/features/communications/router.py`

---

## 2. Análise de Subprodutização do Motor (Capacidades Ociosas)

| Recurso / Capacidade do Motor | O Que o Backend Executa | O Que a Tela Consome Atualmente | Diagnóstico de Subprodutização & Potencial |
| :--- | :--- | :--- | :--- |
| **Transcrição em Tempo Real Faster-Whisper** | Recurso implementado no motor | Não exposto na interface do usuário | **Backend transcreve fala médica, mas UI só exibe pós-chamada** |
| **Gravação de Alta Fidelidade no Cloudflare R2** | Recurso implementado no motor | Não exposto na interface do usuário | **Egress configurado mas sem link de download direto no player** |
