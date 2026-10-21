# 03. Motores de Backend & Diagnóstico de Subprodutização — Rota: dentgo (Auditoria V3)

## 1. Aproveitamento dos Motores do Backend
A tela integra-se diretamente com os serviços FastAPI e tabelas SQLite WAL:
- `src/features/dentgo/router.py`
- `src/features/inventory/router.py`

---

## 2. Capacidades Ociosas do Motor Identificadas (Anti-Subprodutização)
- **Algoritmo de Roteirização Multi-Ponto:** Backend calcula rotas de entrega para 5 clínicas, tela suporta 1 destino
- **Previsão de Tráfego em Tempo Real:** Conector com dados de trânsito existente no backend mas não plotado no mapa