# 01. Visão Geral e Jornada do Usuário — Rota: imaging (Auditoria V3)

## 1. Identificação Técnica
- **Rota Visual:** `https://revnault.vpsconexao.org/#!/imaging`
- **Título Oficial:** Exames 3D e Tomografias (DICOM / STL Viewer)
- **Componente Front-end:** `frontend/src/features/imaging/DicomStl3DViewer.tsx`
- **Motores Backend:** `src/features/imaging/router.py`, `src/features/contracts/router.py`
- **Suíte de Testes:** `tests/test_orthanc_dicom_stl_r2.py`, `tests/test_r2_storage.py`

---

## 2. Jornada do Usuário Real
O usuário acessa o módulo para executar operações cirúrgicas e comerciais sem atrito:
1. **Entrada na Tela:** Carregamento otimizado com dados reais via SQLite WAL.
2. **Navegação por Abas:** Alternância fluida entre as visões do módulo.
3. **Ações Primárias:** Interação com botões de alta densidade sem stubs ou toasts vazios.

---

## 3. Abas e Sub-Rotas Mapeadas
- **Aba `dicom_cone_beam`:** Tomografia Computadorizada Cone Beam
- **Aba `stl_3d`:** Malhas STL 3D de Guias Cirúrgicos
- **Aba `mpr_slices`:** Cortes Multiplanares (Axial, Sagital, Coronal)