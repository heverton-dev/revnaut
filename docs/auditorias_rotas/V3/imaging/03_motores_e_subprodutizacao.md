# 03. Motores de Backend & Diagnóstico de Subprodutização — Rota: imaging (Auditoria V3)

## 1. Aproveitamento dos Motores do Backend
A tela integra-se diretamente com os serviços FastAPI e tabelas SQLite WAL:
- `src/features/imaging/router.py`
- `src/features/contracts/router.py`

---

## 2. Capacidades Ociosas do Motor Identificadas (Anti-Subprodutização)
- **Segmentação Automática por IA:** Backend suporta modelo de segmentação de mandíbula, tela não ativa
- **Renderização Volume Rendering (Raymarching):** Shader 3D volumétrico disponível mas desativado por performance