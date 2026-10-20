# 06. Especificação DD (TDD, BDD, SDD) — Rota: video_sos

## 1. Especificação BDD (Gherkin)
```gherkin
Funcionalidade: Operação da Rota Chamadas e Vídeo SOS (Mesa Cirúrgica)
  Como Usuário Autenticado da Plataforma RevOps
  Eu quero acessar a rota "/#!/video_sos"
  Para executar as rotinas operacionais com integridade e segurança

  Cenário: Carga Inicial de Dados com Sucesso
    Dado que o usuário está autenticado
    Quando navega para "/#!/video_sos"
    Então o sistema carrega os dados correspondentes com status HTTP 200
    E exibe as abas e botões operacionais sem erros no console
```

---

## 2. Cobertura de Testes Automatizados TDD
A rota é suportada pelas seguintes suítes de teste automatizadas reais:
- `tests/test_surgical_sos_livekit.py`
- `tests/test_livekit_webrtc_sip.py`
- `tests/test_faster_whisper_diarization.py`
