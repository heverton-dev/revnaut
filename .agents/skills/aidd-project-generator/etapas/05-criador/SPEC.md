# SPEC — Fase 5: Criador

**Status:** ⚠️ NÃO IMPLEMENTADO.

## Objetivo
Materializar no disco a estrutura decidida nas fases 3-4. **100% determinístico, zero LLM** — a fase mais simples de auditar de todo o pipeline.

## Comportamento real
```python
os.makedirs(...)                                    # estrutura de pastas
subprocess.run(['git', 'init'])                      # git real
subprocess.run(['git', 'add', '.'])
subprocess.run(['git', 'commit', '-m', 'AIDD init'])
sqlite3.connect('estado_projeto.db')                 # schema real
# CREATE TABLE execucoes(id, timestamp, ideia, gates_json)
```

## Output
- `.aidd/config.json`, `.aidd/rules.md`
- `CLAUDE.md`, `README.md`, `.gitignore`, `requirements.txt`
- `estado_projeto.db` com tabela `execucoes(id, timestamp, ideia, gates_json)` — **tem que ter pelo menos 1 linha real** depois da execução
- Commit git real (não só `git init` vazio)

## Gates
| Gate | Regra |
|---|---|
| **E1** | 4 arquivos principais existem de fato no disco (`os.path.exists`, checagem real) |
| **E2** | `.git/` existe E tem pelo menos 1 commit (`git log` não vazio) |
| **E3** | `estado_projeto.db` abre com `sqlite3` e a tabela `execucoes` tem ≥1 linha real |
| **E4** | Permissões corretas em scripts executáveis |
| **E5** | `README.md` não está vazio e menciona o nome do projeto |
| **S1** | Auditoria de segurança: `.gitignore` cobre `.env`/`credentials.json`; `requirements.txt` existe; nenhum secret hardcoded (regex tipo `AWS_KEY`, `API_TOKEN` no código gerado); `README.md` tem seção de segurança |

Nenhum projeto passa da Fase 5 sem S1 — mesma regra que já existe no `aidd-project-generator` original.

## Custo
0 tokens de LLM.
