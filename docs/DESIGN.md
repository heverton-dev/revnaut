# Design System Raycast Zinc • Revnaut Dental

> **Status:** Canônico / SSOT Ativo  
> **Modo de Operação:** Operate (B2B SaaS Clínico & Comercial)  
> **Filosofia:** Ergonomia Visual, Ruído Zero, Contraste Ocular WCAG AAA e Foco em Produtividade de 8 a 12 horas.

---

## 1. Princípios e Fundamentos
1. **Ergonomia Diurna & Noturna**: suporte nativo a `[data-mode="dark"]` e `[data-mode="light"]`.
2. **Alto Contraste WCAG AAA**: nenhum texto funcional abaixo de 11px; taxa de contraste mínima de 14:1 no Modo Claro e 10:1 no Modo Escuro.
3. **Números Tabulares Determinísticos**: valores monetários e métricas financeiras utilizam `font-variant-numeric: tabular-nums` para alinhamento vertical rigoroso.
4. **Elevação Neutra e Bordas Definidas**: proibição absoluta de sombras difusas (60px/70px blur) ou halos cromáticos de IA (`dark-glow`). A profundidade é expressa por bordas ultra-finas de 1px (`var(--border-subtle)`) e elevação física real.

---

## 2. Tokens de Cor (Design Tokens)

### 2.1. Raycast Zinc Dark (Modo Escuro Padrão)
| Token | Valor Hex | Finalidade |
|---|---|---|
| `--bg-root` | `#0d0d0f` | Fundo principal da aplicação |
| `--bg-sidebar` | `#09090b` | Navegação lateral |
| `--bg-surface` | `#141417` | Topbar, cabeçalhos e painéis |
| `--bg-card` | `#19191e` | Cards de pipeline, KPIs e modais |
| `--border-subtle` | `#24242c` | Divisórias e bordas secundárias de 1px |
| `--border-card` | `#222228` | Contorno de cards |
| `--text-primary` | `#f4f4f5` | Texto principal de leitura e títulos |
| `--text-secondary` | `#a1a1aa` | Informações de suporte |
| `--text-muted` | `#71717a` | Legendas, datas e metadados |

### 2.2. Raycast Zinc Light (Modo Claro de Alto Contraste)
| Token | Valor Hex | Finalidade |
|---|---|---|
| `--bg-root` | `#f4f4f5` | Superfície papel puro antirreflexo |
| `--bg-sidebar` | `#ffffff` | Navegação lateral limpa |
| `--bg-surface` | `#ffffff` | Topbar e cabeçalhos |
| `--bg-card` | `#ffffff` | Cards de vendas, modais e formulários |
| `--border-subtle` | `#e4e4e7` | Bordas e divisórias neutras (Zinc-200) |
| `--border-card` | `#d4d4d8` | Borda estrutural de cards (Zinc-300) |
| `--text-primary` | `#09090b` | Títulos, valores e nomes (Zinc-950) |
| `--text-secondary` | `#27272a` | Textos de corpo e cargos (Zinc-800) |
| `--text-muted` | `#52525b` | Rótulos, metadados e tags (Zinc-600) |

---

## 3. Camada de Personalização (Paleta de Cores Principais / Accent)

O usuário pode escolher sua cor de destaque principal, aplicada dinamicamente via `--color-brand`:

| Nome | Hex | Perfil de Aplicação |
|---|---|---|
| **Rose Carmesim (Padrão Raycast)** | `#f43f5e` | Alta nitidez tipográfica e foco executivo |
| **Azul Elétrico (B2B Pro)** | `#0ea5e9` | Ambiente corporativo e comercial padrão |
| **Esmeralda Clínico** | `#10b981` | Saúde, odontologia cirúrgica e aprovações |
| **Violeta Digital** | `#8b5cf6` | Operações modernas e tecnológicas |
| **Âmbar Comercial** | `#f59e0b` | Pipeline dinâmico e metas |
| **Zinco Monocromático** | `#52525b` | Ruído zero absoluto |

---

## 4. Tipografia & Escala de Tamanhos

- **Família Primária**: `Inter, system-ui, -apple-system, sans-serif`
- **Família Numérica**: `'JetBrains Mono', 'Fira Code', monospace` com `tabular-nums`
- **Piso de Legibilidade**:
  - Títulos H1/H2: `20px - 24px` (Bold / Extrabold)
  - Títulos de Seção / Cards: `14px - 16px` (Semi-bold)
  - Texto de Leitura / Inputs: `13px - 14px` (Regular / Medium)
  - Metadados, Badges e Rótulos: `11px - 12px` (Semi-bold / 600) — *Proibido texto < 11px*

---

## 5. Elevação & Sombras

```css
/* Sombras de Elevação Neutra (Proibido blur > 40px) */
--shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.04);
--shadow-md: 0 4px 12px rgba(0, 0, 0, 0.12);
--shadow-lg: 0 20px 40px -12px rgba(0, 0, 0, 0.5), 0 0 0 1px var(--border-subtle);
```

---

## 6. Componentes Canônicos

### 6.1. Botão Primário (`.btn-primary`)
- Fundo: `var(--color-brand)`
- Texto: `#ffffff` (Bold 600)
- Altura mínima: `36px` / Touch target: `44px`
- Borda: `none` com `box-shadow: 0 4px 14px var(--color-brand-glow)`

### 6.2. Card de Oportunidade / Deal (`.deal-card`)
- Fundo: `var(--deal-card-bg)`
- Borda: `1px solid var(--deal-card-border)`
- Raio: `7px`
- Hover: Borda realçada em `var(--color-brand)` com elevação sutil `translateY(-1px)`.
