# AIDD-Spec — Motor de RBAC e Data Scoping Hierárquico Aberto

> **Documento:** `docs/planos/SPEC_RBAC_DATA_SCOPING_HIERARQUICO.md`  
> **Status:** Proposta Formal  
> **Autor:** AIDD Core Architecture  
> **Data:** 16/10/2026  

---

## 1. Context & Explicit Non-Goals

### Context
A plataforma RevNault Dental Ops atende indústrias odontológicas de diversos portes (desde fabricantes enxutos como Plenum e Titaniumfix até multinacionais como Neodent, Straumann e SIN Implantes). A estrutura corporativa exige:
- **Super Admin (User God):** Acesso mestre irrestrito à infraestrutura SaaS multi-tenant.
- **Tenant Admin (RevNault Lead):** Arquiteto corporativo interno da empresa, responsável por criar Divisões (Business Units), Árvore de Equipes (Teams), Cargos (Roles) e convidar usuários.
- **Isolamento Hierárquico Aberto (Data Scoping):** Suporte a árvores organizacionais de profundidade arbitrária (`N` níveis) com restrição automática de visibilidade em nível de linha (*Row-Level Security / Territory Management*).
- **Esteira de 4 Presets Progressivos ("Plug & Play"):** Templates prontos do setor odontológico que geram a estrutura organizacional inicial com 1 clique.

### Explicit Non-Goals
- Não está no escopo desta especificação a integração com provedores externos de SSO/SAML 2.0 ou Active Directory (planejado para fase enterprise futura).
- Não haverá alteração no motor de persistência SQLite WAL nem quebra de compatibilidade com os endpoints legados existentes.
- Não haverá dependência de bibliotecas pesadas de regras externas (Casbin, OPA); toda a resolução de árvore é determinística em Python nativo e SQL puro.

---

## 2. Contracts & Typed Interfaces

### 2.1. Modelagem Relacional (DDL SQLite WAL)

```sql
-- Unidades de Negócio / Divisões Setoriais
CREATE TABLE IF NOT EXISTS business_units (
    id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    name TEXT NOT NULL,
    code TEXT NOT NULL, -- Ex: 'CIRURGICO', 'CAD_CAM', 'ENSINO', 'KEY_ACCOUNTS'
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
);

-- Árvore Hierárquica de Equipes (Territórios)
CREATE TABLE IF NOT EXISTS teams (
    id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    business_unit_id TEXT NOT NULL,
    parent_id TEXT, -- NULL para equipes raiz (Diretoria Nacional)
    name TEXT NOT NULL, -- Ex: 'Distrito Sul', 'Regional Interior SP', 'Equipe Mandic'
    leader_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
    FOREIGN KEY (business_unit_id) REFERENCES business_units(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES teams(id) ON DELETE SET NULL
);

-- Cargos / Perfis de Permissão Criados pela Empresa
CREATE TABLE IF NOT EXISTS roles (
    id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    name TEXT NOT NULL, -- Ex: 'Assessor Cirúrgico', 'Gerente Regional', 'RevNault Lead'
    description TEXT,
    default_data_scope TEXT NOT NULL, -- 'self', 'team', 'subtree', 'business_unit', 'tenant_global'
    is_admin INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
);

-- Permissões Atômicas Vinculadas a cada Perfil
CREATE TABLE IF NOT EXISTS role_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id TEXT NOT NULL,
    role_id TEXT NOT NULL,
    permission_code TEXT NOT NULL, -- Ex: 'deals:read', 'consignments:consume', 'contacts:export'
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
);

-- Usuários e Operadores do Sistema
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    team_id TEXT,
    role_id TEXT NOT NULL,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    custom_data_scope TEXT, -- Opcional: sobrescreve o escopo padrão da Role
    is_active INTEGER DEFAULT 1,
    is_superadmin INTEGER DEFAULT 0, -- 1 apenas para o User God
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE SET NULL,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE RESTRICT
);
```

### 2.2. Contratos Tipados Pydantic (Python 3.14)

```python
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

class DataScopeEnum(str, Enum):
    SELF = "self"                     # Vê apenas registros onde owner_id == user_id
    TEAM = "team"                     # Vê registros do próprio time direto
    SUBTREE = "subtree"               # Vê registros do próprio time e todos os times filhos recursivos
    BUSINESS_UNIT = "business_unit"   # Vê registros de toda a Divisão (ex: todo o CAD/CAM)
    TENANT_GLOBAL = "tenant_global"   # Vê todos os registros da empresa (C-Level / Admin)

class UserContext(BaseModel):
    user_id: str
    account_id: str
    role_id: str
    team_id: Optional[str] = None
    business_unit_id: Optional[str] = None
    data_scope: DataScopeEnum
    permissions: List[str] = Field(default_factory=list)
    is_superadmin: bool = False

class PresetApplyRequest(BaseModel):
    preset_name: str = Field(
        ..., 
        description="Nome do preset: 'fabrica_enxuta', 'nacional_expansao', 'multidivisao_produtos', 'multinacional_enterprise'"
    )
```

---

## 3. Invariants & Business Rules

1. **Invariante de Isolamento Mestre:** Nenhuma consulta disparada por usuário comum ou Tenant Admin pode retornar registros com `account_id` diferente do seu token de autenticação.
2. **Invariante do Super Admin (User God):** Usuários com flag `is_superadmin = 1` têm bypass automático de `account_id` e de escopo hierárquico, acessando o painel de telemetria e o endpoint de impersonation.
3. **Invariante de Hierarquia Acíclica (DAG):** A tabela `teams` forma estritamente um grafo acíclico dirigido. Uma equipe `A` não pode ter como `parent_id` uma equipe `B` que seja sua descendente (validação anti-loop obrigatória no `POST`/`PUT /api/v1/teams`).
4. **Invariante de Resolução Descendente (Subtree Scope):** Quando um gestor com escopo `subtree` consulta uma entidade, a query deve calcular recursivamente todos os IDs de equipes filhas (`WITH RECURSIVE team_tree AS (...)`) e filtrar `team_id IN (team_tree)`.
5. **Invariante de Autoria e Posse de Dados:** Todo novo registro criado em `deals`, `contacts`, `consignments` e `institutions` deve persistir compulsoriamente `owner_id = user.id` e `team_id = user.team_id`.
6. **Invariante dos Presets Idempotentes:** A aplicação de um preset ("Fábrica Enxuta", "Multinacional", etc.) deve rodar dentro de uma transação SQLite atômica. Se a empresa já possuir estrutura, o preset expande as camadas sem sobrescrever ou deletar contatos, negócios e consignações pré-existentes.
7. **Invariante de Autonomia do Tenant Admin:** Apenas usuários com `is_admin = 1` ou permissão `org:manage` podem criar, renomear ou reorganizar Business Units, Teams e Roles da empresa.

---

## 4. Binary Acceptance Criteria

- **Critério 1:** `python -m pytest tests/test_data_scoping.py -q` executa e finaliza com exit code 0 com 100% dos testes aprovados.
- **Critério 2:** Requisição `GET /api/v1/consignments` autenticada com usuário de escopo `self` retorna HTTP 200 contendo apenas as caixas onde `owner_id == user.id`. Se houver caixas de outros consultores no banco, a contagem na resposta deve excluir categoricamente registros de terceiros.
- **Critério 3:** Requisição `GET /api/v1/consignments` autenticada com Gestor Regional (`data_scope='team'`) retorna HTTP 200 com todas as caixas dos consultores de seu time, e zero caixas de outros times.
- **Critério 4:** Requisição `GET /api/v1/consignments` autenticada com Gestor Distrital (`data_scope='subtree'`) retorna HTTP 200 agregando recursivamente as caixas de todas as regionais sob seu distrito.
- **Critério 5:** Tentativa de um Tenant Admin acessar ou criar registros vinculados a outro `account_id` retorna status HTTP 403 Forbidden.
- **Critério 6:** Requisição `POST /api/v1/hierarchy/presets/apply` com payload `{"preset_name": "multinacional_enterprise"}` retorna status HTTP 200 e gera exatamente 4 Business Units, 8 Equipes Hierárquicas e 5 Roles no SQLite WAL.
- **Critério 7:** Tentativa de criar uma relação de parentesco circular entre equipes (ex: Equipe A -> Equipe B -> Equipe A) retorna status HTTP 422 Unprocessable Entity.

---

## 5. Failure & Degradation Modes

- **Token Ausente ou Expirado:** A API rejeita imediatamente com HTTP 401 Unauthorized e payload `{"detail": "Credenciais ausentes ou inválidas"}`.
- **Usuário Sem Time Alocado (`team_id is NULL`):** Se um usuário com escopo `team` ou `subtree` não possuir time atribuído, a engine degrada seguramente para escopo `self`, garantindo que ele não acerte dados de equipes alheias.
- **Falha no Preset ou Conflito de Nomes:** Em caso de erro na injeção do preset, o context manager executa `ROLLBACK` total na transação do SQLite WAL e retorna HTTP 400 com a causa raiz detalhada, mantendo o estado anterior íntegro.
- **Tentativa de Mutação Fora do Escopo:** Se um consultor tentar atualizar (`PUT` / `PATCH`) um negócio ou caixa consignada de outro consultor via ID forjado, o backend retorna HTTP 404 Not Found (não revela a existência do registro) ou HTTP 403.
