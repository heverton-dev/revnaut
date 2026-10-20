# 06. Especificação DD (TDD, BDD, SDD) — Rota: scheduling

## 1. Especificação BDD (Gherkin)
```gherkin
Funcionalidade: Operação da Rota Retorno de Pacientes & Agendamentos
  Como Usuário Autenticado da Plataforma RevOps
  Eu quero acessar a rota "/#!/scheduling"
  Para executar as rotinas operacionais com integridade e segurança

  Cenário: Carga Inicial de Dados com Sucesso
    Dado que o usuário está autenticado
    Quando navega para "/#!/scheduling"
    Então o sistema carrega os dados correspondentes com status HTTP 200
    E exibe as abas e botões operacionais sem erros no console
```

---

## 2. Cobertura de Testes Automatizados TDD
A rota é suportada pelas seguintes suítes de teste automatizadas reais:
- `tests/test_calcom_patient_reactivation.py`
