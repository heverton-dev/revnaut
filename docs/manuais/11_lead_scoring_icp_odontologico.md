# Manual da Rota: Lead Scoring & Critérios ICP (`/#scoring`, `/#scoring-icp`)

## 1. Objetivo da Rota
Qualificar matematicamente a base de cirurgiões-dentistas através de regras de pontuação determinísticas fundamentadas nas características clínicas e comerciais do setor odontológico (posse de CRO ativo, número de implantes instalados por mês, presença de clínica própria e especialização em implantodontia/periodontia). Classifica os leads em faixas (Tier A • Hot Lead, Tier B, Tier C).

---

## 2. O Que o Usuário Consegue Realizar
* **Subrota Matriz Lead Scoring (`/#scoring`):**
  * Visualizar a lista ranqueada de cirurgiões com maior pontuação e propensão de fechamento imediato.
  * Disparar recálculo em massa de toda a base após alteração de parâmetros.
* **Subrota Regras & Critérios ICP (`/#scoring-icp`):**
  * Aplicar Presets Odontológicos Plug & Play pré-configurados pela diretoria:
    * Implantes Premium (prioriza cirurgiões de alto volume com conexão cônica).
    * Acadêmico & Mandic (prioriza docentes e residentes de cursos de especialização).
    * Distribuidores & Redes (prioriza clínicas multidisciplinares e franquias).
    * Multidisciplinar (prioriza clínicas integradas com orto, prótese e cirurgia).
  * Ajustar manualmente as notas de corte para cada Tier (ex: Tier A mínimo 70 pts, Tier B mínimo 40 pts).

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil | Visualizar Scores | Ajustar Parâmetros e Tiers | Aplicar Presets Plug & Play |
|---|---|---|---|
| Consultor de Vendas | Sim (para priorizar seu dia de visitas) | Não | Não |
| Gerente de RevOps | Sim | Sim | Sim |
| Diretor Comercial | Sim | Sim | Sim |
| Super Admin | Sim | Sim | Sim |

---

## 4. Quais Ações Podem Ser Realizadas
* `APPLY_SCORING_PRESET`: Aplicar pesos pré-definidos para focar em determinado nicho odontológico.
* `SET_CUSTOM_TIERS`: Configurar notas mínimas customizadas para Tier A e Tier B.
* `RECALCULATE_SCORES`: Executar recálculo imediato de toda a base através de chamada a `POST /api/v1/scoring/recalculate`.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)

### Ajuste de Critérios e Recálculo da Base
1. Acesse **Marketing & Scoring > Lead Scoring ICP > Regras & Critérios ICP**.
2. Nos cartões de Presets Plug & Play, escolha o foco comercial atual (ex: "Implantes Premium").
3. Ajuste os campos "Nota Mínima para Tier A" (ex: 75) e "Nota Mínima para Tier B" (ex: 45).
4. Clique no botão "Recalcular Base".
5. O backend reavalia todos os cirurgiões cadastrados e atualiza suas classificações de prioridade.
6. Acesse **Matriz Lead Scoring** para ver os profissionais que atingiram o status "Tier A • Hot Lead".

---

## 6. O Que Falta Implementar (Roadmap & Gaps)
* Machine Learning / Regressão Logística para sugerir automaticamente ajustes nos pesos com base nos negócios efetivamente ganhos nos últimos 12 meses.
* Pontuação por engajamento digital (leitura de e-mails, visitas ao site de catálogos técnicos).

---

## ANOTAÇÕES DO HEVERTON

