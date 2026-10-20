# 01. Visão Geral e Jornada do Usuário — Rota: keypartners (Auditoria v2)

## 1. Identificação e Roteamento
- **Identificador / Slug:** `keypartners`
- **Título Visual no Sistema:** Malas em Consignação & KOL (KeyPartners)
- **Classificação:** Frontend SPA View (Single Page Application com Hashbang Router)
- **URL Canônica:** `https://revnault.vpsconexao.org/#!/keypartners`
- **Componente React Raiz:** `frontend/src/features/keypartners/ConsignmentSurgicalBoard.tsx`
- **Ciclo de Auditoria:** v2 (Pós-implementação de gaps e tickets de produção)

---

## 2. Propósito e Objetivo de Negócio
A rota `keypartners` atua no ecossistema RevNault proporcionando aos operadores clínicos e comerciais:
1. Controle determinístico dos fluxos de malas em consignação & kol (keypartners).
2. Redução do tempo de atendimento operacional e eliminação de processos analógicos em campo.
3. Rastreabilidade regulatória ponta a ponta com persistência auditável em SQLite WAL.

---

## 3. Abas e Sub-rotas Mapeadas
- **Aba / Sub-aba `kits`:** Inventário de Maletas & Rastreabilidade ANVISA
- **Aba / Sub-aba `agreements`:** Termos de Consignação & Notas CFOP 5.113
- **Aba / Sub-aba `kol`:** Contratos de Parceria KOL & Speakers
- **Aba / Sub-aba `loyalty`:** Programa de Fidelidade e Pontos de Consumo

---

## 4. Jornada e Fluxo Operacional
O usuário autenticado acessa a rota `#!/keypartners`. O sistema valida os privilégios do papel ativo no RBAC e carrega os dados específicos da fatia vertical de backend de forma reativa. O operador interage através dos controles dedicados sem recarregar a aplicação.
