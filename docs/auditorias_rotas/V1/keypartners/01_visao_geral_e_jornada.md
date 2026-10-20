# 01. Visão Geral e Jornada do Usuário — Rota: keypartners

## 1. Identificação e Roteamento
- **Identificador / Slug:** `keypartners`
- **Título Visual no Sistema:** Malas em Consignação & Parcerias Clínicas
- **Classificação:** Frontend SPA View (Single Page Application com Hashbang Router)
- **URL de Produção:** `https://revnault.vpsconexao.org/#!/keypartners`
- **Componente React Raiz:** `frontend/src/features/keypartners/ConsignmentSurgicalBoard.tsx`

---

## 2. Propósito e Objetivo de Negócio
A rota `keypartners` atua no ecossistema RevNault proporcionando aos operadores clínicos e comerciais:
1. Controle determinístico dos fluxos de malas em consignação & parcerias clínicas.
2. Redução do tempo de atendimento e eliminação de processos analógicos na operação.
3. Rastreabilidade ponta a ponta com persistência auditável no SQLite WAL.

---

## 3. Abas e Sub-rotas Mapeadas
- **Aba `kits`:** Inventário de Maletas & Rastreabilidade ANVISA
- **Aba `agreements`:** Termos de Consignação & Notas CFOP 5.113
- **Aba `kol`:** Contratos de Parceria KOL & Speakers
- **Aba `loyalty`:** Programa de Fidelidade e Pontos

---

## 4. Jornada e Fluxo Operacional
O usuário acessa `#!/keypartners`, o sistema valida as permissões de RBAC do perfil ativo e carrega os dados específicos da fatia vertical. O operador interage através dos controles dedicados sem recarregar a aplicação.
