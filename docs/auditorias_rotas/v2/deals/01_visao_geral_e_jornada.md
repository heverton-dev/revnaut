# 01. Visão Geral e Jornada do Usuário — Rota: deals (Auditoria v2)

## 1. Identificação e Roteamento
- **Identificador / Slug:** `deals`
- **Título Visual no Sistema:** Negociações & Funil Comercial (CRM Cirúrgico)
- **Classificação:** Frontend SPA View (Single Page Application com Hashbang Router)
- **URL Canônica:** `https://revnault.vpsconexao.org/#!/deals`
- **Componente React Raiz:** `frontend/src/features/deals/DealsWorkspace.tsx`
- **Ciclo de Auditoria:** v2 (Pós-implementação de gaps e tickets de produção)

---

## 2. Propósito e Objetivo de Negócio
A rota `deals` atua no ecossistema RevNault proporcionando aos operadores clínicos e comerciais:
1. Controle determinístico dos fluxos de negociações & funil comercial (crm cirúrgico).
2. Redução do tempo de atendimento operacional e eliminação de processos analógicos em campo.
3. Rastreabilidade regulatória ponta a ponta com persistência auditável em SQLite WAL.

---

## 3. Abas e Sub-rotas Mapeadas
- **Aba / Sub-aba `kanban`:** Quadro Kanban Interativo Drag-and-Drop
- **Aba / Sub-aba `table`:** Visão Tabela Densa e Paginada
- **Aba / Sub-aba `stage_qualificacao`:** Estágio: Qualificação Técnica
- **Aba / Sub-aba `stage_diagnostico_3d`:** Estágio: Diagnóstico 3D Tomográfico
- **Aba / Sub-aba `stage_proposta`:** Estágio: Proposta Comercial
- **Aba / Sub-aba `stage_contrato`:** Estágio: Minuta e Assinatura de Contrato
- **Aba / Sub-aba `stage_fechado_ganho`:** Estágio: Negócio Fechado Ganho (MRR)

---

## 4. Jornada e Fluxo Operacional
O usuário autenticado acessa a rota `#!/deals`. O sistema valida os privilégios do papel ativo no RBAC e carrega os dados específicos da fatia vertical de backend de forma reativa. O operador interage através dos controles dedicados sem recarregar a aplicação.
