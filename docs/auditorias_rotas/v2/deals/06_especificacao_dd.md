# 06. Especificação DD (TDD, BDD, SDD) — Rota: deals (Auditoria v2)

## 1. Especificação BDD (Gherkin)
```gherkin
Funcionalidade: Operação da Rota Negociações & Funil Comercial (CRM Cirúrgico)
  Como Usuário Autenticado da Plataforma RevOps
  Eu quero acessar a rota "/#!/deals"
  Para executar as rotinas operacionais com integridade e segurança

  Cenário: Carga Inicial de Dados com Sucesso
    Dado que o usuário está autenticado no sistema
    Quando navega para a URL "/#!/deals"
    Então o sistema carrega os dados correspondentes com status HTTP 200
    E exibe as abas e botões operacionais sem erros no console
```

---

## 2. Cobertura de Testes Automatizados TDD
A rota é suportada pelas seguintes suítes de teste automatizadas reais no repositório:
- `tests/test_deals_advanced_features.py`
- `tests/test_deals_contacts_scoping.py`
- `tests/test_granola_copilot_zerotouch.py`
