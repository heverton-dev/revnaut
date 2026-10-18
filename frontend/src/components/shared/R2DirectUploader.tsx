import * as React from "react";
import { UploadCloud, CheckCircle2, AlertCircle, File, X } from "lucide-react";
import { cn } from "@/lib/utils";

export interface R2DirectUploaderProps {
  module: "consignments" | "dicom" | "contracts" | "media";
  onUploadComplete?: (result: { key: string; filename: string }) => void;
  className?: string;
  accept?: string;
}

export function R2DirectUploader({
  module,
  onUploadComplete,
  className,
  accept = ".pdf,.dcm,.stl,.ply,.ogg,.mp4,.png,.jpg",
}: R2DirectUploaderProps) {
  const [progress, setProgress] = React.useState<number | null>(null);
  const [isUploading, setIsUploading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [uploadedKey, setUploadedKey] = React.useState<string | null>(null);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setError(null);
    setIsUploading(true);
    setProgress(0);

    try {
      // 1. Obter URL pré-assinada do backend
      const presignRes = await fetch("/api/v1/storage/presign-upload", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Account-ID": "0f14ffff",
        },
        body: JSON.stringify({
          filename: file.name,
          module,
          content_type: file.type || "application/octet-stream",
        }),
      });

      if (!presignRes.ok) {
        const errData = await presignRes.json().catch(() => ({}));
        throw new Error(errData.detail || "Falha ao obter autorização de upload");
      }

      const { upload_url, key } = await presignRes.json();

      // 2. Upload direto para o Cloudflare R2 via XMLHttpRequest com progresso real
      const xhr = new XMLHttpRequest();
      xhr.open("PUT", upload_url, true);
      xhr.setRequestHeader("Content-Type", file.type || "application/octet-stream");

      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const pct = Math.round((event.loaded / event.total) * 100);
          setProgress(pct);
        }
      };

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          setIsUploading(false);
          setProgress(100);
          setUploadedKey(key);
          if (onUploadComplete) {
            onUploadComplete({ key, filename: file.name });
          }
        } else {
          setIsUploading(false);
          setError(`Erro durante envio direto ao R2 (HTTP ${xhr.status})`);
        }
      };

      xhr.onerror = () => {
        setIsUploading(false);
        setError("Erro de rede ao enviar arquivo para o Cloudflare R2");
      };

      xhr.send(file);
    } catch (err: any) {
      setIsUploading(false);
      setError(err.message || "Erro inesperado");
    }
  };

  const handleReset = () => {
    setProgress(null);
    setIsUploading(false);
    setError(null);
    setUploadedKey(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div
      className={cn(
        "rounded-lg border border-dashed border-border bg-surface-card p-6 text-center transition-colors",
        className
      )}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept={accept}
        onChange={handleFileChange}
        className="hidden"
        id={`r2-upload-${module}`}
        disabled={isUploading}
      />

      {!isUploading && !uploadedKey && !error && (
        <label
          htmlFor={`r2-upload-${module}`}
          className="flex flex-col items-center justify-center cursor-pointer"
        >
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-brand-primary-subtle text-brand-primary mb-3">
            <UploadCloud className="h-6 w-6 stroke-[1.8]" />
          </div>
          <span className="text-sm font-semibold text-text-main">
            Clique para enviar ou arraste o arquivo
          </span>
          <span className="text-xs text-text-secondary mt-1">
            Armazenamento R2 S3 v4 com Zero Egress Fee ({accept})
          </span>
        </label>
      )}

      {isUploading && (
        <div className="flex flex-col items-center justify-center py-2">
          <div className="flex items-center gap-2 text-sm font-medium text-text-main mb-2">
            <File className="h-4 w-4 text-brand-primary animate-bounce" />
            <span>Enviando direto para Cloudflare R2... {progress}%</span>
          </div>
          <div className="w-full max-w-xs h-2 bg-surface-bg rounded-full overflow-hidden border border-border">
            <div
              className="h-full bg-brand-primary transition-all duration-150"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {uploadedKey && (
        <div className="flex items-center justify-between p-3 rounded-md bg-status-success-subtle border border-status-success/20">
          <div className="flex items-center gap-2 text-xs font-medium text-status-success">
            <CheckCircle2 className="h-4 w-4 shrink-0" />
            <span className="truncate max-w-xs">Enviado com sucesso: {uploadedKey}</span>
          </div>
          <button
            onClick={handleReset}
            className="text-text-muted hover:text-text-main p-1"
            aria-label="Remover"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      {error && (
        <div className="flex items-center justify-between p-3 rounded-md bg-status-danger-subtle border border-status-danger/20">
          <div className="flex items-center gap-2 text-xs font-medium text-status-danger">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
          <button
            onClick={handleReset}
            className="text-text-muted hover:text-text-main p-1"
            aria-label="Tentar novamente"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      )}
    </div>
  );
}
