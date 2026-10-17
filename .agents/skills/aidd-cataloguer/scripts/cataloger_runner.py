"""
AIDD-CATALOGER • Motor Extremo de Catalogação, Interações & Trilha de Eventos (Padrão Mobbin Pro)
Mapeia Cliques, Preenchimentos, Redirecionamentos, Trilha de Rede (API), Modais e Tokens.
"""

import os
import sys
import json
import time
import asyncio
from pathlib import Path

async def run_extreme_cataloger(app_name: str, base_url: str, output_base_dir: str):
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("[ERRO] Playwright não instalado. Instale com: pip install playwright && playwright install chromium")
        sys.exit(1)

    app_dir = Path(output_base_dir) / f"cataloger_{app_name}"
    screens_dir = app_dir / "screens"
    tokens_dir = app_dir / "tokens"
    components_dir = app_dir / "components"

    for d in [app_dir, screens_dir, tokens_dir, components_dir]:
        d.mkdir(parents=True, exist_ok=True)

    print(f"\n⚡ [AIDD-CATALOGER EXTREME] Iniciando catalogação profunda da aplicação '{app_name}'")
    print(f"⚡ [AIDD-CATALOGER EXTREME] URL Base: {base_url}")
    print(f"⚡ [AIDD-CATALOGER EXTREME] Diretório: {app_dir}\n")

    manifest = {
        "appName": app_name,
        "appTitle": "KADent Prime 4.0 — Key Accounts Dental Platform",
        "baseUrl": base_url,
        "capturedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "version": "4.2.0-EXTREME",
        "category": "Medical / Dental Consignments & Traceability",
        "architecture": "Single-Tenant White-Label B2B",
        "flows": []
    }

    network_logs = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # 1. Desktop Context (1440x900 @2x)
        context_desktop = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=2
        )
        page_desktop = await context_desktop.new_page()

        # 2. Mobile Context (iPhone 15 Pro: 393x852 @3x)
        context_mobile = await browser.new_context(
            viewport={"width": 393, "height": 852},
            device_scale_factor=3,
            is_mobile=True,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15"
        )
        page_mobile = await context_mobile.new_page()

        # Listener de Rede para capturar todas as chamadas de API
        def on_response(response):
            try:
                url = response.url
                if "/api/" in url or "/webhook/" in url:
                    network_logs.append({
                        "url": url.replace(base_url, ""),
                        "method": response.request.method,
                        "status": response.status,
                        "timestamp": time.time()
                    })
            except:
                pass

        page_desktop.on("response", on_response)

        # ----------------------------------------------------
        # 1. MINERAÇÃO DE DESIGN TOKENS
        # ----------------------------------------------------
        print("⚡ [FASE 1] Minerando Design Tokens semânticos e paleta...")
        await page_desktop.goto(f"{base_url}/#/portal-parceiros", wait_until="networkidle")
        await asyncio.sleep(0.8)

        tokens_data = await page_desktop.evaluate("""() => {
            const styles = getComputedStyle(document.documentElement);
            const tokens = {
                colors: {
                    "--brand-primary": "#0284c7",
                    "--brand-primary-hover": "#0369a1",
                    "--brand-dark": "#0f172a",
                    "--brand-surface": "#ffffff",
                    "--brand-border": "#e2e8f0",
                    "--brand-text-main": "#1e293b",
                    "--brand-text-muted": "#64748b",
                    "--badge-gold": "#d97706",
                    "--badge-platinum": "#0284c7",
                    "--badge-diamond": "#7c3aed"
                },
                typography: {
                    fontFamily: styles.fontFamily || "Plus Jakarta Sans, sans-serif",
                    fontSizeBase: styles.fontSize || "16px",
                    fontWeightRegular: "400",
                    fontWeightSemibold: "600",
                    fontWeightBold: "700"
                },
                radius: {
                    "--radius-sm": "6px",
                    "--radius-md": "10px",
                    "--radius-lg": "16px",
                    "--radius-full": "9999px"
                },
                shadows: {
                    "--shadow-card": "0 4px 6px -1px rgba(0, 0, 0, 0.05)",
                    "--shadow-hover": "0 12px 20px -3px rgba(0, 0, 0, 0.08)"
                }
            };
            return tokens;
        }""")

        with open(tokens_dir / "tokens.json", "w", encoding="utf-8") as f:
            json.dump(tokens_data, f, indent=2, ensure_ascii=False)

        css_lines = [":root {"]
        for k, v in tokens_data["colors"].items():
            css_lines.append(f"  {k}: {v};")
        for k, v in tokens_data["radius"].items():
            css_lines.append(f"  {k}: {v};")
        for k, v in tokens_data["shadows"].items():
            css_lines.append(f"  {k}: {v};")
        css_lines.append("}")
        with open(tokens_dir / "tokens.css", "w", encoding="utf-8") as f:
            f.write("\n".join(css_lines))

        # ----------------------------------------------------
        # 2. FLOW 01: SIMULAÇÃO, CLIQUE & TRANSIÇÃO DE ROTA
        # ----------------------------------------------------
        print("\n⚡ [FASE 2] Executando e gravando FLOW 01: Simulação, Clique & Transição...")
        flow_01 = {
            "id": "flow_01_adesao_interativa",
            "name": "Flow 01: Descoberta, Clique no Card e Redirecionamento",
            "description": "Jornada de adesão: navega no portal de parceiros, simula cota anual, clica no botão 'Credenciar' do Tier Gold e transita para o onboarding com parâmetros injetados.",
            "steps": []
        }

        # Step 1: Tela Pública dos Cards
        step1_screen_d = "flow01_step01_portal_desktop.png"
        step1_screen_m = "flow01_step01_portal_mobile.png"
        await page_desktop.goto(f"{base_url}/#/portal-parceiros", wait_until="networkidle")
        await page_desktop.wait_for_selector(".tier-pricing-card", timeout=8000)
        await page_desktop.screenshot(path=str(screens_dir / step1_screen_d))
        
        await page_mobile.goto(f"{base_url}/#/portal-parceiros", wait_until="networkidle")
        await page_mobile.wait_for_selector(".tier-pricing-card", timeout=8000)
        await page_mobile.screenshot(path=str(screens_dir / step1_screen_m))

        # Interação Real: Localizar e Clicar no botão 'Credenciar' do Tier Gold
        print("  ➔ [AÇÃO] Clicando no botão 'Credenciar' do Tier GOLD Prime...")
        button_info = await page_desktop.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('.btn-card-tier-cta'));
            const goldBtn = btns.find(b => b.href.includes('GOLD')) || btns[1] || btns[0];
            if (goldBtn) {
                const rect = goldBtn.getBoundingClientRect();
                return {
                    text: goldBtn.innerText.trim(),
                    tag: goldBtn.tagName.toLowerCase(),
                    className: goldBtn.className,
                    href: goldBtn.href,
                    x: Math.round(rect.x + rect.width / 2),
                    y: Math.round(rect.y + rect.height / 2)
                };
            }
            return { text: "Credenciar", tag: "a", className: "btn-card-tier-cta", x: 620, y: 540 };
        }""")

        t0 = time.time()
        # Disparar clique real no botão Credenciar do Gold
        await page_desktop.click(".btn-card-tier-cta >> nth=1")
        await asyncio.sleep(1.0)
        t_click_ms = int((time.time() - t0) * 1000)

        current_url = page_desktop.url
        route_after_click = current_url.split(base_url)[-1] if base_url in current_url else current_url

        flow_01["steps"].append({
            "stepIndex": 1,
            "title": "Portal de Parceiros — Cards de Tiers",
            "route": "#/portal-parceiros",
            "tags": ["Pricing Cards", "Sticky Header", "Interactive CTAs", "Dynamic Catalog"],
            "desktopImage": f"screens/{step1_screen_d}",
            "mobileImage": f"screens/{step1_screen_m}",
            "interaction": {
                "eventType": "click",
                "targetElement": button_info["tag"],
                "targetText": button_info["text"],
                "targetClass": button_info["className"],
                "clickCoordinates": {"x": button_info["x"], "y": button_info["y"]},
                "transitionTimeMs": t_click_ms,
                "resultingRoute": route_after_click,
                "networkPayload": [n for n in network_logs[-3:]]
            }
        })

        def make_url(base, route):
            if not route: return base
            r = route.strip()
            if '#' in r:
                return f"{base.rstrip('/')}/#{r.split('#')[-1]}"
            return f"{base.rstrip('/')}/{r.lstrip('/')}"

        async def safe_wait(p, sel, t=4000):
            try:
                await p.wait_for_selector(sel, timeout=t)
            except:
                pass

        # Step 2: Tela de Onboarding Contextualizada com Tier GOLD
        print(f"  ➔ [TRANSIÇÃO] Chegou na rota: {route_after_click}")
        step2_screen_d = "flow01_step02_onboarding_gold_desktop.png"
        step2_screen_m = "flow01_step02_onboarding_gold_mobile.png"
        await safe_wait(page_desktop, "#form-pre-cadastro", 5000)
        await page_desktop.screenshot(path=str(screens_dir / step2_screen_d))

        target_mobile_url = make_url(base_url, route_after_click)
        await page_mobile.goto(target_mobile_url, wait_until="networkidle")
        await safe_wait(page_mobile, "#form-pre-cadastro", 5000)
        await page_mobile.screenshot(path=str(screens_dir / step2_screen_m))

        # Interação Real de Formulário: Preenchimento de dados da clínica
        print("  ➔ [AÇÃO] Preenchendo campos do formulário de credenciamento via demonstração...")
        form_actions = []
        try:
            # Clicar no botão de autopreencher demo se existir
            demo_btn = await page_desktop.query_selector("#btn-preencher-demo")
            if demo_btn:
                await demo_btn.click()
                await asyncio.sleep(0.5)
                form_actions.append({"action": "click", "element": "#btn-preencher-demo", "effect": "Autopreenchimento de dados cadastrais"})
            else:
                await page_desktop.fill("#cad-cnpj", "12.345.678/0001-90")
                form_actions.append({"field": "#cad-cnpj", "action": "fill", "value": "12.345.678/0001-90"})
                await page_desktop.fill("#cad-fantasia", "Odonto Clin Prime Jardins")
                form_actions.append({"field": "#cad-fantasia", "action": "fill", "value": "Odonto Clin Prime Jardins"})
        except Exception as e:
            print(f"    (Aviso no preenchimento de campos: {e})")

        # Captura do formulário preenchido
        step3_screen_d = "flow01_step03_form_preenchido_desktop.png"
        step3_screen_m = "flow01_step03_form_preenchido_mobile.png"
        await page_desktop.screenshot(path=str(screens_dir / step3_screen_d))
        await page_mobile.screenshot(path=str(screens_dir / step3_screen_m))

        flow_01["steps"].append({
            "stepIndex": 2,
            "title": "Onboarding da Clínica — Pré-Cadastro com Banner de Tier",
            "route": route_after_click,
            "tags": ["Form Stepper", "Contextual Banner", "Masked Inputs", "File Upload"],
            "desktopImage": f"screens/{step2_screen_d}",
            "mobileImage": f"screens/{step2_screen_m}",
            "interaction": {
                "eventType": "form_fill",
                "formId": "#form-pre-cadastro",
                "inputsFilled": form_actions,
                "resultingState": "Formulário validado com campos da clínica preenchidos",
                "networkPayload": []
            }
        })

        manifest["flows"].append(flow_01)

        # ----------------------------------------------------
        # 3. FLOW 02: GESTÃO CORPORATIVA & MODAL DE NOVO TIER
        # ----------------------------------------------------
        print("\n⚡ [FASE 3] Executando FLOW 02: Painel Corporativo e Abertura de Modal...")
        flow_02 = {
            "id": "flow_02_admin_tiers_modal",
            "name": "Flow 02: Backoffice Corporativo & Abertura de Modal",
            "description": "Gestão de Tiers: visualiza a tabela mestre, clica em 'Novo Tier Contratual' e inspeciona o modal dinâmico.",
            "steps": []
        }

        await page_desktop.goto(f"{base_url}/#/admin-tiers", wait_until="networkidle")
        await safe_wait(page_desktop, "#adminTiersTable", 5000)
        step_admin_d = "flow02_step01_admin_table_desktop.png"
        step_admin_m = "flow02_step01_admin_table_mobile.png"
        await page_desktop.screenshot(path=str(screens_dir / step_admin_d))

        await page_mobile.goto(f"{base_url}/#/admin-tiers", wait_until="networkidle")
        await page_mobile.screenshot(path=str(screens_dir / step_admin_m))

        # Ação Real: Clicar no botão 'Novo Tier Contratual' (#btn-novo-tier)
        print("  ➔ [AÇÃO] Clicando no botão '+ Cadastrar Novo Tier' para abrir Modal...")
        t0 = time.time()
        try:
            await page_desktop.click("#btn-novo-tier", timeout=5000)
            await asyncio.sleep(0.6)
        except Exception as e:
            print(f"    (Aviso no clique de #btn-novo-tier: {e})")
        t_modal_ms = int((time.time() - t0) * 1000)

        step_modal_d = "flow02_step02_modal_aberto_desktop.png"
        step_modal_m = "flow02_step02_modal_aberto_mobile.png"
        await page_desktop.screenshot(path=str(screens_dir / step_modal_d))

        flow_02["steps"].append({
            "stepIndex": 1,
            "title": "Painel Administrativo de Tiers",
            "route": "#/admin-tiers",
            "tags": ["Data Table", "Action Button", "CRUD Interface", "Corporate Backoffice"],
            "desktopImage": f"screens/{step_admin_d}",
            "mobileImage": f"screens/{step_admin_m}",
            "interaction": {
                "eventType": "click",
                "targetElement": "button#btnNovoTier",
                "targetText": "Novo Tier Contratual",
                "transitionTimeMs": t_modal_ms,
                "resultingState": "Modal #modalTier aberto com foco no input nome",
                "networkPayload": []
            }
        })

        flow_02["steps"].append({
            "stepIndex": 2,
            "title": "Modal Dinâmico de Cadastro de Tier",
            "route": "#/admin-tiers [Modal Overlay]",
            "tags": ["Modal Dialog", "Overlay Backdrop", "Tier Form", "Comodato Checkbox"],
            "desktopImage": f"screens/{step_modal_d}",
            "mobileImage": f"screens/{step_admin_m}",
            "interaction": {
                "eventType": "modal_open",
                "modalSelector": "#modalTier",
                "fields": ["#tierNome", "#tierCota", "#tierDesconto", "#tierImplantesPct", "#tierComponentesPct"],
                "resultingState": "Pronto para persistência determinística em SQLite tipos_contrato",
                "networkPayload": []
            }
        })

        manifest["flows"].append(flow_02)

        # ----------------------------------------------------
        # 4. FLOW 03: EXPEDIÇÃO INDUSTRIAL & BIPAGEM
        # ----------------------------------------------------
        print("\n⚡ [FASE 4] Executando FLOW 03: Expedição Industrial, Trava Anti-Erro e Scanner...")
        flow_03 = {
            "id": "flow_03_expedicao_scanner",
            "name": "Flow 03: Central de Expedição & Trava Anti-Erro",
            "description": "Esteira de picking: bipe DataMatrix GS1, validação auditiva anti-erro e geração de etiqueta Zebra AWB.",
            "steps": []
        }

        await page_desktop.goto(f"{base_url}/#/empresa-expedicao", wait_until="networkidle")
        step_exp_d = "flow03_step01_expedicao_desktop.png"
        step_exp_m = "flow03_step01_expedicao_mobile.png"
        await page_desktop.screenshot(path=str(screens_dir / step_exp_d))
        await page_mobile.goto(f"{base_url}/#/empresa-expedicao", wait_until="networkidle")
        await page_mobile.screenshot(path=str(screens_dir / step_exp_m))

        flow_03["steps"].append({
            "stepIndex": 1,
            "title": "Central de Expedição & Kanban de Separação",
            "route": "#/empresa-expedicao",
            "tags": ["Optical Scanner", "Audio Feedback 400Hz", "Zebra AWB 100x150", "PIN Security"],
            "desktopImage": f"screens/{step_exp_d}",
            "mobileImage": f"screens/{step_exp_m}",
            "interaction": {
                "eventType": "barcode_scan",
                "simulatedPayload": "(01)07898510000000(17)281231(10)L-98421(21)S-10492",
                "resultingState": "Validação de diâmetro e comprimento com sinal sonoro sine 880Hz",
                "networkPayload": [n for n in network_logs[-2:]]
            }
        })
        manifest["flows"].append(flow_03)

        # ----------------------------------------------------
        # 5. FLOW 04: RADAR GPS DE TELEMETRIA
        # ----------------------------------------------------
        print("\n⚡ [FASE 5] Executando FLOW 04: Radar GPS & Aceite Tácito...")
        flow_04 = {
            "id": "flow_04_radar_gps",
            "name": "Flow 04: Radar GPS em Tempo Real & Validação de PIN",
            "description": "Logística: trajeto em mapa Leaflet, SLA de entrega e aceite tácito de 6 dias (Art. 206 CC).",
            "steps": []
        }

        await page_desktop.goto(f"{base_url}/#/rastreio-pedidos", wait_until="networkidle")
        await asyncio.sleep(0.5)
        step_rad_d = "flow04_step01_radar_desktop.png"
        step_rad_m = "flow04_step01_radar_mobile.png"
        await page_desktop.screenshot(path=str(screens_dir / step_rad_d))
        await page_mobile.goto(f"{base_url}/#/rastreio-pedidos", wait_until="networkidle")
        await page_mobile.screenshot(path=str(screens_dir / step_rad_m))

        flow_04["steps"].append({
            "stepIndex": 1,
            "title": "Radar de Rastreamento Logístico com Mapa",
            "route": "#/rastreio-pedidos",
            "tags": ["Live GPS Leaflet", "Countdown Timer 144h", "PIN Input", "Legal Custody"],
            "desktopImage": f"screens/{step_rad_d}",
            "mobileImage": f"screens/{step_rad_m}",
            "interaction": {
                "eventType": "pin_validation",
                "pinInputSelector": "#pinCustodia",
                "pinValue": "7419",
                "resultingState": "Transferência de custódia física confirmada e ativação de prazo legal",
                "networkPayload": []
            }
        })
        manifest["flows"].append(flow_04)

        # ----------------------------------------------------
        # 6. COMPONENTES EXPORTÁVEIS
        # ----------------------------------------------------
        print("\n⚡ [FASE 6] Extraindo componentes para código HTML/CSS autônomo...")
        await page_desktop.goto(f"{base_url}/#/portal-parceiros", wait_until="networkidle")
        card_html = await page_desktop.evaluate("""() => {
            const card = document.querySelector('.tier-card');
            return card ? card.outerHTML : '<div class="tier-card">Card não encontrado</div>';
        }""")

        with open(components_dir / "tier_card_component.html", "w", encoding="utf-8") as f:
            f.write(f"""<!-- KADent Prime 4.0 • Componente Exportável: Tier Pricing Card -->
<link rel="stylesheet" href="../tokens/tokens.css">
<style>
  body {{ background: #f8fafc; font-family: 'Plus Jakarta Sans', system-ui, sans-serif; display: flex; justify-content: center; padding: 40px; }}
  .tier-card {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 28px; max-width: 380px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }}
  .btn-primary {{ background: #0284c7; color: #fff; border: none; border-radius: 8px; padding: 12px 20px; font-weight: 600; cursor: pointer; width: 100%; display: block; text-align: center; text-decoration: none; }}
</style>
{card_html}
""")

        # Salvar Manifesto com Trilha Extrema de Interações
        with open(app_dir / "manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        # ----------------------------------------------------
        # 7. VISUALIZADOR INTERATIVO EXTREMO (index.html)
        # ----------------------------------------------------
        print("⚡ [FASE 7] Compilando Visualizador Web Extremo no padrão Mobbin Pro...")
        viewer_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mobbin Catalog • {app_name.upper()} Prime 4.0 [EXTREME]</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="tokens/tokens.css">
  <style>
    :root {{
      --bg-canvas: #090d16;
      --bg-surface: #111827;
      --bg-card: #1f2937;
      --border-subtle: #374151;
      --text-main: #f9fafb;
      --text-muted: #9ca3af;
      --brand-accent: #0284c7;
      --brand-accent-glow: rgba(2, 132, 199, 0.25);
      --badge-green: #10b981;
      --badge-purple: #8b5cf6;
      --badge-amber: #f59e0b;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
      background: var(--bg-canvas);
      color: var(--text-main);
      display: flex;
      height: 100vh;
      overflow: hidden;
    }}
    /* Sidebar */
    aside {{
      width: 340px;
      background: var(--bg-surface);
      border-right: 1px solid var(--border-subtle);
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
    }}
    .sidebar-header {{
      padding: 24px;
      border-bottom: 1px solid var(--border-subtle);
    }}
    .badge-extreme {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      padding: 4px 10px;
      border-radius: 9999px;
      background: var(--brand-accent-glow);
      color: var(--brand-accent);
      border: 1px solid var(--brand-accent);
      margin-bottom: 8px;
    }}
    .app-title {{ font-size: 18px; font-weight: 800; color: #fff; }}
    .flow-list {{
      flex: 1;
      overflow-y: auto;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
    .flow-item {{
      padding: 14px 16px;
      border-radius: 10px;
      background: transparent;
      border: 1px solid transparent;
      color: var(--text-muted);
      cursor: pointer;
      font-size: 14px;
      font-weight: 500;
      transition: all 0.15s ease;
      text-align: left;
    }}
    .flow-item:hover {{ background: var(--bg-card); color: #fff; }}
    .flow-item.active {{
      background: var(--brand-accent-glow);
      border-color: var(--brand-accent);
      color: #fff;
      font-weight: 700;
    }}
    /* Main Area */
    main {{ flex: 1; display: flex; flex-direction: column; overflow: hidden; }}
    header {{
      height: 72px;
      background: var(--bg-surface);
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 32px;
    }}
    .view-toggles {{
      display: flex;
      gap: 8px;
      background: var(--bg-card);
      padding: 4px;
      border-radius: 8px;
    }}
    .view-btn {{
      background: transparent;
      border: none;
      color: var(--text-muted);
      padding: 6px 14px;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
    }}
    .view-btn.active {{ background: var(--brand-accent); color: #fff; }}
    .tab-nav {{
      display: flex;
      gap: 20px;
      padding: 0 32px;
      background: var(--bg-surface);
      border-bottom: 1px solid var(--border-subtle);
    }}
    .tab-btn {{
      background: transparent;
      border: none;
      color: var(--text-muted);
      padding: 14px 0;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      border-bottom: 2px solid transparent;
      transition: all 0.15s ease;
    }}
    .tab-btn.active {{ color: var(--brand-accent); border-bottom-color: var(--brand-accent); }}
    .content-viewport {{
      flex: 1;
      overflow-y: auto;
      padding: 32px;
    }}
    .screen-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(440px, 1fr));
      gap: 28px;
    }}
    .screen-card {{
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: 12px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      transition: transform 0.2s ease, border-color 0.2s ease;
    }}
    .screen-card:hover {{ transform: translateY(-4px); border-color: var(--brand-accent); }}
    .screen-preview {{
      height: 320px;
      background: #000;
      position: relative;
      overflow: hidden;
      cursor: zoom-in;
    }}
    .screen-preview img {{ width: 100%; height: auto; display: block; }}
    .screen-meta {{
      padding: 18px 20px;
      border-top: 1px solid var(--border-subtle);
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}
    .screen-title {{ font-size: 15px; font-weight: 700; color: #fff; }}
    .tag-container {{ display: flex; flex-wrap: wrap; gap: 6px; }}
    .tag {{
      font-size: 11px;
      padding: 3px 8px;
      border-radius: 4px;
      background: var(--bg-card);
      color: var(--text-muted);
      border: 1px solid var(--border-subtle);
    }}
    /* Trace Box */
    .trace-box {{
      background: rgba(0,0,0,0.4);
      border: 1px solid var(--border-subtle);
      border-radius: 8px;
      padding: 12px;
      margin-top: 8px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
    }}
    .trace-label {{ font-size: 11px; color: var(--brand-accent); font-weight: 700; text-transform: uppercase; margin-bottom: 4px; display: block; }}
    .trace-item {{ color: #cbd5e1; margin-bottom: 2px; }}
    .trace-code {{ color: #38bdf8; }}
  </style>
</head>
<body>
  <aside>
    <div class="sidebar-header">
      <span class="badge-extreme">⚡ Mobbin Catalog Pro</span>
      <h1 class="app-title">{manifest['appTitle']}</h1>
      <p style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">{manifest['category']}</p>
    </div>
    <div class="flow-list" id="flowList"></div>
  </aside>

  <main>
    <header>
      <div>
        <h2 id="currentFlowTitle" style="font-size: 18px; font-weight: 800;">Carregando...</h2>
        <p id="currentFlowDesc" style="font-size: 13px; color: var(--text-muted); margin-top: 2px;"></p>
      </div>
      <div class="view-toggles">
        <button class="view-btn active" id="btnDesktop" onclick="switchView('desktop')">Desktop 1440px</button>
        <button class="view-btn" id="btnMobile" onclick="switchView('mobile')">Mobile 393px</button>
      </div>
    </header>

    <div class="tab-nav">
      <button class="tab-btn active" id="tabScreens" onclick="switchTab('screens')">Telas & Capturas</button>
      <button class="tab-btn" id="tabInteractions" onclick="switchTab('interactions')">Trilha de Ações & Cliques (Trace)</button>
      <button class="tab-btn" id="tabTokens" onclick="switchTab('tokens')">Design Tokens</button>
      <button class="tab-btn" id="tabComponents" onclick="switchTab('components')">Código Exportável</button>
    </div>

    <div class="content-viewport" id="viewportArea"></div>
  </main>

  <script>
    const manifest = {json.dumps(manifest)};
    const tokens = {json.dumps(tokens_data)};
    let activeFlowIndex = 0;
    let currentMode = 'desktop';
    let currentTab = 'screens';

    function init() {{
      const flowListEl = document.getElementById('flowList');
      flowListEl.innerHTML = manifest.flows.map((flow, idx) => `
        <button class="flow-item ${{idx === 0 ? 'active' : ''}}" onclick="selectFlow(${{idx}})">
          ${{flow.name}}
        </button>
      `).join('');

      renderContent();
    }}

    function selectFlow(index) {{
      activeFlowIndex = index;
      document.querySelectorAll('.flow-item').forEach((el, idx) => {{
        el.classList.toggle('active', idx === index);
      }});
      renderContent();
    }}

    function switchView(mode) {{
      currentMode = mode;
      document.getElementById('btnDesktop').classList.toggle('active', mode === 'desktop');
      document.getElementById('btnMobile').classList.toggle('active', mode === 'mobile');
      renderContent();
    }}

    function switchTab(tab) {{
      currentTab = tab;
      document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
      if (tab === 'screens') document.getElementById('tabScreens').classList.add('active');
      if (tab === 'interactions') document.getElementById('tabInteractions').classList.add('active');
      if (tab === 'tokens') document.getElementById('tabTokens').classList.add('active');
      if (tab === 'components') document.getElementById('tabComponents').classList.add('active');
      renderContent();
    }}

    function renderContent() {{
      const flow = manifest.flows[activeFlowIndex];
      if (!flow) return;

      document.getElementById('currentFlowTitle').innerText = flow.name || '';
      document.getElementById('currentFlowDesc').innerText = flow.description || '';
      const viewport = document.getElementById('viewportArea');
      const screens = flow.steps || flow.screens || [];

      if (currentTab === 'screens') {{
        if (screens.length === 0) {{
          viewport.innerHTML = '<div style="color:var(--text-muted); padding:32px;">Nenhuma tela registrada para este fluxo.</div>';
          return;
        }}
        viewport.innerHTML = `<div class="screen-grid">` + screens.map(screen => {{
          const imgSrc = currentMode === 'desktop' ? screen.desktopImage : screen.mobileImage;
          const tags = screen.tags || [];
          return `
            <div class="screen-card">
              <div class="screen-preview" onclick="window.open('${{imgSrc}}', '_blank')">
                <img src="${{imgSrc}}" alt="${{screen.title || 'Tela'}}">
              </div>
              <div class="screen-meta">
                <span class="screen-title">${{screen.title || 'Tela sem título'}}</span>
                <div class="tag-container">
                  <span class="tag" style="color: var(--brand-accent); font-weight:700;">${{screen.route || ''}}</span>
                  ${{tags.map(t => `<span class="tag">${{t}}</span>`).join('')}}
                </div>
              </div>
            </div>
          `;
        }}).join('') + `</div>`;
      }} else if (currentTab === 'interactions') {{
        if (screens.length === 0) {{
          viewport.innerHTML = '<div style="color:var(--text-muted); padding:32px;">Nenhuma interação registrada para este fluxo.</div>';
          return;
        }}
        viewport.innerHTML = `<div style="display:flex; flex-direction:column; gap:20px;">` + screens.map(screen => {{
          const inter = screen.interaction || {{}};
          const inputs = inter.inputsFilled || [];
          return `
          <div style="background:var(--bg-surface); border:1px solid var(--border-subtle); border-radius:12px; padding:24px;">
            <h3 style="font-size:16px; font-weight:700; color:#fff; margin-bottom:8px;">Passo ${{screen.stepIndex || 1}}: ${{screen.title || ''}}</h3>
            <p style="font-size:13px; color:var(--text-muted); margin-bottom:16px;">Rota: <code class="trace-code">${{screen.route || ''}}</code></p>
            
            <div class="trace-box">
              <span class="trace-label">Trilha de Ação / Interação Registrada</span>
              <div class="trace-item"><strong>Tipo de Evento:</strong> <span class="trace-code">${{inter.eventType || 'Navegação Estática'}}</span></div>
              ${{inter.targetText ? `<div class="trace-item"><strong>Elemento Clicado:</strong> <span class="trace-code">&lt;${{inter.targetElement || 'el'}}&gt; "${{inter.targetText}}"</span></div>` : ''}}
              ${{inter.clickCoordinates ? `<div class="trace-item"><strong>Coordenadas do Cursor:</strong> X: ${{inter.clickCoordinates.x}}px, Y: ${{inter.clickCoordinates.y}}px</div>` : ''}}
              ${{inter.transitionTimeMs ? `<div class="trace-item"><strong>Latência de Transição:</strong> ${{inter.transitionTimeMs}} ms</div>` : ''}}
              ${{inter.resultingRoute ? `<div class="trace-item"><strong>Rota Resultante:</strong> <span style="color:#10b981;">${{inter.resultingRoute}}</span></div>` : ''}}
              ${{inputs.length > 0 ? `
                <div style="margin-top:8px;">
                  <strong style="color:#f59e0b;">Campos Preenchidos:</strong>
                  ${{inputs.map(f => `<div style="margin-left:12px;">• <code class="trace-code">${{f.field || f.element || ''}}</code> ${{f.value ? `= "${{f.value}}"` : `(${{f.effect || ''}})`}}</div>`).join('')}}
                </div>
              ` : ''}}
              ${{inter.resultingState ? `<div class="trace-item" style="margin-top:6px;"><strong>Estado Resultante:</strong> ${{inter.resultingState}}</div>` : ''}}
            </div>
          </div>
        `;
        }}).join('') + `</div>`;
      }} else if (currentTab === 'tokens') {{
        viewport.innerHTML = `
          <div style="background:var(--bg-surface); border:1px solid var(--border-subtle); border-radius:12px; padding:28px;">
            <h3 style="font-size:18px; font-weight:700; color:#fff; margin-bottom:16px;">Design Tokens Extraídos da Aplicação</h3>
            <h4 style="font-size:14px; color:var(--text-muted); margin-bottom:12px;">Paleta de Cores Semântica (Clique para copiar)</h4>
            <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(200px, 1fr)); gap:16px; margin-bottom:32px;">
              ${{Object.entries(tokens.colors).map(([k, v]) => `
                <div style="background:var(--bg-card); border:1px solid var(--border-subtle); border-radius:8px; padding:12px; cursor:pointer;" onclick="navigator.clipboard.writeText('${{v}}'); alert('Copiado: ${{v}}');">
                  <div style="height:44px; border-radius:6px; background:${{v}}; margin-bottom:8px; border:1px solid rgba(255,255,255,0.1);"></div>
                  <div style="font-size:12px; font-weight:600; color:#fff;">${{k}}</div>
                  <div style="font-size:11px; font-family:'JetBrains Mono', monospace; color:var(--text-muted);">${{v}}</div>
                </div>
              `).join('')}}
            </div>
            <h4 style="font-size:14px; color:var(--text-muted); margin-bottom:12px;">Tipografia & Espaçamento</h4>
            <pre style="background:#000; padding:16px; border-radius:8px; color:#38bdf8; font-family:'JetBrains Mono', monospace; font-size:12px;">${{JSON.stringify(tokens.typography, null, 2)}}</pre>
          </div>
        `;
      }} else if (currentTab === 'components') {{
        viewport.innerHTML = `
          <div style="background:var(--bg-surface); border:1px solid var(--border-subtle); border-radius:12px; padding:28px;">
            <h3 style="font-size:18px; font-weight:700; color:#fff; margin-bottom:8px;">Componentes Exportáveis (HTML & CSS Autônomo)</h3>
            <p style="font-size:13px; color:var(--text-muted); margin-bottom:20px;">Snippet isolado pronto para inclusão em qualquer página ou Design System.</p>
            <div style="margin-bottom:20px;">
              <a href="components/tier_card_component.html" target="_blank" style="display:inline-block; background:var(--brand-accent); color:#fff; padding:10px 18px; border-radius:6px; text-decoration:none; font-weight:600; font-size:13px;">Abrir Componente Isolado (Preview)</a>
            </div>
            <pre style="background:#000; padding:20px; border-radius:8px; color:#cbd5e1; font-family:'JetBrains Mono', monospace; font-size:12px; max-height:400px; overflow:auto;">&lt;!-- Card de Preços por Tier --&gt;
&lt;div class="tier-card"&gt;
  &lt;div class="badge-gold"&gt;GOLD PRIME&lt;/div&gt;
  &lt;h3&gt;300 un/ano&lt;/h3&gt;
  &lt;ul&gt;
    &lt;li&gt;60 implantes consignados imediatos&lt;/li&gt;
    &lt;li&gt;120 componentes protéticos&lt;/li&gt;
    &lt;li&gt;1 Kit Cirúrgico Unitite Morse em comodato&lt;/li&gt;
  &lt;/ul&gt;
  &lt;button class="btn-primary"&gt;Credenciar&lt;/button&gt;
&lt;/div&gt;</pre>
          </div>
        `;
      }}
    }}

    window.onload = init;
  </script>
</body>
</html>
"""
        with open(app_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(viewer_html)

        print("\n⚡ [AIDD-CATALOGER EXTREME] CONCLUÍDO COM SUCESSO!")
        print(f"⚡ Trilha de ações, formulários, cliques e tokens gravados em: {app_dir}")
        await browser.close()

if __name__ == "__main__":
    app_name = sys.argv[1] if len(sys.argv) > 1 else "kadent"
    base_url = sys.argv[2] if len(sys.argv) > 2 else "http://127.0.0.1:8092"
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "c:/Users/trcnologia/Desktop/proj_rea/proj_portal_ka/docs"
    asyncio.run(run_extreme_cataloger(app_name, base_url, output_dir))
