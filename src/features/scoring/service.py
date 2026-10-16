# -*- coding: utf-8 -*-
"""
Vertical Slice: Scoring Service (SQLite WAL)
Motor de Lead Scoring Determinístico e Classificação ICP.
"""

from __future__ import annotations
import json
import uuid
from typing import Any, Dict, List, Optional
from src.core.database import get_connection
from src.features.scoring.schemas import ScoringRuleCreate, ScoringRuleUpdate, RecalculateResponse, LeadRankItem


def list_rules(account_id: str = "0f14ffff") -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, account_id, name, category, condition_key, condition_val, points, "
        "impact_description, is_active, created_at "
        "FROM scoring_rules WHERE account_id = ? ORDER BY points DESC, created_at ASC",
        (account_id,)
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_rule(data: ScoringRuleCreate, account_id: str = "0f14ffff") -> Dict[str, Any]:
    rule_id = f"sr-{uuid.uuid4().hex[:6]}"
    conn = get_connection()
    with conn:
        conn.execute(
            "INSERT INTO scoring_rules (id, account_id, name, category, condition_key, condition_val, "
            "points, impact_description, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                rule_id,
                account_id,
                data.name,
                data.category,
                data.condition_key,
                data.condition_val,
                data.points,
                data.impact_description,
                data.is_active
            )
        )
        cur = conn.cursor()
        cur.execute("SELECT * FROM scoring_rules WHERE id = ?", (rule_id,))
        row = cur.fetchone()
    conn.close()
    return dict(row)


def update_rule(rule_id: str, data: ScoringRuleUpdate) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM scoring_rules WHERE id = ?", (rule_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return None

        current = dict(row)
        name = data.name if data.name is not None else current["name"]
        category = data.category if data.category is not None else current["category"]
        c_key = data.condition_key if data.condition_key is not None else current["condition_key"]
        c_val = data.condition_val if data.condition_val is not None else current["condition_val"]
        points = data.points if data.points is not None else current["points"]
        impact = data.impact_description if data.impact_description is not None else current["impact_description"]
        active = data.is_active if data.is_active is not None else current["is_active"]

        cur.execute(
            "UPDATE scoring_rules SET name = ?, category = ?, condition_key = ?, condition_val = ?, "
            "points = ?, impact_description = ?, is_active = ? WHERE id = ?",
            (name, category, c_key, c_val, points, impact, active, rule_id)
        )
        cur.execute("SELECT * FROM scoring_rules WHERE id = ?", (rule_id,))
        updated_row = cur.fetchone()
    conn.close()
    return dict(updated_row) if updated_row else None


def delete_rule(rule_id: str) -> bool:
    conn = get_connection()
    with conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM scoring_rules WHERE id = ?", (rule_id,))
        deleted = cur.rowcount > 0
    conn.close()
    return deleted


PRESETS_CATALOG: Dict[str, Dict[str, Any]] = {
    "implantes_cirurgia_premium": {
        "preset_key": "implantes_cirurgia_premium",
        "name": "Implantes & Cirurgia Premium",
        "description": "Qualificação de cirurgiões implantodontistas e bucomaxilo com foco em consumo direto e alto volume.",
        "target_segment": "Cirurgiões-Dentistas, Clínicas Especializadas e Hospitais Dia",
        "rules": [
            {
                "name": "Volume Alto (> 50 implantes/mês)",
                "category": "Comportamental",
                "condition_key": "monthly_implants_volume",
                "condition_val": "> 50/mês",
                "points": 35,
                "impact_description": "Prioridade Máxima: Visita comercial em até 24h"
            },
            {
                "name": "Especialidade Buco ou Implantodontia",
                "category": "Demográfico",
                "condition_key": "specialty",
                "condition_val": "Implantodontia, Cirurgia Bucomaxilofacial",
                "points": 30,
                "impact_description": "Perfil Cirúrgico Primário"
            },
            {
                "name": "Registro no CRO Ativo",
                "category": "Firmográfico",
                "condition_key": "cro",
                "condition_val": "presente",
                "points": 15,
                "impact_description": "Profissional Habilitado e Ativo"
            },
            {
                "name": "Estrutura Hospitalar / Clínica Própria",
                "category": "Firmográfico",
                "condition_key": "work_model",
                "condition_val": "Hospital Dia, Clínica Própria",
                "points": 15,
                "impact_description": "Decisor Direto da Compra"
            },
            {
                "name": "Engajamento Recente",
                "category": "Comportamental",
                "condition_key": "interaction",
                "condition_val": "interagiu",
                "points": 10,
                "impact_description": "Interação recente no WhatsApp ou Reunião"
            }
        ]
    },
    "ensino_academico": {
        "preset_key": "ensino_academico",
        "name": "Ensino & Acadêmico (Kits Graduação/Pós)",
        "description": "Focado em coordenadores de pós-graduação, professores KOLs e turmas de especialização para kits cirúrgicos.",
        "target_segment": "Faculdades (Mandic, ABO, APCD) e Cursos de Imersão",
        "rules": [
            {
                "name": "Professor / Key Opinion Leader (KOL)",
                "category": "Firmográfico",
                "condition_key": "customer_type",
                "condition_val": "Professor/KOL, Docente",
                "points": 35,
                "impact_description": "Alocação para equipe de Relacionamento Acadêmico"
            },
            {
                "name": "Instituição de Ensino Credenciada",
                "category": "Firmográfico",
                "condition_key": "work_model",
                "condition_val": "Docente Universitário, Instituto Odontológico",
                "points": 30,
                "impact_description": "Agendar Hands-on com Alunos"
            },
            {
                "name": "Aluno de Pós-Graduação",
                "category": "Demográfico",
                "condition_key": "customer_type",
                "condition_val": "Aluno Especialização",
                "points": 20,
                "impact_description": "Ofertar Kit Acadêmico Promocional"
            },
            {
                "name": "Consumo Médio (20-50/mês)",
                "category": "Comportamental",
                "condition_key": "monthly_implants_volume",
                "condition_val": "20-50/mês",
                "points": 15,
                "impact_description": "Potencial Formador de Opinião"
            }
        ]
    },
    "distribuidores_atacado": {
        "preset_key": "distribuidores_atacado",
        "name": "Distribuidores & Contratos Atacado (Sell-In)",
        "description": "Critérios de qualificação para revendas, atacado regional e representantes exclusivos de linha.",
        "target_segment": "Distribuidores Dentais e Redes de Franquias",
        "rules": [
            {
                "name": "Canal Distribuidor Oficial",
                "category": "Firmográfico",
                "condition_key": "customer_type",
                "condition_val": "Distribuidor",
                "points": 40,
                "impact_description": "Canal B2B Atacado"
            },
            {
                "name": "Modelo Franquia / Multi-unidades",
                "category": "Firmográfico",
                "condition_key": "work_model",
                "condition_val": "Franquia Odontológica, Clínica Multidisciplinar",
                "points": 25,
                "impact_description": "Contrato Corporativo Centralizado"
            },
            {
                "name": "Consumo de Grande Porte (> 50/mês)",
                "category": "Comportamental",
                "condition_key": "monthly_implants_volume",
                "condition_val": "> 50/mês",
                "points": 25,
                "impact_description": "Tabela de Preço com Margem Escalonada"
            },
            {
                "name": "Tag Sell-In Identificada",
                "category": "Comportamental",
                "condition_key": "tag",
                "condition_val": "sell-in, atacado, grande conta",
                "points": 10,
                "impact_description": "Direcionar para Gerência Distrital"
            }
        ]
    },
    "clinicas_multidisciplinares": {
        "preset_key": "clinicas_multidisciplinares",
        "name": "Clínicas & Franquias Multidisciplinares",
        "description": "Focado em consultórios com múltiplas especialidades (Prótese, Periodontia e Ortodontia).",
        "target_segment": "Clínicas Integradas e Redes Regionais",
        "rules": [
            {
                "name": "Estrutura Multidisciplinar",
                "category": "Firmográfico",
                "condition_key": "work_model",
                "condition_val": "Clínica Multidisciplinar",
                "points": 35,
                "impact_description": "Apresentação de Linha Completa de Componentes"
            },
            {
                "name": "Volume Moderado a Alto (20-50/mês)",
                "category": "Comportamental",
                "condition_key": "monthly_implants_volume",
                "condition_val": "20-50/mês, > 50/mês",
                "points": 25,
                "impact_description": "Negociação de Pacote Anual"
            },
            {
                "name": "Especialidade em Reabilitação",
                "category": "Demográfico",
                "condition_key": "specialty",
                "condition_val": "Prótese Dentária, Periodontia, Prótese & Reabilitação",
                "points": 20,
                "impact_description": "Ofertar Linha Protética e Biomateriais"
            },
            {
                "name": "CRO Regular",
                "category": "Firmográfico",
                "condition_key": "cro",
                "condition_val": "presente",
                "points": 20,
                "impact_description": "Cadastro Validado"
            }
        ]
    }
}


def list_presets() -> List[Dict[str, Any]]:
    return list(PRESETS_CATALOG.values())


def apply_preset(preset_key: str, account_id: str = "0f14ffff", overwrite_existing: bool = True) -> Dict[str, Any]:
    if preset_key not in PRESETS_CATALOG:
        raise ValueError(f"Preset '{preset_key}' não encontrado. Presets válidos: {list(PRESETS_CATALOG.keys())}")

    preset = PRESETS_CATALOG[preset_key]
    conn = get_connection()
    try:
        with conn:
            cur = conn.cursor()
            if overwrite_existing:
                cur.execute("DELETE FROM scoring_rules WHERE account_id = ?", (account_id,))

            for r in preset["rules"]:
                rule_id = f"sr-{uuid.uuid4().hex[:6]}"
                cur.execute(
                    "INSERT INTO scoring_rules (id, account_id, name, category, condition_key, condition_val, "
                    "points, impact_description, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)",
                    (
                        rule_id, account_id, r["name"], r["category"],
                        r["condition_key"], r["condition_val"], r["points"], r["impact_description"]
                    )
                )

        return {
            "success": True,
            "preset_key": preset_key,
            "name": preset["name"],
            "rules_applied": len(preset["rules"])
        }
    finally:
        conn.close()


def recalculate_all_scores(
    account_id: str = "0f14ffff",
    tier_a_min: int = 80,
    tier_b_min: int = 50
) -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()

    # 1. Obter regras ativas
    cur.execute(
        "SELECT condition_key, condition_val, points FROM scoring_rules WHERE account_id = ? AND is_active = 1",
        (account_id,)
    )
    rules = [dict(r) for r in cur.fetchall()]

    # 2. Obter contatos com campos odontológicos
    cur.execute(
        "SELECT id, name, email, phone, company, tags, score, cro, cro_uf, specialty, "
        "work_model, monthly_implants_volume, customer_type FROM contacts WHERE account_id = ?",
        (account_id,)
    )
    contacts = [dict(r) for r in cur.fetchall()]

    cur.execute("SELECT contact_name, company FROM conversations WHERE account_id = ?", (account_id,))
    convs = [dict(r) for r in cur.fetchall()]
    conv_contacts = {c["contact_name"].lower() for c in convs} | {c["company"].lower() for c in convs}

    ranked: List[Dict[str, Any]] = []
    tier_a = 0
    tier_b = 0
    tier_c = 0
    total_score_sum = 0

    with conn:
        for c in contacts:
            score = 10  # Base inicial de contato cadastrado
            tags_list = []
            try:
                raw_tags = c.get("tags") or "[]"
                tags_list = json.loads(raw_tags) if isinstance(raw_tags, str) else list(raw_tags)
            except Exception:
                tags_list = []

            tags_lower = [t.lower() for t in tags_list]
            company_lower = (c.get("company") or "").lower()
            name_lower = (c.get("name") or "").lower()
            cro_val = (c.get("cro") or "").strip()
            specialty_lower = (c.get("specialty") or "").lower()
            volume_lower = (c.get("monthly_implants_volume") or "").lower()
            customer_type_lower = (c.get("customer_type") or "").lower()
            work_model_lower = (c.get("work_model") or "").lower()

            for r in rules:
                key = r["condition_key"].lower().strip()
                targets = [v.strip().lower() for v in r["condition_val"].split(",") if v.strip()]
                pts = int(r["points"])

                if key in ("tag", "source"):
                    if any(target in tag for target in targets for tag in tags_lower):
                        score += pts
                elif key == "company":
                    if any(target in company_lower for target in targets):
                        score += pts
                elif key == "interaction":
                    if name_lower in conv_contacts or company_lower in conv_contacts:
                        score += pts
                elif key == "cro":
                    if any(t in ("presente", "valido", "has_cro", "sim", "1") for t in targets):
                        if bool(cro_val):
                            score += pts
                    elif any(t in cro_val.lower() for t in targets):
                        score += pts
                elif key == "specialty":
                    if any(target in specialty_lower for target in targets):
                        score += pts
                elif key == "monthly_implants_volume":
                    if any(target in volume_lower for target in targets):
                        score += pts
                elif key == "customer_type":
                    if any(target in customer_type_lower for target in targets):
                        score += pts
                elif key == "work_model":
                    if any(target in work_model_lower for target in targets):
                        score += pts

            # Limita entre 0 e 100
            final_score = max(0, min(100, score))
            total_score_sum += final_score

            tier = "Tier A" if final_score >= tier_a_min else ("Tier B" if final_score >= tier_b_min else "Tier C")
            if tier == "Tier A":
                tier_a += 1
            elif tier == "Tier B":
                tier_b += 1
            else:
                tier_c += 1

            conn.execute("UPDATE contacts SET score = ? WHERE id = ?", (final_score, c["id"]))

            ranked.append({
                "id": c["id"],
                "name": c["name"],
                "company": c["company"],
                "email": c["email"],
                "score": final_score,
                "tier": tier,
                "tags": tags_list,
                "cro": c.get("cro"),
                "specialty": c.get("specialty"),
                "monthly_implants_volume": c.get("monthly_implants_volume")
            })

    conn.close()

    ranked.sort(key=lambda x: x["score"], reverse=True)
    avg_score = round(total_score_sum / len(ranked), 1) if ranked else 0.0

    return {
        "recalculated_count": len(ranked),
        "tier_a_count": tier_a,
        "tier_b_count": tier_b,
        "tier_c_count": tier_c,
        "avg_score": avg_score,
        "ranked_leads": ranked
    }
