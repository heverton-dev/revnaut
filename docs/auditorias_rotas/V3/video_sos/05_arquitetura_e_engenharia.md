# 05. Arquitetura de Software & Vertical Slice Architecture — Rota: video_sos (Auditoria V3)

## 1. Organização em Fatias Verticais (VSA)
- O módulo reside em `frontend/src/features/communications/LiveKitDealRoomModal.tsx` mantendo separação clara entre camada de apresentação, estado e contratos de API.

---

## 2. Acoplamento e Reusabilidade
- Componentes reutilizáveis importados de `@/components/ui/` (`Button`, `Card`, `Badge`, `Tabs`, `Dialog`).
- Ausência de dependências circulares com testes automatizados dedicados:
  - `tests/test_surgical_sos_livekit.py`
  - `tests/test_livekit_webrtc_sip.py`
  - `tests/test_faster_whisper_diarization.py`