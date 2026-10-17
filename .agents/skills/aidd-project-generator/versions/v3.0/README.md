# v3.0 Implementation Plan

**Target:** 75/100  
**Horas:** 250h (~2 meses)  
**User Stories:** 5 (US-3.1 → US-3.5)

## Overview

v3.0 adiciona feedback loops ao sistema. Quando um gate falha, o agent não desiste — tenta múltiplas estratégias de recuperação.

## User Stories

### US-3.1: Feedback Loop Framework (40h)
- [ ] Criar classe `FeedbackLoop`
- [ ] Implementar retry logic com backoff
- [ ] Testes com 5+ cenários de falha
- [ ] Integração em Phase 5 (Criador)

### US-3.2: Self-Correction (50h)
- [ ] Detectar schema violations
- [ ] Gerar correction prompts
- [ ] Reexecuta Agent com feedback
- [ ] Testes de válida/inválida → corrigida

### US-3.3: Error Recovery Strategies (70h)
- [ ] Estratégia A: Retry puro
- [ ] Estratégia B: Contexto reduzido
- [ ] Estratégia C: Adiciona exemplos
- [ ] Estratégia D: Escalona para human

### US-3.4: Honest Uncertainty Communication (40h)
- [ ] Confidence scoring (< 70% flag)
- [ ] Multi-path offering
- [ ] Deixar usuário escolher

### US-3.5: Multi-Turn Conversations (50h)
- [ ] ConversationManager class
- [ ] Integrar em Phase 2
- [ ] State persistence

## Gates

- [ ] FB1: Retry framework funciona
- [ ] FB2: Self-correction funciona
- [ ] FB3: Uncertainty communication funciona
- [ ] FB4: Multi-turn integration funciona

## Timeline

```
Semana 1-2: US-3.1
Semana 2-3: US-3.2
Semana 3-4: US-3.3
Semana 4-5: US-3.4
Semana 5-6: US-3.5
Semana 6-7: Testes + refinamento
Semana 7-8: Documentação + release
```

## Next Step

👉 Começar com US-3.1 (Feedback Loop Framework)
