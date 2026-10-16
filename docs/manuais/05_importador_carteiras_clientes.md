# Manual da Rota: Importador Universal de Carteiras (`/#import-contacts`)

## 1. Objetivo da Rota
Realizar a importação em massa de listas de cirurgiões-dentistas e clínicas (arquivos CSV ou planilhas) com processamento determinístico, deduplicação automática de cadastros por chave única (CRO + UF) e distribuição automática de carteira para os consultores de vendas com base em regras territoriais, especialidade ou revezamento equitativo (Round-Robin).

---

## 2. O Que o Usuário Consegue Realizar
* Fazer upload ou colar dados de cirurgiões em formato CSV / Texto Tabulado.
* Testar a carga com 1 clique utilizando dados de exemplo da indústria odontológica nacional.
* Escolher o algoritmo de distribuição da carteira:
  1. **Distribuição Territorial por UF:** Associa os cirurgiões automaticamente aos consultores responsáveis por cada estado (SP, RJ, MG, PR, etc.).
  2. **Distribuição por Especialidade Clínica:** Aloca profissionais conforme foco técnico (Implantodontia para equipe de cirurgia pesada, Estética para equipe de reabilitação).
  3. **Distribuição Equitativa (Round-Robin):** Divide o lote de novos contatos igualmente entre todos os consultores ativos da equipe comercial.
* Visualizar prévia dos dados antes da confirmação, com contagem de registros válidos e potenciais duplicatas.
* Executar a importação atômica no banco SQLite WAL com registro de log de auditoria.

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil | Acesso à Tela | Pode Importar Carteira | Regras Aplicáveis |
|---|---|---|---|
| Consultor de Vendas | Não | Não | Tela bloqueada para vendedores individuais |
| Coordenador de Equipe | Não | Não | Sem permissão de carga em massa |
| Gerente de Operações / RevOps | Sim | Sim | Apenas para a sua respectiva Business Unit |
| Super Admin | Sim | Sim | Irrestrito para qualquer UF, equipe ou BU nacional |

---

## 4. Quais Ações Podem Ser Realizadas
* `LOAD_SAMPLE_DATA`: Preenchimento instantâneo da caixa de texto com dados fictícios estruturados de cirurgiões com CROs reais.
* `SELECT_DISTRIBUTION_RULE`: Escolha do modo de atribuição (`territorial`, `specialty`, `round_robin`).
* `ANALYZE_PREVIEW`: Análise estática do arquivo com verificação de colunas e identificação de registros sem CRO.
* `EXECUTE_IMPORT`: Disparo da requisição `POST /api/v1/contacts/import` com processamento em transação SQLite.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)

### Importação de Nova Lista de Cirurgiões
1. No menu lateral, acesse **Operações & Carteira > Importar Carteira**.
2. Na área de entrada de dados, cole o conteúdo do CSV ou clique em "Preencher Exemplo Odonto" para testar.
3. Certifique-se de que o cabeçalho contenha: `name,cro,uf,specialty,phone,monthly_surgeries`.
4. No card de regras de distribuição, selecione a regra desejada (ex: "Distribuição Territorial por UF").
5. Clique no botão "Analisar Prévia" para conferir a contagem de cirurgiões identificados.
6. Clique em "Executar Importação Determinística".
7. Uma mensagem informará o total de cirurgiões criados, duplicados ignorados e a distribuição por consultor.

---

## 6. O Que Falta Implementar (Roadmap & Gaps)
* Suporte nativo a upload direto de arquivos binários `.xlsx` (Excel) via drag-and-drop.
* Mapeamento dinâmico visual de colunas (De -> Para) caso o arquivo do cliente utilize nomes de colunas diferentes do padrão.
* Exportação do relatório de auditoria da importação contendo as falhas e linhas descartadas.

---

## ANOTAÇÕES DO HEVERTON

