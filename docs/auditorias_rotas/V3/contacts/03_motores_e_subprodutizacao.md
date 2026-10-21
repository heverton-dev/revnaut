# 03. Motores de Backend & Diagnóstico de Subprodutização — Rota: contacts (Auditoria V3)

## 1. Aproveitamento dos Motores do Backend
A tela integra-se diretamente com os serviços FastAPI e tabelas SQLite WAL:
- `src/features/contacts/router.py`
- `src/features/institutions/router.py`

---

## 2. Capacidades Ociosas do Motor Identificadas (Anti-Subprodutização)
- **Consulta CFO em Lote:** Backend suporta validação de 50 CROs em paralelo, tela valida individual
- **Enriquecimento de CNPJ da Clínica:** Backend possui conector com ReceitaWS, formulário usa entrada manual
- **Vínculo Multiclínica N:N:** Tabelas suportam múltiplos vínculos clínicos, UI restringe a 1 hospital/clínica