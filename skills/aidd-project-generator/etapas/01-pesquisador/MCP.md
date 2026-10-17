# MCP — Fase 1: Pesquisador

**N/A por enquanto.**

Esta fase é 100% Python + chamadas HTTP diretas (GitHub Search API etc) — não envolve o LLM chamando ferramentas, então não há necessidade de expor um servidor MCP.

**Quando isso mudaria:** se no futuro a busca de referências precisar ser feita *pelo agente* de forma interativa (ex: o usuário pedir "procura mais fundo, inclui GitLab também" no meio da execução), aí faria sentido um servidor MCP com uma tool `search_repos(query, fonte)` — até lá, script puro resolve com menos superfície de falha.
