# 03. Motores de Backend & Diagnóstico de Subprodutização — Rota: intelligence (Auditoria V3)

## 1. Aproveitamento dos Motores do Backend
A tela integra-se diretamente com os serviços FastAPI e tabelas SQLite WAL:
- `src/features/intelligence/router.py`
- `src/features/search/router.py`

---

## 2. Capacidades Ociosas do Motor Identificadas (Anti-Subprodutização)
- **Similaridade por Cosseno Híbrida:** Backend suporta busca híbrida (BM25 + Vetores), tela usa busca densa
- **Previsão de Próxima Cirurgia:** Modelo calcula probabilidade de data da próxima cirurgia, tela omite