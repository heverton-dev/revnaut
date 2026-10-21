# 03. Motores de Backend & Diagnóstico de Subprodutização — Rota: keypartners (Auditoria V3)

## 1. Aproveitamento dos Motores do Backend
A tela integra-se diretamente com os serviços FastAPI e tabelas SQLite WAL:
- `src/features/keypartners/router.py`
- `src/features/integrations/totvs/router.py`

---

## 2. Capacidades Ociosas do Motor Identificadas (Anti-Subprodutização)
- **Alerta de Giro Ocioso:** Backend identifica maletas sem uso por > 45 dias, tela não prioriza
- **Cálculo Automático de Depreciação:** Motor calcula desgaste de instrumentais, tela omite dados contábeis