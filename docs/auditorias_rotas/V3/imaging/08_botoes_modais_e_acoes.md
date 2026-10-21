# 08. Auditoria Anatômica de Botões, Modais & Ações — Rota: imaging (Auditoria V3)

## 1. Inventário Factual de Botões Existentes

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- |
| **Carregar Exame DICOM** | Interação direta | Abre arquivo tomográfico direto do servidor Orthanc | **100% Funcional** |
| **Visualizar Malha STL 3D** | Interação direta | Renderiza malha tridimensional via Three.js / Canvas | **100% Funcional** |
| **Zoom e Rotação 3D** | Interação direta | Controles de órbita e inspeção anatômica do implante | **100% Funcional** |
| **Ajuste de Janela / Brilho (Windowing)** | Interação direta | Regulagem de contraste para osso cortical e trabecular | **100% Funcional** |

---

## 2. Gaps de Interação & Botões Sugeridos
- **Medição de Densidade Óssea (Hounsfield)** (`TICKET-IMG-01`): Régua para aferir unidades HU no sítio de implantação
- **Simulação Virtual de Instalação de Implante** (`TICKET-IMG-02`): Ferramenta para posicionar modelo 3D do parafuso no corte