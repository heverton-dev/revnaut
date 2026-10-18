# Manual da Rota: Video SOS Mesa Cirurgica LiveKit (`#video-sos`)

## 1. Objetivo da Rota
Disponibilizar canal de videoconferencia e teleorientacao de emergencia em 1 clique via WebRTC (LiveKit SFU/SIP) para conectar o cirurgiao na mesa operatoria diretamente ao consultor tecnico ou especialista protetico.

---

## 2. O Que o Usuário Consegue Realizar
* Iniciar ou ingressar em sala de teleorientacao cirurgica na rota `#video-sos`.
* Transmitir audio e video de alta definicao com baixa latencia.
* Compartilhar tela ou exame tomografico periapical durante a cirurgia.
* Gravar sessoes de consultoria cirurgica no Cloudflare R2 para fins de conformidade e auditoria.
* Conectar via chamada de voz SIP caso a clinica nao possua conexao de dados estavel.

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil | Abertura de SOS | Atendimento Tecnico | Gravacao de Chamada | Auditoria de Videos |
|---|---|---|---|---|
| Cirurgiao Cadastrado | Sim | Nao | Automatica | Apenas seus exames |
| Consultor Tecnico | Sim | Sim | Sim | Sim (de sua equipe) |
| Gestor de Suporte | Sim | Sim | Sim | Sim (regional) |
| Diretor / Super Admin | Sim | Sim | Sim | Sim (Total) |

---

## 4. Quais Ações Podem Ser Realizadas
* `START_SOS_CALL`: Abrir sala de conferencia instantanea no LiveKit.
* `MUTE_UNMUTE`: Alternar estado de microfone e camera.
* `SHARE_EXAM`: Apresentar exame DICOM ou modelo STL no video.
* `RECORD_SESSION`: Disparar gravacao segura da chamada.
* `END_CALL`: Finalizar sessao e anexar relatorio ao prontuario.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)

### Acionamento de Video SOS em Campo
1. No menu lateral, clique em "Video SOS Cirurgico" na rota `#video-sos`.
2. Clique no botao "Acionar SOS Mesa Cirurgica".
3. A sala WebRTC e gerada e os consultores tecnicos de plantao sao alertados simultaneamente via push e WhatsApp.
4. O consultor disponivel atende e ingressa imediatamente na chamada com visao compartilhada.

---

## 6. O Que Falta Implementar
* Reconhecimento automatico de comandos por voz para cirurgioes com as maos esterilizadas no campo cirurgico.
