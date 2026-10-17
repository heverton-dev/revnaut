# Manual da Rota: Organograma, RBAC, Metas & Comissões (`/#hierarchy`)

## 1. Objetivo da Rota
Gerenciar a arquitetura corporativa completa da indústria odontológica conforme a `SPEC_RBAC_DATA_SCOPING_HIERARQUICO.md`:
1. Árvore hierárquica e Business Units (BUs Nacionais, Regionais e Distritos) com resolução recursiva de alta performance (`WITH RECURSIVE` em SQLite WAL).
2. Matriz granular de papéis e escopos de dados (`self`, `team`, `subtree`, `business_unit`, `tenant_global`).
3. Presets Odontológicos de Estrutura Organizacional em 1 clique.
4. Motor de Metas Comerciais e Cálculo Hierárquico de Comissões (vendas diretas, override gerencial de equipe e acelerador de supermeta).

---

## 2. O Que o Usuário Consegue Realizar
* **Aba 1: Árvore Corporativa & BUs:**
  * Visualizar a topologia corporativa completa com validação anti-ciclo (DAG) impedindo parentescos circulares.
  * **Aplicação de Presets Odontológicos (`/api/v1/hierarchy/presets/apply`):**
    1. `fabrica_enxuta`: Estrutura ágil (Diretoria ➔ Closer ➔ Representante).
    2. `nacional_expansao`: Modelo com Gerências Regionais (Sul, Sudeste, Centro-Oeste, Norte/Nordeste).
    3. `multidivisao_produtos`: Divisões especializadas (Implantes, Próteses CAD/CAM, Biomateriais, Equipamentos).
    4. `multinacional_enterprise`: Operações com múltiplas BUs, filiais e conselhos de auditoria.
* **Aba 2: Matriz de Permissões & Data Scoping:**
  * Inspecionar papéis e escopos de acesso a dados (resolvidos em < 0.2ms via índices compostos).
  * Invariante de Super Admin restrita exclusivamente ao Heverton (`is_superadmin = 1`).
* **Aba 3: Metas & Comissões de Equipes:**
  * Cadastro de metas financeiras periódicas por vendedor, time ou unidade.
  * Simulação e cálculo de extrato consolidado com detalhamento de comissão direta versus comissão indireta de liderança (override).

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil | Árvore Corporativa | Matriz de Permissões | Aplicar Presets | Cadastro de Metas | Extrato de Comissões |
|---|---|---|---|---|---|
| Consultor de Vendas | Apenas visualiza seu nó na árvore | Visualiza seus direitos | Não | Não | Apenas seu próprio extrato |
| Gerente Regional | Visualiza sua regional e equipes filhas | Visualiza papéis | Não | Sim (para sua equipe) | Extrato consolidado da regional |
| Diretor de BU | Visualiza toda a sua Business Unit | Visualiza papéis | Sim (na sua BU) | Sim (para toda a BU) | Extrato consolidado da BU |
| Super Admin (Heverton) | Controle total e irrestrito da árvore | Edição de permissões | Sim (Global) | Irrestrito | Extrato de qualquer colaborador |

---

## 4. Quais Ações Podem Ser Realizadas
* `SET_HIERARCHY_TAB`: Alternar entre as abas `tree` (Árvore), `matrix` (RBAC) e `targets` (Metas & Comissões).
* `APPLY_HIERARCHY_PRESET`: Aplicar um dos 4 modelos organizacionais pré-configurados.
* `CREATE_TEAM`: Inserir nova equipe com validação determinística de árvore acíclica.
* `SET_TARGET`: Cadastrar meta financeira em R$ para determinado período (mês/ano).
* `SIMULATE_COMMISSION`: Gerar extrato consolidado com cálculo de comissão direta e bônus de liderança.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)

### Aplicação de um Preset Organizacional Odontológico
1. Acesse **Gestão & Equipe > Organograma & RBAC**.
2. Na aba superior **Árvore Corporativa**, localize o painel de Presets Plug & Play.
3. Clique no modelo desejado (ex: "Nacional Expansão").
4. Confirme a aplicação. O backend executa uma transação atômica no SQLite WAL instanciando as BUs, regionais e cargos padrão.

### Simulação do Fechamento de Comissões
1. Clique na aba **Metas & Comissões de Equipes**.
2. Selecione o colaborador ou gerente no seletor de extrato.
3. O sistema calcula instantaneamente:
   * Total de Vendas Diretas Faturadas.
   * Total de Vendas da Equipe Subordinada (resolvido por recursão de árvore).
   * Percentual de batimento da meta individual e da equipe.
   * Valor líquido total da comissão a pagar.

---

## 6. O Que Falta Implementar (Roadmap & Gaps)
* Exportação do arquivo de remessa bancária para liquidação de comissões (padrão CNAB 240 / folha).
* Travas de comissão vinculadas à efetiva liquidação financeira dos boletos das cirurgias pelo cliente (comissão pós-pagamento).

---

## ANOTAÇÕES DO HEVERTON

* **[RESOLUÇÃO DE SUBÁRVORE EM < 0.2MS]**: As consultas de visibilidade hierárquica utilizam CTE recursiva (`WITH RECURSIVE`) respaldada por índices compostos (`idx_teams_hierarchy`, `idx_deals_scope`, `idx_contacts_scope`), garantindo velocidade instantânea no SQLite WAL.
* **[PRESETS PLUG & PLAY]**: 4 estruturas organizacionais prontas e auditadas disponíveis para ativação imediata.
