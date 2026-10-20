# 06. Especificação DD (TDD, BDD, SDD) — Rota: dashboard

## 1. Especificação BDD (Behavior-Driven Development) em Gherkin

```gherkin
Funcionalidade: Cockpit Executivo RevNault e Indicadores Vitais da Carteira
  Como Diretor Comercial ou Gestor de RevNault
  Eu quero acessar o dashboard consolidado
  Para monitorar a receita de vendas, ROAS de mídia e saúde da carteira de cirurgiões

  Cenário: Carregamento do Cockpit com Métricas Vitais
    Dado que o usuário está autenticado com o perfil "Diretor Nacional"
    Quando navega para a rota "/#!/dashboard"
    Então o sistema dispara requisições assíncronas concorrentes para os endpoints de métricas
    E exibe o Card de "Pipeline Ativo Total" com o valor monetário formatado em BRL
    E exibe o Card de "MRR / Receita Recorrente" com o fechado ganho
    E exibe o Card de "Performance Mídia & ROAS" com o multiplicador ponderado
    E exibe o Card de "Grafo Clínico & Radar Churn" com a contagem de nós e alertas críticos

  Cenário: Detecção e Alerta de Risco Anti-Churn RFM
    Dado que existem cirurgiões na base sem recompra de implantes há mais de 45 dias
    Quando o Cockpit processa a resposta de "GET /api/v1/intelligence/churn-risk"
    Então renderiza a barra de risco na cor de alerta correspondente (vermelho para crítico)
    E exibe a ação corretiva recomendada para o consultor comercial daquela conta

  Cenário: Exportação de Snapshot Analítico para Cloudflare R2
    Dado que o usuário visualiza o Cockpit Executivo
    Quando clica no botão "Exportar Snapshot R2"
    Então o sistema submete a requisição para "POST /api/v1/intelligence/bi/export-dataset"
    E exibe um toast de confirmação contendo a chave de persistência e a contagem de registros exportados
    E reabilita o botão após a finalização com sucesso

  Cenário: Bloqueio de Acesso por Usuário Não Autenticado
    Dado que a sessão do usuário expirou ou o token JWT é inválido
    Quando o usuário tenta acessar "/#!/dashboard"
    Então o sistema intercepta a rota e redireciona imediatamente para "/#!/login"
```

---

## 2. Contratos TDD (Test-Driven Development) Red-Green

| Arquivo de Teste | Suíte de Teste / Função | Status Atual | Critério de Aceitação |
| :--- | :--- | :--- | :--- |
| `tests/test_clinical_graph_churn.py` | `test_dental_rfm_churn_risk_radar` | PASSED (100%) | Retorna scores RFM calculados e recomendações por cirurgião. |
| `tests/test_clinical_graph_churn.py` | `test_clinical_graph_and_kol_speakers_identification` | PASSED (100%) | Mapeia relacionamentos entre cirurgiões e laboratórios CAD/CAM. |
| `tests/test_superset_rls_embedded.py` | `test_export_analytics_dataset` | PASSED (100%) | Gera snapshot no storage R2 retornando status 200 e chave válida. |
| `tests/test_text_to_sql_security.py` | `test_security_blocks_destructive_drop_table` | PASSED (100%) | Bloqueia AST maliciosa e previne mutações SQL no banco. |

---

## 3. Matriz SDD (Spec-Driven Development) de Invariantes

- **INV-DASH-01 (Zero Emojis):** Todo elemento visual na rota deve utilizar estritamente SVGs vetoriais (Lucide React) ou tags HTML canônicas.
- **INV-DASH-02 (Concorrência sem Bloqueio):** Métricas agregadas de tela devem ser carregadas em paralelo sem encadeamento de waterfalls.
- **INV-DASH-03 (Isolamento de Tenant RLS):** Nenhuma métrica ou cirurgião pode ser exibido sem filtro obrigatório pelo `account_id` do usuário conectado.
