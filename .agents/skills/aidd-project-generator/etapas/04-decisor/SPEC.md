# SPEC — Fase 4: Decisor

**Status:** ⚠️ NÃO IMPLEMENTADO.

## Objetivo
Decidir, para cada artefato (CLAUDE.md, Skills, MCPs, Hooks, Agents, Scripts), se ele será GLOBAL (`~/.claude/`) ou LOCAL (projeto).

## Comportamento real
1 chamada real de LLM com schema JSON forçado (`tool_choice` obrigatório no provedor, não texto livre) retornando decisão + justificativa + confiança auto-reportada.

**Modo interativo (default):** pergunta via `input()` real no terminal — não um modal simulado.
**Modo `--nao-interativo`:** usa uma heurística real baseada no design da Fase 3 (não um dict fixo disfarçado de heurística).

## Input
- `.aidd/cache/_phase_03_index.json`

## Output
`.aidd/cache/_phase_04_index.json`:
```json
{
  "fase": 4,
  "status": "COMPLETO",
  "decisoes": {"claude_md": "GLOBAL|LOCAL", "skills": "...", "mcps": "...", "hooks": "...", "agents": "...", "scripts": "..."},
  "justificativas": {"claude_md": "texto mencionando termos especificos da ideia"},
  "confianca": 0.0,
  "symlinks_criados": ["caminho1", "caminho2"]
}
```

## Gates
| Gate | Regra |
|---|---|
| **C1** | Toda decisão em `decisoes{}` é literalmente `"GLOBAL"` ou `"LOCAL"` — nenhum outro valor |
| **C2** | Todo symlink em `symlinks_criados[]` resolve para um arquivo que **existe de fato** (`Path(destino).resolve().exists()`) — tem que poder falhar de verdade, não ser sempre `True` por construção |
