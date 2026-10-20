# -*- coding: utf-8 -*-
"""
Minutas e Disparo Determinístico de Campanhas Táticas com Trava Anti-Spam de 15 Dias
(TICKET-MKTINTEL-07 e TICKET-MKTINTEL-08).

Invariantes:
- Somente director/regional_manager aprovam e disparam (regional_manager apenas na própria praça).
- field_sales não gera minuta; inside_sales gera minuta mas não dispara.
- Nenhum contato recebe nova campanha automatizada se houver trava em campaign_recipient_locks
  nos últimos 15 dias (independente da campanha ou oportunidade de origem).
- Toda minuta passa pelo validador ético CFO 196/2019 (cro_validator) antes de ser gravada.
"""

from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from src.core.database import get_connection
from src.core.events import StreamName, default_event_bus
from src.features.contacts.cro_validator import validate_cfo_marketing_compliance
from src.features.market_intel.rbac import MarketIntelForbidden, MarketIntelPrincipal, VALID_REGIONS

COOLDOWN_DAYS = 15
VALID_CHANNELS = ("WHATSAPP", "EMAIL")
DEFAULT_PURCHASE_WINDOW_DAYS = 90
MARKET_INTEL_WHATSAPP_INSTANCE = "inst_market_intel"


class CampaignValidationError(Exception):
    """Minuta/campanha inválida (mapeada para HTTP 422)."""

    def __init__(self, message: str, violations: Optional[List[str]] = None) -> None:
        super().__init__(message)
        self.violations = violations or []


class CampaignStateError(Exception):
    """Transição de estado inválida (mapeada para HTTP 409)."""


def _responsible_technical_signature() -> str:
    name = os.getenv("MARKET_INTEL_RT_NAME", "Dra. Juliana Frota")
    cro = os.getenv("MARKET_INTEL_RT_CRO", "CRO-SP 89450")
    return f"Responsável Técnico: {name} - {cro}"


def _loads(raw: Optional[str], default: Any) -> Any:
    try:
        return json.loads(raw) if raw else default
    except (TypeError, ValueError):
        return default


def build_campaign_template(opportunity: Dict[str, Any], product_names: List[str], channel: str) -> str:
    """Minuta determinística: mesma oportunidade + canal -> mesmo texto."""
    portfolio = ", ".join(product_names) if product_names else "nosso portfólio cirúrgico"
    opp_type = opportunity["opportunity_type"]
    if opp_type == "PRICE_COUNTER_ATTACK":
        hook = (
            f"preparamos uma condição comercial dedicada para {portfolio}, com garantia ANVISA e rastreabilidade UDI "
            "de cada lote e entrega DENTGO em até 45 minutos na sua clínica"
        )
    elif opp_type == "EVENT_SURGE":
        hook = (
            f"organizamos agenda de demonstração técnica de {portfolio} e reserva de estoque com reposição DENTGO "
            "para o período do evento"
        )
    else:
        hook = (
            f"compartilhamos um resumo técnico atualizado sobre {portfolio}, com protocolo de torque e documentação "
            "ANVISA/UDI para seus próximos casos"
        )
    greeting = "Olá Dr(a). {{nome}}," if channel == "WHATSAPP" else "Prezado(a) Dr(a). {{nome}},"
    return (
        f"{greeting} {hook}. Posso agendar uma conversa de 15 minutos com o seu consultor para avaliar os casos "
        f"da sua agenda em {opportunity['bu_target']}? {_responsible_technical_signature()}."
    )


def generate_campaign_draft(
    principal: MarketIntelPrincipal,
    opportunity_id: str,
    target_region: Optional[str] = None,
    channel: str = "WHATSAPP",
    specialty: Optional[str] = None,
    purchase_window: int = DEFAULT_PURCHASE_WINDOW_DAYS,
    message_template: Optional[str] = None,
) -> Dict[str, Any]:
    if not principal.can_generate_draft:
        raise MarketIntelForbidden("Perfil sem permissão para gerar minuta de campanha (Consultor Externo / Campo).")
    channel = (channel or "").upper()
    if channel not in VALID_CHANNELS:
        raise CampaignValidationError(f"Canal inválido: '{channel}'. Use WHATSAPP ou EMAIL.")
    if purchase_window < 1 or purchase_window > 365:
        raise CampaignValidationError("purchase_window deve estar entre 1 e 365 dias.")

    conn = get_connection()
    try:
        opp = conn.execute(
            "SELECT * FROM market_opportunities WHERE id = ? AND account_id = ?",
            (opportunity_id, principal.account_id),
        ).fetchone()
        if not opp:
            raise LookupError(f"Oportunidade '{opportunity_id}' não encontrada.")
        opp = dict(opp)
        if opp["status"] == "DISMISSED":
            raise CampaignStateError("Oportunidade descartada não pode gerar campanha.")

        region = (target_region or opp["region_code"] or "GLOBAL").upper()
        if region not in VALID_REGIONS:
            raise CampaignValidationError(f"Região inválida: '{region}'.")
        if not principal.can_see_scope(opp["region_code"]) or not principal.can_operate_region(region):
            raise MarketIntelForbidden(f"Praça '{region}' fora do escopo territorial do perfil ({principal.region}).")

        skus = _loads(opp["recommended_product_ids"], [])
        names: List[str] = []
        if skus:
            placeholders = ",".join("?" for _ in skus)
            rows = conn.execute(f"SELECT sku, name FROM products_catalog WHERE sku IN ({placeholders})", tuple(skus)).fetchall()
            by_sku = {r["sku"]: r["name"] for r in rows}
            names = [by_sku[s] for s in skus if s in by_sku]

        template = (message_template or "").strip() or build_campaign_template(opp, names, channel)
        compliance = validate_cfo_marketing_compliance(template)
        if not compliance["is_compliant"]:
            raise CampaignValidationError("Minuta reprovada no validador ético CFO 196/2019.", compliance["violations"])

        audience = {"region": region, "specialty": specialty or None, "purchase_window": int(purchase_window)}
        campaign_id = f"tcmp-{uuid.uuid4().hex[:12]}"
        now_iso = datetime.now(timezone.utc).isoformat()
        conn.execute(
            """
            INSERT INTO targeted_campaigns (
                id, account_id, opportunity_id, target_audience_filter, message_template, channel,
                dispatch_status, created_by_user_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, 'DRAFT', ?, ?)
            """,
            (campaign_id, principal.account_id, opportunity_id, json.dumps(audience, ensure_ascii=False), template, channel,
             principal.user_id, now_iso),
        )
        conn.commit()
    finally:
        conn.close()

    return {
        "id": campaign_id,
        "account_id": principal.account_id,
        "opportunity_id": opportunity_id,
        "target_audience_filter": audience,
        "message_template": template,
        "channel": channel,
        "dispatch_status": "DRAFT",
        "sent_count": 0,
        "skipped_cooldown_15d_count": 0,
        "created_by_user_id": principal.user_id,
        "created_at": now_iso,
        "compliance": compliance,
    }


def _region_clause(region: str) -> tuple[str, List[Any]]:
    """Mapeia praça para filtro de contatos: BR-UF por CRO/UF ou estado; US-FL por estado; GLOBAL/LATAM sem filtro."""
    if region.startswith("BR-"):
        uf = region.split("-", 1)[1]
        return "(UPPER(COALESCE(cro_uf, '')) = ? OR UPPER(COALESCE(state, '')) = ?)", [uf, uf]
    if region == "US-FL":
        return "UPPER(COALESCE(state, '')) = ?", ["FL"]
    return "1 = 1", []


def select_eligible_contacts(conn, account_id: str, audience: Dict[str, Any], channel: str, now: datetime) -> List[Dict[str, Any]]:
    region_sql, params = _region_clause(str(audience.get("region") or "GLOBAL").upper())
    conditions = ["account_id = ?", region_sql]
    args: List[Any] = [account_id, *params]

    specialty = audience.get("specialty")
    if specialty:
        conditions.append("LOWER(COALESCE(specialty, '')) LIKE ?")
        args.append(f"%{str(specialty).lower()}%")

    window = int(audience.get("purchase_window") or DEFAULT_PURCHASE_WINDOW_DAYS)
    conditions.append("(last_order_date IS NULL OR last_order_date = '' OR last_order_date >= ?)")
    args.append((now - timedelta(days=window)).date().isoformat())

    if channel == "WHATSAPP":
        conditions.append("phone IS NOT NULL AND TRIM(phone) != ''")
    else:
        conditions.append("email IS NOT NULL AND TRIM(email) != ''")

    rows = conn.execute(
        f"SELECT id, name, email, phone FROM contacts WHERE {' AND '.join(conditions)} ORDER BY id",
        tuple(args),
    ).fetchall()
    return [dict(r) for r in rows]


def is_contact_locked(conn, account_id: str, contact_id: str, now: datetime) -> bool:
    cutoff = (now - timedelta(days=COOLDOWN_DAYS)).isoformat()
    row = conn.execute(
        "SELECT 1 FROM campaign_recipient_locks WHERE account_id = ? AND contact_id = ? AND sent_at >= ? LIMIT 1",
        (account_id, contact_id, cutoff),
    ).fetchone()
    return row is not None


def _render(template: str, contact: Dict[str, Any]) -> str:
    first_name = str(contact.get("name") or "").replace("Dr.", "").replace("Dra.", "").strip()
    return template.replace("{{nome}}", first_name or "Doutor(a)")


def _whatsapp_jid(phone: str) -> str:
    digits = re.sub(r"\D", "", phone)
    if not digits.startswith("55") and len(digits) <= 11:
        digits = f"55{digits}"
    return f"{digits}@s.whatsapp.net"


def dispatch_campaign(principal: MarketIntelPrincipal, campaign_id: str, now: Optional[datetime] = None) -> Dict[str, Any]:
    if not principal.can_dispatch:
        raise MarketIntelForbidden("Somente Diretoria e Gerente Regional podem aprovar e disparar campanhas.")
    now = now or datetime.now(timezone.utc)
    now_iso = now.isoformat()

    conn = get_connection()
    try:
        camp = conn.execute(
            "SELECT * FROM targeted_campaigns WHERE id = ? AND account_id = ?",
            (campaign_id, principal.account_id),
        ).fetchone()
        if not camp:
            raise LookupError(f"Campanha '{campaign_id}' não encontrada.")
        camp = dict(camp)
        if camp["dispatch_status"] == "EXECUTED":
            raise CampaignStateError("Campanha já executada; gere nova minuta para um novo disparo.")

        audience = _loads(camp["target_audience_filter"], {})
        region = str(audience.get("region") or "GLOBAL").upper()
        if not principal.can_operate_region(region):
            raise MarketIntelForbidden(f"Gerente Regional ({principal.region}) não pode disparar campanha da praça '{region}'.")

        contacts = select_eligible_contacts(conn, principal.account_id, audience, camp["channel"], now)
        sent = skipped = failed = 0
        email_client = None
        if camp["channel"] == "EMAIL":
            from src.features.campaigns.listmonk_adapter import ListmonkClient
            email_client = ListmonkClient()

        for contact in contacts:
            contact_id = str(contact["id"])
            if is_contact_locked(conn, principal.account_id, contact_id, now):
                skipped += 1
                continue
            body = _render(camp["message_template"], contact)
            if camp["channel"] == "WHATSAPP":
                conn.execute(
                    """
                    INSERT INTO omnichannel_messages (
                        id, account_id, instance_name, remote_jid, sender_phone, message_type, content, from_me
                    ) VALUES (?, ?, ?, ?, ?, 'text', ?, 1)
                    """,
                    (f"omni-{uuid.uuid4().hex[:12]}", principal.account_id, MARKET_INTEL_WHATSAPP_INSTANCE,
                     _whatsapp_jid(str(contact["phone"])), str(contact["phone"]), body),
                )
            else:
                try:
                    email_client.send_transactional(
                        subscriber_email=str(contact["email"]),
                        template_id=int(os.getenv("LISTMONK_MKTINTEL_TEMPLATE_ID", "1")),
                        data={"body": body, "campaign_id": campaign_id, "opportunity_id": camp["opportunity_id"]},
                    )
                except Exception:
                    failed += 1
                    continue
            conn.execute(
                """
                INSERT INTO campaign_recipient_locks (id, account_id, contact_id, campaign_id, opportunity_id, channel, sent_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (f"lock-{uuid.uuid4().hex[:12]}", principal.account_id, contact_id, campaign_id,
                 camp["opportunity_id"], camp["channel"], now_iso),
            )
            sent += 1

        conn.execute(
            """
            UPDATE targeted_campaigns
            SET dispatch_status = 'EXECUTED', sent_count = ?, skipped_cooldown_15d_count = ?,
                approved_by_user_id = ?, executed_at = ?
            WHERE id = ?
            """,
            (sent, skipped, principal.user_id, now_iso, campaign_id),
        )
        conn.execute(
            "UPDATE market_opportunities SET status = 'CAMPAIGN_TRIGGERED' WHERE id = ? AND account_id = ?",
            (camp["opportunity_id"], principal.account_id),
        )
        conn.commit()
    finally:
        conn.close()

    default_event_bus.publish_sync(
        StreamName.MARKET_INTEL,
        "targeted_campaign.executed",
        {"campaign_id": campaign_id, "sent_count": sent, "skipped_cooldown_15d_count": skipped, "failed_count": failed},
        tenant_id=principal.account_id,
    )
    return {
        "campaign_id": campaign_id,
        "dispatch_status": "EXECUTED",
        "eligible_count": len(contacts),
        "sent_count": sent,
        "skipped_cooldown_15d_count": skipped,
        "failed_count": failed,
        "approved_by_user_id": principal.user_id,
        "executed_at": now_iso,
    }
