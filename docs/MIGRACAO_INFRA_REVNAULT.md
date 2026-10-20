# Migração de infraestrutura para RevNault (VPS)

Os arquivos do repositório já usam os novos nomes. A VPS ainda está com os antigos até este roteiro ser executado.

## O que mudou no repositório
| Antes | Depois |
|---|---|
| Stack swarm `revnault` (serviços `revnault_*`) | `revnault` (serviços `revnault_*`) |
| Pasta remota `/opt/revnault` | `/opt/revnault` |
| Imagens `revnault_app`, `revnault_frontend` | `revnault_app`, `revnault_frontend` |
| Host `revnault.vpsconexao.org` / `revnault.vpsconexao.org` | `revnault.vpsconexao.org` |
| Banco SQLite `revnault.db` / `revnault.db` / `revnault.db` | `revnault.db` |
| `REVNAULT_DB_PATH` / `REVNAULT_DB_PATH` | `REVNAULT_DB_PATH` (os antigos ainda funcionam como fallback) |

## O que NÃO foi renomeado (estado persistido ou recurso externo)
- Postgres: banco `revnault`, usuário `revnault_admin` e senha padrão `revnault_pg_pass` (o volume existente mantém esses nomes; renomear exige `ALTER DATABASE`/`ALTER ROLE` e atualizar todos os serviços).
- Buckets R2 `revnaut-wal-backups` e `revnaut-media`, domínio `cdn.revnaut.io`.
- Hostnames internos `*.revnault.internal`/`*.revnault.local` e e-mails `@revnault.*` gravados em dados e testes.
- Salt do cofre (`_VAULT_SALT`) e chave legada em `src/core/security.py` e `src/core/config.py`: alterar invalida credenciais cifradas.

## Roteiro (executar com janela de manutenção)
1. DNS: criar `revnault.vpsconexao.org` (`python scripts/setup_dns.py`); manter o host antigo até validar.
2. Backup: `docker exec` do `wal_backup_s3.py` e cópia de `/opt/revnault`.
3. VPS: `docker stack rm revnault`; `mv /opt/revnault /opt/revnault`; `mv /opt/revnault/data/revnault.db /opt/revnault/data/revnault.db`.
4. Deploy: `python scripts/deploy_vps.py` (usa `/opt/revnault` e o stack `revnault`).
5. Validar: `python scripts/verify_live.py`; só então remover o host antigo.
6. Reverter, se falhar: `mv /opt/revnault /opt/revnault` e redeploy do commit anterior.
