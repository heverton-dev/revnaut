# AGENTS — Fase 3: Designer

**N/A — e isso é deliberado.** Esta é a fase onde a documentação antiga (`SKILL.md`) mais exagerou, afirmando "5 subagentes LLM paralelos" (Arquiteto de Camadas, Engenheiro de Scripts, Especialista em Tokens, Arquiteto de Ferramentas, Especialista em Gates). O desenho corrigido usa 1 chamada de API simples dentro do script — nenhum subagente do Claude Code (`.claude/agents/`) está envolvido. Se um dia isso evoluir para usar subagentes de verdade (ex: via `Agent` tool do harness), este arquivo passa a documentar papel/tools/modelo de cada um — hoje não se aplica.
