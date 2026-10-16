# Manual da Rota: Organograma, RBAC, Metas & Comissões (`/#hierarchy`)

## 1. Objetivo da Rota
Gerenciar a arquitetura corporativa completa da empresa:
1. Árvore hierárquica e Business Units (BUs Nacionais e Regionais).
2. Matriz granular de permissões e controle de acesso baseado em papéis (RBAC).
3. Motor de Metas Comerciais e Cálculo Hierárquico de Comissões (comissionamento de vendas diretas do consultor, comissionamento de override gerencial sobre a equipe e aceleradores por supermeta).

---

## 2. O Que o Usuário Consegue Realizar
* **Aba 1: Árvore Corporativa & BUs:**
  * Visualizar toda a estrutura corporativa em formato de árvore hierárquica (C-Level -> Distritos -> Regionais -> Consultores).
  * Cadastrar novas Business Units ou equipes filhas com validação anti-loop de hierarquia.
* **Aba 2: Matriz Granular de Permissões (RBAC):**
  * Consultar a matriz de papéis (Super Admin, Diretor Regional, Gerente Regional, Coordenador de Equipe, Consultor de Vendas).
  * Inspecionar permissões ativas para cada recurso do sistema (Ver, Criar, Editar, Excluir, Exportar).
* **Aba 3: Metas & Comissões de Equipes:**
  * Cadastrar metas financeiras periódicas por vendedor, equipe ou BU.
  * Configurar regras de comissão base e percentuais de aceleração de supermeta.
  * Simular e consultar o extrato consolidado de comissão líquida de qualquer colaborador.

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil | Árvore Corporativa | Matriz de Permissões | Cadastro de Metas | Extrato de Comissões |
|---|---|---|---|---|
| Consultor de Vendas | Apenas visualiza seu nó na árvore | Visualiza seus direitos | Não | Apenas o seu próprio extrato |
| Gerente Regional | Visualiza sua regional e equipes filhas | Visualiza papéis | Sim (para sua equipe) | Extrato consolidado da regional |
| Diretor de BU | Visualiza toda a sua Business Unit | Visualiza papéis | Sim (para toda a BU) | Extrato consolidado da BU |
| Super Admin | Controle total da árvore, BUs e nós | Edição de permissões | Irrestrito | Extrato de qualquer colaborador |

---

## 4. Quais Ações Podem Ser Realizadas
* `SET_HIERARCHY_TAB`: Alternar entre as abas `tree` (Árvore), `matrix` (RBAC) e `targets` (Metas & Comissões).
* `CREATE_BU_OR_TEAM`: Inserir nova unidade ou time na estrutura da empresa.
* `SET_TARGET`: Cadastrar valor da meta de faturamento para determinado período (mês/ano).
* `SET_COMMISSION_RULE`: Definir taxa base de comissão (%) e gatilho de aceleração (%).
* `CALCULATE_COMMISSION_STATEMENT`: Disparar cálculo consolidado de faturamento e comissão a pagar.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)

### Configuração de Metas e Consulta de Comissões
1. Acesse **Gestão & Equipe > Organograma & RBAC**.
2. Clique na aba superior **Metas & Comissões de Equipes**.
3. No painel superior, clique em "Definir Nova Meta".
4. Selecione o colaborador ou equipe, informe o período (ex: "2026-10") e o valor da meta em R$ (ex: R$ 150.000,00).
5. Clique em "Salvar Meta".
6. Para consultar o fechamento de um vendedor, selecione seu nome no dropdown de simulação de extrato.
7. O sistema exibe: Vendas Diretas, Vendas da Equipe (sub-árvore), Acelerador aplicado e o Valor Total Líquido a Pagar.

---

## 6. O Que Falta Implementar (Roadmap & Gaps)
* Exportação do arquivo de remessa bancária para pagamento de comissões (padrão CNAB ou folha de pagamento).
* Travas de comissão vinculadas à efetiva liquidação financeira dos boletos das cirurgias pelo cliente (comissão pós-pagamento).
