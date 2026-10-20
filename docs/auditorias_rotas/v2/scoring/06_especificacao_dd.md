# 06. Especificação DD (TDD, BDD, SDD) — Rota: scoring (Auditoria v2)

## 1. Especificação BDD (Gherkin)
```gherkin
Funcionalidade: Operação da Rota Qualificação de Clientes (ICP Scoring)
  Como Usuário Autenticado da Plataforma RevOps
  Eu quero acessar a rota "/#!/scoring"
  Para executar as rotinas operacionais com integridade e segurança

  Cenário: Carga Inicial de Dados com Sucesso
    Dado que o usuário está autenticado no sistema
    Quando navega para a URL "/#!/scoring"
    Então o sistema carrega os dados correspondentes com status HTTP 200
    E exibe as abas e botões operacionais sem erros no console
```

---

## 2. Cobertura de Testes Automatizados TDD
A rota é suportada pelas seguintes suítes de teste automatizadas reais no repositório:
- `tests/test_lead_scoring_handoff.py`
- `tests/test_lead_scoring_auto_handoff.py`
