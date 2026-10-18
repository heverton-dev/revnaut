# Manual da Rota: Imagiologia DICOM & STL 3D (`#dicom-viewer`)

## 1. Objetivo da Rota
Visualizar, manipular e analisar exames tomograficos volumetricos odontologicos (CBCT Cone-Beam) em formato DICOM e malhas tridimensionais STL de arcos e guias cirurgicos diretamente no navegador via WebGL, sem necessidade de softwares pesados instalados localmente.

---

## 2. O Que o Usuário Consegue Realizar
* Carregar estudos tomograficos DICOM e arquivos STL na rota `#dicom-viewer`.
* Alternar entre eixos de corte axial, sagital e coronal com controle de contraste e brilho (Window/Level).
* Rotacionar, aplicar zoom e medir distancias milimetricas em modelos tridimensionais de arcos dentarios.
* Armazenar e consultar exames associados a deals ou cirurgioes no servidor Orthanc integrado ao Cloudflare R2.
* Gerar link temporario e seguro de compartilhamento de exame.

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil | Visualizacao de Exames | Upload de Tomografias | Medicoes Milimetricas | Download de Arquivos STL |
|---|---|---|---|---|
| Cirurgiao Titular | Sim | Sim | Sim | Sim |
| Consultor Tecnico | Sim | Sim | Sim | Sim |
| Clinica Parceira | Sim (de seus pacientes) | Sim | Sim | Sim |
| Super Admin | Acesso irrestrito ao PACS | Sim | Sim | Sim (Total) |

---

## 4. Quais Ações Podem Ser Realizadas
* `LOAD_STUDY`: Carregar exame pelo ID do estudo tomografico.
* `ADJUST_SLICE`: Navegar entre fatias axiais, coronais e sagitais.
* `ROTATE_STL_3D`: Rotacionar malha 3D em 360 graus.
* `MEASURE_BONE`: Realizar medicao linear de densidade e espessura ossea.
* `EXPORT_VIEW`: Exportar captura do planejamento cirurgico.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)

### Visualizacao de Exame 3D
1. Acesse o menu lateral e clique em "Tomografias DICOM 3D" na rota `#dicom-viewer`.
2. Selecione o caso cirurgico na lista de estudos disponiveis.
3. Utilize os controles do visualizador para inspecionar os planos de corte e o modelo STL do guia cirurgico.

---

## 6. O Que Falta Implementar
* Planejamento automatizado de posicionamento de implantes com deteccao por visao computacional do canal mandibular.
