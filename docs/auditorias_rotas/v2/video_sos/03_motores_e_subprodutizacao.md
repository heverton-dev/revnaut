# 03. Motores de Backend e Subprodutização — Rota: video_sos (Auditoria v2)

## 1. Motores Subjacentes do Ecossistema
A rota conecta-se diretamente às seguintes fatias verticais do backend:
- **Fatia de Backend:** `src/features/communications/router.py`
- **Fatia de Backend:** `src/features/intelligence/router.py`

---

## 2. Análise de Subprodutização do Motor (Capacidades Ociosas)

| Recurso / Capacidade do Motor | O Que o Backend Executa | O Que a Tela Consome Atualmente | Diagnóstico de Subprodutização & Potencial |
| :--- | :--- | :--- | :--- |
| **Transmissão em Baixa Latência (P2P)** | Recurso implementado no motor | Não exposto na interface do usuário | **LiveKit suporta fallback P2P para internet oscilante, UI usa modo MCU fixo** |
| **Detecção de Emoção / Tensão** | Recurso implementado no motor | Não exposto na interface do usuário | **Motor de áudio analisa estresse na voz do cirurgião, tela não expõe indicador** |
