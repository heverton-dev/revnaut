# 06. Especificação DD (TDD, BDD, SDD) — Rota: intelligence (Auditoria v2)

## 1. Especificação BDD (Gherkin)
```gherkin
Funcionalidade: Operação da Rota Assistente Comercial & RAG Clínico
  Como Usuário Autenticado da Plataforma RevNault
  Eu quero acessar a rota "/#!/intelligence"
  Para executar as rotinas operacionais com integridade e segurança

  Cenário: Carga Inicial de Dados com Sucesso
    Dado que o usuário está autenticado no sistema
    Quando navega para a URL "/#!/intelligence"
    Então o sistema carrega os dados correspondentes com status HTTP 200
    E exibe as abas e botões operacionais sem erros no console
```

---

## 2. Cobertura de Testes Automatizados TDD
A rota é suportada pelas seguintes suítes de teste automatizadas reais no repositório:
- `tests/test_clinical_graph_churn.py`
- `tests/test_surgical_catalog_rag.py`
- `tests/test_pgvector_store.py`
