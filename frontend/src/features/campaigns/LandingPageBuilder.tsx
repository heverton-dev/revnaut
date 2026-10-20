import React, { useEffect, useState } from "react";
import {
  UploadCloud,
  Save,
  ShieldCheck,
  Loader2,
  Sparkles,
  Mail,
  Send,
  Zap,
  Share2,
  Users,
  Award,
  Link as LinkIcon,
  Play,
  RotateCw,
  Activity,
  Plus,
  Monitor,
  Tablet,
  Smartphone,
  Code2,
  Eye,
  ExternalLink,
  Wand2,
  Trash2,
  FlaskConical,
  X,
} from "lucide-react";
import { QrCodeSvg } from "@/components/shared/QrCodeSvg";
import { RouteHeader } from "@/components/ui/RouteHeader";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { Tabs } from "@/components/ui/Tabs";

export interface LandingPageTemplate {
  template_type: string;
  name: string;
  description: string;
  category: string;
  html: string;
  css: string;
}

export interface LandingPageItem {
  id: string;
  slug: string;
  title: string;
  campaign_id?: string;
  cfo_cro?: string;
  cfo_name?: string;
  is_published: boolean;
  published_url?: string;
  created_at?: string;
}

export interface AutomationFlowItem {
  id: string;
  account_id: string;
  name: string;
  category: string;
  trigger_event: string;
  action_description: string;
  is_active: boolean;
  execution_count: number;
  last_run_at?: string;
}

export interface AutomationLogItem {
  id: string;
  flow_id: string;
  result_summary: string;
  status: string;
  executed_at: string;
}

export interface ReferralDashboardData {
  referrer_id: string;
  referrer_name?: string;
  referrer_cro_uf?: string;
  referral_code?: string;
  referral_url?: string;
  total_referrals: number;
  qualified_referrals: number;
  total_rewards_earned?: number;
  conversions?: any[];
}

export interface LandingPageBuilderProps {
  pageId?: string;
  campaignId?: string;
  initialSlug?: string;
  initialTitle?: string;
  onPublished?: (url: string) => void;
}

export const LandingPageBuilder: React.FC<LandingPageBuilderProps> = ({
  pageId,
  campaignId,
  initialSlug = "nova-pagina-odonto",
  initialTitle = "Nova Landing Page Odontológica",
  onPublished,
}) => {
  const [activeMainTab, setActiveMainTab] = useState<string>("builder");

  // ==========================================
  // TAB 1: ESTÚDIO VISUAL DE LANDING PAGE & R2
  // ==========================================
  const [editorHtml, setEditorHtml] = useState<string>("");
  const [editorCss, setEditorCss] = useState<string>("");
  const [renderedHtml, setRenderedHtml] = useState<string>("");
  const [viewport, setViewport] = useState<"desktop" | "tablet" | "mobile">("desktop");
  const [editorMode, setEditorMode] = useState<"visual" | "code">("visual");
  const [copyFixLog, setCopyFixLog] = useState<string[]>([]);
  const [tokenCss, setTokenCss] = useState<string>("");

  // TICKET-MKT-01: Teste A/B Split 50/50
  const [abTestEnabled, setAbTestEnabled] = useState<boolean>(false);
  const [showAbModal, setShowAbModal] = useState<boolean>(false);
  const [abVariantA, setAbVariantA] = useState<string>("");
  const [abVariantB, setAbVariantB] = useState<string>("");
  const [abVariantName, setAbVariantName] = useState<string>("Hero Headline Test");

  const [savedPages, setSavedPages] = useState<LandingPageItem[]>([]);
  const [resolvedCampaignId, setResolvedCampaignId] = useState<string>(campaignId || "");

  useEffect(() => {
    if (!campaignId) {
      fetch("/api/v1/campaigns")
        .then((r) => r.json())
        .then((data) => {
          if (Array.isArray(data) && data.length > 0) {
            setResolvedCampaignId(data[0].id);
          }
        })
        .catch(() => {});
    }
  }, [campaignId]);

  const activeCampaignId = campaignId || resolvedCampaignId || "camp-01";
  const [title, setTitle] = useState(initialTitle);
  const [slug, setSlug] = useState(campaignId ? `${initialSlug}-${campaignId}` : initialSlug);
  const [cfoCro, setCfoCro] = useState("CRO-SP 123456");
  const [cfoName, setCfoName] = useState("Dr. Especialista Técnico");
  const [templates, setTemplates] = useState<LandingPageTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState("imersao_fluxo_digital");
  const [isSaving, setIsSaving] = useState(false);
  const [isPublishing, setIsPublishing] = useState(false);
  const [publishedUrl, setPublishedUrl] = useState<string | null>(null);
  const [cfoStatus, setCfoStatus] = useState<string | null>(null);
  const [currentId, setCurrentId] = useState<string | null>(pageId || null);

  // Teste de captura pública de lead
  const [testLeadName, setTestLeadName] = useState("Dr. Cirurgião Teste");
  const [testLeadEmail, setTestLeadEmail] = useState("teste.lead@clinica.com");
  const [testLeadPhone, setTestLeadPhone] = useState("+5511999998888");
  const [testLeadCro, setTestLeadCro] = useState("CRO-SP-88776");
  const [testLeadFeedback, setTestLeadFeedback] = useState<string | null>(null);

  // ==========================================
  // TAB 2: LISTMONK & MAUTIC AUTOMATIONS
  // ==========================================
  const [broadcastTitle, setBroadcastTitle] = useState("Lançamento Implante Cônico 2026");
  const [broadcastSubject, setBroadcastSubject] = useState("Condição Especial de Pré-Lançamento para Cirurgiões SP");
  const [broadcastHtml, setBroadcastHtml] = useState("<p>Olá Dr(a), conheça a nova linha de implantes com torque guiado.</p>");
  const [broadcastUf, setBroadcastUf] = useState("SP");
  const [broadcastSpecialty, setBroadcastSpecialty] = useState("Implantodontia");
  const [dispatchingBroadcast, setDispatchingBroadcast] = useState(false);
  const [broadcastResult, setBroadcastResult] = useState<any>(null);

  const [simulatingWebhook, setSimulatingWebhook] = useState(false);
  const [webhookResult, setWebhookResult] = useState<any>(null);

  const [flows, setFlows] = useState<AutomationFlowItem[]>([]);
  const [logs, setLogs] = useState<AutomationLogItem[]>([]);
  const [, setLoadingFlows] = useState(false);

  // ==========================================
  // TAB 3: MEMBER-GET-MEMBER (MGM)
  // ==========================================
  const [referrerId, setReferrerId] = useState("ref-cirurgiao-01");
  const [referrerName, setReferrerName] = useState("Dr. Roberto Silveira");
  const [referrerCro, setReferrerCro] = useState("CRO-SP-54321");
  const [referralLinkData, setReferralLinkData] = useState<any>(null);
  const [mgmDashboard, setMgmDashboard] = useState<ReferralDashboardData | null>(null);

  // Registro de indicado
  const [referredName, setReferredName] = useState("Dra. Beatriz Lins");
  const [referredPhone, setReferredPhone] = useState("+5511988884444");
  const [referredCro, setReferredCro] = useState("CRO-SP-77112");
  const [referredEmail, setReferredEmail] = useState("beatriz.lins@odonto.com");
  const [registerResult, setRegisterResult] = useState<any>(null);

  // Qualificação
  const [qualifyDealId, setQualifyDealId] = useState("deal-01");
  const [qualifyResult, setQualifyResult] = useState<any>(null);

  // Carregar Templates e Páginas Salvas
  const fetchLandingPages = async () => {
    try {
      const res = await fetch("/api/v1/campaigns/landing-pages");
      if (res.ok) {
        const data = await res.json();
        setSavedPages(data);
      }
    } catch {
      // fallback
    }
  };

  useEffect(() => {
    fetch("/api/v1/campaigns/landing-pages/templates")
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) setTemplates(data);
      })
      .catch(() => {});

    fetchLandingPages();
  }, []);

  // Carregar Fluxos de Automação
  const fetchAutomations = async () => {
    setLoadingFlows(true);
    try {
      const [resFlows, resLogs] = await Promise.all([
        fetch("/api/v1/automations/flows"),
        fetch("/api/v1/automations/logs"),
      ]);
      if (resFlows.ok) {
        const flowsData = await resFlows.json();
        setFlows(flowsData);
      }
      if (resLogs.ok) {
        const logsData = await resLogs.json();
        setLogs(logsData);
      }
    } catch {
      // fallback
    } finally {
      setLoadingFlows(false);
    }
  };

  // Carregar Dashboard MGM
  const fetchMgmDashboard = async () => {
    try {
      const res = await fetch(`/api/v1/campaigns/referral/dashboard/${encodeURIComponent(referrerId)}`);
      if (res.ok) {
        const data = await res.json();
        setMgmDashboard(data);
        if (data.referral_url) {
          setReferralLinkData({
            referral_code: data.referral_code,
            referral_url: data.referral_url,
          });
        }
      }
    } catch {
      // fallback
    }
  };

  useEffect(() => {
    if (activeMainTab === "automations") {
      fetchAutomations();
    } else if (activeMainTab === "referral") {
      fetchMgmDashboard();
    }
  }, [activeMainTab, referrerId]);

  // Tokens do design system injetados no iframe (variáveis CSS não atravessam o srcDoc)
  useEffect(() => {
    const root = getComputedStyle(document.documentElement);
    const names = [
      "--color-brand-primary", "--color-brand-primary-hover", "--color-brand-primary-subtle",
      "--color-brand-navy", "--color-brand-navy-subtle", "--color-surface-bg", "--color-surface-card",
      "--color-border", "--color-border-subtle", "--color-text-main", "--color-text-secondary",
      "--color-text-muted", "--color-text-inverse", "--color-success", "--color-success-subtle",
      "--color-warning", "--color-warning-subtle", "--color-danger", "--color-danger-subtle",
    ];
    const decl = names.map((n) => `${n}:${root.getPropertyValue(n).trim()};`).join("");
    setTokenCss(`:root{${decl}}body{margin:0;font-family:var(--font-family-sans,sans-serif);color:var(--color-text-main);background:var(--color-surface-card)}`);
  }, []);

  // Recebe edições inline do iframe (sem recarregar para não perder o cursor)
  useEffect(() => {
    const onMsg = (ev: MessageEvent) => {
      if (ev.data && ev.data.type === "lp-inline-edit" && typeof ev.data.html === "string") {
        setEditorHtml(ev.data.html);
      }
    };
    window.addEventListener("message", onMsg);
    return () => window.removeEventListener("message", onMsg);
  }, []);

  const applyContent = (html: string, css: string) => {
    setEditorHtml(html);
    setEditorCss(css);
    setRenderedHtml(html);
  };

  const loadTemplate = (tpl: LandingPageTemplate) => {
    setSelectedTemplate(tpl.template_type);
    applyContent(tpl.html || "", tpl.css || "");
    setCopyFixLog([]);
  };

  // Template padrão carregado assim que a lista chega
  useEffect(() => {
    if (templates.length > 0 && !editorHtml && !currentId) {
      const tpl = templates.find((t) => t.template_type === selectedTemplate) || templates[0];
      applyContent(tpl.html || "", tpl.css || "");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [templates]);

  const loadSavedPage = async (id: string) => {
    setCurrentId(id || null);
    const found = savedPages.find((p) => p.id === id);
    if (!found) return;
    setTitle(found.title);
    setSlug(found.slug);
    if (found.cfo_cro) setCfoCro(found.cfo_cro);
    if (found.cfo_name) setCfoName(found.cfo_name);
    if (found.published_url) setPublishedUrl(found.published_url);
    try {
      const res = await fetch(`/api/v1/campaigns/landing-pages/${id}`);
      if (res.ok) {
        const detail = await res.json();
        applyContent(detail.html ?? "", detail.css ?? "");
        return;
      }
    } catch {
      // fallback abaixo
    }
    const inline = found as unknown as { html?: string; css?: string };
    applyContent(inline.html ?? "", inline.css ?? "");
  };

  const dentalBlocks: Array<{ id: string; label: string; html: string }> = [
    {
      id: "hero",
      label: "Hero Cirúrgico",
      html: `<section style="padding:48px 20px;text-align:center;background:var(--color-brand-navy);color:var(--color-text-inverse)"><h1 style="font-size:28px;font-weight:700;margin:0 0 12px">Implantes de Alta Precisão com Protocolo Guiado</h1><p style="font-size:15px;max-width:600px;margin:0 auto 20px">Planejamento digital, osso D1-D4 e entrega Same-Day DENTGO Express.</p><a href="#captura" style="display:inline-block;padding:10px 22px;border-radius:6px;background:var(--color-brand-primary);color:var(--color-text-inverse);text-decoration:none;font-weight:600">Quero conhecer o protocolo</a></section>`,
    },
    {
      id: "cfo",
      label: "Banner Ético CFO 196/2019",
      html: `<div class="cfo-banner" style="padding:12px;background:var(--color-surface-bg);border-top:2px solid var(--color-brand-primary);font-size:12px;text-align:center;color:var(--color-text-secondary)"><p style="margin:0">Responsável Técnico: ${cfoName} - ${cfoCro} | Conforme Resolução CFO 196/2019 e Art. 43 do CEO</p></div>`,
    },
    {
      id: "torque",
      label: "Tabela de Torques ANVISA",
      html: `<section style="padding:28px 20px"><h2 style="font-size:20px;margin:0 0 12px">Torques de Inserção Recomendados</h2><table style="width:100%;border-collapse:collapse;font-size:14px"><thead><tr style="background:var(--color-surface-bg)"><th style="text-align:left;padding:8px;border:1px solid var(--color-border)">Densidade óssea</th><th style="text-align:left;padding:8px;border:1px solid var(--color-border)">Torque (Ncm)</th><th style="text-align:left;padding:8px;border:1px solid var(--color-border)">Registro ANVISA</th></tr></thead><tbody><tr><td style="padding:8px;border:1px solid var(--color-border)">D1</td><td style="padding:8px;border:1px solid var(--color-border)">45 - 60</td><td style="padding:8px;border:1px solid var(--color-border)">Conforme IFU</td></tr><tr><td style="padding:8px;border:1px solid var(--color-border)">D2-D3</td><td style="padding:8px;border:1px solid var(--color-border)">35 - 45</td><td style="padding:8px;border:1px solid var(--color-border)">Conforme IFU</td></tr><tr><td style="padding:8px;border:1px solid var(--color-border)">D4</td><td style="padding:8px;border:1px solid var(--color-border)">20 - 35</td><td style="padding:8px;border:1px solid var(--color-border)">Conforme IFU</td></tr></tbody></table></section>`,
    },
    {
      id: "casos",
      label: "Galeria de Casos Clínicos com TCLE",
      html: `<section style="padding:28px 20px"><h2 style="font-size:20px;margin:0 0 12px">Casos Clínicos</h2><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px"><figure style="margin:0;padding:12px;border:1px solid var(--color-border);border-radius:8px"><div style="height:110px;background:var(--color-brand-navy-subtle);border-radius:6px"></div><figcaption style="font-size:12px;margin-top:6px">Caso 01 - Reabilitação unitária</figcaption></figure><figure style="margin:0;padding:12px;border:1px solid var(--color-border);border-radius:8px"><div style="height:110px;background:var(--color-brand-navy-subtle);border-radius:6px"></div><figcaption style="font-size:12px;margin-top:6px">Caso 02 - Protocolo total</figcaption></figure></div><p style="font-size:11px;color:var(--color-text-muted);margin:10px 0 0">Imagens publicadas com Termo de Consentimento Livre e Esclarecido (TCLE) assinado pelo paciente. Resultados individuais variam.</p></section>`,
    },
    {
      id: "form",
      label: "Formulário de Captura CRO/UF",
      html: `<section id="captura" style="padding:28px 20px;background:var(--color-surface-bg)"><h2 style="font-size:20px;margin:0 0 12px">Receba o material técnico</h2><form onsubmit="return false" style="display:grid;gap:10px;max-width:420px"><input name="name" placeholder="Nome do cirurgião" style="padding:8px 12px;border:1px solid var(--color-border);border-radius:6px" /><input name="email" placeholder="E-mail" style="padding:8px 12px;border:1px solid var(--color-border);border-radius:6px" /><input name="phone" placeholder="WhatsApp" style="padding:8px 12px;border:1px solid var(--color-border);border-radius:6px" /><input name="cro" placeholder="CRO/UF (ex.: CRO-SP 123456)" style="padding:8px 12px;border:1px solid var(--color-border);border-radius:6px" /><button type="submit" style="padding:10px;border:0;border-radius:6px;background:var(--color-brand-primary);color:var(--color-text-inverse);font-weight:600">Enviar</button></form></section>`,
    },
    {
      id: "kol",
      label: "Depoimentos KOL",
      html: `<section style="padding:28px 20px"><h2 style="font-size:20px;margin:0 0 12px">Quem usa recomenda</h2><blockquote style="margin:0;padding:14px;border-left:4px solid var(--color-brand-primary);background:var(--color-brand-primary-subtle);font-size:14px">"O fluxo digital reduziu o tempo cirúrgico e deu previsibilidade ao protocolo."<footer style="margin-top:6px;font-size:12px;color:var(--color-text-secondary)">Dr. Especialista - CRO-SP 000000 (opinião pessoal)</footer></blockquote></section>`,
    },
  ];

  const appendBlock = (html: string) => {
    const next = `${editorHtml}\n${html}`;
    setEditorHtml(next);
    setRenderedHtml(next);
  };

  // Auto-correção determinística da copy conforme CFO 196/2019 (sem LLM)
  const autoFixCopyCfo = () => {
    const rules: Array<[RegExp, string, string]> = [
      [/resultados? garantidos?/gi, "resultados individuais variam", "promessa de resultado"],
      [/100% (?:de )?(?:sucesso|garantido|seguro)/gi, "alta previsibilidade clínica", "garantia absoluta"],
      [/o melhor (?:implante )?do (?:brasil|mundo)/gi, "tecnologia com registro ANVISA", "autopromoção superlativa"],
      [/sem (?:nenhum )?risco/gi, "com riscos informados no TCLE", "ausência de risco"],
      [/antes e depois/gi, "caso clínico (com TCLE)", "antes/depois sem consentimento"],
      [/promoção imperdível|preço de banana|desconto imperdível/gi, "condições comerciais informadas", "apelo mercantilista"],
    ];
    const log: string[] = [];
    let out = editorHtml;
    for (const [re, repl, why] of rules) {
      if (re.test(out)) {
        re.lastIndex = 0;
        out = out.replace(re, repl);
        log.push(`Substituído: ${why}`);
      }
      re.lastIndex = 0;
    }
    if (!/cfo-banner|Resolução CFO 196\/2019/i.test(out)) {
      out += `\n${dentalBlocks[1].html}`;
      log.push("Adicionado banner de Responsável Técnico CFO 196/2019");
    }
    if (log.length === 0) log.push("Copy já conforme: nenhuma alteração necessária.");
    applyContent(out, editorCss);
    setCopyFixLog(log);
  };

  const iframeScript = `(function(){var root=document.getElementById('lp-root');if(!root)return;var sel='h1,h2,h3,h4,p,li,td,th,label,figcaption,blockquote,footer,a,button';root.querySelectorAll(sel).forEach(function(el){el.setAttribute('contenteditable','true');el.style.outline='none'});function send(){var c=root.cloneNode(true);c.querySelectorAll('[contenteditable]').forEach(function(e){e.removeAttribute('contenteditable')});parent.postMessage({type:'lp-inline-edit',html:c.innerHTML},'*')}root.addEventListener('input',send);root.addEventListener('click',function(e){var a=e.target.closest('a');if(a)e.preventDefault()})})();`;

  const previewDoc = `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>${tokenCss}</style><style>${editorCss}</style></head><body><div id="lp-root">${renderedHtml}</div><script>${iframeScript}</script></body></html>`;

  const viewportWidth = viewport === "desktop" ? "100%" : viewport === "tablet" ? "768px" : "375px";

  // Ações Tab 1: Salvar & Publicar
  const handleCreateLandingPage = async () => {
    setIsSaving(true);
    setCfoStatus(null);
    try {
      const html = editorHtml;
      const css = editorCss;

      const payload = {
        title,
        slug: slug || `lp-${Date.now()}`,
        html,
        css,
        cfo_cro: cfoCro,
        cfo_name: cfoName,
        campaign_id: activeCampaignId,
        account_id: "0f14ffff",
      };

      const res = await fetch("/api/v1/campaigns/landing-pages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Erro ao criar landing page.");
      }

      const saved = await res.json();
      setCurrentId(saved.id);
      setCfoStatus(saved.cfo_compliance_status || "COMPLIANT");
      await fetchLandingPages();
    } catch (e: any) {
      alert(e.message || "Falha ao criar landing page");
    } finally {
      setIsSaving(false);
    }
  };

  const handleUpdateLandingPage = async () => {
    if (!currentId) {
      return handleCreateLandingPage();
    }
    setIsSaving(true);
    setCfoStatus(null);
    try {
      const html = editorHtml;
      const css = editorCss;

      const payload = {
        title,
        slug,
        html,
        css,
        cfo_cro: cfoCro,
        cfo_name: cfoName,
      };

      const res = await fetch(`/api/v1/campaigns/landing-pages/${currentId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Erro ao atualizar landing page.");
      }

      const saved = await res.json();
      setCfoStatus(saved.cfo_compliance_status || "COMPLIANT");
      await fetchLandingPages();
    } catch (e: any) {
      alert(e.message || "Falha ao atualizar landing page");
    } finally {
      setIsSaving(false);
    }
  };

  const handleSavePage = async () => {
    if (currentId) {
      await handleUpdateLandingPage();
    } else {
      await handleCreateLandingPage();
    }
  };

  const handlePublishPage = async () => {
    if (!currentId) {
      await handleSavePage();
    }
    setIsPublishing(true);
    try {
      const pageToPublish = currentId || "lp-demo-01";
      const res = await fetch(`/api/v1/campaigns/landing-pages/${pageToPublish}/publish`, {
        method: "PUT",
      });
      if (!res.ok) throw new Error("Erro na publicação no R2");
      const result = await res.json();
      setPublishedUrl(result.published_url);
      if (onPublished) onPublished(result.published_url);
      await fetchLandingPages();
    } catch (e: any) {
      alert(e.message || "Erro na publicação");
    } finally {
      setIsPublishing(false);
    }
  };

  // Teste de Submissão Pública de Lead
  const handleTestSubmitLead = async (e: React.FormEvent) => {
    e.preventDefault();
    setTestLeadFeedback(null);
    try {
      const res = await fetch(`/api/v1/campaigns/public/lp/${encodeURIComponent(slug)}/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: testLeadName,
          email: testLeadEmail,
          phone: testLeadPhone,
          cro: testLeadCro,
        }),
      });
      if (!res.ok) throw new Error("Falha ao registrar lead público");
      const data = await res.json();
      setTestLeadFeedback(`Lead recebido com sucesso! Contact ID: ${data.contact_id || "Registrado"}`);
    } catch (err: any) {
      setTestLeadFeedback(`Erro: ${err.message}`);
    }
  };

  // Ações Tab 2: Listmonk & Mautic
  const handleDispatchListmonk = async (e: React.FormEvent) => {
    e.preventDefault();
    setDispatchingBroadcast(true);
    setBroadcastResult(null);
    try {
      const res = await fetch("/api/v1/campaigns/broadcast-listmonk", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: broadcastTitle,
          subject: broadcastSubject,
          body_html: broadcastHtml,
          target_uf: broadcastUf,
          target_specialty: broadcastSpecialty,
        }),
      });
      if (!res.ok) throw new Error("Falha no disparo Listmonk");
      const data = await res.json();
      setBroadcastResult(data);
    } catch (err: any) {
      setBroadcastResult({ error: err.message });
    } finally {
      setDispatchingBroadcast(false);
    }
  };

  const handleSimulateListmonkWebhook = async () => {
    setSimulatingWebhook(true);
    try {
      const res = await fetch("/api/v1/campaigns/webhooks/listmonk", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          event: "campaign.open",
          subscriber_email: "cirurgiao.vip@clinica.com.br",
          campaign_id: "listmonk-camp-01",
        }),
      });
      const data = await res.json();
      setWebhookResult(data);
    } catch (err: any) {
      setWebhookResult({ error: err.message });
    } finally {
      setSimulatingWebhook(false);
    }
  };

  const handleSimulateMauticAction = async () => {
    try {
      const res = await fetch("/api/v1/webhooks/mautic/campaign-action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "send_whatsapp",
          contact: {
            id: 1,
            name: "Dr. Roberto Silveira",
            phone: "+5511999998888",
            cro: "CRO-SP-54321",
          },
          template: "Olá {{contact.name}}, seu kit de teste All-on-4 está disponível para envio express.",
        }),
      });
      const data = await res.json();
      alert(`Mautic Action disparada! Shard Evolution: ${data.instance_name || "OK"}`);
    } catch (err: any) {
      alert(`Erro: ${err.message}`);
    }
  };

  const handleToggleFlow = async (flowId: string) => {
    try {
      const res = await fetch(`/api/v1/automations/flows/${flowId}/toggle`, {
        method: "PUT",
      });
      if (res.ok) {
        await fetchAutomations();
      }
    } catch {
      // fallback
    }
  };

  const handleTestFlow = async (flowId: string) => {
    try {
      const res = await fetch(`/api/v1/automations/flows/${flowId}/test`, {
        method: "POST",
      });
      if (res.ok) {
        await fetchAutomations();
      }
    } catch {
      // fallback
    }
  };

  // Ações Tab 3: MGM Referral
  const handleGenerateReferralLink = async () => {
    try {
      const res = await fetch("/api/v1/campaigns/referral/generate-link", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          referrer_id: referrerId,
          referrer_name: referrerName,
          referrer_cro_uf: referrerCro,
          account_id: "0f14ffff",
        }),
      });
      if (!res.ok) throw new Error("Erro ao gerar link MGM");
      const data = await res.json();
      setReferralLinkData(data);
      await fetchMgmDashboard();
    } catch (err: any) {
      alert(err.message || "Erro");
    }
  };

  const handleRegisterReferred = async (e: React.FormEvent) => {
    e.preventDefault();
    setRegisterResult(null);
    try {
      const res = await fetch("/api/v1/campaigns/referral/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          referral_code: referralLinkData?.referral_code || `MGM-${referrerCro}`,
          referred_name: referredName,
          referred_phone: referredPhone,
          referred_cro_uf: referredCro,
          referred_email: referredEmail,
          account_id: "0f14ffff",
        }),
      });
      if (!res.ok) throw new Error("Falha no cadastro do colega indicado");
      const data = await res.json();
      setRegisterResult(data);
      await fetchMgmDashboard();
    } catch (err: any) {
      setRegisterResult({ error: err.message });
    }
  };

  const handleQualifyDealWon = async () => {
    setQualifyResult(null);
    try {
      const res = await fetch("/api/v1/campaigns/referral/qualify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          deal_id: qualifyDealId,
          account_id: "0f14ffff",
        }),
      });
      if (!res.ok) throw new Error("Falha ao qualificar bonificação MGM");
      const data = await res.json();
      setQualifyResult(data);
      await fetchMgmDashboard();
    } catch (err: any) {
      setQualifyResult({ error: err.message });
    }
  };

  // Nova régua de automação
  const [newFlowName, setNewFlowName] = useState("");
  const [newFlowCategory, setNewFlowCategory] = useState("NURTURING");
  const [newFlowTrigger, setNewFlowTrigger] = useState("lead.created");
  const [newFlowAction, setNewFlowAction] = useState("");
  const [newFlowHtml, setNewFlowHtml] = useState("");
  const [newFlowFeedback, setNewFlowFeedback] = useState<string | null>(null);

  const emailPresets = [
    {
      id: "boas-vindas",
      name: "Boas-vindas ao Cirurgião",
      trigger: "lead.created",
      subject: "Seu material técnico de implantodontia",
      action: "Enviar e-mail de boas-vindas com material técnico",
      html: `<h2 style="color:var(--color-brand-navy)">Olá, Dr(a)!</h2><p>Recebemos seu interesse. Segue o material técnico do protocolo guiado.</p><p style="font-size:11px;color:var(--color-text-muted)">Conforme Resolução CFO 196/2019.</p>`,
    },
    {
      id: "reativacao",
      name: "Reativação 90 dias",
      trigger: "contact.inactive_90d",
      subject: "Novidades para o seu consultório",
      action: "Reativar cirurgiões sem pedido há 90 dias",
      html: `<h2 style="color:var(--color-brand-navy)">Sentimos sua falta</h2><p>Há novidades no catálogo cirúrgico e na entrega Same-Day DENTGO Express.</p>`,
    },
    {
      id: "pos-venda",
      name: "Pós-venda e Rastreabilidade",
      trigger: "deal.won",
      subject: "Rastreabilidade do seu lote",
      action: "Enviar etiqueta de rastreabilidade ANVISA pós-venda",
      html: `<h2 style="color:var(--color-brand-navy)">Pedido confirmado</h2><p>O registro de rastreabilidade do lote está disponível na sua área.</p>`,
    },
  ];

  const handleCreateFlow = async (e: React.FormEvent) => {
    e.preventDefault();
    setNewFlowFeedback(null);
    try {
      const res = await fetch("/api/v1/automations/flows", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: newFlowName,
          category: newFlowCategory,
          trigger_event: newFlowTrigger,
          action_description: newFlowAction,
          email_html: newFlowHtml,
          is_active: true,
          account_id: "0f14ffff",
        }),
      });
      if (!res.ok) throw new Error("Falha ao criar régua de automação");
      setNewFlowFeedback("Régua criada com sucesso.");
      setNewFlowName("");
      await fetchAutomations();
    } catch (err: any) {
      setNewFlowFeedback(`Erro: ${err.message}`);
    }
  };

  return (
    <div className="space-y-4">
      <RouteHeader
        title="Campanhas e Indicações"
        description="Criação de páginas para captação de clientes, réguas de automação e programa de indicações."
        badge={
          <Badge variant="outline" className="border-brand-primary/30 text-brand-primary bg-brand-primary-subtle text-xs">
            Páginas, E-mails & Indicações
          </Badge>
        }
      />

      {/* Main Tabs Navigation */}
      <Tabs
        activeTab={activeMainTab}
        onChange={(tabId) => setActiveMainTab(tabId)}
        tabs={[
          { id: "builder", label: "Páginas de Captura" },
          { id: "automations", label: "Disparo de E-mails & Mensagens Automáticas", count: flows.length },
          { id: "referral", label: "Programa de Indicações", count: mgmDashboard?.total_referrals },
        ]}
      />

      {/* ========================================================================= */}
      {/* TAB 1: ESTÚDIO VISUAL DE LANDING PAGE & R2 */}
      {/* ========================================================================= */}
      {activeMainTab === "builder" && (
        <div className="space-y-4">
          {/* Barra de Seleção e Ações de LP */}
          <Card className="p-3 bg-surface-card border border-border flex flex-wrap items-center justify-between gap-3">
            <div className="flex flex-wrap items-center gap-3 flex-1 min-w-[280px]">
              <div>
                <label className="text-[11px] font-semibold text-text-secondary block">
                  Página Salva / Selecionada
                </label>
                <select
                  value={currentId || ""}
                  onChange={(e) => loadSavedPage(e.target.value)}
                  className="px-2.5 py-1.5 rounded-lg border border-border bg-surface-bg text-xs font-mono text-text-main"
                >
                  <option value="">+ Criar Nova Landing Page</option>
                  {savedPages.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.title} ({p.slug}) {p.is_published ? "[PUBLICADA]" : "[RASCUNHO]"}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex-1 min-w-[160px]">
                <label className="text-[11px] font-semibold text-text-secondary block">Título da LP</label>
                <Input
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="h-8 text-xs"
                  placeholder="Título da página"
                />
              </div>

              <div className="w-44">
                <label className="text-[11px] font-semibold text-text-secondary block">Slug Único</label>
                <Input
                  value={slug}
                  onChange={(e) => setSlug(e.target.value)}
                  className="h-8 text-xs font-mono"
                  placeholder="slug-da-pagina"
                />
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleCreateLandingPage}
                disabled={isSaving}
                className="flex items-center gap-1.5 text-xs"
              >
                {isSaving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Plus className="w-3.5 h-3.5" />}
                Nova LP (POST)
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleUpdateLandingPage}
                disabled={isSaving}
                className="flex items-center gap-1.5 text-xs"
              >
                {isSaving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />}
                Salvar HTML/CSS (PUT)
              </Button>
              <Button
                variant="default"
                size="sm"
                onClick={handlePublishPage}
                disabled={isPublishing}
                className="flex items-center gap-1.5 text-xs"
              >
                {isPublishing ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <UploadCloud className="w-3.5 h-3.5" />}
                Publicar no R2
              </Button>
            </div>
          </Card>

          {/* CFO Badge & Compliance Bar */}
          <div className="p-3 bg-surface-bg border border-border rounded-xl flex flex-wrap items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-2">
              <ShieldCheck className="h-4 w-4 text-status-success" />
              <span className="font-semibold text-text-main">Conformidade CFO 196/2019:</span>
              <span className="font-mono text-text-secondary">{cfoName} ({cfoCro})</span>
              {cfoStatus && (
                <Badge variant={cfoStatus === "COMPLIANT" ? "success" : "warning"} className="text-[10px]">
                  {cfoStatus}
                </Badge>
              )}
            </div>

            {publishedUrl && (
              <div className="flex items-center gap-2 font-mono text-status-success">
                <span>R2 URL:</span>
                <a href={publishedUrl} target="_blank" rel="noreferrer" className="underline truncate max-w-xs">
                  {publishedUrl}
                </a>
              </div>
            )}
          </div>

          {/* Estúdio Visual de Landing Page (self-contained) */}
          <div className="flex flex-col lg:flex-row gap-4 min-h-[480px]">
            {/* Sidebar de Templates & Paleta de Blocos */}
            <div className="w-full lg:w-64 bg-surface-card border border-border rounded-xl p-3 space-y-3">
              <div>
                <span className="text-xs font-bold text-text-main flex items-center gap-1 mb-2">
                  <Sparkles className="h-3.5 w-3.5 text-brand-primary" />
                  Templates Odontológicos
                </span>
                <div className="space-y-1">
                  {templates.map((tpl) => (
                    <button
                      key={tpl.template_type}
                      onClick={() => loadTemplate(tpl)}
                      className={`w-full text-left p-2 rounded-lg border text-xs transition ${
                        selectedTemplate === tpl.template_type
                          ? "border-brand-primary bg-brand-primary-subtle text-brand-primary font-semibold"
                          : "border-border bg-surface-bg text-text-secondary hover:text-text-main"
                      }`}
                    >
                      <div className="font-semibold truncate">{tpl.name}</div>
                      <div className="text-[10px] text-text-muted truncate">{tpl.description}</div>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <span className="text-xs font-bold text-text-main block mb-1">Paleta de Blocos Odontológicos</span>
                <div className="space-y-1.5">
                  {dentalBlocks.map((b) => (
                    <button
                      key={b.id}
                      type="button"
                      onClick={() => appendBlock(b.html)}
                      className="w-full flex items-center gap-1.5 text-left p-2 rounded-lg border border-border bg-surface-bg text-xs text-text-secondary hover:text-text-main hover:border-brand-primary transition"
                    >
                      <Plus className="h-3 w-3 text-brand-primary shrink-0" />
                      <span className="truncate">{b.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              <div className="space-y-1.5 pt-2 border-t border-border">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={autoFixCopyCfo}
                  className="w-full flex items-center justify-center gap-1.5 text-xs"
                >
                  <Wand2 className="h-3.5 w-3.5 text-brand-primary" />
                  Auto-Corrigir Copy CFO 196/2019
                </Button>
                <Button
                  type="button"
                  variant={abTestEnabled ? "default" : "outline"}
                  size="sm"
                  onClick={() => {
                    if (!abTestEnabled) {
                      setAbVariantA(editorHtml);
                      setAbVariantB(editorHtml);
                      setShowAbModal(true);
                    }
                    setAbTestEnabled(!abTestEnabled);
                  }}
                  className="w-full flex items-center justify-center gap-1.5 text-xs"
                >
                  <FlaskConical className="h-3.5 w-3.5 text-brand-navy" />
                  {abTestEnabled ? "A/B Ativo (Split 50/50)" : "Ativar Teste A/B (Split 50/50)"}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => applyContent("", editorCss)}
                  className="w-full flex items-center justify-center gap-1.5 text-xs"
                >
                  <Trash2 className="h-3.5 w-3.5 text-status-danger" />
                  Limpar Canvas
                </Button>
                {copyFixLog.length > 0 && (
                  <ul className="text-[10px] text-text-secondary bg-status-success-subtle border border-status-success/30 rounded p-2 space-y-0.5">
                    {copyFixLog.map((l, i) => (
                      <li key={i}>{l}</li>
                    ))}
                  </ul>
                )}
              </div>
            </div>

            {/* Canvas: Preview Visual Interativo / Editor de Código */}
            <div className="flex-1 bg-surface-card border border-border rounded-xl p-3 flex flex-col gap-2 min-w-0">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-1">
                  {([
                    { id: "desktop", label: "Desktop 100%", Icon: Monitor },
                    { id: "tablet", label: "Tablet 768px", Icon: Tablet },
                    { id: "mobile", label: "Mobile 375px", Icon: Smartphone },
                  ] as const).map(({ id, label, Icon }) => (
                    <button
                      key={id}
                      type="button"
                      onClick={() => setViewport(id)}
                      className={`flex items-center gap-1 px-2 py-1 rounded-lg border text-[11px] ${
                        viewport === id
                          ? "border-brand-primary bg-brand-primary-subtle text-brand-primary font-semibold"
                          : "border-border bg-surface-bg text-text-secondary"
                      }`}
                    >
                      <Icon className="h-3.5 w-3.5" />
                      {label}
                    </button>
                  ))}
                </div>

                <div className="flex items-center gap-1">
                  <button
                    type="button"
                    onClick={() => {
                      setRenderedHtml(editorHtml);
                      setEditorMode("visual");
                    }}
                    className={`flex items-center gap-1 px-2 py-1 rounded-lg border text-[11px] ${
                      editorMode === "visual"
                        ? "border-brand-primary bg-brand-primary-subtle text-brand-primary font-semibold"
                        : "border-border bg-surface-bg text-text-secondary"
                    }`}
                  >
                    <Eye className="h-3.5 w-3.5" />
                    Preview Visual Interativo
                  </button>
                  <button
                    type="button"
                    onClick={() => setEditorMode("code")}
                    className={`flex items-center gap-1 px-2 py-1 rounded-lg border text-[11px] ${
                      editorMode === "code"
                        ? "border-brand-primary bg-brand-primary-subtle text-brand-primary font-semibold"
                        : "border-border bg-surface-bg text-text-secondary"
                    }`}
                  >
                    <Code2 className="h-3.5 w-3.5" />
                    Editor de Código HTML/CSS
                  </button>
                  <a
                    href={`/lp/${slug}`}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-1 px-2 py-1 rounded-lg border border-border bg-surface-bg text-[11px] text-brand-primary underline"
                  >
                    <ExternalLink className="h-3.5 w-3.5" />
                    /lp/{slug}
                  </a>
                </div>
              </div>

              {editorMode === "visual" ? (
                <div className="flex-1 bg-surface-bg rounded-lg border border-border overflow-auto flex justify-center p-2 min-h-[420px]">
                  <iframe
                    title="Preview da Landing Page"
                    srcDoc={previewDoc}
                    sandbox="allow-scripts"
                    style={{ width: viewportWidth, maxWidth: "100%" }}
                    className="bg-surface-card border border-border rounded min-h-[420px] h-full transition-all"
                  />
                </div>
              ) : (
                <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-2 min-h-[420px]">
                  <div className="flex flex-col">
                    <label className="text-[11px] font-semibold text-text-secondary mb-1">HTML</label>
                    <textarea
                      value={editorHtml}
                      onChange={(e) => setEditorHtml(e.target.value)}
                      spellCheck={false}
                      className="flex-1 min-h-[400px] p-2 rounded-lg border border-border bg-surface-bg text-[11px] text-text-main font-mono"
                    />
                  </div>
                  <div className="flex flex-col">
                    <label className="text-[11px] font-semibold text-text-secondary mb-1">CSS</label>
                    <textarea
                      value={editorCss}
                      onChange={(e) => setEditorCss(e.target.value)}
                      spellCheck={false}
                      className="flex-1 min-h-[400px] p-2 rounded-lg border border-border bg-surface-bg text-[11px] text-text-main font-mono"
                    />
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Simulador de Captura Pública de Leads */}
          <Card className="p-4 border border-border bg-surface-card space-y-3">
            <div className="flex items-center justify-between border-b border-border pb-2">
              <h3 className="text-xs font-bold text-text-main flex items-center gap-1.5">
                <Users className="h-4 w-4 text-brand-primary" />
                Simulador de Captura Pública de Lead (Página Publicada)
              </h3>
              <span className="text-[10px] text-text-muted font-mono">
                Endpoint: POST /api/v1/campaigns/public/lp/{slug}/submit
              </span>
            </div>

            <form onSubmit={handleTestSubmitLead} className="grid grid-cols-1 sm:grid-cols-4 gap-2">
              <Input
                placeholder="Nome do Cirurgião"
                value={testLeadName}
                onChange={(e) => setTestLeadName(e.target.value)}
                className="text-xs"
                required
              />
              <Input
                placeholder="E-mail"
                value={testLeadEmail}
                onChange={(e) => setTestLeadEmail(e.target.value)}
                className="text-xs"
                required
              />
              <Input
                placeholder="WhatsApp (E.164)"
                value={testLeadPhone}
                onChange={(e) => setTestLeadPhone(e.target.value)}
                className="text-xs"
                required
              />
              <div className="flex gap-2">
                <Input
                  placeholder="CRO/UF"
                  value={testLeadCro}
                  onChange={(e) => setTestLeadCro(e.target.value)}
                  className="text-xs"
                  required
                />
                <Button type="submit" variant="default" size="sm" className="text-xs whitespace-nowrap">
                  Simular Lead
                </Button>
              </div>
            </form>

            {testLeadFeedback && (
              <p className="text-xs text-status-success font-mono bg-status-success-subtle p-2 rounded border border-status-success/30">
                {testLeadFeedback}
              </p>
            )}
          </Card>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 2: DISPARO EM MASSA LISTMONK & AUTOMAÇÃO MAUTIC */}
      {/* ========================================================================= */}
      {activeMainTab === "automations" && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Form de Disparo em Massa Listmonk */}
            <Card className="p-4 border border-border bg-surface-card space-y-3">
              <div className="flex items-center justify-between border-b border-border pb-2">
                <h3 className="text-xs font-bold text-text-main flex items-center gap-1.5">
                  <Mail className="h-4 w-4 text-brand-primary" />
                  Disparo em Massa de E-mails via Listmonk Engine
                </h3>
                <Badge variant="outline" className="text-[10px]">
                  Engine SMTP / API
                </Badge>
              </div>

              <form onSubmit={handleDispatchListmonk} className="space-y-2.5">
                <div>
                  <label className="text-[11px] font-semibold text-text-secondary block mb-1">
                    Nome Interno da Campanha
                  </label>
                  <Input
                    value={broadcastTitle}
                    onChange={(e) => setBroadcastTitle(e.target.value)}
                    className="text-xs"
                    required
                  />
                </div>

                <div>
                  <label className="text-[11px] font-semibold text-text-secondary block mb-1">
                    Assunto do E-mail
                  </label>
                  <Input
                    value={broadcastSubject}
                    onChange={(e) => setBroadcastSubject(e.target.value)}
                    className="text-xs"
                    required
                  />
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-[11px] font-semibold text-text-secondary block mb-1">
                      UF Alvo
                    </label>
                    <select
                      value={broadcastUf}
                      onChange={(e) => setBroadcastUf(e.target.value)}
                      className="w-full px-2.5 py-1.5 rounded-lg border border-border bg-surface-bg text-xs text-text-main"
                    >
                      <option value="SP">São Paulo (SP)</option>
                      <option value="RJ">Rio de Janeiro (RJ)</option>
                      <option value="MG">Minas Gerais (MG)</option>
                      <option value="PR">Paraná (PR)</option>
                      <option value="ALL">Todo o Brasil</option>
                    </select>
                  </div>

                  <div>
                    <label className="text-[11px] font-semibold text-text-secondary block mb-1">
                      Especialidade Alvo
                    </label>
                    <select
                      value={broadcastSpecialty}
                      onChange={(e) => setBroadcastSpecialty(e.target.value)}
                      className="w-full px-2.5 py-1.5 rounded-lg border border-border bg-surface-bg text-xs text-text-main"
                    >
                      <option value="Implantodontia">Implantodontia</option>
                      <option value="Periodontia">Periodontia</option>
                      <option value="Cirurgia Bucomaxilo">Cirurgia Bucomaxilo</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="text-[11px] font-semibold text-text-secondary block mb-1">
                    Corpo do E-mail (HTML)
                  </label>
                  <textarea
                    value={broadcastHtml}
                    onChange={(e) => setBroadcastHtml(e.target.value)}
                    rows={3}
                    className="w-full p-2 rounded-lg border border-border bg-surface-bg text-xs text-text-main font-mono"
                    required
                  />
                </div>

                <div className="flex items-center justify-between pt-2">
                  <button
                    type="button"
                    onClick={handleSimulateListmonkWebhook}
                    disabled={simulatingWebhook}
                    className="text-[11px] text-text-secondary hover:text-text-main underline"
                  >
                    {simulatingWebhook ? "Simulando webhook..." : "Simular Webhook (Open/Click)"}
                  </button>

                  <Button type="submit" variant="default" size="sm" disabled={dispatchingBroadcast} className="text-xs">
                    <Send className="h-3.5 w-3.5 mr-1" />
                    {dispatchingBroadcast ? "Enfileirando..." : "Disparar Campanha"}
                  </Button>
                </div>
              </form>

              {broadcastResult && (
                <div className="p-2.5 rounded-lg bg-surface-bg border border-border text-xs font-mono">
                  <div className="text-status-success font-semibold">Disparo enfileirado com sucesso:</div>
                  <pre className="text-[10px] text-text-secondary mt-1 overflow-x-auto">
                    {JSON.stringify(broadcastResult, null, 2)}
                  </pre>
                </div>
              )}
            </Card>

            {/* Simulador de Ação de Campanha Mautic */}
            <Card className="p-4 border border-border bg-surface-card space-y-3">
              <div className="flex items-center justify-between border-b border-border pb-2">
                <h3 className="text-xs font-bold text-text-main flex items-center gap-1.5">
                  <Zap className="h-4 w-4 text-status-warning" />
                  Ponte Híbrida Mautic & Despacho Dinâmico Evolution
                </h3>
                <Badge variant="outline" className="text-[10px]">
                  Webhook Inbound
                </Badge>
              </div>

              <p className="text-xs text-text-secondary">
                Roteia automações do Mautic para a instância WhatsApp Evolution do consultor responsável com injeção de variáveis cirúrgicas.
              </p>

              <div className="p-3 bg-surface-bg border border-border rounded-lg space-y-2 text-xs">
                <div className="font-semibold text-text-main">Ação Padrão Cadastrada:</div>
                <div className="font-mono text-[11px] text-brand-primary">send_whatsapp_template</div>
                <div className="text-[11px] text-text-muted">
                  Dispara template All-on-4 com link de agendamento profilático Cal.com.
                </div>
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleSimulateMauticAction}
                  className="flex items-center gap-1.5 text-xs"
                >
                  <Play className="h-3.5 w-3.5 text-brand-primary" />
                  Simular Trigger de Campanha Mautic
                </Button>
              </div>

              {webhookResult && (
                <div className="p-2.5 rounded-lg bg-surface-bg border border-border text-xs font-mono">
                  <div className="text-status-success font-semibold">Resultado do Webhook Listmonk:</div>
                  <pre className="text-[10px] text-text-secondary mt-1 overflow-x-auto">
                    {JSON.stringify(webhookResult, null, 2)}
                  </pre>
                </div>
              )}
            </Card>
          </div>

          {/* Nova Régua de Automação + Preview de E-mail */}
          <Card className="p-4 border border-border bg-surface-card space-y-3">
            <div className="flex items-center justify-between border-b border-border pb-2">
              <h3 className="text-xs font-bold text-text-main flex items-center gap-1.5">
                <Plus className="h-4 w-4 text-brand-primary" />
                + Nova Régua de Automação
              </h3>
              <Badge variant="outline" className="text-[10px]">
                POST /api/v1/automations/flows
              </Badge>
            </div>

            <div className="flex flex-wrap gap-1.5">
              {emailPresets.map((p) => (
                <button
                  key={p.id}
                  type="button"
                  onClick={() => {
                    setNewFlowName(p.name);
                    setNewFlowTrigger(p.trigger);
                    setNewFlowAction(p.action);
                    setNewFlowHtml(p.html);
                    setBroadcastSubject(p.subject);
                    setBroadcastHtml(p.html);
                  }}
                  className="px-2 py-1 rounded-lg border border-border bg-surface-bg text-[11px] text-text-secondary hover:text-text-main hover:border-brand-primary"
                >
                  {p.name}
                </button>
              ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <form onSubmit={handleCreateFlow} className="space-y-2">
                <Input
                  value={newFlowName}
                  onChange={(e) => setNewFlowName(e.target.value)}
                  placeholder="Nome da régua"
                  className="text-xs"
                  required
                />
                <div className="grid grid-cols-2 gap-2">
                  <select
                    value={newFlowCategory}
                    onChange={(e) => setNewFlowCategory(e.target.value)}
                    className="px-2.5 py-1.5 rounded-lg border border-border bg-surface-bg text-xs text-text-main"
                  >
                    <option value="NURTURING">Nutrição</option>
                    <option value="REACTIVATION">Reativação</option>
                    <option value="ONBOARDING">Onboarding</option>
                    <option value="POST_SALE">Pós-venda</option>
                  </select>
                  <Input
                    value={newFlowTrigger}
                    onChange={(e) => setNewFlowTrigger(e.target.value)}
                    placeholder="Gatilho (ex.: lead.created)"
                    className="text-xs font-mono"
                    required
                  />
                </div>
                <Input
                  value={newFlowAction}
                  onChange={(e) => setNewFlowAction(e.target.value)}
                  placeholder="Descrição da ação"
                  className="text-xs"
                  required
                />
                <textarea
                  value={newFlowHtml}
                  onChange={(e) => setNewFlowHtml(e.target.value)}
                  rows={5}
                  className="w-full p-2 rounded-lg border border-border bg-surface-bg text-xs text-text-main font-mono"
                  placeholder="HTML do e-mail"
                />
                <div className="flex items-center justify-between">
                  {newFlowFeedback ? (
                    <span className="text-[11px] text-text-secondary">{newFlowFeedback}</span>
                  ) : (
                    <span />
                  )}
                  <Button type="submit" variant="default" size="sm" className="text-xs">
                    Criar Régua
                  </Button>
                </div>
              </form>

              <div className="border border-border rounded-lg overflow-hidden bg-surface-bg">
                <div className="px-2 py-1 text-[10px] font-semibold text-text-secondary border-b border-border">
                  Preview do E-mail (ao vivo)
                </div>
                <iframe
                  title="Preview do E-mail"
                  sandbox=""
                  srcDoc={`<!doctype html><html><head><meta charset="utf-8"><style>${tokenCss}</style></head><body style="padding:12px;font-size:14px">${newFlowHtml || broadcastHtml}</body></html>`}
                  className="w-full h-56 bg-surface-card"
                />
              </div>
            </div>
          </Card>

          {/* Gerenciador de Fluxos de Automação (Automation Flows) */}
          <Card className="p-4 border border-border bg-surface-card space-y-3">
            <div className="flex items-center justify-between border-b border-border pb-2">
              <h3 className="text-xs font-bold text-text-main flex items-center gap-1.5">
                <Activity className="h-4 w-4 text-brand-primary" />
                Réguas de Automação Ativas ({flows.length}) — {logs.length} logs
              </h3>
              <Button variant="outline" size="sm" onClick={fetchAutomations} className="text-xs py-1 h-7">
                <RotateCw className="h-3 w-3 mr-1" />
                Atualizar
              </Button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="bg-surface-bg text-text-secondary uppercase text-[10px] border-b border-border">
                  <tr>
                    <th className="p-2">Fluxo</th>
                    <th className="p-2">Categoria</th>
                    <th className="p-2">Gatilho</th>
                    <th className="p-2">Execuções</th>
                    <th className="p-2">Status</th>
                    <th className="p-2 text-right">Ações</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {flows.map((f) => (
                    <tr key={f.id} className="hover:bg-surface-bg/50">
                      <td className="p-2 font-semibold text-text-main">{f.name}</td>
                      <td className="p-2 font-mono text-[10px] text-text-secondary">{f.category}</td>
                      <td className="p-2 font-mono text-[10px] text-brand-primary">{f.trigger_event}</td>
                      <td className="p-2 font-mono text-[11px]">{f.execution_count}</td>
                      <td className="p-2">
                        <span
                          className={`px-1.5 py-0.5 rounded text-[10px] font-semibold border whitespace-nowrap shrink-0 inline-block ${
                            f.is_active
                              ? "bg-status-success-subtle text-status-success border-status-success/30"
                              : "bg-surface-bg text-text-muted border-border"
                          }`}
                        >
                          {f.is_active ? "ATIVO" : "PAUSADO"}
                        </span>
                      </td>
                      <td className="p-2 text-right space-x-1.5">
                        <button
                          onClick={() => handleToggleFlow(f.id)}
                          className="px-2 py-1 rounded bg-surface-bg hover:bg-surface-card border border-border text-[11px]"
                        >
                          {f.is_active ? "Pausar" : "Ativar"}
                        </button>
                        <button
                          onClick={() => handleTestFlow(f.id)}
                          className="px-2 py-1 rounded bg-brand-primary text-text-inverse text-[11px] hover:bg-brand-primary-hover"
                        >
                          Testar
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 3: LOOP VIRAL B2B (MEMBER-GET-MEMBER — MGM) */}
      {/* ========================================================================= */}
      {activeMainTab === "referral" && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Coluna 1: Gerador de Link MGM do Cirurgião */}
            <Card className="p-4 border border-border bg-surface-card space-y-3">
              <div className="flex items-center justify-between border-b border-border pb-2">
                <h3 className="text-xs font-bold text-text-main flex items-center gap-1.5">
                  <Share2 className="h-4 w-4 text-brand-primary" />
                  Link Exclusivo do Embaixador KeyPartners
                </h3>
                <Badge variant="outline" className="text-[10px]">
                  MGM B2B
                </Badge>
              </div>

              <div className="space-y-2">
                <div>
                  <label className="text-[11px] font-semibold text-text-secondary block mb-1">
                    ID do Cirurgião Embaixador
                  </label>
                  <Input
                    value={referrerId}
                    onChange={(e) => setReferrerId(e.target.value)}
                    className="text-xs font-mono"
                  />
                </div>

                <div>
                  <label className="text-[11px] font-semibold text-text-secondary block mb-1">
                    Nome do Titular
                  </label>
                  <Input
                    value={referrerName}
                    onChange={(e) => setReferrerName(e.target.value)}
                    className="text-xs"
                  />
                </div>

                <div>
                  <label className="text-[11px] font-semibold text-text-secondary block mb-1">
                    CRO/UF
                  </label>
                  <Input
                    value={referrerCro}
                    onChange={(e) => setReferrerCro(e.target.value)}
                    className="text-xs font-mono"
                  />
                </div>

                <Button
                  onClick={handleGenerateReferralLink}
                  variant="default"
                  size="sm"
                  className="w-full text-xs mt-2"
                >
                  <LinkIcon className="h-3.5 w-3.5 mr-1" />
                  Gerar / Obter Link Único
                </Button>
              </div>

              {referralLinkData && (
                <div className="p-3 bg-brand-primary-subtle border border-brand-primary/30 rounded-lg space-y-1.5 text-xs">
                  <div className="font-bold text-brand-primary">Link Ativo:</div>
                  <div className="font-mono text-[11px] text-text-main break-all select-all p-1 bg-surface-card rounded border border-border">
                    {referralLinkData.referral_url}
                  </div>
                  <div className="text-[10px] text-text-secondary font-mono">
                    Código: <strong>{referralLinkData.referral_code}</strong>
                  </div>
                </div>
              )}
              {referralLinkData && (
                <div className="p-3 bg-surface-bg border border-border rounded-lg flex flex-col items-center gap-2">
                  <QrCodeSvg
                    value={`${window.location.origin}/r/${referralLinkData.referral_code}`}
                    size={140}
                  />
                  <a
                    href={`/r/${referralLinkData.referral_code}`}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-1 text-[11px] font-mono text-brand-primary underline"
                  >
                    <ExternalLink className="h-3 w-3" />
                    /r/{referralLinkData.referral_code}
                  </a>
                </div>
              )}
            </Card>

            {/* Coluna 2: Formulário de Indicação / Cadastro de Colega */}
            <Card className="p-4 border border-border bg-surface-card space-y-3">
              <div className="flex items-center justify-between border-b border-border pb-2">
                <h3 className="text-xs font-bold text-text-main flex items-center gap-1.5">
                  <Users className="h-4 w-4 text-status-success" />
                  Cadastrar Colega Indicado (Score Acelerado)
                </h3>
              </div>

              <form onSubmit={handleRegisterReferred} className="space-y-2">
                <div>
                  <label className="text-[11px] font-semibold text-text-secondary block mb-0.5">Nome do Colega</label>
                  <Input
                    value={referredName}
                    onChange={(e) => setReferredName(e.target.value)}
                    className="text-xs"
                    required
                  />
                </div>

                <div>
                  <label className="text-[11px] font-semibold text-text-secondary block mb-0.5">Telefone E.164</label>
                  <Input
                    value={referredPhone}
                    onChange={(e) => setReferredPhone(e.target.value)}
                    className="text-xs font-mono"
                    required
                  />
                </div>

                <div>
                  <label className="text-[11px] font-semibold text-text-secondary block mb-0.5">CRO/UF Indicado</label>
                  <Input
                    value={referredCro}
                    onChange={(e) => setReferredCro(e.target.value)}
                    className="text-xs font-mono"
                    required
                  />
                </div>

                <div>
                  <label className="text-[11px] font-semibold text-text-secondary block mb-0.5">E-mail</label>
                  <Input
                    value={referredEmail}
                    onChange={(e) => setReferredEmail(e.target.value)}
                    className="text-xs"
                    required
                  />
                </div>

                <Button type="submit" variant="default" size="sm" className="w-full text-xs mt-1">
                  Registrar Indicação
                </Button>
              </form>

              {registerResult && (
                <p className="text-xs text-status-success bg-status-success-subtle p-2 rounded border border-status-success/30 font-mono">
                  Colega registrado com sucesso! Contact ID: {registerResult.contact_id || "OK"}
                </p>
              )}
            </Card>

            {/* Coluna 3: Bonificação & Painel de Recompensas */}
            <Card className="p-4 border border-border bg-surface-card space-y-3">
              <div className="flex items-center justify-between border-b border-border pb-2">
                <h3 className="text-xs font-bold text-text-main flex items-center gap-1.5">
                  <Award className="h-4 w-4 text-status-warning" />
                  Bonificação & Qualificação Deal Ganho
                </h3>
              </div>

              <div className="grid grid-cols-2 gap-2 text-center">
                <div className="p-3 bg-surface-bg rounded-lg border border-border">
                  <span className="text-[11px] text-text-secondary block">Total Indicados</span>
                  <span className="text-lg font-bold text-text-main font-mono">
                    {mgmDashboard?.total_referrals || 0}
                  </span>
                </div>
                <div className="p-3 bg-surface-bg rounded-lg border border-border">
                  <span className="text-[11px] text-text-secondary block">Qualificados</span>
                  <span className="text-lg font-bold text-status-success font-mono">
                    {mgmDashboard?.qualified_referrals || 0}
                  </span>
                </div>
              </div>

              <div className="space-y-2 pt-2 border-t border-border">
                <label className="text-[11px] font-semibold text-text-secondary block">
                  Simular Faturamento do Primeiro Deal
                </label>
                <div className="flex gap-2">
                  <Input
                    value={qualifyDealId}
                    onChange={(e) => setQualifyDealId(e.target.value)}
                    className="text-xs font-mono"
                    placeholder="deal-01"
                  />
                  <Button
                    onClick={handleQualifyDealWon}
                    variant="outline"
                    size="sm"
                    className="text-xs whitespace-nowrap"
                  >
                    Qualificar
                  </Button>
                </div>
              </div>

              {qualifyResult && (
                <div className="p-2.5 rounded-lg bg-surface-bg border border-border text-xs font-mono">
                  <div className="text-status-success font-semibold">Deal Qualificado:</div>
                  <pre className="text-[10px] text-text-secondary mt-1 overflow-x-auto">
                    {JSON.stringify(qualifyResult, null, 2)}
                  </pre>
                </div>
              )}
            </Card>
          </div>
        </div>
      )}

      {/* TICKET-MKT-01: Modal de Teste A/B Split 50/50 */}
      {showAbModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-surface-overlay backdrop-blur-sm transition-all duration-200 animate-in fade-in-0">
          <div className="bg-surface-card border border-border rounded-xl w-full max-w-2xl p-5 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-text-main">Ativar Teste A/B (Split 50/50)</h3>
              <button type="button" onClick={() => setShowAbModal(false)} className="text-text-secondary hover:text-text-main">
                <X className="h-4 w-4" />
              </button>
            </div>
            <p className="text-xs text-text-secondary">
              O tráfego da landing page será dividido igualmente entre as variantes A e B. A variante com maior conversão será promovida automaticamente.
            </p>
            <div>
              <label className="block text-xs font-medium text-text-secondary mb-1">Nome do Experimento</label>
              <input
                value={abVariantName}
                onChange={(e) => setAbVariantName(e.target.value)}
                className="w-full h-9 rounded-md border border-border bg-surface-card px-3 text-sm text-text-main"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-text-secondary mb-1">Variante A (Controle)</label>
                <textarea
                  value={abVariantA}
                  onChange={(e) => setAbVariantA(e.target.value)}
                  className="w-full h-32 rounded-md border border-border bg-surface-card p-2 text-[11px] font-mono text-text-main"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-text-secondary mb-1">Variante B (Teste)</label>
                <textarea
                  value={abVariantB}
                  onChange={(e) => setAbVariantB(e.target.value)}
                  className="w-full h-32 rounded-md border border-border bg-surface-card p-2 text-[11px] font-mono text-text-main"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" size="sm" onClick={() => setShowAbModal(false)}>Cancelar</Button>
              <Button
                size="sm"
                onClick={() => {
                  setAbTestEnabled(true);
                  setShowAbModal(false);
                }}
              >
                Ativar Split 50/50
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LandingPageBuilder;
