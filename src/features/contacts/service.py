# -*- coding: utf-8 -*-
"""
Vertical Slice: Contacts Service
"""

from __future__ import annotations
import json
from typing import Any, Dict, List, Optional
from src.core.database import get_connection
from src.core.security import get_user_context, resolve_data_scope_clause
from src.features.contacts.schemas import ContactCreate


def list_contacts(
    query: Optional[str] = None, 
    account_id: str = "0f14ffff", 
    user_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        user_ctx = get_user_context(conn, user_id, account_id) if user_id else None
        scope_clause, scope_params = resolve_data_scope_clause(conn, user_ctx, account_id)

        cur = conn.cursor()
        if query:
            sql = f"""
                SELECT * FROM contacts 
                WHERE ({scope_clause}) AND (name LIKE ? OR email LIKE ? OR company LIKE ?)
                ORDER BY score DESC
            """
            params = list(scope_params) + [f"%{query}%", f"%{query}%", f"%{query}%"]
            cur.execute(sql, tuple(params))
        else:
            sql = f"SELECT * FROM contacts WHERE {scope_clause} ORDER BY score DESC"
            cur.execute(sql, tuple(scope_params))

        rows = [dict(r) for r in cur.fetchall()]
        return rows
    finally:
        conn.close()


def create_contact(payload: ContactCreate) -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()
    tags_json = json.dumps(payload.tags)
    cur.execute("""
        INSERT INTO contacts (account_id, name, email, phone, company, tags, score, cro, cro_uf, specialty, work_model, monthly_implants_volume, customer_type, city, state)
        VALUES ('0f14ffff', ?, ?, ?, ?, ?, 60, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        payload.name,
        payload.email,
        payload.phone,
        payload.company,
        tags_json,
        payload.cro,
        payload.cro_uf,
        payload.specialty,
        payload.work_model,
        payload.monthly_implants_volume,
        payload.customer_type,
        payload.city,
        payload.state
    ))
    cid = cur.lastrowid
    conn.commit()
    conn.close()
    return {
        "id": cid,
        "name": payload.name,
        "email": payload.email,
        "company": payload.company,
        "score": 60,
        "cro": payload.cro,
        "cro_uf": payload.cro_uf,
        "specialty": payload.specialty,
        "work_model": payload.work_model,
        "monthly_implants_volume": payload.monthly_implants_volume,
        "customer_type": payload.customer_type,
        "city": payload.city,
        "state": payload.state
    }


def parse_csv_contacts(csv_text: str) -> List[Dict[str, Any]]:
    """Parser determinístico de linhas CSV para registros de contatos odontológicos."""
    import csv
    import io

    lines = [l for l in csv_text.strip().splitlines() if l.strip()]
    if not lines:
        return []

    # Detecta delimitador (vírgula ou ponto-e-vírgula)
    delimiter = ";" if ";" in lines[0] else ","
    reader = csv.DictReader(io.StringIO(csv_text), delimiter=delimiter)

    items = []
    for row in reader:
        # Normaliza chaves dos cabeçalhos para minúsculo sem acentos
        norm_row = {k.strip().lower().replace(" ", "_"): v.strip() for k, v in row.items() if k}
        name = norm_row.get("nome") or norm_row.get("name") or norm_row.get("dr") or norm_row.get("cirurgiao")
        if not name:
            continue
        cro = norm_row.get("cro") or norm_row.get("registro_cro")
        cro_uf = norm_row.get("cro_uf") or norm_row.get("uf") or norm_row.get("estado") or "SP"
        specialty = norm_row.get("especialidade") or norm_row.get("specialty") or "Implantodontia"
        phone = norm_row.get("telefone") or norm_row.get("phone") or norm_row.get("whatsapp")
        email = norm_row.get("email") or norm_row.get("e-mail") or f"{name.lower().replace(' ', '.')}@clinica.com.br"
        company = norm_row.get("clinica") or norm_row.get("empresa") or norm_row.get("company") or f"Clínica {name}"
        city = norm_row.get("cidade") or norm_row.get("city")
        state = norm_row.get("estado") or norm_row.get("uf") or cro_uf
        vol = norm_row.get("volume") or norm_row.get("volume_implantes") or "20-50/mês"

        items.append({
            "name": name,
            "cro": cro,
            "cro_uf": cro_uf,
            "specialty": specialty,
            "phone": phone,
            "email": email,
            "company": company,
            "city": city,
            "state": state,
            "monthly_implants_volume": vol,
            "work_model": norm_row.get("modelo_trabalho") or "Clínica Própria",
            "customer_type": norm_row.get("tipo_cliente") or "Cirurgião"
        })
    return items


def import_contacts_batch(
    payload: Any,
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """Processa importação em massa de contatos com distribuição determinística (territorial, especialidade ou round-robin)."""
    raw_items = []
    if getattr(payload, "csv_raw", None):
        raw_items.extend(parse_csv_contacts(payload.csv_raw))

    if getattr(payload, "contacts", None):
        for c in payload.contacts:
            if isinstance(c, dict):
                raw_items.append(c)
            else:
                raw_items.append(c.model_dump())

    if not raw_items:
        return {
            "success": True,
            "total_received": 0,
            "created_count": 0,
            "updated_count": 0,
            "skipped_count": 0,
            "strategy_used": payload.strategy,
            "allocations_by_rep": {},
            "items_preview": []
        }

    conn = get_connection()
    cur = conn.cursor()

    # Busca consultores ativos para regras de distribuição
    cur.execute(
        "SELECT u.id, u.name, u.team_id, t.name as team_name "
        "FROM users u "
        "LEFT JOIN teams t ON u.team_id = t.id "
        "WHERE u.account_id = ? AND coalesce(u.is_active, 1) = 1 AND coalesce(u.is_superadmin, 0) = 0",
        (account_id,)
    )
    active_reps = [dict(r) for r in cur.fetchall()]
    if not active_reps:
        # Fallback para o usuário God ou qualquer usuário se não houver reps comuns
        cur.execute("SELECT id, name, team_id FROM users WHERE account_id = ?", (account_id,))
        active_reps = [dict(r) for r in cur.fetchall()]

    # Mapeamento territorial para consultores
    sp_reps = [r for r in active_reps if "capital" in (r.get("team_name") or "").lower() or "sp" in (r.get("team_name") or "").lower()]
    interior_reps = [r for r in active_reps if "interior" in (r.get("team_name") or "").lower()]
    if not sp_reps:
        sp_reps = active_reps
    if not interior_reps:
        interior_reps = active_reps

    allocations_by_rep: Dict[str, int] = {}
    created_count = 0
    updated_count = 0
    preview_items = []

    strategy = payload.strategy or "territorial"
    round_robin_idx = 0

    for item in raw_items:
        name = item.get("name")
        email = (item.get("email") or "").strip().lower()
        cro = item.get("cro")
        cro_uf = item.get("cro_uf") or item.get("state") or "SP"
        specialty = item.get("specialty") or "Implantodontia"
        phone = item.get("phone")
        company = item.get("company")
        city = item.get("city")
        state = item.get("state") or cro_uf
        work_model = item.get("work_model") or "Clínica Própria"
        vol = item.get("monthly_implants_volume") or "20-50/mês"
        cust_type = item.get("customer_type") or "Cirurgião"

        # Decisão de Atribuição de Proprietário (Owner) e Equipe (Team)
        assigned_rep = None
        if strategy == "territorial":
            uf_clean = (cro_uf or state or "SP").upper()
            if uf_clean == "SP":
                # Divide entre capital e interior se houver cidade identificada
                if city and ("ribeirao" in city.lower() or "campinas" in city.lower() or "interior" in city.lower()):
                    assigned_rep = interior_reps[round_robin_idx % len(interior_reps)]
                else:
                    assigned_rep = sp_reps[round_robin_idx % len(sp_reps)]
            else:
                assigned_rep = active_reps[round_robin_idx % len(active_reps)]
        elif strategy == "specialty":
            # Distribui cirurgiões buco/implante prioritariamente
            assigned_rep = active_reps[round_robin_idx % len(active_reps)]
        else: # round_robin
            assigned_rep = active_reps[round_robin_idx % len(active_reps)]

        round_robin_idx += 1
        owner_id = assigned_rep["id"] if assigned_rep else None
        team_id = assigned_rep.get("team_id") if assigned_rep else None
        rep_name = assigned_rep.get("name") if assigned_rep else "Sem Atribuição"

        allocations_by_rep[rep_name] = allocations_by_rep.get(rep_name, 0) + 1

        # Deduplicação determinística por CRO + CRO_UF ou E-mail
        existing_id = None
        if cro:
            cur.execute("SELECT id FROM contacts WHERE account_id = ? AND cro = ? AND cro_uf = ?", (account_id, cro, cro_uf))
            row = cur.fetchone()
            if row:
                existing_id = row[0]

        if not existing_id and email:
            cur.execute("SELECT id FROM contacts WHERE account_id = ? AND lower(email) = ?", (account_id, email))
            row = cur.fetchone()
            if row:
                existing_id = row[0]

        tags_json = json.dumps(["Importação Em Massa", f"Estratégia: {strategy.title()}"])

        if existing_id:
            # Atualiza dados existentes
            cur.execute("""
                UPDATE contacts 
                SET name = ?, phone = coalesce(?, phone), company = coalesce(?, company),
                    specialty = ?, work_model = ?, monthly_implants_volume = ?,
                    customer_type = ?, city = coalesce(?, city), state = coalesce(?, state),
                    owner_id = coalesce(owner_id, ?), team_id = coalesce(team_id, ?)
                WHERE id = ?
            """, (name, phone, company, specialty, work_model, vol, cust_type, city, state, owner_id, team_id, existing_id))
            updated_count += 1
            cid = existing_id
        else:
            # Insere novo cirurgião
            cur.execute("""
                INSERT INTO contacts (
                    account_id, name, email, phone, company, tags, score,
                    cro, cro_uf, specialty, work_model, monthly_implants_volume,
                    customer_type, city, state, owner_id, team_id
                ) VALUES (?, ?, ?, ?, ?, ?, 65, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                account_id, name, email, phone, company, tags_json,
                cro, cro_uf, specialty, work_model, vol,
                cust_type, city, state, owner_id, team_id
            ))
            cid = cur.lastrowid
            created_count += 1

        if len(preview_items) < 10:
            preview_items.append({
                "id": cid,
                "name": name,
                "cro": f"{cro_uf}-{cro}" if cro else "N/I",
                "specialty": specialty,
                "city_uf": f"{city or 'São Paulo'} / {state or cro_uf}",
                "assigned_to": rep_name,
                "action": "Atualizado" if existing_id else "Criado"
            })

    conn.commit()
    conn.close()

    return {
        "success": True,
        "total_received": len(raw_items),
        "created_count": created_count,
        "updated_count": updated_count,
        "skipped_count": 0,
        "strategy_used": strategy,
        "allocations_by_rep": allocations_by_rep,
        "items_preview": preview_items
    }


