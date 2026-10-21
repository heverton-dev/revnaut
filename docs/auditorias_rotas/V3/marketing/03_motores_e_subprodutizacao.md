# 03. Motores de Backend & Diagnóstico de Subprodutização — Rota: marketing (Auditoria V3)

## 1. Aproveitamento dos Motores do Backend
A tela integra-se diretamente com os serviços FastAPI e tabelas SQLite WAL:
- `src/features/campaigns/router.py`
- `src/features/integrations/omnichannel/router.py`

---

## 2. Capacidades Ociosas do Motor Identificadas (Anti-Subprodutização)
- **Disparo via Listmonk:** Motor de automação de e-mails conectado mas sem disparador manual na tela
- **Pixel e Tags Customizadas:** Campos de GTM/Meta Pixel no schema mas ausentes no formulário básico