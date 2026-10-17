---
name: team-handoff
description: Protocolo determinístico de passagem de bastão (shift handover) e revezamento de desenvolvedores no Antigravity sem perda de contexto, histórico ou cota diária. Use quando o usuário digitar /handoff, /retomar, pedir para passar a tarefa para outro dev ou quando a cota da conta estiver esgotada.
---

# Protocolo Team Handoff & Troca de Desenvolvedores

Esta skill padroniza a alternância contínua entre desenvolvedores da equipe em um mesmo ambiente de trabalho no Antigravity, garantindo **zero perda de contexto**, **zero retrabalho** e recuperação instantânea do ponto exato onde o desenvolvedor anterior parou.

---

## 1. Quando Ativar

- **Passagem de Turno**: Um desenvolvedor encerrou seu expediente ou precisa passar a tarefa para outro membro da equipe.
- **Esgotamento de Cota (Quota Exceeded / Rate Limit)**: A cota de tokens diária do dev atual estourou e outro dev precisa assumir a sessão imediatamente com suas credenciais.
- **Retomada de Contexto**: Um novo desenvolvedor abre o projeto e quer saber o status exato e a próxima ação imediata.

---

## 2. Comandos do Protocolo

### A. Comando `/handoff` (Congelar & Passar o Bastão)
Quando o desenvolvedor atual precisa sair ou sua cota esgota:

1. **Executar Diagnóstico Automático**:
   - Rodar `python scripts/handoff.py create` (ou coletar `git status -s`, testes pendentes e arquivos abertos).
2. **Gerar Snapshot em `secoes/HANDOFF_ATIVO.md`**:
   O arquivo deve conter estritamente:
   - **Desenvolvedor Cedente**: Nome/Slot (`DEV_01`, etc.) e timestamp UTC/local.
   - **Objetivo Atual**: O que estava sendo construído no momento do congelamento.
   - **Estado do Workspace**: Arquivos alterados não commitados (`git status -s`).
   - **Status da Suíte de Testes**: Último resultado dos testes (`pytest`).
   - **Invariantes Arquiteturais & Decisões**: Decisões técnicas tomadas durante a sessão.
   - **Próximo Passo Imediato (Linha de Ação)**: A ação exata de 1 passo que o próximo dev deve executar.
3. **Confirmar ao Desenvolvedor**:
   - Informar que o snapshot foi gravado com segurança em [secoes/HANDOFF_ATIVO.md](file:///c:/Users/trcnologia/Desktop/_inbox/proj_revops/secoes/HANDOFF_ATIVO.md).
   - Indicar o comando para o novo dev alternar a conta via `python scripts/switch_dev.py`.

---

### B. Comando `/retomar` (Carregar Snapshot & Executar)
Quando o novo desenvolvedor assume a sessão:

1. **Ler o Snapshot Ativo**:
   - Ler [secoes/HANDOFF_ATIVO.md](file:///c:/Users/trcnologia/Desktop/_inbox/proj_revops/secoes/HANDOFF_ATIVO.md).
2. **Identificar o Desenvolvedor Atual**:
   - Verificar credencial ativa no `.env-gemini` ou executar `python scripts/switch_dev.py --status`.
3. **Restabelecer o Plano de Voo**:
   - Validar se os arquivos citados no snapshot estão intactos.
   - Executar os testes rápidos (`pytest -q`) para checar integridade imediata.
   - Apresentar em 3 linhas:
     - Quem congelou o trabalho e o que foi feito.
     - O estado atual do código.
     - A ação imediata que o agente está pronto para executar.

---

## 3. Estrutura do Snapshot Canônico (`secoes/HANDOFF_ATIVO.md`)

```markdown
# 🤝 Snapshot de Transição de Contexto (Team Handoff)

- **Timestamp**: YYYY-MM-DD HH:MM:SS
- **Dev Cedente**: [Nome / DEV_XX]
- **Dev Assumindo**: [Aguardando próximo dev]
- **Branch Ativa**: main

## 1. Missão em Andamento
[Descrição concisa do objetivo]

## 2. Arquivos no Radar
- [arquivo_1.py](file:///c:/path/to/arquivo_1.py) (Modificado / Em edição)
- [arquivo_2.py](file:///c:/path/to/arquivo_2.py)

## 3. Estado dos Testes & Quality Gates
- Testes: [Passando / X falhas conhecidas]

## 4. Invariantes & Gaps em Aberto
- Invariante 1...
- Detalhe a não esquecer...

## 4. Comandos Rápidos do Switcher (`scripts/switch_dev.py`)

- `python scripts/switch_dev.py --login --dev DEV_02`: Prepara a troca, sincroniza autor no Git e abre o navegador oficial do Google para o dev logar com sua senha e 2FA (Human-in-the-Loop sem bloqueio anti-bot).
- `python scripts/switch_dev.py --next`: Rotaciona automaticamente para a próxima conta do time (Round-Robin quando estoura cota de API Key).
- `python scripts/switch_dev.py --auto`: Detecta e ativa o slot do desenvolvedor a partir do e-mail do Git local (`git config user.email`).
- `python scripts/switch_dev.py --status`: Exibe o dev ativo e se há handoffs pendentes.

