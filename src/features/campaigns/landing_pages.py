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
from src.core.events import EventBus, StreamName, default_event_bus
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
        final_html = data.gjs_html or data.html or chosen_template["html"]
        final_css = data.gjs_css or data.css or chosen_template["css"]
        ab_enabled_int = 1 if data.ab_test_enabled else 0

        cur.execute("SELECT id FROM landing_pages WHERE slug = ? AND tenant_id = ?", (clean_slug, tenant_id))
        existing = cur.fetchone()
        if existing:
            page_id = existing["id"]
            cur.execute("""
                UPDATE landing_pages
                SET title = ?, template_type = ?, gjs_html = ?, gjs_css = ?,
                    gjs_components_json = ?, cfo_responsible_cro = ?, cfo_responsible_name = ?,
                    ab_test_enabled = ?, variant_b_html = ?,
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
                ab_enabled_int,
                data.variant_b_html,
                page_id,
            ))
        else:
            page_id = f"lp_{uuid.uuid4().hex[:12]}"
            cur.execute("""
                INSERT INTO landing_pages (
                    id, tenant_id, slug, title, template_type,
                    gjs_html, gjs_css, gjs_components_json,
                    cfo_responsible_cro, cfo_responsible_name,
                    ab_test_enabled, variant_b_html,
                    published_r2_url, is_published
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, 0)
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
                ab_enabled_int,
                data.variant_b_html,
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
            "html": final_html,
            "css": final_css,
            "gjs_components_json": data.gjs_components_json,
            "cfo_responsible_cro": data.cfo_responsible_cro,
            "cfo_responsible_name": data.cfo_responsible_name,
            "published_r2_url": None,
            "published_url": f"/lp/{clean_slug}",
            "is_published": False,
            "ab_test_enabled": bool(data.ab_test_enabled),
            "variant_b_html": data.variant_b_html,
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
        d["ab_test_enabled"] = bool(d.get("ab_test_enabled"))
        d["html"] = d.get("gjs_html")
        d["css"] = d.get("gjs_css")
        d["published_url"] = f"/lp/{d['slug']}" if d.get("slug") else None
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
        d["ab_test_enabled"] = bool(d.get("ab_test_enabled"))
        d["html"] = d.get("gjs_html")
        d["css"] = d.get("gjs_css")
        d["published_url"] = f"/lp/{d['slug']}" if d.get("slug") else None
        return d
    finally:
        conn.close()


def update_landing_page(page_id: str, data: LandingPageUpdate, tenant_id: str = "0f14ffff") -> Optional[Dict[str, Any]]:
    current = get_landing_page(page_id, tenant_id)
    if not current:
        return None

    html_val = data.gjs_html if data.gjs_html is not None else data.html
    css_val = data.gjs_css if data.gjs_css is not None else data.css
    cro_val = data.cfo_responsible_cro if data.cfo_responsible_cro is not None else data.cfo_cro
    name_val = data.cfo_responsible_name if data.cfo_responsible_name is not None else data.cfo_name
    ab_enabled_int = (1 if data.ab_test_enabled else 0) if data.ab_test_enabled is not None else None

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
                ab_test_enabled = COALESCE(?, ab_test_enabled),
                variant_b_html = COALESCE(?, variant_b_html),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND tenant_id = ?
        """, (
            data.title,
            data.slug.strip().lower() if data.slug else None,
            data.template_type,
            html_val,
            css_val,
            data.gjs_components_json,
            cro_val,
            name_val,
            ab_enabled_int,
            data.variant_b_html,
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
            r["ab_test_enabled"] = bool(r.get("ab_test_enabled"))
            r["html"] = r.get("gjs_html")
            r["css"] = r.get("gjs_css")
            r["published_url"] = f"/lp/{r['slug']}" if r.get("slug") else None
        return rows
    finally:
        conn.close()


def publish_landing_page(
    page_id: str,
    tenant_id: str = "0f14ffff",
    block_on_cfo_violation: bool = False,
) -> Dict[str, Any]:
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

    if not cfo_audit["is_compliant"] and block_on_cfo_violation:
        raise ValueError(
            f"Publicação bloqueada por violação ética CFO: {'; '.join(cfo_audit['violations'])}"
        )

    slug = lp["slug"]
    cfo_cro = lp.get("cfo_responsible_cro") or "CRO-SP 00000"
    cfo_name = lp.get("cfo_responsible_name") or "Responsável Técnico Clínico"

    cfo_footer_html = f"""
    <footer class="cfo-compliance-footer" style="text-align: center; font-size: 0.8rem; color: #64748b; padding: 28px 16px; margin-top: 40px; border-top: 1px solid #e2e8f0; background: #f8fafc; font-family: Inter, system-ui, sans-serif;">
        <p style="margin: 0 0 6px 0; font-weight: 600; color: #334155;">Responsável Técnico: {cfo_name} — {cfo_cro}</p>
        <p style="margin: 0; line-height: 1.4;">Divulgação estritamente em conformidade com o Art. 43 do Código de Ética Odontológica e a Resolução CFO 196/2019. Resultados clínicos dependem de diagnóstico e anamnese individualizada.</p>
        <p style="margin: 8px 0 0 0; font-size: 0.75rem; color: #94a3b8;">&copy; 2026 RevNault Health Technologies. Todos os direitos reservados.</p>
    </footer>
    """

    interactive_script = f"""
    <script>
    document.addEventListener("DOMContentLoaded", function() {{
        const forms = document.querySelectorAll("form");
        forms.forEach(function(form) {{
            form.addEventListener("submit", async function(e) {{
                e.preventDefault();
                const formData = new FormData(form);
                const payload = {{
                    name: formData.get("name") || "",
                    email: formData.get("email") || "",
                    phone: formData.get("phone") || "",
                    cro: formData.get("cro") || "",
                    cro_uf: formData.get("cro_uf") || formData.get("cro") || "",
                    specialty: formData.get("specialty") || "Implantodontia"
                }};
                const btn = form.querySelector("button[type='submit']") || form.querySelector("button");
                const oldText = btn ? btn.innerText : "";
                if (btn) {{ btn.disabled = true; btn.innerText = "Enviando..."; }}
                try {{
                    const res = await fetch("/api/v1/campaigns/public/lp/{slug}/submit", {{
                        method: "POST",
                        headers: {{"Content-Type": "application/json"}},
                        body: JSON.stringify(payload)
                    }});
                    const data = await res.json();
                    if (res.ok) {{
                        form.innerHTML = "<div style='padding:24px;background:#ecfdf5;color:#065f46;border-radius:8px;text-align:center;font-family:sans-serif;'><h3>Solicitação Confirmada com Sucesso!</h3><p style='margin-top:8px;'>Nossa equipe de consultoria entrará em contato em breve.</p></div>";
                    }} else {{
                        alert("Erro ao registrar: " + (data.detail || "Verifique os dados informados."));
                        if (btn) {{ btn.disabled = false; btn.innerText = oldText; }}
                    }}
                }} catch(err) {{
                    alert("Erro ao conectar ao servidor. Tente novamente em instantes.");
                    if (btn) {{ btn.disabled = false; btn.innerText = oldText; }}
                }}
            }});
        }});
    }});
    </script>
    """

    body_content = lp.get("gjs_html") or ""
    if cfo_cro:
        body_content = body_content.replace("CRO-SP 00000", cfo_cro).replace("Dr. Consultor Clínico", cfo_name)
    if "cfo-compliance-footer" not in body_content:
        body_content += cfo_footer_html

    html_doc = (
        f"<!DOCTYPE html>\n<html lang=\"pt-BR\">\n<head>\n"
        f"<meta charset=\"UTF-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
        f"<title>{lp['title']}</title>\n"
        f"<style>\n{lp.get('gjs_css') or ''}\n</style>\n</head>\n"
        f"<body>\n{body_content}\n{interactive_script}\n</body>\n</html>"
    )
    html_bytes = html_doc.encode("utf-8")

    storage = R2StorageClient()
    r2_key = storage.generate_storage_key(
        tenant_id=tenant_id,
        module="r2_landing_pages",
        filename=f"{slug}.html",
        custom_uuid=slug,
    )
    r2_upload_res = storage.upload_bytes(r2_key, html_bytes, "text/html")
    published_r2_url = f"https://r2.revnault.internal/{r2_key}"
    published_url = f"/lp/{slug}"
    r2_url = f"/api/v1/storage/files/{r2_key}"

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE landing_pages
            SET is_published = 1,
                published_r2_url = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND tenant_id = ?
        """, (published_r2_url, page_id, tenant_id))
        conn.commit()
    finally:
        conn.close()

    status_msg = "CONFORME" if cfo_audit["is_compliant"] else "COM_ALERTA_ETICO"

    return {
        "id": page_id,
        "slug": slug,
        "is_published": True,
        "published_r2_url": published_r2_url,
        "published_url": published_url,
        "r2_url": r2_url,
        "r2_key": r2_key,
        "cfo_compliance_status": status_msg,
        "message": "Landing page compilada e publicada no Cloudflare R2 com sucesso."
    }


def render_landing_page_html(slug: str) -> Optional[str]:
    """Compila ou recupera o HTML5 completo da landing page para exibição direta no navegador."""
    lp = get_landing_page_by_slug(slug)
    if not lp:
        return None

    cfo_cro = lp.get("cfo_responsible_cro") or "CRO-SP 00000"
    cfo_name = lp.get("cfo_responsible_name") or "Responsável Técnico Clínico"

    cfo_footer_html = f"""
    <footer class="cfo-compliance-footer" style="text-align: center; font-size: 0.8rem; color: #64748b; padding: 28px 16px; margin-top: 40px; border-top: 1px solid #e2e8f0; background: #f8fafc; font-family: Inter, system-ui, sans-serif;">
        <p style="margin: 0 0 6px 0; font-weight: 600; color: #334155;">Responsável Técnico: {cfo_name} — {cfo_cro}</p>
        <p style="margin: 0; line-height: 1.4;">Divulgação estritamente em conformidade com o Art. 43 do Código de Ética Odontológica e a Resolução CFO 196/2019. Resultados clínicos dependem de diagnóstico e anamnese individualizada.</p>
        <p style="margin: 8px 0 0 0; font-size: 0.75rem; color: #94a3b8;">&copy; 2026 RevNault Health Technologies. Todos os direitos reservados.</p>
    </footer>
    """

    interactive_script = f"""
    <script>
    document.addEventListener("DOMContentLoaded", function() {{
        const forms = document.querySelectorAll("form");
        forms.forEach(function(form) {{
            form.addEventListener("submit", async function(e) {{
                e.preventDefault();
                const formData = new FormData(form);
                const payload = {{
                    name: formData.get("name") || "",
                    email: formData.get("email") || "",
                    phone: formData.get("phone") || "",
                    cro: formData.get("cro") || "",
                    cro_uf: formData.get("cro_uf") || formData.get("cro") || "",
                    specialty: formData.get("specialty") || "Implantodontia"
                }};
                const btn = form.querySelector("button[type='submit']") || form.querySelector("button");
                const oldText = btn ? btn.innerText : "";
                if (btn) {{ btn.disabled = true; btn.innerText = "Enviando..."; }}
                try {{
                    const res = await fetch("/api/v1/campaigns/public/lp/{slug}/submit", {{
                        method: "POST",
                        headers: {{"Content-Type": "application/json"}},
                        body: JSON.stringify(payload)
                    }});
                    const data = await res.json();
                    if (res.ok) {{
                        form.innerHTML = "<div style='padding:24px;background:#ecfdf5;color:#065f46;border-radius:8px;text-align:center;font-family:sans-serif;'><h3>Solicitação Confirmada com Sucesso!</h3><p style='margin-top:8px;'>Nossa equipe de consultoria entrará em contato em breve.</p></div>";
                    }} else {{
                        alert("Erro ao registrar: " + (data.detail || "Verifique os dados informados."));
                        if (btn) {{ btn.disabled = false; btn.innerText = oldText; }}
                    }}
                }} catch(err) {{
                    alert("Erro ao conectar ao servidor. Tente novamente em instantes.");
                    if (btn) {{ btn.disabled = false; btn.innerText = oldText; }}
                }}
            }});
        }});
    }});
    </script>
    """

    body_content = lp.get("gjs_html") or "<h1>RevNault Landing Page</h1>"
    if lp.get("ab_test_enabled") and lp.get("variant_b_html"):
        if not hasattr(render_landing_page_html, "_ab_counter"):
            render_landing_page_html._ab_counter = 0
        render_landing_page_html._ab_counter += 1
        if render_landing_page_html._ab_counter % 2 == 0:
            body_content = lp.get("variant_b_html")
    if cfo_cro:
        body_content = body_content.replace("CRO-SP 00000", cfo_cro).replace("Dr. Consultor Clínico", cfo_name)
    if "cfo-compliance-footer" not in body_content:
        body_content += cfo_footer_html

    return (
        f"<!DOCTYPE html>\n<html lang=\"pt-BR\">\n<head>\n"
        f"<meta charset=\"UTF-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
        f"<title>{lp['title']}</title>\n"
        f"<style>\n{lp.get('gjs_css') or ''}\n</style>\n</head>\n"
        f"<body>\n{body_content}\n{interactive_script}\n</body>\n</html>"
    )


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

    default_event_bus.publish_sync(
        StreamName.MARKETING,
        "lead.captured",
        {
            "submission_id": submission_id,
            "landing_page_slug": slug,
            "contact_id": contact_id,
            "name": data.name,
            "email": data.email,
            "cro": data.cro,
            "cro_verified": bool(contact.get("cro_verified", False)),
            "utm_campaign": data.utm_campaign,
        },
        tenant_id=tenant_id,
    )

    return {
        "success": True,
        "lead_id": contact_id,
        "landing_page_slug": slug,
        "cro_verified": bool(contact.get("cro_verified")),
        "message": "Lead capturado com sucesso e atribuído no CRM."
    }


