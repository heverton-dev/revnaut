# Migração de infraestrutura para RevNault (VPS)

Os arquivos do repositório já usam os novos nomes. A VPS ainda está com os antigos até este roteiro ser executado.

## O que mudou no repositório
| Antes | Depois |
|---|---|
| Stack swarm `rvops` (serviços `rvops_*`) | `revnault` (serviços `revnault_*`) |
| Pasta remota `/opt/rvops` | `/opt/revnault` |
| Imagens `rvops_app`, `rvops_frontend` | `revnault_app`, `revnault_frontend` |
| Host `rvops.vpsconexao.org` / `revnaut.vpsconexao.org` | `revnault.vpsconexao.org` |
| Banco SQLite `revnaut.db` / `rvops.db` / `revops.db` | `revnault.db` |
| `REVNAUT_DB_PATH` / `RVOPS_DB_PATH` | `REVNAULT_DB_PATH` (os antigos ainda funcionam como fallback) |

## O que NÃO foi renomeado (estado persistido ou recurso externo)
- Postgres: banco `revnaut`, usuário `revnaut_admin` e senha padrão `revnaut_pg_pass` (o volume existente mantém esses nomes; renomear exige `ALTER DATABASE`/`ALTER ROLE` e atualizar todos os serviços).
- Buckets R2 `revnaut-wal-backups` e `revnaut-media`, domínio `cdn.revnaut.io`.
- Hostnames internos `*.revnaut.internal`/`*.revnaut.local` e e-mails `@revnaut.*` gravados em dados e testes.
- Salt do cofre (`_VAULT_SALT`) e chave legada em `src/core/security.py` e `src/core/config.py`: alterar invalida credenciais cifradas.

## Roteiro (executar com janela de manutenção)
1. DNS: criar `revnault.vpsconexao.org` (`python scripts/setup_dns.py`); manter o host antigo até validar.
2. Backup: `docker exec` do `wal_backup_s3.py` e cópia de `/opt/rvops`.
3. VPS: `docker stack rm rvops`; `mv /opt/rvops /opt/revnault`; `mv /opt/revnault/data/revnaut.db /opt/revnault/data/revnault.db`.
4. Deploy: `python scripts/deploy_vps.py` (usa `/opt/revnault` e o stack `revnault`).
5. Validar: `python scripts/verify_live.py`; só então remover o host antigo.
6. Reverter, se falhar: `mv /opt/revnault /opt/rvops` e redeploy do commit anterior.
