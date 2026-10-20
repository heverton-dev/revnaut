# 06. Especificação DD (TDD, BDD, SDD) — Rota: omnichannel (Auditoria v2)

## 1. Especificação BDD (Gherkin)
```gherkin
Funcionalidade: Operação da Rota Atendimento Clínico WhatsApp (Omnichannel)
  Como Usuário Autenticado da Plataforma RevOps
  Eu quero acessar a rota "/#!/omnichannel"
  Para executar as rotinas operacionais com integridade e segurança

  Cenário: Carga Inicial de Dados com Sucesso
    Dado que o usuário está autenticado no sistema
    Quando navega para a URL "/#!/omnichannel"
    Então o sistema carrega os dados correspondentes com status HTTP 200
    E exibe as abas e botões operacionais sem erros no console
```

---

## 2. Cobertura de Testes Automatizados TDD
A rota é suportada pelas seguintes suítes de teste automatizadas reais no repositório:
- `tests/test_chatwoot_omnichannel_context_sidebar.py`
- `tests/test_evolution_signed_call_offer.py`
- `tests/test_omnichannel_webhooks.py`
