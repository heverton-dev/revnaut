# 01. Visão Geral e Jornada do Usuário — Rota: imaging (Auditoria v2)

## 1. Identificação e Roteamento
- **Identificador / Slug:** `imaging`
- **Título Visual no Sistema:** Exames 3D e Tomografias (DICOM / STL Viewer)
- **Classificação:** Frontend SPA View (Single Page Application com Hashbang Router)
- **URL Canônica:** `https://revnault.vpsconexao.org/#!/imaging`
- **Componente React Raiz:** `frontend/src/features/imaging/DicomStl3DViewer.tsx`
- **Ciclo de Auditoria:** v2 (Pós-implementação de gaps e tickets de produção)

---

## 2. Propósito e Objetivo de Negócio
A rota `imaging` atua no ecossistema RevNault proporcionando aos operadores clínicos e comerciais:
1. Controle determinístico dos fluxos de exames 3d e tomografias (dicom / stl viewer).
2. Redução do tempo de atendimento operacional e eliminação de processos analógicos em campo.
3. Rastreabilidade regulatória ponta a ponta com persistência auditável em SQLite WAL.

---

## 3. Abas e Sub-rotas Mapeadas
- **Aba / Sub-aba `dicom_cone_beam`:** Tomografia Computadorizada Cone Beam
- **Aba / Sub-aba `stl_3d`:** Malhas STL 3D de Guias Cirúrgicos
- **Aba / Sub-aba `mpr_slices`:** Cortes Multiplanares (Axial, Sagital, Coronal)

---

## 4. Jornada e Fluxo Operacional
O usuário autenticado acessa a rota `#!/imaging`. O sistema valida os privilégios do papel ativo no RBAC e carrega os dados específicos da fatia vertical de backend de forma reativa. O operador interage através dos controles dedicados sem recarregar a aplicação.
