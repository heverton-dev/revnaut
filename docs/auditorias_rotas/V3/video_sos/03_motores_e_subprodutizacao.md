# 03. Motores de Backend & Diagnóstico de Subprodutização — Rota: video_sos (Auditoria V3)

## 1. Aproveitamento dos Motores do Backend
A tela integra-se diretamente com os serviços FastAPI e tabelas SQLite WAL:
- `src/features/communications/router.py`
- `src/features/intelligence/router.py`

---

## 2. Capacidades Ociosas do Motor Identificadas (Anti-Subprodutização)
- **Transmissão em Baixa Latência (P2P):** LiveKit suporta fallback P2P para internet oscilante, UI usa modo MCU fixo
- **Detecção de Emoção / Tensão:** Motor de áudio analisa estresse na voz do cirurgião, tela não expõe indicador