# 01. Visão Geral e Jornada do Usuário — Rota: intelligence (Auditoria V3)

## 1. Identificação Técnica
- **Rota Visual:** `https://revnault.vpsconexao.org/#!/intelligence`
- **Título Oficial:** Assistente Comercial & RAG Clínico
- **Componente Front-end:** `frontend/src/features/intelligence/IntelligenceSuiteWorkspace.tsx`
- **Motores Backend:** `src/features/intelligence/router.py`, `src/features/search/router.py`
- **Suíte de Testes:** `tests/test_clinical_graph_churn.py`, `tests/test_surgical_catalog_rag.py`, `tests/test_pgvector_store.py`

---

## 2. Jornada do Usuário Real
O usuário acessa o módulo para executar operações cirúrgicas e comerciais sem atrito:
1. **Entrada na Tela:** Carregamento otimizado com dados reais via SQLite WAL.
2. **Navegação por Abas:** Alternância fluida entre as visões do módulo.
3. **Ações Primárias:** Interação com botões de alta densidade sem stubs ou toasts vazios.

---

## 3. Abas e Sub-Rotas Mapeadas
- **Aba `churn`:** Radar Preditivo de Evasão RFM
- **Aba `kol_graph`:** Topologia do Ecossistema Clínico e KOL
- **Aba `rag_chat`:** Assistente RAG com Catálogo Técnico Cirúrgico