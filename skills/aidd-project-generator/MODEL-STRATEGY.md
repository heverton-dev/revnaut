# 🎯 MODELO STRATEGY: aidd-project-generator v2.1

**REGRA FUNDAMENTAL:** Nada oculto. Transparência total. Conhecimento = Poder.

---

## 📋 Estratégia Híbrida de Modelos

### **Princípio Padrão: HERANÇA DO HARNESS**

Cada phase usa o **modelo configurado no harness** automaticamente:

```
┌─────────────────────────────┐
│   Harness (Claude Code)     │
│   - Modelo: Claude Haiku 4.5│
│   - Provider: Anthropic     │
│   - Speed: /fast OFF        │
└────────────┬────────────────┘
             │
             ├─→ Phase 2 (Agent) herda: Haiku
             ├─→ Phase 3 (Agent) herda: Haiku
             └─→ Todos agents: Haiku
```

✅ **Vantagem:** Usuário controla modelo CENTRALMENTE via:
- `/fast` — ativa Fast Mode (Opus + faster output)
- `/model haiku|sonnet|opus` — muda globalmente
- Settings → Claude Model — escolhe versão
- Nada replicado, tudo sincronizado

---

### **Sobrescrita Opcional: POR QUÊ E COMO**

Usuário PODE forçar modelo diferente para fase específica:

```bash
# Usar Opus para Phase 3 (mais complexa), Haiku para Phase 2
python orquestrador.py \
  --fase-3-model "opus" \
  --fase-2-model "haiku"
```

#### **Casos de Uso Legítimos:**

| Caso | Phase | Razão | Model |
|------|-------|-------|-------|
| Analysis densa | Phase 2 | Precisa entender requirements complexos | opus |
| Design com 5 subagentes | Phase 3 | Orquestração paralela exige coerência | opus |
| Prototipagem rápida | Phase 2-3 | Validar fluxo antes de produção | haiku |
| Produção econômica | Todas | Máxima eficiência | haiku |

---

## 🔍 TRANSPARÊNCIA: O Que o Usuário Vê

### **Na Inicialização da Skill**

```
📊 aidd-project-generator v2.1
   Harness Model: Claude Haiku 4.5
   Provider: Anthropic
   Speed Mode: OFF (/fast para ativar)
   
⚙️ Configuração de Modelos:
   Phase 1 (Pesquisador):   herança → Haiku
   Phase 2 (Analisador):    herança → Haiku (pode: --phase-2-model opus)
   Phase 3 (Designer):      herança → Haiku (pode: --phase-3-model opus)
   Phase 4 (Decisor):       herança → Haiku (determinístico, sem LLM)
   Phase 5 (Criador):       herança → Haiku (determinístico, sem LLM)
   Phase 6 (Documentador):  herança → Haiku (pode: --phase-6-model opus)
```

### **Durante Execução de Each Agent**

```
🚀 Phase 3.1: Subagente "Arquiteto de Camadas"
   ├─ Model: Claude Haiku 4.5 (herdado)
   ├─ Tokens estimados: 8k
   ├─ Reasoning effort: medium
   └─ Command override: --phase-3-model opus [disponível]

💭 Enviando prompt para Haiku...
✅ Resposta recebida: 5 camadas AIDD definidas
```

### **No Final da Fase**

```
📊 Phase 2 Relatório
   ├─ Model usado: Claude Haiku 4.5
   ├─ Tokens consumidos: 5,234
   ├─ Gate A1: PASSOU
   ├─ Gate A2: PASSOU
   └─ ℹ️ Para próxima vez: considere --phase-2-model opus
      (análise ficou ok, mas se quiser mais profundidade: Opus)
```

---

## 💡 Implementação no Código

### **Phase 2: Analisador da Ideia**

```python
class AnalisadorFase2:
    def __init__(self, pasta_cache: Path, model_override: str = None):
        self.model_override = model_override  # ← Parâmetro explícito
        self.model_final = self._resolver_modelo()

    def _resolver_modelo(self) -> str:
        """
        Resolve qual modelo usar com TOTAL TRANSPARÊNCIA
        
        Regra:
        1. Se --model-override foi passado → usar esse
        2. Senão → herdar do harness (padrão)
        3. LOG sempre qual foi decidido
        """
        if self.model_override:
            self.log(f"⚙️ Override detectado: Phase 2 → {self.model_override}")
            return self.model_override
        else:
            harness_model = self._detectar_harness_model()  # Ler do ambiente
            self.log(f"📦 Herdando do harness: Phase 2 → {harness_model}")
            return harness_model

    def executar(self, ideia_projeto: str) -> Dict:
        print(f"\n📊 PHASE 2: Analisador da Ideia")
        print(f"   Modelo: {self.model_final}")  # ← EXPLÍCITO
        print(f"   {'-' * 60}")
        
        # Chamar Agent com modelo resolvido
        analise = agent(
            prompt=f"Analise: {ideia_projeto}...",
            model=self.model_final,  # ← Passado explicitamente
            label="analisador:ideia",
            phase="Phase 2"
        )
        
        return analise
```

### **Phase 3: Designer AIDD**

```python
class DesignerFase3:
    def __init__(self, pasta_cache: Path, model_override: str = None):
        self.model_override = model_override
        self.model_final = self._resolver_modelo()

    def executar(self, ideia_projeto: str) -> Dict:
        print(f"\n🎨 PHASE 3: Designer AIDD (5 Subagentes)")
        print(f"   Modelo de orquestração: {self.model_final}")
        print(f"   {'-' * 60}")
        
        # Cada subagente HERDA O MESMO MODELO
        resultados = []
        for i, (nome, prompt) in enumerate(PROMPTS_SUBAGENTES.items(), 1):
            print(f"\n   🤖 Subagente {i}/5: {nome}")
            print(f"      Model: {self.model_final}")  # ← EXPLÍCITO
            
            resultado = agent(
                prompt=prompt,
                model=self.model_final,  # ← Mesmo modelo para todos
                label=f"designer:subagente-{i}",
                phase="Phase 3"
            )
            resultados.append(resultado)
        
        return resultados
```

---

## 🎮 CLI: Como Usuário Controla

### **Uso Padrão (Herança)**

```bash
# Phase 2 e 3 herdam do harness (Haiku por padrão)
python orquestrador.py --ideia "Criar API REST"
```

### **Potencializar Fase 2 com Opus**

```bash
# Phase 2 usa Opus (análise mais profunda)
# Phase 3 usa Haiku (economia)
python orquestrador.py \
  --ideia "Criar API REST" \
  --phase-2-model opus
```

### **Potencializar Fase 3 com Opus**

```bash
# Phase 3 usa Opus (5 subagentes = mais complexo)
python orquestrador.py \
  --ideia "Criar API REST" \
  --phase-3-model opus
```

### **Ambas com Opus**

```bash
# Máxima qualidade (mais caro, mais tokens)
python orquestrador.py \
  --ideia "Criar API REST" \
  --phase-2-model opus \
  --phase-3-model opus
```

### **Forçar Fable (Mais barato que Haiku)**

```bash
# Máxima economia (experimental)
python orquestrador.py \
  --ideia "Criar API REST" \
  --phase-2-model fable \
  --phase-3-model fable
```

---

## 📊 Tabela: Impacto de Cada Escolha

| Config | Phase 2 | Phase 3 | Tokens | Custo | Speed | Qualidade |
|--------|---------|---------|--------|-------|-------|-----------|
| **Default** | Haiku | Haiku | 35k | $ | ⚡⚡ | ✅✅ |
| **Otimizado P2** | Opus | Haiku | 45k | $$$ | ⚡ | ✅✅✅ |
| **Otimizado P3** | Haiku | Opus | 45k | $$$ | ⚡ | ✅✅✅ |
| **Premium** | Opus | Opus | 55k | $$$$ | ⚡ | ✅✅✅✅ |
| **Econômico** | Fable | Fable | 25k | $$ | ⚡⚡⚡ | ✅ |

---

## 📝 Logging: Rastreabilidade Total

Cada execution gera LOG com modelo usado:

```json
{
  "_phase_02_index.json": {
    "model_utilizado": "claude-haiku-4-5-20251001",
    "model_origem": "herança do harness",
    "override_aplicado": false,
    "tokens_consumidos": 5234,
    "recomendacao": "Para análise mais profunda, considere --phase-2-model opus"
  }
}
```

---

## 🎓 Educação: Help Text Explícito

```bash
$ python orquestrador.py --help

Optional arguments:
  --phase-2-model {haiku|sonnet|opus|fable}
        Modelo LLM para Phase 2 (Analisador)
        Padrão: herda do harness
        Quando mudar: se análise parecer superficial
        Custo: +10k tokens com Opus vs Haiku
        
  --phase-3-model {haiku|sonnet|opus|fable}
        Modelo LLM para Phase 3 (Designer + 5 subagentes)
        Padrão: herda do harness
        Quando mudar: para orquestração paralela complexa
        Custo: +15k tokens com Opus vs Haiku
        
Exemplos:
  python orquestrador.py --ideia "..." --phase-3-model opus
  python orquestrador.py --ideia "..." --phase-2-model opus --phase-3-model opus
```

---

## ✅ Checklist de Transparência

- [x] Usuário vê qual modelo é usado no início
- [x] Usuário vê qual modelo é usado durante execução
- [x] Usuário vê qual modelo foi usado no relatório final
- [x] Usuário PODE mudar modelo (CLI parameters)
- [x] Usuário ENTENDE por quê mudar (help text + recomendações)
- [x] Usuário VÊ impacto (tokens, custo, speed)
- [x] Logs rastreiam TUDO (JSON index com modelo_utilizado)
- [x] Zero mistério. Zero magic. Conhecimento total = Poder total.

---

**Versão:** 1.0  
**Data:** 29/08/2026  
**Princípio:** Nada Oculto. Transparência Total. Conhecimento É Poder.
