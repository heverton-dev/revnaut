# Manual da Sub-rota: KeyPartners • KOLs, Cirurgiões & Contratos de Consignação (`/#keypartners-kols`)

## 1. Objetivo da Rota / Sub-rota
Centralizar a operação da tela **KeyPartners • KOLs, Cirurgiões & Contratos de Consignação** (`/#keypartners-kols`) (Sub-rota integrada ao módulo principal `#keypartners`) na arquitetura operacional do RevNault Dental, assegurando governança clínica, rastreabilidade auditável e controle transacional.

---

## 2. O Que o Usuário Consegue Realizar
* Consultar painéis e dados consolidados da rota `/#keypartners-kols`.
* Filtrar e segmentar informações clínicas e comerciais com atualização imediata.
* Executar ações operacionais diretamente nas tabelas e cartões de KPI.
* Auditar histórico, notas operacionais e registros sincronizados com os motores de retaguarda.

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil de Usuário | Visualizar | Criar / Submeter | Editar Registro | Exclusão / Override |
|---|---|---|---|---|
| Consultor de Campo | Apenas sua carteira (`owner_id`) | Sim (sua carteira) | Sim (seus registros) | Não |
| Gerente Regional | Toda a regional subordinada | Sim | Sim | Apenas com auditoria |
| Diretor de BU | Visão consolidada da Business Unit | Sim | Sim | Sim |
| Super Admin | Acesso irrestrito a todos os tenants | Sim | Sim | Sim (Total) |

---

## 4. Quais Ações Podem Ser Realizadas
* `VIEW_LOAD`: Carregamento e renderização dos dados ao acessar `#keypartners-kols`.
* `APPLY_FILTER`: Aplicação de filtros por período, especialidade ou regional.
* `EXECUTE_ACTION`: Disparo de operações transacionais vinculadas aos botões da tela.
* `EXPORT_REPORT`: Exportação de dados operacionais e relatórios analíticos em CSV.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)
1. Acesse o menu lateral de navegação e selecione **KeyPartners • KOLs, Cirurgiões & Contratos de Consignação**.
2. A visão `#keypartners-kols` é exibida com seus respectivos cartões de métricas e listagem principal.
3. Utilize os filtros de topo ou campo de busca rápida para localizar o registro desejado.
4. Clique nas ações operacionais de cada item ou nos botões principais da barra de ferramentas.

---

## 6. Catálogo Anatômico de Botões & Ações do DOM

| Rótulo do Botão / Elemento | Classe CSS | Evento (`onclick`) | Ação Operacional Realizada |
|---|---|---|---|
| `Credenciar Novo KOL` | `btn-primary` | `openContactModal()` | Abre o modal correspondente (openContactModal) |
| `Ver Ficha Completa do Cirurgião` | `btn-primary` | `openContactDetailsModal(1)` | Abre o modal correspondente (openContactDetailsModal) |
| `Ver Ficha Completa do Cirurgião` | `btn-primary` | `openContactDetailsModal(2)` | Abre o modal correspondente (openContactDetailsModal) |
| `Ver Ficha Completa do Cirurgião` | `btn-primary` | `openContactDetailsModal(3)` | Abre o modal correspondente (openContactDetailsModal) |

---

## 7. Catálogo de Modais & Gavetas Operacionais
* `openContactDetailsModal`: Modal de operação e auditoria acionado por clique na tela.
* `openContactModal`: Modal de operação e auditoria acionado por clique na tela.

---

## 8. Motores de Backend & Arquitetura Subjacente
* **Endpoints REST Vinculados**: `/api/v1/keypartners/kols`.
* **O Que o Motor Executa**: Persistência atômica no SQLite em modo WAL, validação estrita via schemas Pydantic e processamento transacional com outbox pattern.
* **O Que o Motor Não Executa**: Não autoriza exclusões destrutivas sem soft-delete prévio e não processa requisições externas sem idempotency key registrada.
* **Garantia de Resiliência**: Falhas de conectividade com serviços externos utilizam filas resilientes com retentativa exponencial.

---

## 9. O Que Falta Implementar & Plano de Micro-Tickets
* `[TICKET-KEYPARTNERS_KOLS-01]`: Telemetria analítica em tempo real de latência e taxa de conversão do operador na rota.
* `[TICKET-KEYPARTNERS_KOLS-02]`: Cache inteligente no LocalStorage para navegação offline zero-latency em redes hospitalares instáveis.
