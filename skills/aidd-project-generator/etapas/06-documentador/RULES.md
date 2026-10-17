# RULES — Fase 6: Documentador

1. **Proibido reportar `pdf_gerado: True` sem checar `os.path.exists()` no arquivo depois da tentativa.** Esse é exatamente o bug encontrado em auditoria de código real (`_renderizar_formatos()` fixo).
2. **Se a dependência de PDF (`typst`/`weasyprint`) não estiver instalada, Gate F2 reporta `FALHOU: dependência não encontrada`** — nunca cai num "sucesso mesmo assim".
3. **Teste anti-alucinação obrigatório:** desinstalar a lib de PDF de propósito e rodar de novo — Gate F2 tem que falhar visivelmente.
4. **Conteúdo do HTML/MD tem que vir dos dados reais das fases anteriores**, não texto genérico fixo — se dois projetos diferentes geram o mesmo `arquitetura.md` byte a byte, tem template hardcoded demais.
