import * as React from "react";
import { ShieldCheck, Lock, Mail, ArrowRight, AlertCircle, KeyRound, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";

interface LoginPageProps {
  onLoginSuccess: (token: string, user: any) => void;
}

export function LoginPage({ onLoginSuccess }: LoginPageProps) {
  const [email, setEmail] = React.useState("hevertoneduardoperes@gmail.com");
  const [password, setPassword] = React.useState("@#Khen741963@#");
  const [isLoading, setIsLoading] = React.useState(false);
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const response = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim(), password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Falha na autenticação. Verifique e-mail e senha.");
      }

      // Persiste sessão determinística
      localStorage.setItem("revnaut_auth_token", data.access_token);
      localStorage.setItem("revnaut_user", JSON.stringify(data.user));
      localStorage.setItem("revnaut_user_id", data.user.id);

      onLoginSuccess(data.access_token, data.user);
    } catch (err: any) {
      setErrorMessage(err.message || "Erro de rede ou servidor ao tentar login.");
    } finally {
      setIsLoading(false);
    }
  };

  const fillSuperadminCredentials = () => {
    setEmail("hevertoneduardoperes@gmail.com");
    setPassword("@#Khen741963@#");
    setErrorMessage(null);
  };

  return (
    <div className="min-h-screen w-full bg-surface-bg flex items-center justify-center p-4 selection:bg-brand-primary selection:text-text-inverse">
      <div className="w-full max-w-md space-y-6">
        {/* Header do Produto & Branding */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center justify-center h-12 w-12 rounded-xl bg-brand-navy text-text-inverse shadow-card border border-brand-navy/20">
            <ShieldCheck className="h-6 w-6 text-brand-primary" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-text-main">
            RevVault Enterprise
          </h1>
          <p className="text-xs text-text-secondary">
            Revenue Operations, Governança Cirúrgica & CRM Omnichannel
          </p>
        </div>

        {/* Card Principal de Autenticação */}
        <Card className="border-border shadow-card bg-surface-card">
          <CardHeader className="pb-4">
            <CardTitle className="text-base font-semibold text-text-main">Acessar Plataforma</CardTitle>
            <CardDescription className="text-xs text-text-secondary">
              Informe suas credenciais corporativas com autenticação criptográfica HMAC-SHA256.
            </CardDescription>
          </CardHeader>

          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-4">
              {errorMessage && (
                <div
                  role="alert"
                  className="p-3 rounded-lg bg-status-danger-subtle border border-status-danger/30 text-status-danger text-xs flex items-start gap-2"
                >
                  <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
                  <span className="flex-1">{errorMessage}</span>
                </div>
              )}

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-text-main flex items-center justify-between">
                  <span>E-mail Corporativo</span>
                  <span className="text-[10px] text-text-muted">Usuário único / IAM</span>
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-text-muted">
                    <Mail className="h-4 w-4" />
                  </div>
                  <Input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="consultor@revvault.com"
                    className="pl-9 text-xs"
                    disabled={isLoading}
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-text-main flex items-center justify-between">
                  <span>Senha de Acesso</span>
                  <span className="text-[10px] text-text-muted">Hash SHA-256</span>
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-text-muted">
                    <Lock className="h-4 w-4" />
                  </div>
                  <Input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••••••"
                    className="pl-9 text-xs"
                    disabled={isLoading}
                  />
                </div>
              </div>
            </CardContent>

            <CardFooter className="flex flex-col gap-3 pt-2">
              <Button
                type="submit"
                disabled={isLoading}
                className="w-full flex items-center justify-center gap-2 bg-brand-primary hover:bg-brand-primary-hover text-text-inverse font-medium text-xs h-9 cursor-pointer"
              >
                {isLoading ? (
                  <span>Autenticando sessão...</span>
                ) : (
                  <>
                    <span>Entrar no RevVault</span>
                    <ArrowRight className="h-3.5 w-3.5" />
                  </>
                )}
              </Button>
            </CardFooter>
          </form>
        </Card>

        {/* Atalho de Demonstração para Super Admin (God User) */}
        <div className="p-3.5 rounded-lg border border-border bg-surface-card/60 space-y-2 text-xs">
          <div className="flex items-center justify-between">
            <span className="font-semibold text-text-main flex items-center gap-1.5">
              <KeyRound className="h-3.5 w-3.5 text-brand-primary" />
              Credenciais de Demonstração
            </span>
            <Badge variant="navy" className="text-[10px]">
              Super Admin God
            </Badge>
          </div>
          <p className="text-[11px] text-text-secondary leading-relaxed">
            Usuário Heverton Eduardo Peres com perfil irrestrito de Governança, Totvs ERP, LiveKit SOS e RBAC.
          </p>
          <div className="flex items-center justify-between pt-1 border-t border-border/50">
            <div className="font-mono text-[10px] text-text-muted truncate max-w-[240px]">
              hevertoneduardoperes@gmail.com
            </div>
            <button
              type="button"
              onClick={fillSuperadminCredentials}
              className="text-[11px] font-medium text-brand-primary hover:text-brand-primary-hover underline underline-offset-2 cursor-pointer"
            >
              Preencher dados
            </button>
          </div>
        </div>

        {/* Rodapé de Governança e Segurança */}
        <div className="text-center text-[11px] text-text-muted space-y-1">
          <p>RevVault Enterprise v1.0.0 • SQLite WAL • OpenAPI 3.1</p>
          <p className="flex items-center justify-center gap-1">
            <CheckCircle2 className="h-3 w-3 text-status-success" />
            <span>Sessões assinadas com HMAC-SHA256 e rate limit anti-força bruta</span>
          </p>
        </div>
      </div>
    </div>
  );
}
