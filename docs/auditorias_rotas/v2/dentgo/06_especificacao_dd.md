# 06. Especificação DD (TDD, BDD, SDD) — Rota: dentgo (Auditoria v2)

## 1. Especificação BDD (Gherkin)
```gherkin
Funcionalidade: Operação da Rota Entregas Expressas Same-Day (DENTGO)
  Como Usuário Autenticado da Plataforma RevOps
  Eu quero acessar a rota "/#!/dentgo"
  Para executar as rotinas operacionais com integridade e segurança

  Cenário: Carga Inicial de Dados com Sucesso
    Dado que o usuário está autenticado no sistema
    Quando navega para a URL "/#!/dentgo"
    Então o sistema carrega os dados correspondentes com status HTTP 200
    E exibe as abas e botões operacionais sem erros no console
```

---

## 2. Cobertura de Testes Automatizados TDD
A rota é suportada pelas seguintes suítes de teste automatizadas reais no repositório:
- `tests/test_dentgo_express_route.py`
- `tests/test_dentgo_fefo_flash_deals.py`
- `tests/test_dentgo_financial_split.py`
