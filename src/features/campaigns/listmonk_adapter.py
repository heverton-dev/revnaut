# -*- coding: utf-8 -*-
"""
Vertical Slice: Listmonk Adapter & High-Speed Broadcast Engine
Integração com o motor open-source Listmonk v2 para disparo em massa de newsletters técnicas e boletins odontológicos.
"""

from __future__ import annotations
import json
import os
import time
import uuid
from typing import Any, Dict, List, Optional
import httpx
from src.core.database import get_connection
from src.core.events import StreamName, default_event_bus


class ListmonkClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        mock_mode: Optional[bool] = None,
    ) -> None:
        self.base_url = (base_url or os.getenv("LISTMONK_URL", "http://localhost:9000")).rstrip("/")
        self.username = username or os.getenv("LISTMONK_USER", "revnault_admin")
        self.password = password or os.getenv("LISTMONK_PASSWORD", "revnault_secret")
        if mock_mode is not None:
            self.mock_mode = mock_mode
        else:
            env_mock = os.getenv("LISTMONK_MOCK_MODE")
            if env_mock is not None:
                self.mock_mode = env_mock.lower() in ("1", "true", "yes")
            else:
                self.mock_mode = "mock" in self.base_url or "localhost" in self.base_url

    def _auth(self) -> tuple[str, str]:
        return (self.username, self.password)

    def build_subscriber_payload(
        self,
        email: str,
        name: str,
        cro: Optional[str] = None,
        cro_uf: Optional[str] = None,
        specialty: Optional[str] = None,
        implant_brand: Optional[str] = None,
        list_ids: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        return {
            "email": email,
            "name": name,
            "status": "enabled",
            "lists": list_ids or [1],
            "attribs": {
                "cro": cro,
                "cro_uf": cro_uf,
                "specialty": specialty,
                "implant_brand": implant_brand,
            },
            "preconfirm_subscriptions": True,
        }

    def build_campaign_payload(
        self,
        name: str,
        subject: str,
        body: str,
        list_ids: Optional[List[int]] = None,
        content_type: str = "html",
    ) -> Dict[str, Any]:
        return {
            "name": name,
            "subject": subject,
            "lists": list_ids or [1],
            "type": "regular",
            "content_type": content_type,
            "body": body,
            "messenger": "email",
        }

    def sync_subscribers(
        self,
        subscribers: List[Dict[str, Any]],
        list_ids: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        synced_ids: List[int] = []
        for idx, sub in enumerate(subscribers):
            payload = self.build_subscriber_payload(
                email=sub["email"],
                name=sub.get("name") or sub["email"],
                cro=sub.get("cro"),
                cro_uf=sub.get("cro_uf"),
                specialty=sub.get("specialty"),
                implant_brand=sub.get("implant_brand"),
                list_ids=list_ids or sub.get("list_ids") or [1],
            )
            if not self.mock_mode:
                with httpx.Client(auth=self._auth(), timeout=10.0) as client:
                    resp = client.post(f"{self.base_url}/api/subscribers", json=payload)
                    resp.raise_for_status()
                    data = resp.json().get("data") or {}
                    synced_ids.append(int(data.get("id") or (idx + 1)))
            else:
                synced_ids.append(1000 + idx + 1)

        return {
            "synced_count": len(synced_ids),
            "subscriber_ids": synced_ids,
            "status": "synced",
        }

    def create_campaign(
        self,
        name: str,
        subject: str,
        body: str,
        list_ids: Optional[List[int]] = None,
        start_immediately: bool = True,
    ) -> Dict[str, Any]:
        payload = self.build_campaign_payload(
            name=name,
            subject=subject,
            body=body,
            list_ids=list_ids or [1],
        )
        if not self.mock_mode:
            with httpx.Client(auth=self._auth(), timeout=10.0) as client:
                resp = client.post(f"{self.base_url}/api/campaigns", json=payload)
                resp.raise_for_status()
                camp_data = resp.json().get("data") or {}
                camp_id = int(camp_data.get("id") or 2001)
                camp_status = camp_data.get("status", "draft")
                if start_immediately:
                    status_resp = client.put(
                        f"{self.base_url}/api/campaigns/{camp_id}/status",
                        json={"status": "running"},
                    )
                    status_resp.raise_for_status()
                    camp_status = "running"
                return {
                    "campaign_id": camp_id,
                    "status": camp_status,
                    "name": name,
                }

        camp_id = int(time.time() % 100000) + 1000
        return {
            "campaign_id": camp_id,
            "status": "running" if start_immediately else "draft",
            "name": name,
        }

    def create_and_start_campaign(
        self,
        name: str,
        subject: str,
        body: str,
        list_ids: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        return self.create_campaign(
            name=name,
            subject=subject,
            body=body,
            list_ids=list_ids,
            start_immediately=True,
        )

    def send_transactional(
        self,
        subscriber_email: str,
        template_id: int,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        tx_payload = {
            "subscriber_email": subscriber_email,
            "template_id": template_id,
            "data": data or {},
            "content_type": "html",
        }
        if not self.mock_mode:
            with httpx.Client(auth=self._auth(), timeout=10.0) as client:
                resp = client.post(f"{self.base_url}/api/tx", json=tx_payload)
                resp.raise_for_status()
                return {
                    "success": True,
                    "subscriber_email": subscriber_email,
                    "template_id": template_id,
                    "provider_response": resp.json(),
                }

        return {
            "success": True,
            "subscriber_email": subscriber_email,
            "template_id": template_id,
            "tx_id": f"tx-{uuid.uuid4().hex[:8]}",
        }

    def dispatch_broadcast(
        self,
        title: str,
        subject: str,
        body_html: str,
        target_uf: Optional[str] = None,
        target_specialty: Optional[str] = None,
        list_id: int = 1,
    ) -> Dict[str, Any]:
        conn = get_connection()
        try:
            cur = conn.cursor()
            conditions = ["email IS NOT NULL"]
            params: List[Any] = []

            if target_uf:
                conditions.append("(cro_uf = ? OR state = ?)")
                params.extend([target_uf, target_uf])

            if target_specialty:
                conditions.append("specialty = ?")
                params.append(target_specialty)

            where_clause = " AND ".join(conditions)
            cur.execute(f"SELECT id, name, email, cro, cro_uf, specialty FROM contacts WHERE {where_clause}", tuple(params))
            matched_contacts = [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

        if matched_contacts:
            self.sync_subscribers(matched_contacts, list_ids=[list_id])

        camp_res = self.create_campaign(
            name=title,
            subject=subject,
            body=body_html,
            list_ids=[list_id],
            start_immediately=True,
        )
        campaign_id = camp_res["campaign_id"]

        default_event_bus.publish_sync(
            StreamName.MARKETING,
            "campaign.broadcast.dispatched",
            {
                "campaign_id": campaign_id,
                "title": title,
                "subject": subject,
                "target_count": len(matched_contacts),
                "list_id": list_id,
                "target_uf": target_uf,
                "target_specialty": target_specialty,
            },
        )

        return {
            "success": True,
            "status": camp_res["status"],
            "queued_count": len(matched_contacts),
            "listmonk_campaign_id": campaign_id,
            "message": f"Broadcast enfileirado com sucesso para {len(matched_contacts)} cirurgiões no Listmonk Engine.",
        }


def process_listmonk_webhook_event(
    payload: Dict[str, Any],
    account_id: str = "0f14ffff",
) -> Dict[str, Any]:
    """
    Processa webhooks do Listmonk (bounce, open, click), atualizando timeline
    (contact_audit_logs), tags de bounce e score de engajamento do contato.
    """
    event_type = str(payload.get("event") or payload.get("type") or "open").lower().strip()
    email = (
        payload.get("email")
        or (payload.get("subscriber") or {}).get("email")
        or ""
    ).strip()
    campaign_name = (
        payload.get("campaign_name")
        or (payload.get("campaign") or {}).get("name")
        or "Campanha Listmonk"
    )
    target_url = payload.get("url") or payload.get("link") or ""

    if not email:
        raise ValueError("E-mail do destinatário é obrigatório no webhook do Listmonk.")

    conn = get_connection()
    try:
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name, score, tags FROM contacts WHERE email = ?", (email,))
            row = cur.fetchone()
            if not row:
                return {
                    "success": False,
                    "event_type": event_type,
                    "email": email,
                    "contact_id": None,
                    "score_delta": 0,
                    "new_score": 0,
                    "email_bounced": False,
                    "message": "Contato não encontrado para o e-mail informado.",
                }

            contact_id = int(row["id"])
            old_score = int(row["score"] or 0)
            raw_tags = row["tags"] or "[]"
            try:
                tags_list = json.loads(raw_tags) if isinstance(raw_tags, str) else list(raw_tags)
            except Exception:
                tags_list = []

            score_delta = 0
            email_bounced = False
            if "bounce" in event_type:
                score_delta = -15
                email_bounced = True
                if "email_bounced" not in tags_list:
                    tags_list.append("email_bounced")
                action_label = "listmonk_bounce"
                comment = f"Hard/Soft bounce reportado na campanha '{campaign_name}'."
            elif "click" in event_type:
                score_delta = 15
                if "engaged_catalog_click" not in tags_list:
                    tags_list.append("engaged_catalog_click")
                action_label = "listmonk_click"
                comment = f"Clique registrado em '{target_url or campaign_name}' (+15 pts)."
            else:
                score_delta = 5
                if "email_opened" not in tags_list:
                    tags_list.append("email_opened")
                action_label = "listmonk_open"
                comment = f"Abertura de e-mail registrada na campanha '{campaign_name}' (+5 pts)."

            new_score = max(0, min(100, old_score + score_delta))
            cur.execute(
                "UPDATE contacts SET score = ?, tags = ? WHERE id = ?",
                (new_score, json.dumps(tags_list), contact_id),
            )
            cur.execute("""
                INSERT INTO contact_audit_logs (
                    contact_id, user_id, author_name, action, old_value, new_value, comment
                ) VALUES (?, 'system-listmonk', 'Listmonk Engine', ?, ?, ?, ?)
            """, (
                contact_id,
                action_label,
                str(old_score),
                str(new_score),
                comment,
            ))
    finally:
        conn.close()

    default_event_bus.publish_sync(
        StreamName.MARKETING,
        f"listmonk.{event_type}",
        {
            "contact_id": contact_id,
            "email": email,
            "event_type": event_type,
            "score_delta": score_delta,
            "new_score": new_score,
            "email_bounced": email_bounced,
            "campaign_name": campaign_name,
        },
        tenant_id=account_id,
    )

    return {
        "success": True,
        "event_type": event_type,
        "email": email,
        "contact_id": contact_id,
        "score_delta": score_delta,
        "new_score": new_score,
        "email_bounced": email_bounced,
        "message": comment,
    }

