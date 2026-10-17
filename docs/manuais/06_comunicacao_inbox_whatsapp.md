# Manual da Rota: Inbox WhatsApp & Comunicações (`/#inbox`)

## 1. Objetivo da Rota
Centralizar conversas, mensagens e interações técnicas com cirurgiões-dentistas através da integração omnichannel com WhatsApp (Evolution API / Chatwoot). Garante a rastreabilidade corporativa de negociações, cotações de caixas cirúrgicas e suporte técnico, eliminando a dispersão de dados em aparelhos particulares.

---

## 2. O Que o Usuário Consegue Realizar
* Visualizar conversas ativas com cirurgiões organizadas por recência e status de atendimento.
* Trocar mensagens de texto diretamente com o profissional de saúde em tempo real.
* Enviar catálogos técnicos em PDF, tabelas de instrumentais e laudos de biocompatibilidade.
* Registrar notas internas confidenciais visíveis apenas para a equipe comercial na mesma thread.
* **Gateway Omnichannel Unificado (`src/features/integrations/omnichannel/`):**
  * Recebimento e processamento de webhooks da **Evolution API v2** e **Chatwoot** com validação HMAC.
  * Atualização dinâmica de engajamento no Lead Scoring quando o cirurgião interage.
  * Arquitetura Ports & Adapters: operação com `InMemoryMockAdapter` em testes locais e conexão aos containers oficiais na VPS Swarm.

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil | Visualizar Conversas | Responder Mensagens | Transferir Atendimento | Ver Notas Internas |
|---|---|---|---|---|
| Consultor de Vendas | Apenas conversas de seus contatos atribuídos (`owner_id`) | Sim | Sim (para suporte técnico) | Sim |
| SAC / Suporte Clínico | Todas as conversas de dúvidas técnicas e instrumentação | Sim | Sim | Sim |
| Gerente Comercial | Todas as conversas da equipe regional (`team_id`) | Sim | Sim | Sim |
| Super Admin (Heverton) | Acesso irrestrito a todas as conversas corporativas | Sim | Sim | Sim |

---

## 4. Quais Ações Podem Ser Realizadas
* `SEND_MESSAGE`: Enviar texto ou arquivo pela API do WhatsApp integrada.
* `ADD_INTERNAL_NOTE`: Gravar nota interna confidencial na timeline da conversa.
* `TRANSFER_CHAT`: Transferir a conversa para outro consultor ou instrumentador cirúrgico.
* `WEBHOOK_RECEIVE`: Ingestão de mensagens recebidas via `/api/v1/webhooks/evolution` ou `/api/v1/webhooks/chatwoot`.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)
1. Acesse **Operações & Carteira > Inbox WhatsApp**.
2. Na coluna esquerda, selecione o cirurgião desejado (ex: "Dr. Carlos Eduardo - CRO 44102").
3. A timeline de mensagens será exibida na coluna central.
4. Digite a mensagem no campo inferior e clique em "Enviar" ou pressione Enter.
5. Para registrar um alinhamento interno sem notificar o cirurgião, alterne para o modo "Nota Interna".
6. Caso o cirurgião envie uma solicitação urgente de kit cirúrgico, utilize a opção "Transferir Atendimento" para encaminhar o chat ao instrumentador responsável.

---

## 6. O Que Falta Implementar (Roadmap & Gaps)
* Transcrição automática de áudios longos enviados pelos cirurgiões utilizando modelo Whisper / Gemini.
* Templates oficiais HSM pré-aprovados pela Meta para disparo automático de tracking de rastreio de caixas cirúrgicas despachadas via transportadora.
* Chatbot de triagem clínica inicial para identificação prévia do tipo de cirurgia (Unitária, Múltipla, Carga Imediata, Zigomático).

---

## ANOTAÇÕES DO HEVERTON

* **[ARQUITETURA DUAL PORTS & ADAPTERS]**: No ambiente local de desenvolvimento, os testes operam com `InMemoryMockAdapter` com latência zero de rede; na VPS de produção, o sistema conecta-se aos webhooks reais da Evolution API.
* **[ENGAGEMENT SCORE]**: Cada resposta recebida de cirurgião via WhatsApp incrementa a nota de engajamento do contato no Lead Scoring ICP.
