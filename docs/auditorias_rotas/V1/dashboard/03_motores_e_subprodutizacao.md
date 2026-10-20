# 03. Motores de Backend e Subprodutização — Rota: dashboard

## 1. Motores Subjacentes do Ecossistema

O Cockpit Executivo conecta-se a 4 motores de domínio especializados:

```
[Frontend: SupersetEmbeddedDashboard]
          │
          ├──► [Motor 1: Deals & Revenue Pipeline]
          │      └── Endpoint: GET /api/v1/metrics | GET /api/v1/deals
          │      └── Repositório: SQLite WAL com agregação determinística de estágios
          │
          ├──► [Motor 2: Growth & Media Attribution]
          │      └── Endpoint: GET /api/v1/campaigns/metrics
          │      └── Cálculos: ROAS ponderado, CAC médio e contagem de leads
          │
          ├──► [Motor 3: Algoritmo RFM Odontológico & Grafo Clínico]
          │      └── Endpoint: GET /api/v1/intelligence/churn-risk
          │      └── Endpoint: GET /api/v1/intelligence/clinical-graph
          │      └── Topologia: Cirurgiões, Clínicas, Laboratórios CAD/CAM, Polos Universitários
          │
          └──► [Motor 4: Cloudflare R2 Data Storage & Superset Guest Token]
                 └── Endpoint: POST /api/v1/intelligence/bi/export-dataset
                 └── Endpoint: POST /api/v1/intelligence/bi/guest-token
                 └── Persistência: Chaves no bucket R2 com criptografia em trânsito
```

---

## 2. Análise de Subprodutização do Motor (Capacidades Ociosas)

Subprodutização ocorre quando o backend já possui funcionalidades robustas implementadas e testadas, mas a interface do usuário consome apenas uma fração reduzida dessas capacidades.

| Motor / Recurso no Backend | Capacidade Implementada no Backend | O Que a Rota/Tela Consome Atualmente | Diagnóstico de Subprodutização & Potencial |
| :--- | :--- | :--- | :--- |
| **Radar Anti-Churn RFM** (`src/features/intelligence/router.py`) | Suporta parâmetro de consulta `days_threshold` para filtrar clientes por janela temporal de atraso personalizada, além de segregação por `tier` (VIP, Regular, Inativo). | Executa a chamada sem parâmetros (`GET /churn-risk`), trazendo apenas a lista padrão com slice estático dos primeiros 6 itens. | **Subprodutização Média:** Falta adicionar na UI um seletor rápido de janela de dias (30d, 60d, 90d+) para o diretor focar em faixas específicas de risco. |
| **Topologia do Grafo Clínico** (`src/features/intelligence/router.py`) | Retorna nós e arestas direcionadas com atributos `relationship` ("opera_em", "prescreve", "palestrante_kol") e flag booleana `is_kol`. | Renderiza apenas cards numéricos agregados e uma listagem vertical simples dos primeiros 8 nós. | **Subprodutização Alta:** As arestas e conexões entre cirurgiões e laboratórios CAD/CAM estão disponíveis no payload, mas não há visualizador visual de teia/grafo interativo no Cockpit. |
| **Exportação de Datasets Analíticos** (`src/features/intelligence/router.py`) | Aceita parâmetros `format="csv"` e `format="parquet"` para geração de arquivos analíticos colunares de alta performance. | A interface fixa hardcoded a exportação exclusivamente no formato `"csv"` (`handleExportDataset("csv")`). | **Subprodutização Baixa/Média:** O backend está pronto para emitir arquivos Apache Parquet para ingestão direta em Data Lakes / Databricks, mas o botão na tela não oferece essa opção. |
| **Estágios e Oportunidades do Funil** (`src/features/deals/router.py`) | Retorna detalhes por regional, responsável (`owner_id`) e probabilidade ponderada de fechamento. | O gráfico de estágio na tela apenas soma os valores absolutos sem drill-down por regional ou consultor. | **Subprodutização Média:** A tela poderia permitir filtrar o funil do dashboard pela regional comercial selecionada. |

---

## 3. Recomendações de Ativação do Motor Ocioso

1. **Expor Seletor de Formato na Exportação:** Permitir que o usuário escolha entre CSV convencional ou Apache Parquet para analistas de dados.
2. **Adicionar Filtro Temporal no Radar RFM:** Incluir um `Select` com opções: "Todos os riscos", "Críticos (> 45 dias)", "Em Alerta (30 a 45 dias)".
3. **Drill-down de Nós do Grafo:** Permitir clicar em um cirurgião KOL para destacar instantaneamente quais clínicas e laboratórios estão vinculados àquele profissional.
