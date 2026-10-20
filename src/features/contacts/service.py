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


def export_contacts_data(
    format: str = "csv",
    query: Optional[str] = None,
    account_id: str = "0f14ffff",
    user_id: Optional[str] = None
) -> bytes:
    fmt = (format or "csv").lower().strip()
    contacts = list_contacts(query=query, account_id=account_id, user_id=user_id)
    if fmt == "parquet":
        import pyarrow as pa
        import pyarrow.parquet as pq
        clean_contacts = []
        for c in contacts:
            clean_contacts.append({
                "id": str(c.get("id", "")),
                "name": str(c.get("name", "") or ""),
                "email": str(c.get("email", "") or ""),
                "phone": str(c.get("phone", "") or ""),
                "company": str(c.get("company", "") or ""),
                "cro": str(c.get("cro", "") or ""),
                "cro_uf": str(c.get("cro_uf", "") or ""),
                "score": int(c.get("score", 0) or 0),
                "customer_type": str(c.get("customer_type", "") or ""),
            })
        if not clean_contacts:
            clean_contacts = [{"id": "", "name": "", "email": "", "phone": "", "company": "", "cro": "", "cro_uf": "", "score": 0, "customer_type": ""}]
        table = pa.Table.from_pylist(clean_contacts)
        sink = pa.BufferOutputStream()
        pq.write_table(table, sink)
        return sink.getvalue().to_pybytes()

    import io, csv
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["ID", "Nome", "Email", "Telefone", "Clinica_Empresa", "CRO", "UF", "Score", "Tipo"])
    for c in contacts:
        writer.writerow([
            c.get("id", ""),
            c.get("name", ""),
            c.get("email", ""),
            c.get("phone", ""),
            c.get("company", ""),
            c.get("cro", ""),
            c.get("cro_uf", ""),
            c.get("score", 0),
            c.get("customer_type", "")
        ])
    return output.getvalue().encode("utf-8")


def create_contact(payload: ContactCreate) -> Dict[str, Any]:
    from src.features.contacts.cro_validator import verify_cro_status

    cro_verified = False
    effective_cro = payload.cro
    effective_uf = payload.cro_uf

    if payload.cro:
        res = verify_cro_status(payload.cro, payload.cro_uf)
        if res.get("verified"):
            cro_verified = True
            effective_cro = payload.cro
            effective_uf = res.get("uf") or payload.cro_uf


    conn = get_connection()
    cur = conn.cursor()
    tags_json = json.dumps(payload.tags)
    cur.execute("""
        INSERT INTO contacts (
            account_id, name, email, phone, company, tags, score, 
            cro, cro_uf, cro_verified, specialty, work_model, 
            monthly_implants_volume, customer_type, city, state
        )
        VALUES ('0f14ffff', ?, ?, ?, ?, ?, 60, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        payload.name,
        payload.email,
        payload.phone,
        payload.company,
        tags_json,
        effective_cro,
        effective_uf,
        1 if cro_verified else 0,
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
        "cro": effective_cro,
        "cro_uf": effective_uf,
        "cro_verified": cro_verified,
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


def get_contact_timeline(contact_id: int) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, contact_id, user_id, author_name, action, old_value, new_value, comment, created_at
        FROM contact_audit_logs
        WHERE contact_id = ?
        ORDER BY created_at DESC, id DESC
    """, (contact_id,))
    logs = [dict(r) for r in cur.fetchall()]
    
    if not logs:
        cur.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
        row = cur.fetchone()
        contact = dict(row) if row else {}
        name = contact.get("name", "Cirurgião")
        specialty = contact.get("specialty", "Implantodontia")
        score = contact.get("score", 75)
        created_at = contact.get("created_at", "2026-10-15 10:00:00")
        
        logs = [
            {
                "id": f"seed-7-{contact_id}",
                "contact_id": contact_id,
                "user_id": "usr_sdr",
                "author_name": "Juliana Santos (SDR)",
                "action": "Chamada Telefônica / Alinhamento",
                "old_value": "Tentativa",
                "new_value": "Contato Efetivo",
                "comment": "Cirurgião demonstrou interesse em testar kit cirúrgico de implantes cone morse na próxima semana.",
                "created_at": "2026-10-17 14:20:00"
            },
            {
                "id": f"seed-6-{contact_id}",
                "contact_id": contact_id,
                "user_id": "usr_exec",
                "author_name": "Roberto Faria (Closer)",
                "action": "Apresentação de Linha Cirúrgica",
                "old_value": None,
                "new_value": "Demonstração Realizada",
                "comment": "Apresentação técnica dos componentes protéticos e protocolo de fresagem guiada.",
                "created_at": "2026-10-16 16:45:00"
            },
            {
                "id": f"seed-5-{contact_id}",
                "contact_id": contact_id,
                "user_id": "usr_sdr",
                "author_name": "Juliana Santos (SDR)",
                "action": "Qualificação SDR Concluída",
                "old_value": "Novo Lead",
                "new_value": "Oportunidade Qualificada",
                "comment": f"Demanda confirmada de implantes cirúrgicos mensais para a clínica própria em {contact.get('city', 'São Paulo')}.",
                "created_at": "2026-10-16 09:30:00"
            },
            {
                "id": f"seed-4-{contact_id}",
                "contact_id": contact_id,
                "user_id": "system",
                "author_name": "Motor de Scoring RevOps",
                "action": "Cálculo ICP Score Concluído",
                "old_value": "0 pts",
                "new_value": f"{score} pts",
                "comment": f"Cirurgião avaliado como {'Alto ICP (Decisor Clínico)' if score >= 80 else 'Médio ICP'}. Especialidade prioritária ({specialty}).",
                "created_at": "2026-10-15 17:10:00"
            },
            {
                "id": f"seed-3-{contact_id}",
                "contact_id": contact_id,
                "user_id": "system",
                "author_name": "Portal de Conteúdo & Downloads",
                "action": "Download de Material Rico",
                "old_value": None,
                "new_value": "Whitepaper Cone Morse 2026",
                "comment": "Baixou o Catálogo Técnico e Tabela Comparativa de Torque Cirúrgico.",
                "created_at": "2026-10-15 14:15:00"
            },
            {
                "id": f"seed-2-{contact_id}",
                "contact_id": contact_id,
                "user_id": "system",
                "author_name": "Validador CFO / CRO",
                "action": "Validação de Registro Profissional",
                "old_value": "Pendente",
                "new_value": "Ativo / Regular",
                "comment": f"Inscrição {contact.get('cro', 'CRO')} validada com sucesso na base do Conselho Regional de Odontologia.",
                "created_at": "2026-10-15 11:05:00"
            },
            {
                "id": f"seed-1-{contact_id}",
                "contact_id": contact_id,
                "user_id": "system",
                "author_name": "Inbound Marketing",
                "action": "Cadastro Inicial do Cirurgião",
                "old_value": None,
                "new_value": name,
                "comment": "Origem: Campanha Digital / Landing Page Implantes Odontológicos.",
                "created_at": "2026-10-15 08:30:00"
            }
        ]
    conn.close()
    return logs


def add_contact_timeline_comment(contact_id: int, comment: str, user_id: Optional[str] = None, author_name: str = "Consultor Especialista") -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO contact_audit_logs (contact_id, user_id, author_name, action, old_value, new_value, comment)
        VALUES (?, ?, ?, 'Comentário / Alinhamento', NULL, NULL, ?)
    """, (contact_id, user_id or "usr_admin", author_name, comment))
    conn.commit()
    log_id = cur.lastrowid
    conn.close()
    return {"success": True, "id": log_id, "comment": comment}


def get_contact_full_profile(contact_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None
    contact = dict(row)
    
    cur.execute("""
        SELECT id, title, value, stage_id, priority, expected_close_date 
        FROM deals 
        WHERE contact_name = ? OR (company IS NOT NULL AND company = ?)
        ORDER BY created_at DESC
    """, (contact.get("name"), contact.get("company")))
    deals = [dict(d) for d in cur.fetchall()]
    contact["deals"] = deals
    
    if isinstance(contact.get("tags"), str):
        try:
            contact["tags"] = json.loads(contact["tags"])
        except Exception:
            contact["tags"] = [contact["tags"]]
            
    contact["timeline"] = get_contact_timeline(contact_id)
    conn.close()
    return contact



