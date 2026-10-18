---
name: aidd-manuais
description: Orquestrador autônomo e determinístico para auditoria, extração anatômica do DOM e geração de manuais canônicos de rotas e sub-rotas (9 seções obrigatórias, relação 1-para-1 estrita e zero emojis). Use sempre que criar, alterar rotas no frontend ou quando o usuário solicitar '/manuais', '/aidd-manual', 'gerar manual', 'auditar manuais' ou 'documentar rotas'.
---

# AIDD Manuais — Orquestrador de Manuais Anatômicos de Rotas & Sub-rotas

## Visão Geral & Finalidade
A skill `aidd-manuais` atua como guardiã determinística da documentação operacional da aplicação. Ela assegura que **100% das rotas e sub-rotas** declaradas no frontend (`VIEW_CONFIG`) possuam manuais operacionais dedicados (relação 1-para-1 estrita, sem aglutinação), estruturados rigorosamente em **9 seções anatômicas**, com zero emojis (Lei #14) e integração factual com o código-fonte (DOM, eventos `onclick`, modais e motores de backend).

---

## As 9 Seções Obrigatórias de Governança
Todo manual gerado ou auditado em `docs/manuais/*.md` deve conter rigorosamente as seguintes seções em Markdown:

1. `## 1. Objetivo da Rota / Sub-rota`: Propósito clínico/operacional claro no fluxo de trabalho.
2. `## 2. O Que o Usuário Consegue Realizar`: Lista detalhada de casos de uso e operações permitidas.
3. `## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)`: Tabela com perfis (Consultor, Gerente, Diretor, Super Admin) e permissões granulares.
4. `## 4. Quais Ações Podem Ser Realizadas`: Catálogo de comandos técnicos / tópicos de evento disparados.
5. `## 5. Como o Usuário Realiza as Ações (Passo a Passo)`: Sequência operacional real dentro da interface.
6. `## 6. Catálogo Anatômico de Botões & Ações do DOM`: Tabela com cada botão da tela, ID/classe, texto visual, evento de clique, alvo disparado e feedback visual/toast.
7. `## 7. Catálogo de Modais & Gavetas Operacionais`: Lista de modais da rota, finalidade, campos obrigatórios, regras de validação e mecanismo de escape/fechamento.
8. `## 8. Motores de Backend & Arquitetura Subjacente`: Mapeamento factual dos motores FastAPI/SQLite/Outbox/S3/LiveKit, endpoints consumidos, o que executam, o que não executam e garantias transacionais (ACID/WAL).
9. `## 9. O Que Falta Implementar & Plano de Micro-Tickets`: Gaps técnicos, roadmap e tickets atômicos TDD com critérios binários de aceitação.

---

## Invariantes Inegociáveis
* **Lei #14 (Zero Emojis)**: Proibição estrita de qualquer caractere Unicode de emoji nos manuais.
* **Relação 1-para-1 Estrita**: Cada entrada em `VIEW_CONFIG` do frontend deve possuir um arquivo markdown exclusivo correspondente.
* **Factualidade Fidedigna**: Os botões e modais listados devem ser extraídos diretamente do DOM (`index.html` ou componentes equivalentes).
* **Bloqueio por Quality Gate**: O portão `gates/G_MANUAIS_ROTAS.py` deve retornar código `exit 0` para aprovação ou `exit 1` para bloqueio de commit.

---

## Procedimento de Execução

### Passo 1: Auditoria Mecânica de Cobertura
Execute o script em modo auditoria para listar rotas sem manual ou manuais fora do padrão:
```bash
python scripts/audit_rotas_manuais.py --audit
```

### Passo 2: Extração Factual do DOM & Geração do Scaffold
Para rotas ou sub-rotas faltantes, execute o gerador anatômico fornecendo o ID da rota:
```bash
python scripts/audit_rotas_manuais.py --generate <route_id>
```
O gerador realiza o parsing de `<section id="{route_id}-view">` no `index.html`, descobre automaticamente todos os botões, links `onclick`, modais chamados e endpoints referenciados, preenchendo as seções 6, 7 e 8 com precisão factual.

### Passo 3: Enriquecimento das Regras de Negócio
Complete as seções conceituais (Objetivo, RBAC, Passo a Passo e Plano de Micro-Tickets) com os dados de domínio daquela frente.

### Passo 4: Validação no Quality Gate
Valide que todos os manuais atendem aos critérios canônicos:
```bash
python gates/G_MANUAIS_ROTAS.py
```
Se o gate retornar `PASS` (código 0), prossiga com o commit e deploy.
