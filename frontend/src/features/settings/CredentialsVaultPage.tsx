import * as React from "react";
import {
  KeyRound,
  ShieldCheck,
  Plus,
  Trash2,
  Lock,
  Eye,
  EyeOff,
  CheckCircle2,
  FileKey,
  Server,
  RefreshCw,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Badge } from "@/components/ui/Badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Dialog } from "@/components/ui/Dialog";
import { Skeleton } from "@/components/ui/Skeleton";
import { EmptyState } from "@/components/ui/EmptyState";
import { cn } from "@/lib/utils";

export interface VaultCredential {
  id: string;
  service_name: string;
  credential_type: string;
  masked_value: string;
  metadata?: Record<string, any>;
  created_at?: string;
}

export function CredentialsVaultPage() {
  const [credentials, setCredentials] = React.useState<VaultCredential[]>([
    {
      id: "cred-evo-01",
      service_name: "evolution_api_v2",
      credential_type: "api_token",
      masked_value: "****89a1",
      metadata: { cluster: "1000_instancias_sp" },
      created_at: "2026-10-15 11:30:00",
    },
    {
      id: "cred-a1-totvs",
      service_name: "totvs_protheus",
      credential_type: "certificado_fiscal_a1",
      masked_value: "****c4d2",
      metadata: { validade: "2027-10-01" },
      created_at: "2026-10-16 09:45:00",
    },
    {
      id: "cred-wh-sec",
      service_name: "mautic_webhook",
      credential_type: "hmac_sha256_secret",
      masked_value: "****ef33",
      metadata: { status: "ativo" },
      created_at: "2026-10-17 14:20:00",
    },
  ]);

  const [isLoading, setIsLoading] = React.useState(false);
  const [isDialogOpen, setIsDialogOpen] = React.useState(false);
  const [serviceName, setServiceName] = React.useState("evolution_api_v2");
  const [credentialType, setCredentialType] = React.useState("api_token");
  const [secretPayload, setSecretPayload] = React.useState("");

  const handleSave = () => {
    if (!secretPayload) return;
    const last4 = secretPayload.slice(-4);
    const newCred: VaultCredential = {
      id: `cred-${Date.now().toString(36)}`,
      service_name: serviceName,
      credential_type: credentialType,
      masked_value: `****${last4}`,
      created_at: new Date().toISOString().replace("T", " ").slice(0, 19),
    };
    setCredentials((prev) => [newCred, ...prev]);
    setSecretPayload("");
    setIsDialogOpen(false);
  };

  const handleDelete = (id: string) => {
    setCredentials((prev) => prev.filter((c) => c.id !== id));
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-text-main flex items-center gap-2">
            <Lock className="h-6 w-6 text-brand-primary" />
            Cofre Seguro de Credenciais & Chaves de API
          </h1>
          <p className="text-sm text-text-secondary mt-1">
            Criptografia simétrica em repouso AES-256-GCM (PBKDF2 SHA-256) com isolamento estrito multi-tenant.
          </p>
        </div>
        <Button onClick={() => setIsDialogOpen(true)} size="sm" className="inline-flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Nova Credencial Cifrada
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4 border-border">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-md bg-brand-primary-subtle text-brand-primary flex items-center justify-center">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <span className="text-xs text-text-secondary uppercase font-semibold">Algoritmo</span>
              <p className="text-sm font-bold text-text-main">AES-256-GCM Autenticado</p>
            </div>
          </div>
        </Card>

        <Card className="p-4 border-border">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-md bg-brand-navy-subtle text-brand-navy flex items-center justify-center">
              <Server className="h-5 w-5" />
            </div>
            <div>
              <span className="text-xs text-text-secondary uppercase font-semibold">Traefik Edge Gateway</span>
              <p className="text-sm font-bold text-text-main">Rate Limit 100 req/s</p>
            </div>
          </div>
        </Card>

        <Card className="p-4 border-border">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-md bg-status-success-subtle text-status-success flex items-center justify-center">
              <CheckCircle2 className="h-5 w-5" />
            </div>
            <div>
              <span className="text-xs text-text-secondary uppercase font-semibold">OWASP Compliance</span>
              <p className="text-sm font-bold text-text-main">Zero Plaintext</p>
            </div>
          </div>
        </Card>
      </div>

      {isLoading ? (
        <Card className="p-6">
          <Skeleton className="h-6 w-48 mb-4" />
          <div className="space-y-3">
            <Skeleton className="h-12 w-full" />
            <Skeleton className="h-12 w-full" />
          </div>
        </Card>
      ) : credentials.length === 0 ? (
        <EmptyState
          icon={FileKey}
          title="Nenhuma credencial cadastrada no cofre"
          description="Adicione tokens da Evolution API, certificados fiscais A1 ou chaves de integração ERP."
          actionLabel="Adicionar Primeira Chave"
          onAction={() => setIsDialogOpen(true)}
        />
      ) : (
        <Card className="border-border">
          <CardHeader>
            <CardTitle>Credenciais Ativas Cifradas</CardTitle>
            <CardDescription>
              Os segredos brutos são descriptografados estritamente em tempo de execução pelos adaptadores de produção.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="divide-y divide-border-subtle">
              {credentials.map((cred) => (
                <div key={cred.id} className="py-3.5 flex items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <KeyRound className="h-5 w-5 text-brand-navy shrink-0" />
                    <div>
                      <div className="font-semibold text-sm text-text-main flex items-center gap-2">
                        <span>{cred.service_name}</span>
                        <Badge variant="navy" className="text-[10px]">
                          {cred.credential_type}
                        </Badge>
                      </div>
                      <div className="text-xs text-text-secondary font-mono mt-0.5">
                        Valor Mascarado: <span className="text-text-main font-semibold">{cred.masked_value}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className="text-xs text-text-muted">{cred.created_at}</span>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(cred.id)}
                      className="text-status-danger hover:bg-status-danger-subtle p-2"
                      aria-label="Excluir credencial"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Modal de Cadastro de Credencial */}
      <Dialog
        isOpen={isDialogOpen}
        onClose={() => setIsDialogOpen(false)}
        title="Cadastrar Credencial no Cofre Cifrado"
        description="O segredo será cifrado com AES-256-GCM antes de qualquer persistência em disco ou banco de dados."
        footer={
          <>
            <Button variant="secondary" size="sm" onClick={() => setIsDialogOpen(false)}>
              Cancelar
            </Button>
            <Button size="sm" onClick={handleSave}>
              Cifrar e Salvar
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <Select
            label="Serviço Alvo"
            value={serviceName}
            onChange={(e) => setServiceName(e.target.value)}
            options={[
              { value: "evolution_api_v2", label: "Evolution API v2 (WhatsApp Gateway)" },
              { value: "totvs_protheus", label: "TOTVS Protheus (Certificado / Token ERP)" },
              { value: "mautic_webhook", label: "Mautic (Assinatura HMAC Webhook)" },
              { value: "documenso_api", label: "Documenso (Assinatura Eletrônica)" },
              { value: "livekit_sip", label: "LiveKit SFU / SIP (WebRTC Trunk)" },
            ]}
          />

          <Select
            label="Tipo de Credencial"
            value={credentialType}
            onChange={(e) => setCredentialType(e.target.value)}
            options={[
              { value: "api_token", label: "API Token / Bearer Key" },
              { value: "certificado_fiscal_a1", label: "Certificado Fiscal A1 (Base64 + Senha)" },
              { value: "oauth2_client_secret", label: "OAuth2 Client Secret" },
              { value: "hmac_sha256_secret", label: "HMAC-SHA256 Webhook Secret" },
            ]}
          />

          <div>
            <label className="mb-1.5 block text-xs font-medium text-text-secondary">
              Segredo em Texto Puro (será cifrado imediatamente)
            </label>
            <Input
              type="password"
              placeholder="Cole aqui o token, chave privada ou senha..."
              value={secretPayload}
              onChange={(e) => setSecretPayload(e.target.value)}
            />
          </div>
        </div>
      </Dialog>
    </div>
  );
}
export default CredentialsVaultPage;
