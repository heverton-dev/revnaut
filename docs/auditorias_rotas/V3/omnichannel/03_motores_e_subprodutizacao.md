# 03. Motores de Backend & Diagnóstico de Subprodutização — Rota: omnichannel (Auditoria V3)

## 1. Aproveitamento dos Motores do Backend
A tela integra-se diretamente com os serviços FastAPI e tabelas SQLite WAL:
- `src/features/integrations/omnichannel/router.py`
- `src/features/communications/router.py`

---

## 2. Capacidades Ociosas do Motor Identificadas (Anti-Subprodutização)
- **Diarização Faster-Whisper:** Backend transcreve áudios com separação de vozes, tela mostra texto corrido
- **Webhooks de Entrega e Leitura:** Status de leitura processado no backend mas sem check azul na UI