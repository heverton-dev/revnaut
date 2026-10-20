# 06. Especificação DD (TDD, BDD, SDD) — Rota: marketing (Auditoria v2)

## 1. Especificação BDD (Gherkin)
```gherkin
Funcionalidade: Operação da Rota Campanhas e Indicações (Growth & Referral)
  Como Usuário Autenticado da Plataforma RevOps
  Eu quero acessar a rota "/#!/marketing"
  Para executar as rotinas operacionais com integridade e segurança

  Cenário: Carga Inicial de Dados com Sucesso
    Dado que o usuário está autenticado no sistema
    Quando navega para a URL "/#!/marketing"
    Então o sistema carrega os dados correspondentes com status HTTP 200
    E exibe as abas e botões operacionais sem erros no console
```

---

## 2. Cobertura de Testes Automatizados TDD
A rota é suportada pelas seguintes suítes de teste automatizadas reais no repositório:
- `tests/test_landing_pages_grapesjs.py`
- `tests/test_b2b_referral_mgm_loop.py`
- `tests/test_listmonk_campaigns.py`
