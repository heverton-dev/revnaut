# 06. Especificação DD (TDD, BDD, SDD) — Rota: keypartners (Auditoria v2)

## 1. Especificação BDD (Gherkin)
```gherkin
Funcionalidade: Operação da Rota Malas em Consignação & KOL (KeyPartners)
  Como Usuário Autenticado da Plataforma RevOps
  Eu quero acessar a rota "/#!/keypartners"
  Para executar as rotinas operacionais com integridade e segurança

  Cenário: Carga Inicial de Dados com Sucesso
    Dado que o usuário está autenticado no sistema
    Quando navega para a URL "/#!/keypartners"
    Então o sistema carrega os dados correspondentes com status HTTP 200
    E exibe as abas e botões operacionais sem erros no console
```

---

## 2. Cobertura de Testes Automatizados TDD
A rota é suportada pelas seguintes suítes de teste automatizadas reais no repositório:
- `tests/test_erp_consignment_cfop_flow.py`
- `tests/test_keypartners_dispatch_custody_route.py`
- `tests/test_keypartners_kol_contracts.py`
