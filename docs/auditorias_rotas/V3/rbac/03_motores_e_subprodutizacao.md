# 03. Motores de Backend & Diagnóstico de Subprodutização — Rota: rbac (Auditoria V3)

## 1. Aproveitamento dos Motores do Backend
A tela integra-se diretamente com os serviços FastAPI e tabelas SQLite WAL:
- `src/features/rbac/router.py`
- `src/features/hierarchy/router.py`

---

## 2. Capacidades Ociosas do Motor Identificadas (Anti-Subprodutização)
- **Herança Recursiva de Permissões:** Backend resolve permissões em cascata N-níveis, UI exibe tabela estática
- **Split de Comissão Entre Vendedores:** Cálculo suporta divisão da comissão em vendas conjuntas, tela usa 1 recebedor