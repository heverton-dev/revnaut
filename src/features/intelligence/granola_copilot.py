# -*- coding: utf-8 -*-
"""
Vertical Slice: Granola-like Copilot & Zero-Touch Deal Automation
Extração cognitiva estruturada com LiteLLM e auto-preenchimento determinístico do CRM.
"""

from __future__ import annotations
import json
import os
import re
import uuid
from typing import Any, Dict, List, Optional
import httpx
from src.core.database import get_connection
from src.features.intelligence.schemas import MeetingIntelligenceExtraction


def _call_llm_structured_extraction(transcription_text: str) -> Optional[MeetingIntelligenceExtraction]:
    api_key = os.getenv("LITELLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = (
        os.getenv("LITELLM_BASE_URL")
        or os.getenv("OPENAI_BASE_URL")
        or os.getenv("OLLAMA_BASE_URL")
    )
    if not api_key and not base_url:
        return None

    endpoint = f"{(base_url or 'https://api.openai.com/v1').rstrip('/')}/chat/completions"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    prompt = (
        "Extraia os dados estruturados da reunião comercial odontológica em JSON estrito com as chaves: "
        "executive_summary (str), implant_systems_mentioned (list[str]), competitors_cited (list[str]), "
        "objections_raised (list[dict com category, objection_text, suggested_counter_argument]), "
        "next_steps_tasks (list[dict com title, due_date, assignee, priority]), "
        "suggested_deal_value (float|null), suggested_probability (int).\n\n"
        f"Transcrição:\n{transcription_text}"
    )

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(
                endpoint,
                headers=headers,
                json={
                    "model": os.getenv("LITELLM_MODEL", "gpt-4o-mini"),
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.0,
                },
            )
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                return MeetingIntelligenceExtraction(**parsed)
    except Exception:
        return None
    return None


def extract_meeting_intelligence(
    transcription_text: str,
    deal_id: Optional[str] = None,
    account_id: str = "0f14ffff"
) -> MeetingIntelligenceExtraction:
    """
    Submete a transcrição comercial odontológica para extração estruturada de inteligência
    via LiteLLM/OpenAI (quando configurado) ou extrator NLP determinístico generalizado.
    """
    llm_result = _call_llm_structured_extraction(transcription_text)
    if llm_result is not None:
        return llm_result

    text_lower = transcription_text.lower()

    # 1. Detecção de Sistemas de Implante e Kits
    implant_systems: List[str] = []
    system_patterns = [
        (r"cone\s+morse", "Cone Morse"),
        (r"hex[áa]gono\s+externo|\bhe\b", "Hexágono Externo"),
        (r"hex[áa]gono\s+interno|\bhi\b", "Hexágono Interno"),
        (r"zigom[áa]tico", "Zigomático"),
        (r"grand\s+morse|\bgm\b", "Grand Morse"),
        (r"cirurgia\s+guiada|kit\s+guiado", "Kit Cirurgia Guiada"),
        (r"biomaterial|enxerto", "Biomaterial Ósseo"),
    ]
    for pattern, label in system_patterns:
        if re.search(pattern, text_lower) and label not in implant_systems:
            implant_systems.append(label)
    if not implant_systems:
        implant_systems.append("Cone Morse Universal")

    # 2. Detecção de Concorrentes Citados
    competitors: List[str] = []
    known_competitors = [
        "neodent", "straumann", "sin", "implacil", "dsp", "bicon",
        "zimmer", "nobel", "biomax", "titaniumfix", "conexao", "conexão"
    ]
    for comp in known_competitors:
        if re.search(rf"\b{comp}\b", text_lower):
            comp_norm = comp.capitalize()
            if comp_norm not in competitors:
                competitors.append(comp_norm)

    # 3. Detecção Generalizada de Objeções (prazos arbitrários, preços, frete, estoque/lote)
    objections: List[Dict[str, str]] = []
    days_match = re.search(r"(\d+)\s*dias", text_lower)
    if any(k in text_lower for k in ["prazo", "parcela", "boleto", "pagamento", "faturar"]) or days_match:
        d_str = f"{days_match.group(1)} dias" if days_match else "60 dias"
        objections.append({
            "category": "prazo",
            "objection_text": f"Cirurgião solicitou condição de faturamento em {d_str}.",
            "suggested_counter_argument": f"Oferecer faturamento escalonado ({d_str}) vinculado a volume mínimo ou contrato KeyPartners."
        })
    if any(k in text_lower for k in ["caro", "desconto", "preço", "preco", "valor alto", "custo", "tabela"]):
        objections.append({
            "category": "preco",
            "objection_text": "Sensibilidade ao preço unitário por implante/componente comparado à concorrência.",
            "suggested_counter_argument": "Demonstrar bonificação de componentes protéticos e economia com kit cirúrgico único."
        })
    if any(k in text_lower for k in ["entrega", "urgência", "urgencia", "demora", "frete"]):
        objections.append({
            "category": "logistica",
            "objection_text": "Preocupação com SLA de entrega para cirurgia agendada.",
            "suggested_counter_argument": "Ativar entrega expressa DENTGO em até 2h a partir do Hub regional mais próximo."
        })

    # 4. Cálculo Generalizado de Quantidade, Preço Unitário e Valor Sugerido
    suggested_value: Optional[float] = None
    explicit_val_match = re.search(r"r\$\s*([\d\.]+(?:,\d{1,2})?)", text_lower)
    unit_price = 450.0
    unit_match = re.search(r"a\s*r\$\s*(\d+(?:[.,]\d{1,2})?)", text_lower)
    if unit_match:
        try:
            unit_price = float(unit_match.group(1).replace(".", "").replace(",", "."))
        except ValueError:
            unit_price = 450.0

    qty_matches = re.findall(r"(\d+)\s+(?:implantes|unidades|caixas|kits|componentes)", text_lower)
    if qty_matches:
        total_qty = sum(int(q) for q in qty_matches)
        suggested_value = float(total_qty * unit_price)
    elif explicit_val_match:
        try:
            raw_v = explicit_val_match.group(1).replace(".", "").replace(",", ".")
            suggested_value = float(raw_v)
        except ValueError:
            suggested_value = None

    # 5. Detecção de Tarefas e Prazos
    due = "Em 2 dias"
    for pat, label in [
        (r"sexta(?:-feira)?", "Sexta-feira"),
        (r"segunda(?:-feira)?", "Segunda-feira"),
        (r"ter[çc]a(?:-feira)?", "Terça-feira"),
        (r"quarta(?:-feira)?", "Quarta-feira"),
        (r"quinta(?:-feira)?", "Quinta-feira"),
        (r"amanh[ãa]", "Amanhã"),
        (r"hoje", "Hoje"),
    ]:
        if re.search(pat, text_lower):
            due = label
            break

    tasks: List[Dict[str, Any]] = []
    if any(k in text_lower for k in ["proposta", "enviar proposta", "fechar", "pedido", "orçamento", "orcamento"]):
        tasks.append({
            "title": "Enviar proposta comercial formal e termo de faturamento",
            "due_date": due,
            "assignee": "Inside Sales / Consultor Comercial",
            "priority": "alta"
        })
    if any(k in text_lower for k in ["visita", "presencial", "levar kit", "hands-on", "amostra"]):
        tasks.append({
            "title": "Agendar visita presencial com demonstração física do Kit Cirúrgico",
            "due_date": due,
            "assignee": "Consultor Field Sales",
            "priority": "alta"
        })
    if not tasks:
        tasks.append({
            "title": "Follow-up de alinhamento clínico pós-reunião",
            "due_date": due,
            "assignee": "Consultor Comercial",
            "priority": "media"
        })

    summary = (
        f"Alinhamento comercial com cirurgião. Sistemas de interesse: {', '.join(implant_systems)}. "
        f"Concorrentes citados: {', '.join(competitors) if competitors else 'nenhum'}. "
        f"Objeções: {', '.join(o['category'] for o in objections) if objections else 'nenhuma'}. "
        f"Próximo passo agendado para {due}."
    )

    return MeetingIntelligenceExtraction(
        executive_summary=summary,
        implant_systems_mentioned=implant_systems,
        competitors_cited=competitors,
        objections_raised=objections,
        next_steps_tasks=tasks,
        suggested_deal_value=suggested_value,
        suggested_probability=80 if suggested_value else 75
    )


def apply_copilot_intelligence_to_deal(
    deal_id: str,
    extraction: MeetingIntelligenceExtraction,
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """
    Zero-Touch CRM: atualiza o Deal, insere objeções e agenda tarefas operacionais
    automaticamente a partir da extração cognitiva.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()

        if extraction.suggested_deal_value is not None:
            cur.execute("""
                UPDATE deals
                SET value = ?,
                    executive_summary = ?
                WHERE id = ? AND account_id = ?
            """, (extraction.suggested_deal_value, extraction.executive_summary, deal_id, account_id))
        else:
            cur.execute("""
                UPDATE deals
                SET executive_summary = ?
                WHERE id = ? AND account_id = ?
            """, (extraction.executive_summary, deal_id, account_id))

        objections_inserted = 0
        for obj in extraction.objections_raised:
            obj_id = f"obj-{uuid.uuid4().hex[:6]}"
            cur.execute("""
                INSERT INTO deal_objections (
                    id, account_id, deal_id, category, objection_text,
                    suggested_counter_argument, resolved
                ) VALUES (?, ?, ?, ?, ?, ?, 0)
            """, (
                obj_id, account_id, deal_id,
                obj.get("category", "outros"),
                obj.get("objection_text", ""),
                obj.get("suggested_counter_argument", "")
            ))
            objections_inserted += 1

        tasks_inserted = 0
        for task in extraction.next_steps_tasks:
            task_id = f"task-{uuid.uuid4().hex[:6]}"
            cur.execute("""
                INSERT INTO tasks (
                    id, account_id, title, due_date, assignee, priority, completed
                ) VALUES (?, ?, ?, ?, ?, ?, 0)
            """, (
                task_id, account_id,
                task.get("title", "Follow-up de Deal"),
                task.get("due_date", "Hoje"),
                task.get("assignee", "Consultor Comercial"),
                task.get("priority", "alta")
            ))
            tasks_inserted += 1

        conn.commit()
    finally:
        conn.close()

    return {
        "success": True,
        "deal_id": deal_id,
        "updated_value": extraction.suggested_deal_value,
        "objections_count": objections_inserted,
        "tasks_count": tasks_inserted,
        "executive_summary": extraction.executive_summary
    }


def process_field_voice_note(
    deal_id: str,
    voice_note_text: Optional[str] = None,
    r2_audio_key: Optional[str] = None,
    account_id: str = "0f14ffff",
) -> Dict[str, Any]:
    """
    Processa notas rápidas de voz de 30s enviadas pelo consultor externo (Field Sales) via WhatsApp
    após visita presencial à clínica, transcrevendo e aplicando Zero-Touch no Deal.
    """
    from src.features.intelligence.transcription_worker import process_call_audio

    call_id = f"field-vn-{uuid.uuid4().hex[:8]}"
    transc_res = process_call_audio(
        call_id=call_id,
        account_id=account_id,
        dialogue_text=voice_note_text,
        r2_audio_key=r2_audio_key,
        duration_seconds=30.0,
    )
    full_text = " ".join(s["text"] for s in transc_res["segments"])
    extraction = extract_meeting_intelligence(
        transcription_text=full_text,
        deal_id=deal_id,
        account_id=account_id,
    )
    applied = apply_copilot_intelligence_to_deal(
        deal_id=deal_id,
        extraction=extraction,
        account_id=account_id,
    )
    return {
        "success": True,
        "deal_id": deal_id,
        "call_id": call_id,
        "transcription_id": transc_res["transcription_id"],
        "extraction": extraction,
        "updated_value": applied["updated_value"],
        "objections_count": applied["objections_count"],
        "tasks_count": applied["tasks_count"],
    }

