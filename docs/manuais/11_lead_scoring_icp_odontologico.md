# Manual da Rota: Lead Scoring & Critérios ICP (`/#scoring`, `/#scoring-icp`)

## 1. Objetivo da Rota
Qualificar matematicamente a base de cirurgiões-dentistas através de regras determinísticas baseadas em características clínicas e comerciais (CRO ativo, volume mensal de implantes instalados, especialidade cirúrgica e engajamento digital via Mautic/WhatsApp). Classifica os leads em faixas (Tier A • Hot Lead, Tier B, Tier C) e aciona o **Transbordo Automático de Receita** com SLA de 15 minutos.

---

## 2. O Que o Usuário Consegue Realizar
* **Subrota Matriz Lead Scoring (`/#scoring`):**
  * Visualizar cirurgiões ranqueados por nota ICP e tag de prioridade.
  * Disparar recálculo em lote de toda a base após ajustes de parâmetros.
  * **Gatilho de Transbordo Automático (Tier A):** Ao atingir a pontuação de Tier A (ex: volume >= 30 implantes/mês + engajamento ativo), o sistema cria automaticamente a oportunidade no Kanban, define o Closer do território e gera tarefa com SLA de 15 minutos.
* **Subrota Regras & Critérios ICP (`/#scoring-icp`):**
  * Aplicar Presets Odontológicos Plug & Play pré-configurados:
    * Implantes Premium (prioriza cirurgiões de alto volume com conexão cônica).
    * Acadêmico & Mandic (prioriza docentes e residentes de especialização).
    * Distribuidores & Redes (prioriza clínicas multidisciplinares e franquias).
    * Multidisciplinar (prioriza clínicas integradas com orto, prótese e cirurgia).
  * **Engajamento Digital Integrado:** Inclusão de pontuação por interações capturadas via webhooks do Mautic e Evolution API.
  * Ajustar notas de corte para cada Tier (Tier A mínimo 75 pts, Tier B mínimo 45 pts).

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil | Visualizar Scores | Ajustar Parâmetros e Tiers | Aplicar Presets Plug & Play | Disparar Transbordo |
|---|---|---|---|---|
| Consultor de Vendas | Sim (para priorizar seu dia de visitas) | Não | Não | Recebe lead via transbordo |
| Gerente de RevOps | Sim | Sim | Sim | Sim |
| Diretor Comercial | Sim | Sim | Sim | Sim |
| Super Admin (Heverton) | Sim | Sim | Sim | Sim |

---

## 4. Quais Ações Podem Ser Realizadas
* `APPLY_SCORING_PRESET`: Aplicar pesos pré-definidos para focar em nicho cirúrgico específico.
* `SET_CUSTOM_TIERS`: Configurar notas mínimas para enquadramento em Tier A e Tier B.
* `RECALCULATE_SCORES`: Executar recálculo imediato de toda a base via `POST /api/v1/scoring/recalculate`.
* `TRIGGER_REVENUE_HANDOFF`: Execução do transbordo de leads qualificados para a força de vendas regional.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)

### Ajuste de Critérios e Recálculo da Base
1. Acesse **Marketing & Scoring > Lead Scoring ICP > Regras & Critérios ICP**.
2. Nos cartões de Presets Plug & Play, escolha o foco comercial atual (ex: "Implantes Premium").
3. Ajuste os campos "Nota Mínima para Tier A" (ex: 75) e "Nota Mínima para Tier B" (ex: 45).
4. Clique no botão "Recalcular Base".
5. O backend reavalia todos os cirurgiões cadastrados e atualiza suas classificações de prioridade.
6. Todos os cirurgiões promovidos a Tier A entram imediatamente no fluxo de transbordo territorial.

---

## 6. O Que Falta Implementar (Roadmap & Gaps)
* Machine Learning / Regressão Logística para sugerir automaticamente ajustes nos pesos com base na taxa histórica de conversão dos últimos 12 meses.
* Simulação preditiva de faturamento gerado caso a nota de corte do Tier A seja reduzida ou aumentada em 5%.

---

## ANOTAÇÕES DO HEVERTON

* **[TRANSBORDO AUTOMÁTICO DE TIER A]**: Cirurgiões com pontuação Tier A não ficam parados no banco de dados; geram oportunidade automática no funil e notificação imediata para o vendedor da região com SLA de 15 minutos.
* **[ENGAJAMENTO DIGITAL ATIVO]**: O score agora soma automaticamente pontos quando o cirurgião responde no WhatsApp ou abre e-mails técnicos disparados pelo Mautic.
