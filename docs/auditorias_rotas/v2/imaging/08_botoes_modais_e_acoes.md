# 08. Auditoria Anatômica de Botões, Modais & Ações de Interface — Rota: imaging (Auditoria v2)

## 1. Inventário Factual de Botões Existentes na Rota

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | O Que Abre / Dispara | Por Que Existe (Propósito de Negócio) | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Carregar Exame DICOM** | Interação direta | Abre arquivo tomográfico direto do servidor Orthanc | Ação reativa | Suporte operacional | **100% Funcional** |
| **Visualizar Malha STL 3D** | Interação direta | Renderiza malha tridimensional via Three.js / Canvas | Ação reativa | Suporte operacional | **100% Funcional** |
| **Zoom e Rotação 3D** | Interação direta | Controles de órbita e inspeção anatômica do implante | Ação reativa | Suporte operacional | **100% Funcional** |
| **Ajuste de Janela / Brilho (Windowing)** | Interação direta | Regulagem de contraste para osso cortical e trabecular | Ação reativa | Suporte operacional | **100% Funcional** |

---

## 2. Modais e Gavetas (Drawers) na Rota
As ações de alta densidade disparam formulários em modais Dialog centralizados ou gavetas laterais Sheet, garantindo que o operador não perca o contexto de navegação.

---

## 3. Catálogo de Botões Faltantes (Gaps de Interação & UX)

| Botão Faltante | Localização Sugerida na Tela | O Que Deveria Abrir / Fazer | Por Que Está Faltando (Impacto na Jornada) | Micro-Ticket Vinculado |
| :--- | :--- | :--- | :--- | :--- |
| **Medição de Densidade Óssea (Hounsfield)** | Barra de ações da rota | Régua para aferir unidades HU no sítio de implantação | Lacuna identificada no fluxo | `TICKET-IMG-01` |
| **Simulação Virtual de Instalação de Implante** | Barra de ações da rota | Ferramenta para posicionar modelo 3D do parafuso no corte | Lacuna identificada no fluxo | `TICKET-IMG-02` |
