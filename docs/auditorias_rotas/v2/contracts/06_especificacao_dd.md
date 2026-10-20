# 06. Especificação DD (TDD, BDD, SDD) — Rota: contracts (Auditoria v2)

## 1. Especificação BDD (Gherkin)
```gherkin
Funcionalidade: Operação da Rota Propostas e Contratos (Documenso & ANVISA)
  Como Usuário Autenticado da Plataforma RevNault
  Eu quero acessar a rota "/#!/contracts"
  Para executar as rotinas operacionais com integridade e segurança

  Cenário: Carga Inicial de Dados com Sucesso
    Dado que o usuário está autenticado no sistema
    Quando navega para a URL "/#!/contracts"
    Então o sistema carrega os dados correspondentes com status HTTP 200
    E exibe as abas e botões operacionais sem erros no console
```

---

## 2. Cobertura de Testes Automatizados TDD
A rota é suportada pelas seguintes suítes de teste automatizadas reais no repositório:
- `tests/test_documenso_contract_flow.py`
- `tests/test_r2_storage.py`
- `tests/test_catalog_pricing_approval.py`
