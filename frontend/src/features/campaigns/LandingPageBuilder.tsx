import React, { useEffect, useRef, useState } from "react";
import {
  Globe,
  UploadCloud,
  Save,
  Eye,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Loader2,
  Sparkles,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Badge } from "@/components/ui/Badge";

export interface LandingPageTemplate {
  template_type: string;
  name: string;
  description: string;
  category: string;
  html: string;
  css: string;
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
  const editorRef = useRef<HTMLDivElement>(null);
  const grapesInstanceRef = useRef<any>(null);

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

  useEffect(() => {
    fetch("/api/v1/campaigns/landing-pages/templates")
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) {
          setTemplates(data);
        }
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    const initEditor = () => {
      if (!editorRef.current) return;

      const win = window as any;
      if (win.grapesjs && !grapesInstanceRef.current) {
        try {
          const editor = win.grapesjs.init({
            container: editorRef.current,
            height: "600px",
            width: "auto",
            storageManager: false,
            blockManager: {
              appendTo: 'div[id="blocks-panel"]',
              blocks: [
                {
                  id: "cfo-responsible",
                  label: "Responsável Técnico CFO",
                  category: "Odontologia CFO",
                  content: `<div class="cfo-banner" style="padding: 12px; background: var(--color-surface-card); border-top: 2px solid var(--color-brand-primary); font-size: 12px; text-align: center; color: var(--color-text-secondary);">
                    <p>Responsável Técnico: ${cfoName} — ${cfoCro} | Conforme Resolução CFO 196/2019 e Art. 43 do CEO</p>
                  </div>`,
                },
                {
                  id: "cro-verified-input",
                  label: "Input CRO/UF Verificado",
                  category: "Formulários",
                  content: `<div style="margin-bottom: 12px;">
                    <label style="display: block; font-size: 13px; font-weight: 600; margin-bottom: 4px;">CRO/UF do Cirurgião</label>
                    <input type="text" name="cro" placeholder="CRO-SP 123456" style="width: 100%; padding: 8px 12px; border: 1px solid var(--color-border-subtle); border-radius: 6px;" required />
                  </div>`,
                },
                {
                  id: "implant-system-select",
                  label: "Seletor de Sistema de Implante",
                  category: "Formulários",
                  content: `<div style="margin-bottom: 12px;">
                    <label style="display: block; font-size: 13px; font-weight: 600; margin-bottom: 4px;">Sistema Utilizado</label>
                    <select name="implant_system" style="width: 100%; padding: 8px 12px; border: 1px solid var(--color-border-subtle); border-radius: 6px;">
                      <option value="Cone Morse">Cone Morse / Conexão Cônica</option>
                      <option value="Hexágono Externo">Hexágono Externo (HE)</option>
                      <option value="Hexágono Interno">Hexágono Interno (HI)</option>
                      <option value="Zircônia">Implante Cerâmico / Zircônia</option>
                    </select>
                  </div>`,
                },
              ],
            },
          });
          grapesInstanceRef.current = editor;
        } catch {
          // fallback visual quando GrapesJS CDN não está injetada
        }
      }
    };

    initEditor();

    return () => {
      if (grapesInstanceRef.current && typeof grapesInstanceRef.current.destroy === "function") {
        try {
          grapesInstanceRef.current.destroy();
        } catch {}
        grapesInstanceRef.current = null;
      }
    };
  }, [cfoCro, cfoName]);

  const handleSaveDraft = async () => {
    setIsSaving(true);
    try {
      const gjsHtml = grapesInstanceRef.current
        ? grapesInstanceRef.current.getHtml()
        : null;
      const gjsCss = grapesInstanceRef.current
        ? grapesInstanceRef.current.getCss()
        : null;

      const payload = {
        title,
        slug,
        template_type: selectedTemplate,
        gjs_html: gjsHtml,
        gjs_css: gjsCss,
        cfo_responsible_cro: cfoCro,
        cfo_responsible_name: cfoName,
      };

      let resp;
      if (currentId) {
        resp = await fetch(`/api/v1/campaigns/landing-pages/${currentId}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      } else {
        resp = await fetch("/api/v1/campaigns/landing-pages", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      }

      if (resp.ok) {
        const data = await resp.json();
        setCurrentId(data.id);
      }
    } finally {
      setIsSaving(false);
    }
  };

  const handlePublish = async () => {
    if (!currentId) {
      await handleSaveDraft();
    }
    const targetId = currentId;
    if (!targetId) return;

    setIsPublishing(true);
    try {
      const resp = await fetch(`/api/v1/campaigns/landing-pages/${targetId}/publish`, {
        method: "PUT",
      });
      if (resp.ok) {
        const data = await resp.json();
        setPublishedUrl(data.published_r2_url);
        setCfoStatus(data.cfo_compliance_status);
        if (onPublished) {
          onPublished(data.published_r2_url);
        }
      }
    } finally {
      setIsPublishing(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-surface-bg border border-border rounded-lg overflow-hidden font-sans">
      <header className="flex flex-wrap items-center justify-between gap-3 p-4 bg-surface-card border-b border-border">
        <div className="flex items-center gap-2">
          <Globe className="w-5 h-5 text-brand-primary" />
          <h2 className="text-base font-bold text-text-main">
            Construtor de Landing Pages Odontológicas
          </h2>
          <Badge variant="navy" className="text-xs">
            GrapesJS & Cloudflare R2
          </Badge>
        </div>

        <div className="flex items-center gap-2">
          {publishedUrl && (
            <Badge variant="success" className="gap-1 text-xs">
              <CheckCircle2 className="w-3.5 h-3.5" />
              Publicada no R2
            </Badge>
          )}

          {cfoStatus === "COM_ALERTA_ETICO" && (
            <Badge variant="danger" className="gap-1 text-xs">
              <AlertTriangle className="w-3.5 h-3.5" />
              Alerta CFO
            </Badge>
          )}

          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={handleSaveDraft}
            disabled={isSaving}
            className="gap-1.5"
          >
            {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            Salvar Rascunho
          </Button>

          <Button
            type="button"
            size="sm"
            onClick={handlePublish}
            disabled={isPublishing}
            className="bg-brand-primary text-text-inverse gap-1.5"
          >
            {isPublishing ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <UploadCloud className="w-4 h-4" />
            )}
            Publicar no R2
          </Button>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-3 p-3 bg-surface-bg border-b border-border text-xs">
        <div>
          <label className="block font-semibold text-text-secondary mb-1">
            Título da Campanha
          </label>
          <Input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="h-8 text-xs"
            placeholder="Título da LP"
          />
        </div>

        <div>
          <label className="block font-semibold text-text-secondary mb-1">
            Slug da URL
          </label>
          <Input
            value={slug}
            onChange={(e) => setSlug(e.target.value)}
            className="h-8 text-xs"
            placeholder="slug-da-url"
          />
        </div>

        <div>
          <label className="block font-semibold text-text-secondary mb-1 flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5 text-status-success" />
            Responsável Técnico CRO/UF (Art. 43)
          </label>
          <Input
            value={cfoCro}
            onChange={(e) => setCfoCro(e.target.value)}
            className="h-8 text-xs"
            placeholder="CRO-SP 123456"
          />
        </div>

        <div>
          <label className="block font-semibold text-text-secondary mb-1">
            Nome do Titular
          </label>
          <Input
            value={cfoName}
            onChange={(e) => setCfoName(e.target.value)}
            className="h-8 text-xs"
            placeholder="Dr. Nome do Cirurgião"
          />
        </div>
      </div>

      <div className="flex-1 flex flex-col md:flex-row overflow-hidden min-h-[500px]">
        <div className="w-full md:w-64 bg-surface-card border-r border-border p-3 overflow-y-auto">
          <div className="flex items-center gap-1 text-xs font-bold text-text-main mb-2">
            <Sparkles className="w-4 h-4 text-brand-primary" />
            Blocos de Anatomia Odonto
          </div>
          {templates.length > 0 && (
            <div className="mb-3 space-y-1">
              {templates.map((tpl) => (
                <button
                  key={tpl.template_type}
                  type="button"
                  onClick={() => setSelectedTemplate(tpl.template_type)}
                  className={`w-full text-left p-2 rounded border text-xs transition-colors ${
                    selectedTemplate === tpl.template_type
                      ? "border-brand-primary bg-brand-primary-subtle text-brand-primary font-semibold"
                      : "border-border bg-surface-bg text-text-secondary"
                  }`}
                >
                  {tpl.name}
                </button>
              ))}
            </div>
          )}
          <div id="blocks-panel" className="space-y-2">
            <div className="p-2 border border-dashed border-border rounded text-xs text-text-secondary">
              Arraste os blocos do painel para o corpo da página no editor.
            </div>
          </div>
        </div>

        <div className="flex-1 bg-surface-bg p-4 overflow-auto flex flex-col">
          {publishedUrl && (
            <div className="mb-3 p-2 bg-status-success-subtle border border-status-success/30 rounded text-xs text-status-success flex items-center justify-between">
              <span className="flex items-center gap-1">
                <CheckCircle2 className="w-4 h-4 text-status-success" />
                URL CDN Ativa:{" "}
                <a href={publishedUrl} target="_blank" rel="noreferrer" className="underline font-mono">
                  {publishedUrl}
                </a>
              </span>
              <a
                href={publishedUrl}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1 font-semibold hover:underline"
              >
                <Eye className="w-3.5 h-3.5" /> Abrir Página
              </a>
            </div>
          )}

          <div
            ref={editorRef}
            id="gjs"
            className="flex-1 bg-surface-card rounded shadow-card border border-border overflow-hidden min-h-[450px]"
          />
        </div>
      </div>
    </div>
  );
};
