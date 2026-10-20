# 07. Plano de Ação em Micro-Tickets Cirúrgicos — Rota: deals

## Catálogo de Micro-Tickets Executáveis

---

### TICKET-DEALS-01: Extração Arquitetural VSA de DealsWorkspace.tsx
- **O Que Fazer:** Desacoplar a rota de negociações de `frontend/src/App.tsx`, movendo todo o código de Kanban, DataTable e Drawer para `frontend/src/features/deals/DealsWorkspace.tsx`.
- **Como Fazer:** Criar o componente autônomo com suas props e tipagens, e atualizar `frontend/src/router.tsx` no case `"deals"` para instanciar `<DealsWorkspace />`.
- **Onde Fazer:**
  - Criar: `frontend/src/features/deals/DealsWorkspace.tsx`
  - Limpar: `frontend/src/App.tsx` (linhas 148-1120)
- **Critério Binário de Aceitação:** `npm run build` ou `tsc --noEmit` executando com código `exit 0`.

---

### TICKET-DEALS-02: Integração do Catálogo Odontológico no Drawer de Oportunidades
- **O Que Fazer:** Substituir o input numérico solto de valor por um seletor de itens do catálogo de produtos odontológicos (`/api/v1/deals/catalog/products`), calculando o valor do negócio automaticamente com base na quantidade de implantes e kit protético selecionados.
- **Como Fazer:** Adicionar chamada `useQuery(["catalog_products"])` no Drawer lateral e renderizar um componente `Select` com busca de implantes.
- **Onde Fazer:**
  - Arquivo: `frontend/src/App.tsx` (ou novo `DealsWorkspace.tsx`, seção do Drawer)
- **Critério Binário de Aceitação:** Ao selecionar produtos, o valor total do negócio é calculado e exibido em BRL de forma determinística.

---

### TICKET-DEALS-03: Ação Rápida de Despacho DENTGO a Partir de Negócios Ganhos
- **O Que Fazer:** Incluir um botão "Despachar com DENTGO (45 min)" no Drawer lateral para negócios no estágio "Contrato" ou "Fechado Ganho".
- **Como Fazer:** Ao clicar, navegar para `#!/dentgo?deal_id=...` ou abrir modal pré-preenchido para solicitar motoboy express com os implantes da oportunidade.
- **Onde Fazer:**
  - Arquivo: Drawer lateral de Deals
- **Critério Binário de Aceitação:** Redirecionamento ou abertura de modal transferindo o ID do negócio e produtos para o formulário de entrega rápida.
