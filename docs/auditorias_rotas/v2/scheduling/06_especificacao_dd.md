# 06. Especificação DD (TDD, BDD, SDD) — Rota: scheduling (Auditoria v2)

## 1. Especificação BDD (Gherkin)
```gherkin
Funcionalidade: Operação da Rota Reativação de Pacientes (Cal.com)
  Como Usuário Autenticado da Plataforma RevNault
  Eu quero acessar a rota "/#!/scheduling"
  Para executar as rotinas operacionais com integridade e segurança

  Cenário: Carga Inicial de Dados com Sucesso
    Dado que o usuário está autenticado no sistema
    Quando navega para a URL "/#!/scheduling"
    Então o sistema carrega os dados correspondentes com status HTTP 200
    E exibe as abas e botões operacionais sem erros no console
```

---

## 2. Cobertura de Testes Automatizados TDD
A rota é suportada pelas seguintes suítes de teste automatizadas reais no repositório:
- `tests/test_calcom_patient_reactivation.py`
- `tests/test_outbound_webhooks_hmac.py`
