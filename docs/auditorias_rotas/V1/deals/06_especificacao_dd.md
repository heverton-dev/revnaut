# 06. Especificação DD (TDD, BDD, SDD) — Rota: deals

## 1. Especificação BDD (Behavior-Driven Development) em Gherkin

```gherkin
Funcionalidade: Gestão do Funil de Negociações Cirúrgicas
  Como Consultor Comercial ou Gestor de RevNault
  Eu quero visualizar e movimentar as oportunidades de venda de implantes
  Para acompanhar a evolução dos negócios desde a qualificação até o fechamento ganho

  Cenário: Movimentação de Estágio e Registro de Auditoria
    Dado que o consultor visualiza o negócio "Implantes Cônicos Clínica Sorriso" no estágio "Qualificação"
    Quando altera o estágio para "Proposta Comercial" e confirma
    Então o sistema atualiza o status via "PUT /api/v1/deals/{id}"
    E grava um evento na linha do tempo indicando a transição de estágio
    E recalcula o somatório financeiro da coluna de Proposta Comercial

  Cenário: Trava Automática de Limite de Crédito
    Dado que uma clínica possui limite de crédito de R$ 50.000
    Quando o consultor tenta fechar um negócio de R$ 75.000
    Então o sistema bloqueia o avanço para "Fechado Ganho"
    E exibe o alerta de "Limite de Crédito Excedido"
    E exige aprovação formal de um Gerente ou Diretor para liberação
```

---

## 2. Contratos TDD (Test-Driven Development) Red-Green

| Arquivo de Teste | Suíte de Teste / Função | Status Atual | Critério de Aceitação |
| :--- | :--- | :--- | :--- |
| `tests/test_deals_advanced_features.py` | `test_deal_inline_update_and_timeline` | PASSED (100%) | Atualização de negócio grava evento na linha do tempo. |
| `tests/test_deals_advanced_features.py` | `test_credit_limit_lock_and_approval` | PASSED (100%) | Bloqueia avanço de negócio sem crédito e permite aprovação gerencial. |
| `tests/test_deals_contacts_scoping.py` | `test_deals_consultor_sees_only_own_deals` | PASSED (100%) | Consultor enxerga apenas seus próprios negócios no funil. |
| `tests/test_granola_copilot_zerotouch.py` | `test_granola_copilot_extraction_and_zero_touch_deal_update` | PASSED (100%) | IA extrai notas e preenche dados do negócio sem esforço manual. |
