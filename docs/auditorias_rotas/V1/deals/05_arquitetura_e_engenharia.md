# 05. Arquitetura e Engenharia de Software — Rota: deals

## 1. Aderência à Arquitetura VSA (Vertical Slice Architecture)

A rota de Negociações apresenta excelente separação de responsabilidades no backend, mas possui concentração de código no frontend:

- **Frontend (`frontend/src/App.tsx`):**
  - O código de renderização do funil, tabela, kanban e drawer lateral está acoplado diretamente dentro de `App.tsx` (mais de 1.000 linhas).
  - **Recomendação VSA:** Extrair a rota inteira para um módulo autônomo `frontend/src/features/deals/DealsWorkspace.tsx`, deixando `App.tsx` apenas como orquestrador raiz da casca (`AppShell`).

- **Backend (`src/features/deals/`):**
  - A fatia vertical de backend é exemplar: `router.py` cuida dos contratos OpenAPI, `service.py` aplica regras de negócio e limites de crédito, e `repository.py` gerencia o acesso ao SQLite WAL.

---

## 2. Desempenho e Concorrência

- **Gerenciamento de Cache com React Query:**
  - Utiliza `useQuery` com chave `["deals", selectedPipelineId, currentUserId]`, garantindo invalidação cirúrgica de cache e evitando buscas redundantes no banco ao alternar entre abas.
- **Transacionalidade ACID:**
  - Alterações de estágio e aprovações de crédito são executadas em bloco transacional com o SQLite WAL, garantindo que o status do negócio e a linha do tempo sejam gravados juntos ou abortados em caso de falha.
