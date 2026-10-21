# 03. Motores de Backend & Diagnóstico de Subprodutização — Rota: scheduling (Auditoria V3)

## 1. Aproveitamento dos Motores do Backend
A tela integra-se diretamente com os serviços FastAPI e tabelas SQLite WAL:
- `src/features/scheduling/router.py`
- `src/features/integrations/omnichannel/router.py`

---

## 2. Capacidades Ociosas do Motor Identificadas (Anti-Subprodutização)
- **Alocação por Dentista Titular:** Backend suporta rodízio entre especialistas da clínica, tela usa agenda única
- **Disparo via SMS / Flash Call:** Conectores SIP de telefonia para lembrete automático não ativos na tela