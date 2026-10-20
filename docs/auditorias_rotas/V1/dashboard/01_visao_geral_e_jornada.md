# 01. Visão Geral e Jornada do Usuário — Rota: dashboard

## 1. Identificação e Roteamento
- **Identificador / Slug:** `dashboard`
- **Classificação:** Frontend SPA View (Single Page Application com Hashbang Router)
- **URL de Produção:** `https://revnault.vpsconexao.org/#!/dashboard`
- **Componente React Raiz:** `frontend/src/features/bi/SupersetEmbeddedDashboard.tsx`
- **Modo de Renderização Ativo:** `mode="executive_cockpit"`
- **Roteador Principal:** `frontend/src/router.tsx` (linhas 63-69)

---

## 2. Propósito e Objetivo de Negócio
O Cockpit Executivo RevNault consolida em uma única tela gerencial os principais indicadores vitais da operação comercial e clínica de implantes odontológicos:
1. **Pipeline de Vendas em Tempo Real:** Volume total negociado, contagem de oportunidades ativas, taxa de conversão e faturamento fechado ganho (MRR).
2. **Eficiência de Aquisição e Mídia:** Monitoramento de ROAS das campanhas de tráfego, volume de leads qualificados gerados e Custo de Aquisição de Clientes (CAC).
3. **Radar Preditivo Anti-Churn RFM:** Detecção algorítmica de cirurgiões dentistas em risco de interrupção de recompra de implantes (intervalo de recompra estourado).
4. **Ecossistema Clínico KOL:** Visualização da malha de relacionamentos entre cirurgiões implantodontistas credenciados, clínicas, laboratórios CAD/CAM e polos universitários.

---

## 3. Jornada e Fluxo Operacional

```
[Login / Autenticação]
         │
         ▼
[Acesso Direto à URL /#!/dashboard]
         │
         ├─► [Disparo Paralelo: Promise.all]
         │      ├── GET /api/v1/metrics (Deals)
         │      ├── GET /api/v1/campaigns/metrics (Campanhas)
         │      ├── GET /api/v1/intelligence/churn-risk (RFM Anti-Churn)
         │      ├── GET /api/v1/intelligence/clinical-graph (Grafo KOL)
         │      └── GET /api/v1/deals (Estágios do Funil)
         │
         ▼
[Exibição Instantânea dos KPI Cards]
  - Card 1: Pipeline Ativo Total (R$) e Taxa de Conversão
  - Card 2: MRR / Receita Recorrente & Fechado Ganho
  - Card 3: Performance Mídia, ROAS e CAC Médio
  - Card 4: Alertas Críticos de Churn e Nós de KOL Mapeados
         │
         ▼
[Análise Interativa de Indicadores]
  - Gráfico SVG de Barras: Visão por Estágio, Tendência Mensal ou Giro de Consignação
  - Barra Horizontal de Risco Anti-Churn por Cirurgião (com score e ação recomendada)
  - Painel Topológico de Vínculos KOL (Relações N:N entre cirurgião e polo)
         │
         ▼
[Ações Operacionais Disponíveis]
  - Botão "Atualizar Cockpit": Re-executa requisições de telemetria sem recarregar a página
  - Botão "Exportar Snapshot R2": Gera exportação determinística em Parquet/CSV no storage Cloudflare R2
```

---

## 4. Estados de Interface e Tratamento de Exceções
- **Estado de Carregamento (Loading):** Skeletons e flags de desabilitação nos botões de ação (`loadingExecutive=true`, `exporting=true`).
- **Estado Vazio (Empty State):** Mensagem de fallback sem alarmismo quando o radar anti-churn não detecta clientes em risco crítico.
- **Tolerância a Falhas de Rede:** Requisições assíncronas encapsuladas em `try/catch` individual para garantir que a indisponibilidade de métricas de campanhas não impeça a exibição das métricas de vendas.
