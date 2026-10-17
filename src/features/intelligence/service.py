# -*- coding: utf-8 -*-
"""
Vertical Slice: Intelligence Service
Lógica de Negócio para Grafo Clínico KOL, Vínculos N:N e Radar Anti-Churn Odontológico.
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from src.core.database import get_connection
from src.features.intelligence.schemas import (
    ContactInstitutionCreate, ContactInstitutionOut,
    ClinicalGraphNode, ClinicalGraphEdge, ClinicalGraphResponse,
    KOLSpeakerItem, KOLSpeakerResponse,
    ChurnRiskItem, ChurnRiskSummary, ChurnRiskResponse
)


def link_contact_institution(data: ContactInstitutionCreate, account_id: str = "0f14ffff") -> Dict[str, Any]:
    """Vincula Cirurgião (CRO) a Clínica, Laboratório CAD/CAM ou Instituição de Ensino."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        # Valida existência do contato
        cur.execute("SELECT id, name, cro FROM contacts WHERE id = ? AND account_id = ?", (data.contact_id, account_id))
        contact_row = cur.fetchone()
        if not contact_row:
            raise ValueError(f"Cirurgião/Contato ID {data.contact_id} não encontrado.")

        # Valida existência da instituição
        cur.execute("SELECT id, name, institution_type FROM institutions WHERE id = ? AND account_id = ?", (data.institution_id, account_id))
        inst_row = cur.fetchone()
        if not inst_row:
            raise ValueError(f"Instituição ID '{data.institution_id}' não encontrada.")

        # Determina flag KOL
        is_kol = 1 if (data.is_kol or data.relationship_type in ("teaches_at", "kol_speaker")) else 0

        link_id = f"link_{uuid.uuid4().hex[:10]}"
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        cur.execute("""
            INSERT INTO contact_institutions (
                id, account_id, contact_id, institution_id, relationship_type, role_title, is_kol, notes, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            link_id,
            account_id,
            data.contact_id,
            data.institution_id,
            data.relationship_type,
            data.role_title,
            is_kol,
            data.notes,
            now_str
        ))
        conn.commit()

        return {
            "id": link_id,
            "account_id": account_id,
            "contact_id": data.contact_id,
            "institution_id": data.institution_id,
            "relationship_type": data.relationship_type,
            "role_title": data.role_title,
            "is_kol": bool(is_kol),
            "notes": data.notes,
            "created_at": now_str,
            "institution_name": inst_row["name"],
            "institution_type": inst_row["institution_type"],
            "contact_name": contact_row["name"],
            "contact_cro": contact_row["cro"]
        }
    finally:
        conn.close()


def list_contact_institutions(contact_id: int, account_id: str = "0f14ffff") -> List[Dict[str, Any]]:
    """Lista todos os vínculos institucionais de um cirurgião."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                ci.id, ci.account_id, ci.contact_id, ci.institution_id, ci.relationship_type,
                ci.role_title, ci.is_kol, ci.notes, ci.created_at,
                i.name as institution_name, i.institution_type,
                c.name as contact_name, c.cro as contact_cro
            FROM contact_institutions ci
            JOIN institutions i ON ci.institution_id = i.id
            JOIN contacts c ON ci.contact_id = c.id
            WHERE ci.contact_id = ? AND ci.account_id = ?
            ORDER BY ci.created_at DESC
        """, (contact_id, account_id))
        
        results = []
        for r in cur.fetchall():
            row_dict = dict(r)
            row_dict["is_kol"] = bool(row_dict["is_kol"])
            results.append(row_dict)
        return results
    finally:
        conn.close()


def unlink_contact_institution(link_id: str, account_id: str = "0f14ffff") -> bool:
    """Remove um vínculo N:N entre contato e instituição."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM contact_institutions WHERE id = ? AND account_id = ?", (link_id, account_id))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def get_clinical_graph(account_id: str = "0f14ffff") -> Dict[str, Any]:
    """Constrói a topologia completa do Grafo Clínico KOL (Cirurgião <-> Clínicas <-> Labs <-> Universidades)."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        
        # 1. Obter nós de Instituições
        cur.execute("SELECT id, name, institution_type, city, state FROM institutions WHERE account_id = ?", (account_id,))
        inst_rows = cur.fetchall()

        # 2. Obter vínculos N:N
        cur.execute("""
            SELECT 
                ci.id, ci.contact_id, ci.institution_id, ci.relationship_type, ci.is_kol, ci.role_title,
                c.name as contact_name, c.cro, c.uf, c.specialty,
                i.name as institution_name, i.institution_type
            FROM contact_institutions ci
            JOIN contacts c ON ci.contact_id = c.id
            JOIN institutions i ON ci.institution_id = i.id
            WHERE ci.account_id = ?
        """, (account_id,))
        links = cur.fetchall()

        nodes: Dict[str, Dict[str, Any]] = {}
        edges: List[Dict[str, Any]] = []
        kol_speakers_set = set()

        for inst in inst_rows:
            node_type = "university"
            itype = (inst["institution_type"] or "").lower()
            if "laborat" in itype or "cad" in itype:
                node_type = "cadcam_lab"
            elif "clínica" in itype or "hospital" in itype:
                node_type = "clinic"
            elif "radio" in itype:
                node_type = "radiology"

            nodes[inst["id"]] = {
                "id": inst["id"],
                "label": inst["name"],
                "node_type": node_type,
                "metadata": {
                    "city": inst["city"],
                    "state": inst["state"],
                    "institution_type": inst["institution_type"]
                }
            }

        relationship_labels = {
            "operates_at": "Opera na Clínica",
            "partner_cadcam": "Parceiro Laboratorial CAD/CAM",
            "teaches_at": "Docente / Leciona em",
            "kol_speaker": "Key Opinion Leader (Speaker Oficial)"
        }

        for l in links:
            c_node_id = f"surgeon_{l['contact_id']}"
            if c_node_id not in nodes:
                nodes[c_node_id] = {
                    "id": c_node_id,
                    "label": f"Dr(a). {l['contact_name']}",
                    "node_type": "surgeon",
                    "metadata": {
                        "contact_id": l["contact_id"],
                        "cro": l["cro"],
                        "uf": l["uf"],
                        "specialty": l["specialty"]
                    }
                }

            if l["is_kol"] or l["relationship_type"] in ("teaches_at", "kol_speaker"):
                kol_speakers_set.add(c_node_id)

            edges.append({
                "source": c_node_id,
                "target": l["institution_id"],
                "relationship": l["relationship_type"],
                "is_kol": bool(l["is_kol"]),
                "label": relationship_labels.get(l["relationship_type"], l["relationship_type"])
            })

        return {
            "nodes": list(nodes.values()),
            "edges": edges,
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "kol_speakers_count": len(kol_speakers_set)
        }
    finally:
        conn.close()


def list_kol_speakers(account_id: str = "0f14ffff") -> Dict[str, Any]:
    """Lista cirurgiões identificados como Key Opinion Leaders (KOLs) / Speakers com ecossistema vinculado."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                c.id as contact_id, c.name, c.cro, c.uf,
                ci.relationship_type, ci.is_kol,
                i.name as institution_name, i.institution_type
            FROM contact_institutions ci
            JOIN contacts c ON ci.contact_id = c.id
            JOIN institutions i ON ci.institution_id = i.id
            WHERE ci.account_id = ? 
              AND ci.contact_id IN (
                  SELECT DISTINCT sub_ci.contact_id 
                  FROM contact_institutions sub_ci 
                  WHERE sub_ci.account_id = ? 
                    AND (sub_ci.is_kol = 1 OR sub_ci.relationship_type IN ('teaches_at', 'kol_speaker'))
              )
        """, (account_id, account_id))
        rows = cur.fetchall()

        speakers_map: Dict[int, Dict[str, Any]] = {}
        for r in rows:
            cid = r["contact_id"]
            if cid not in speakers_map:
                speakers_map[cid] = {
                    "contact_id": cid,
                    "name": r["name"],
                    "cro": r["cro"],
                    "uf": r["uf"],
                    "institutions_count": 0,
                    "teaching_institutions": [],
                    "affiliated_clinics": [],
                    "cadcam_labs": [],
                    "monthly_volume": 0,
                    "kol_badge": "KOL Speaker Master"
                }
            item = speakers_map[cid]
            item["institutions_count"] += 1
            itype = (r["institution_type"] or "").lower()
            rel = (r["relationship_type"] or "").lower()
            if "laborat" in itype or "cad" in itype or rel == "partner_cadcam":
                item["cadcam_labs"].append(r["institution_name"])
            elif "clínica" in itype or "clinica" in itype or "hospital" in itype or rel == "operates_at":
                item["affiliated_clinics"].append(r["institution_name"])
            else:
                item["teaching_institutions"].append(r["institution_name"])

        speakers_list = list(speakers_map.values())
        return {
            "total_kols": len(speakers_list),
            "speakers": speakers_list
        }
    finally:
        conn.close()


def get_churn_risk_radar(account_id: str = "0f14ffff", days_threshold: Optional[int] = None) -> Dict[str, Any]:
    """
    Motor de Inteligência de Carteira & Previsão de Churn (RFM Odontológico).
    Cruza o ciclo médio de recompra de implantes/componentes com a data do último faturamento/pedido.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        
        # Busca contatos do tenant
        cur.execute("""
            SELECT 
                c.id, c.name, c.cro, c.clinic_name, c.company, c.uf, c.score,
                c.monthly_implant_volume, c.reorder_cycle_days, c.last_order_date, c.created_at,
                (
                    SELECT MAX(d.created_at) 
                    FROM deals d 
                    WHERE (d.contact_name = c.name OR d.company = c.company) 
                      AND d.account_id = c.account_id
                ) as latest_deal_date
            FROM contacts c
            WHERE c.account_id = ?
            ORDER BY c.score DESC, c.id ASC
        """, (account_id,))
        contacts = cur.fetchall()

        now = datetime.now(timezone.utc)
        radar_items: List[Dict[str, Any]] = []

        critical_count = 0
        high_risk_count = 0
        medium_risk_count = 0
        low_risk_count = 0

        for row in contacts:
            c = dict(row)
            # Volume mensal
            vol = c.get("monthly_implant_volume") or 0
            if isinstance(vol, str):
                try:
                    vol = int(vol)
                except ValueError:
                    vol = 0

            # Ciclo médio estimado ou configurado
            reorder_cycle = c.get("reorder_cycle_days") or 0
            if reorder_cycle <= 0:
                if vol >= 50:
                    reorder_cycle = 12
                elif vol >= 25:
                    reorder_cycle = 18
                elif vol >= 10:
                    reorder_cycle = 24
                else:
                    reorder_cycle = 30

            # Data da última compra
            order_date_str = c.get("last_order_date") or c.get("latest_deal_date") or c.get("created_at")
            days_since = 30  # fallback
            if order_date_str:
                try:
                    # Trata variações de formato ISO / SQLite
                    clean_date = str(order_date_str).replace("Z", "").split(".")[0]
                    if " " in clean_date:
                        dt = datetime.strptime(clean_date, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                    else:
                        dt = datetime.strptime(clean_date[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
                    days_since = max(0, (now - dt).days)
                except Exception:
                    days_since = 30

            # Cálculo de atraso
            days_overdue = max(0, days_since - reorder_cycle)

            # Cálculo do Churn Risk Score (0 a 100)
            if days_overdue == 0:
                score = min(35, int((days_since / max(1, reorder_cycle)) * 35))
            else:
                pct_over = days_overdue / max(1, reorder_cycle)
                score = min(100, int(50 + (pct_over * 50)))

            # Invariante da Spec: cirurgião que comprava a cada <= 20 dias e passa de 30 dias sem faturar
            if reorder_cycle <= 20 and days_since >= 30:
                score = max(score, 85)

            # Classificação de Risco
            if score >= 80:
                level = "critico"
                action = "Disparar visita técnica presencial do Assessor Comercial e reposição emergencial de kit"
                critical_count += 1
            elif score >= 60:
                level = "alto"
                action = "Contato telefônico imediato do Closer Regional em até 24h com checagem de estoque clínico"
                high_risk_count += 1
            elif score >= 40:
                level = "medio"
                action = "Disparo de cadência automatizada de reposição via WhatsApp (Evolution API)"
                medium_risk_count += 1
            else:
                level = "baixo"
                action = "Manter relacionamento padrão e monitoramento de consumo cirúrgico"
                low_risk_count += 1

            tier = "Tier A" if (c.get("score") or 0) >= 80 else ("Tier B" if (c.get("score") or 0) >= 50 else "Tier C")

            radar_items.append({
                "contact_id": c["id"],
                "name": c["name"],
                "cro": c.get("cro"),
                "clinic_name": c.get("clinic_name") or c.get("company"),
                "uf": c.get("uf"),
                "tier": tier,
                "monthly_implant_volume": vol,
                "avg_reorder_interval_days": reorder_cycle,
                "days_since_last_order": days_since,
                "days_overdue": days_overdue,
                "last_order_date": str(order_date_str) if order_date_str else None,
                "churn_risk_score": score,
                "churn_risk_level": level,
                "recommended_action": action
            })

        # Ordena por risco decrescente (maior score primeiro)
        radar_items.sort(key=lambda x: x["churn_risk_score"], reverse=True)

        return {
            "summary": {
                "total_monitored": len(radar_items),
                "critical_count": critical_count,
                "high_risk_count": high_risk_count,
                "medium_risk_count": medium_risk_count,
                "low_risk_count": low_risk_count
            },
            "radar": radar_items
        }
    finally:
        conn.close()
