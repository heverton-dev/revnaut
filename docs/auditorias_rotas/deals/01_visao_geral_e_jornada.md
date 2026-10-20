# 01. Visão Geral e Jornada do Usuário — Rota: deals

## 1. Identificação e Roteamento
- **Identificador / Slug:** `deals`
- **Classificação:** Frontend SPA View (Single Page Application com Hashbang Router)
- **URL de Produção:** `https://revnault.vpsconexao.org/#!/deals`
- **Componentes React Principais:** `frontend/src/App.tsx` (linhas 148-1120), `frontend/src/components/ui/KanbanBoard.tsx`, `frontend/src/components/ui/DataTable.tsx` e `frontend/src/features/deals/components/GranolaCopilotCard.tsx`.
- **Roteador Principal:** `frontend/src/router.tsx` (linhas 53-54).

---

## 2. Propósito e Objetivo de Negócio
A rota de Negociações (`deals`) é o coração operacional do CRM cirúrgico de implantes odontológicos:
1. **Gestão Visual do Pipeline:** Visualização bifuncional por Quadro Kanban arrastável ou Tabela densa paginada.
2. **Ciclo de Vida do Negócio:** Acompanhamento dos 5 estágios canônicos da venda clínica: Qualificação, Diagnóstico 3D, Proposta Comercial, Contrato e Fechado Ganho.
3. **Cockpit de Fechamento Integrado (Drawer Lateral):** Ao clicar em um negócio, abre-se uma gaveta operacional contendo:
   - Resumo financeiro e risco de crédito com trava automática caso o limite do cliente seja excedido.
   - Copilot Comercial Granola para transcrição e extração automática de notas de reunião cirúrgica.
   - Sala de Videoconferência LiveKit SOS para contato direto com o cirurgião em campo.
   - Edição inline de valor, probabilidade, estágio e prioridade.
   - Vinculação de contratos e minutas regulatórias Documenso.
   - Trilha de auditoria e linha do tempo imutável de alterações.

---

## 3. Jornada e Fluxo Operacional

```
[Acesso Direto à URL /#!/deals]
         │
         ├─► [Disparo Paralelo: React Query]
         │      ├── GET /api/v1/pipelines (Lista funis disponíveis)
         │      ├── GET /api/v1/metrics (Métricas financeiras do funil)
         │      └── GET /api/v1/deals?pipeline_id=... (Oportunidades filtradas pelo RLS do usuário)
         │
         ▼
[Exibição de Indicadores do Topo]
  - Card 1: Negócios no Funil (Quantidade de oportunidades ativas)
  - Card 2: Valor do Pipeline Ativo (R$)
  - Card 3: Receita Faturada / Fechado Ganho (MRR)
  - Card 4: Ticket Médio Cirúrgico
         │
         ▼
[Barra de Filtro e Controles]
  - Seletor de Pipeline Comercial (Select de Funil)
  - Input de Busca Textual Instantânea (Nome da clínica, cirurgião ou produto)
  - Alternador de Visualização: Botão "Tabela" vs Botão "Kanban"
  - Botão "Novo Negócio" (Abre modal Dialog)
  - Botão "Exportar CSV" (Download instantâneo de dados)
         │
         ▼
[Visualização do Funil]
  ├─ Se Modo Tabela: Exibe DataTable paginada com ordenação de colunas e badges de prioridade
  └─ Se Modo Kanban: Exibe colunas por estágio com contadores de quantidade e somatório em R$
         │
         ▼
[Interação com Card / Linha: Abertura do Drawer Lateral]
  - Visualização de detalhes completos da oportunidade
  - Ajuste de campos com gravação imediata (PUT /api/v1/deals/{id})
  - Execução de ações de aprovação de crédito e consulta da Linha do Tempo
```
