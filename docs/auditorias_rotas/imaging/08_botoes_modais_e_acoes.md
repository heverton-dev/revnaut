# 08. Auditoria Anatômica de Botões, Modais & Ações de Interface — Rota: imaging

## 1. Inventário Factual de Botões Existentes na Rota

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | O Que Abre / Dispara | Por Que Existe (Propósito de Negócio) | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Carregar Tomografia** | Interação direta | Upload de série DICOM para bucket médico seguro | Ação reativa | Suporte operacional | **100% Funcional** |
| **Ajustar Brilho / Contraste (Janela Óssea)** | Interação direta | Regula visualização de densidade óssea mandibular | Ação reativa | Suporte operacional | **100% Funcional** |
| **Rotacionar Modelo 3D STL** | Interação direta | Manipulação tridimensional do guia cirúrgico | Ação reativa | Suporte operacional | **100% Funcional** |
| **Medir Distância Óssea (Régua)** | Interação direta | Ferramenta de medição em milímetros para escolha do implante | Ação reativa | Suporte operacional | **100% Funcional** |

---

## 2. Modais e Gavetas (Drawers) na Rota
As ações de alta complexidade disparam formulários em modais Dialog centralizados ou gavetas laterais Sheet, garantindo que o operador não perca o contexto de navegação.

---

## 3. Catálogo de Botões Faltantes (Gaps de Interação & UX)

| Botão Faltante | Localização Sugerida na Tela | O Que Deveria Abrir / Fazer | Por Que Está Faltando (Impacto na Jornada) | Micro-Ticket Vinculado |
| :--- | :--- | :--- | :--- | :--- |
| **Simulação de Posicionamento do Implante** | Barra de ações da rota | Inserção de modelo 3D virtual do implante no corte tomográfico | Lacuna identificada no fluxo | `TICKET-IMG-01` |
| **Exportar Guia Cirúrgico em STL** | Barra de ações da rota | Download do arquivo preparado para impressão 3D | Lacuna identificada no fluxo | `TICKET-IMG-02` |
