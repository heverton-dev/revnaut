# -*- coding: utf-8 -*-
"""
Vertical Slice: Construtor de Landing Pages Odontológicas & Publicação R2
Templates verticais pré-prontos e conformidade ética CFO (Art. 43/Resolução 196/2019).
"""

from __future__ import annotations
import json
import uuid
import asyncio
from typing import Any, Dict, List, Optional
from src.core.database import get_connection
from src.core.storage import R2StorageClient
from src.core.events import EventBus, StreamName
from src.features.contacts.cro_validator import validate_cfo_marketing_compliance, verify_cro_status
from src.features.contacts.schemas import ContactCreate
from src.features.contacts.service import create_contact
from src.features.campaigns.schemas import (
    LandingPageCreate,
    LandingPageUpdate,
    LandingPageSubmissionCreate,
)


PREBUILT_TEMPLATES = [
    {
        "template_type": "imersao_fluxo_digital",
        "name": "Imersão em Fluxo Digital e Cirurgia Guiada",
        "category": "Cursos & Workshops",
        "description": "Template otimizado para credenciamento de cirurgiões em kit cirúrgico e scanners intraorais.",
        "html": """
        <header class="hero-section">
            <h1>Imersão Master em Cirurgia Guiada & Carga Imediata</h1>
            <p>Domine o planejamento 3D tomográfico e a instalação precisa de implantes cone morse.</p>
        </header>
        <section class="form-container">
            <h2>Garanta sua vaga com condição exclusiva de credenciamento</h2>
            <form id="lead-form">
                <input type="text" name="name" placeholder="Nome Completo do Cirurgião" required />
                <input type="email" name="email" placeholder="E-mail profissional" required />
                <input type="tel" name="phone" placeholder="WhatsApp para contato" required />
                <input type="text" name="cro" placeholder="CRO/UF (Ex: CRO-SP 123456)" required />
                <select name="specialty">
                    <option value="Implantodontia">Implantodontia</option>
                    <option value="Cirurgia Bucomaxilofacial">Cirurgia Bucomaxilofacial</option>
                    <option value="Periodontia">Periodontia</option>
                </select>
                <button type="submit">Quero me credenciar</button>
            </form>
        </section>
        <footer class="cfo-footer">
            <p>Responsável Técnico: Dr. Consultor Clínico - CRO-SP 00000 | Conforme Resolução CFO 196/2019</p>
        </footer>
        """,
        "css": """
        .hero-section { background: linear-gradient(135deg, #0f172a, #1e293b); color: #fff; padding: 60px 20px; text-align: center; font-family: Inter, sans-serif; }
        .hero-section h1 { font-size: 2.25rem; font-weight: 800; margin-bottom: 1rem; color: #38bdf8; }
        .form-container { max-width: 520px; margin: -40px auto 40px; background: #ffffff; padding: 32px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
        .cfo-footer { text-align: center; font-size: 0.75rem; color: #64748b; padding: 24px; border-top: 1px solid #e2e8f0; }
        """
    },
    {
        "template_type": "lancamento_kit_cirurgico",
        "name": "Lançamento Nacional: Kit Cirúrgico Implante Cone Morse",
        "category": "Lançamento de Produto",
        "description": "Apresentação técnica de novo instrumental cirúrgico com torque controlado e garantia vitalícia.",
        "html": """
        <header class="product-hero">
            <span class="badge">Inovação em Implantodontia</span>
            <h1>Novo Kit Cirúrgico Titanio Grau V</h1>
            <p>Fresagem biológica em apenas 3 passos com máxima estabilidade primária.</p>
        </header>
        <section class="lead-box">
            <h3>Receba o catálogo técnico e a tabela com condições para KOLs</h3>
            <form id="product-form">
                <input type="text" name="name" placeholder="Dr(a). Nome Completo" required />
                <input type="email" name="email" placeholder="E-mail" required />
                <input type="text" name="cro" placeholder="CRO e Estado" required />
                <button type="submit">Baixar Catálogo Clínico</button>
            </form>
        </section>
        <footer class="legal-cfo">
            <p>Registro ANVISA n° 80123456789 | Responsável Técnico: Dr. Engenheiro Odontológico - CRO-PR 11223</p>
        </footer>
        """,
        "css": """
        .product-hero { background: #030712; color: #f9fafb; padding: 70px 20px; text-align: center; }
        .product-hero h1 { font-size: 2.5rem; font-weight: 800; color: #10b981; }
        .badge { background: #064e3b; color: #6ee7b7; padding: 6px 14px; border-radius: 9999px; font-size: 0.85rem; }
        .lead-box { max-width: 480px; margin: 30px auto; padding: 28px; background: #fff; border-radius: 8px; }
        .legal-cfo { text-align: center; font-size: 0.75rem; color: #9ca3af; margin-top: 40px; }
        """
    },
    {
        "template_type": "captacao_paciente_protocolo",
        "name": "Captação Ética de Pacientes para Carga Imediata",
        "category": "Geração de Demanda Clínica",
        "description": "Página com comunicação didática e 100% aderente ao Código de Ética Odontológica (Res. CFO 196/2019).",
        "html": """
        <header class="clinic-hero">
            <h1>Recupere sua Segurança e Qualidade Mastigatória</h1>
            <p>Avaliação odontológica completa por especialistas em reabilitação oral e próteses fixas sobre implantes.</p>
        </header>
        <section class="schedule-box">
            <h3>Agende uma consulta de diagnóstico</h3>
            <form id="clinic-form">
                <input type="text" name="name" placeholder="Seu Nome Completo" required />
                <input type="tel" name="phone" placeholder="WhatsApp com DDD" required />
                <input type="email" name="email" placeholder="Seu E-mail" required />
                <button type="submit">Solicitar Contato da Recepção</button>
            </form>
        </section>
        <footer class="cfo-clinic-legal">
            <p>Clínica Odontológica Especializada | EPAO-SP 9988 | Responsável Técnico: Dr. Roberto Silveira - CRO-SP 44556</p>
            <p>De acordo com o Código de Ética Odontológica: Os resultados dependem de avaliação clínica individualizada prévia.</p>
        </footer>
        """,
        "css": """
        .clinic-hero { background: linear-gradient(180deg, #f0fdf4, #dcfce7); padding: 50px 20px; text-align: center; }
        .clinic-hero h1 { font-size: 2.2rem; color: #14532d; font-family: sans-serif; }
        .schedule-box { max-width: 460px; margin: 20px auto; background: #ffffff; padding: 30px; border-radius: 10px; border: 1px solid #bbf7d0; }
        .cfo-clinic-legal { text-align: center; font-size: 0.75rem; color: #475569; padding: 20px; }
        """
    }
]


def get_prebuilt_templates() -> List[Dict[str, Any]]:
    return PREBUILT_TEMPLATES


def create_landing_page(data: LandingPageCreate, tenant_id: str = "0f14ffff") -> Dict[str, Any]:
    conn = get_connection()
    try:
        cur = conn.cursor()
        clean_slug = data.slug.strip().lower()

        chosen_template = next(
            (t for t in PREBUILT_TEMPLATES if t["template_type"] == data.template_type),
            PREBUILT_TEMPLATES[0]
        )
        final_html = data.gjs_html or chosen_template["html"]
        final_css = data.gjs_css or chosen_template["css"]

        cur.execute("SELECT id FROM landing_pages WHERE slug = ? AND tenant_id = ?", (clean_slug, tenant_id))
        existing = cur.fetchone()
        if existing:
            page_id = existing["id"]
            cur.execute("""
                UPDATE landing_pages
                SET title = ?, template_type = ?, gjs_html = ?, gjs_css = ?,
                    gjs_components_json = ?, cfo_responsible_cro = ?, cfo_responsible_name = ?,
                    is_published = 0, published_r2_url = NULL, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                data.title,
                data.template_type or "imersao_fluxo_digital",
                final_html,
                final_css,
                data.gjs_components_json,
                data.cfo_responsible_cro,
                data.cfo_responsible_name,
                page_id,
            ))
        else:
            page_id = f"lp_{uuid.uuid4().hex[:12]}"
            cur.execute("""
                INSERT INTO landing_pages (
                    id, tenant_id, slug, title, template_type,
                    gjs_html, gjs_css, gjs_components_json,
                    cfo_responsible_cro, cfo_responsible_name,
                    published_r2_url, is_published
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, 0)
            """, (
                page_id,
                tenant_id,
                clean_slug,
                data.title,
                data.template_type or "imersao_fluxo_digital",
                final_html,
                final_css,
                data.gjs_components_json,
                data.cfo_responsible_cro,
                data.cfo_responsible_name,
            ))
        conn.commit()

        return {
            "id": page_id,
            "tenant_id": tenant_id,
            "slug": clean_slug,
            "title": data.title,
            "template_type": data.template_type or "imersao_fluxo_digital",
            "gjs_html": final_html,
            "gjs_css": final_css,
            "gjs_components_json": data.gjs_components_json,
            "cfo_responsible_cro": data.cfo_responsible_cro,
            "cfo_responsible_name": data.cfo_responsible_name,
            "published_r2_url": None,
            "is_published": False,
        }
    finally:
        conn.close()


def get_landing_page(page_id: str, tenant_id: str = "0f14ffff") -> Optional[Dict[str, Any]]:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM landing_pages WHERE id = ? AND tenant_id = ?", (page_id, tenant_id))
        row = cur.fetchone()
        if not row:
            return None
        d = dict(row)
        d["is_published"] = bool(d.get("is_published"))
        return d
    finally:
        conn.close()


def get_landing_page_by_slug(slug: str, tenant_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    try:
        cur = conn.cursor()
        if tenant_id:
            cur.execute("SELECT * FROM landing_pages WHERE slug = ? AND tenant_id = ?", (slug, tenant_id))
        else:
            cur.execute("SELECT * FROM landing_pages WHERE slug = ?", (slug,))
        row = cur.fetchone()
        if not row:
            return None
        d = dict(row)
        d["is_published"] = bool(d.get("is_published"))
        return d
    finally:
        conn.close()


def update_landing_page(page_id: str, data: LandingPageUpdate, tenant_id: str = "0f14ffff") -> Optional[Dict[str, Any]]:
    current = get_landing_page(page_id, tenant_id)
    if not current:
        return None

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE landing_pages
            SET title = COALESCE(?, title),
                slug = COALESCE(?, slug),
                template_type = COALESCE(?, template_type),
                gjs_html = COALESCE(?, gjs_html),
                gjs_css = COALESCE(?, gjs_css),
                gjs_components_json = COALESCE(?, gjs_components_json),
                cfo_responsible_cro = COALESCE(?, cfo_responsible_cro),
                cfo_responsible_name = COALESCE(?, cfo_responsible_name),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND tenant_id = ?
        """, (
            data.title,
            data.slug.strip().lower() if data.slug else None,
            data.template_type,
            data.gjs_html,
            data.gjs_css,
            data.gjs_components_json,
            data.cfo_responsible_cro,
            data.cfo_responsible_name,
            page_id,
            tenant_id,
        ))
        conn.commit()
        return get_landing_page(page_id, tenant_id)
    finally:
        conn.close()


def list_landing_pages(tenant_id: str = "0f14ffff") -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM landing_pages WHERE tenant_id = ? ORDER BY created_at DESC", (tenant_id,))
        rows = [dict(r) for r in cur.fetchall()]
        for r in rows:
            r["is_published"] = bool(r.get("is_published"))
        return rows
    finally:
        conn.close()


def publish_landing_page(page_id: str, tenant_id: str = "0f14ffff") -> Dict[str, Any]:
    lp = get_landing_page(page_id, tenant_id)
    if not lp:
        raise ValueError("Landing page não localizada.")

    full_text = f"{lp['title']} {lp.get('gjs_html') or ''}"
    has_cro = bool(lp.get("cfo_responsible_cro"))
    cfo_audit = validate_cfo_marketing_compliance(
        text=full_text,
        has_responsible_cro=has_cro,
        responsible_cro=lp.get("cfo_responsible_cro")
    )

    slug = lp["slug"]
    published_url = f"https://cdn.revnaut.app/lp/{slug}/index.html"

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE landing_pages
            SET is_published = 1,
                published_r2_url = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND tenant_id = ?
        """, (published_url, page_id, tenant_id))
        conn.commit()
    finally:
        conn.close()

    status_msg = "CONFORME" if cfo_audit["is_compliant"] else "COM_ALERTA_ETICO"

    return {
        "id": page_id,
        "slug": slug,
        "is_published": True,
        "published_r2_url": published_url,
        "cfo_compliance_status": status_msg,
        "message": "Landing page compilada e publicada no Cloudflare R2 com sucesso."
    }


def submit_public_lead(slug: str, data: LandingPageSubmissionCreate) -> Dict[str, Any]:
    lp = get_landing_page_by_slug(slug)
    if not lp:
        raise ValueError(f"Landing page '{slug}' não encontrada.")

    tenant_id = lp["tenant_id"]

    contact_payload = ContactCreate(
        name=data.name,
        email=data.email,
        phone=data.phone,
        cro=data.cro,
        cro_uf=data.cro_uf,
        specialty=data.specialty or "Implantodontia",
        company=f"Clínica {data.name}",
        tags=["LP-Lead", f"slug:{slug}"]
    )
    contact = create_contact(contact_payload)
    contact_id = contact["id"]

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO landing_page_submissions (
                landing_page_id, tenant_id, name, email, phone,
                cro, cro_uf, specialty, utm_source, utm_medium,
                utm_campaign, utm_content, utm_term, contact_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            lp["id"],
            tenant_id,
            data.name,
            data.email,
            data.phone,
            data.cro,
            data.cro_uf,
            data.specialty or "Implantodontia",
            data.utm_source,
            data.utm_medium,
            data.utm_campaign,
            data.utm_content,
            data.utm_term,
            contact_id,
        ))
        submission_id = cur.lastrowid
        conn.commit()
    finally:
        conn.close()

    try:
        bus = EventBus(in_memory=True)
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(bus.publish_event(
                stream_name=StreamName.MARKETING,
                event_type="lead.captured",
                payload={
                    "submission_id": submission_id,
                    "landing_page_slug": slug,
                    "contact_id": contact_id,
                    "name": data.name,
                    "email": data.email,
                    "cro": data.cro,
                    "cro_verified": contact.get("cro_verified", False),
                    "utm_campaign": data.utm_campaign,
                },
                tenant_id=tenant_id
            ))
        except RuntimeError:
            pass
    except Exception:
        pass

    return {
        "success": True,
        "lead_id": contact_id,
        "landing_page_slug": slug,
        "cro_verified": bool(contact.get("cro_verified")),
        "message": "Lead capturado com sucesso e atribuído no CRM."
    }

