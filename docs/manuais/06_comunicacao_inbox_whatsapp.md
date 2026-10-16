# Manual da Rota: Inbox WhatsApp & Comunicações (`/#inbox`)

## 1. Objetivo da Rota
Centralizar conversas, mensagens e interações de suporte comercial com cirurgiões-dentistas através da integração omnichannel com WhatsApp. Evita que dados de negociação fiquem dispersos nos celulares particulares dos consultores.

---

## 2. O Que o Usuário Consegue Realizar
* Visualizar conversas ativas com cirurgiões organizadas por ordem cronológica e status de atendimento.
* Trocar mensagens de texto diretamente com o profissional de saúde.
* Enviar tabelas de preços, catálogos técnicos em PDF e laudos de biocompatibilidade.
* Registrar notas internas visíveis apenas para a equipe comercial durante o atendimento.

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil | Visualizar Conversas | Responder Mensagens | Transferir Atendimento |
|---|---|---|---|
| Consultor de Vendas | Apenas conversas de seus contatos atribuídos | Sim | Sim (para suporte técnico) |
| SAC / Suporte Clínico | Todas as conversas de dúvidas técnicas | Sim | Sim |
| Gerente Comercial | Todas as conversas da equipe regional | Sim | Sim |
| Super Admin | Acesso irrestrito a todas as conversas | Sim | Sim |

---

## 4. Quais Ações Podem Ser Realizadas
* `SEND_MESSAGE`: Enviar texto ou arquivo pela API oficial do WhatsApp Business.
* `ADD_INTERNAL_NOTE`: Gravar nota interna confidencial na thread da conversa.
* `TRANSFER_CHAT`: Transferir a conversa para outro consultor ou para o instrumentador cirúrgico.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)
1. Acesse **Operações & Carteira > Inbox WhatsApp**.
2. Na coluna esquerda, selecione o cirurgião desejado (ex: "Dr. Carlos Eduardo - CRO 44102").
3. A timeline de mensagens será exibida na coluna central.
4. Digite a mensagem no campo inferior e clique em "Enviar" ou pressione Enter.
5. Para registrar um alinhamento interno sem notificar o cliente, alterne para o modo "Nota Interna".

---

## 6. O Que Falta Implementar (Roadmap & Gaps)
* Conector oficial com a API do WhatsApp Cloud / Gupshup / Z-API com webhooks bidirecionais ativos.
* Transcrição automática de áudios enviados pelos cirurgiões utilizando modelo Whisper / Gemini.
* Templates aprovados pela Meta para disparo de notificações de envio de caixas cirúrgicas.
