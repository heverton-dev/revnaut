# RULES — Fase 4: Decisor

1. **Proibido modal mockado.** `_apresentar_modal_mock()` (encontrado em auditoria de código real anterior) retorna dict fixo sempre — isso é o exato antipadrão que esta fase existe pra evitar. Usar `input()` real ou heurística real documentada.
2. **Gate C2 tem que poder falhar de verdade.** Se a implementação sempre retorna `True` pra "symlinks resolvem", o gate é fachada — testar deliberadamente com um symlink pra arquivo inexistente e confirmar que reporta `FALHOU`.
3. **Justificativa tem que ser específica à ideia**, não genérica — teste anti-alucinação: rodar com 2 ideias bem diferentes (ex: "CLI" vs "dashboard web tempo real") e confirmar que a justificativa de cada uma menciona termos daquela ideia especificamente, não frase intercambiável.
