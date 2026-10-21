# 06. Especificação Orientada por Comportamento (BDD / SDD) — Rota: support (Auditoria V3)

## Cenário 1: Carregamento do Módulo e Autenticação
- **Dado** que o operador possui sessão ativa e perfil compatível,
- **Quando** navega para `#!/support`,
- **Então** os dados são carregados do backend sem erros e a interface renderiza os componentes correspondentes.

## Cenário 2: Execução de Ações Primárias sem Toasters Vazios
- **Dado** que a interface expõe botões de interação comercial/operacional,
- **Quando** o usuário clica em qualquer ação primária,
- **Então** o sistema executa a mutação real no backend e reflete imediatamente no estado visual.
