# Regra de Governança: Fluxo de Revisão e Homologação de Manuais

> **Origem:** Instrução canônica do Heverton (Super Admin / Líder do Projeto).

---

## 1. Estrutura Obrigatória dos Manuais
Todo documento em `docs/manuais/*.md` possui, compulsoriamente no final, a seção:
```markdown
---

## ANOTAÇÕES DO HEVERTON
```

## 2. Ciclo de Vida e Fluxo de Trabalho (Loop Interativo)

1. **Leitura e Anotação pelo Usuário (Heverton):**
   - O usuário lê o manual da rota e insere suas dúvidas, correções, solicitações e erros no final do documento sob `## ANOTAÇÕES DO HEVERTON`.

2. **Diagnóstico, Implementação e Relatório pelo Agente:**
   - O agente analisa as anotações do Heverton.
   - O agente implementa as correções no código/banco/interface e roda os Quality Gates e testes.
   - O agente apresenta um **relatório conciso** no chat contendo: o que foi respondido, implementado e corrigido, solicitando formalmente a aprovação do Heverton.

3. **Aprovação do Usuário:**
   - O Heverton avalia e dá seu comando de aprovação ("aprovado", "pode seguir", etc.).

4. **Marcação com Sufixo `[RESOLVIDO]` e Próximo Passo:**
   - **SOMENTE APÓS A CONFIRMAÇÃO DO HEVERTON**, o agente atualiza o manual alvo adicionando o sufixo `[RESOLVIDO]` a cada item respondido/implementado/corrigido.
   - O agente pergunta se parte para o próximo manual ou se aguarda o comando do usuário.

## 3. Invariantes
- **Zero Emojis:** Proibição absoluta em código, documentação e respostas.
- **Idioma:** Estritamente PT-BR.
- **Determinismo:** Nenhuma marcação `[RESOLVIDO]` sem aprovação prévia explícita do Heverton.
