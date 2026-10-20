# 03. Motores de Backend e Subprodutização — Rota: deals

## 1. Motores Subjacentes do Ecossistema

A rota de Negociações conecta-se a 5 motores transacionais especializados:

```
[Frontend: App.tsx / Deals View]
          │
          ├──► [Motor 1: Pipelines & Deals CRUD Engine]
          │      └── Endpoints: GET /api/v1/deals | POST /api/v1/deals | PUT /api/v1/deals/{id}
          │      └── Persistência: SQLite WAL com transações atômicas ACID
          │
          ├──► [Motor 2: Motor de Auditoria & Timeline Imutável]
          │      └── Endpoint: GET /api/v1/deals/{id}/timeline
          │      └── Rastreabilidade: Gravação automática de autor, timestamp e delta de campos alterados
          │
          ├──► [Motor 3: Motor Regulatório & Trava de Limite de Crédito]
          │      └── Endpoint: POST /api/v1/deals/{id}/approve-credit
          │      └── Regra de Negócio: Bloqueia fechamento se o saldo em aberto da clínica exceder o teto
          │
          ├──► [Motor 4: Catálogo Técnico & Tabelas de Preço Odontológicas]
          │      └── Endpoints: GET /api/v1/deals/catalog/products | GET /api/v1/deals/catalog/price-tables
          │      └── Domínio: Implantes cônicos, titânio grau 4, kits protéticos e preços diferenciados
          │
          └──► [Motor 5: Copilot Granola Zero-Touch & LiveKit SOS]
                 └── Endpoint: POST /api/v1/deals/copilot/extract
                 └── Endpoint: POST /api/v1/communications/livekit/rooms
```

---

## 2. Análise de Subprodutização do Motor (Capacidades Ociosas)

| Motor / Recurso no Backend | Capacidade Implementada no Backend | O Que a Rota/Tela Consome Atualmente | Diagnóstico de Subprodutização & Potencial |
| :--- | :--- | :--- | :--- |
| **Catálogo de Produtos Odontológicos** (`src/features/deals/router.py`) | Expõe catálogo técnico completo com códigos ANVISA, diâmetros, plataformas protéticas e tabelas de preço com desconto por volume (`/catalog/products` e `/catalog/price-tables`). | A tela permite apenas inserir um valor numérico solto no campo "Valor da Oportunidade (R$)", sem vincular os produtos específicos. | **Subprodutização Alta:** O backend possui motor completo de catálogo odontológico pronto, mas a UI não expõe o seletor de produtos ao criar ou editar negócios. |
| **Vinculação de Contratos Documenso** (`src/features/deals/router.py`) | O backend possui endpoint dedicado `GET /api/v1/deals/{deal_id}/contracts` para listar minutas jurídicas, termos de garantia e laudos ANVISA vinculados ao deal. | A interface renderiza apenas uma menção simples de texto, sem permitir criar ou enviar contratos diretamente da tela de negócios. | **Subprodutização Média:** O consultor é forçado a alternar de tela para gerar o contrato formal. |
| **Filtro de Funil por Regional e Owner** (`src/features/deals/router.py`) | O endpoint aceita parâmetros avançados `owner_id`, `priority` e `stage_id` para filtragem fina. | A interface filtra apenas por `pipeline_id` e busca textual no cliente, sem dropdown de seleção de consultor responsável. | **Subprodutização Média:** Gestores não conseguem isolar a visão por consultor comercial específico no funil. |
