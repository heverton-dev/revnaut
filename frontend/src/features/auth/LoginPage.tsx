import * as React from "react";
import { ShieldCheck, Lock, Mail, ArrowRight, ArrowLeft, AlertCircle, CheckCircle2, KeyRound } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/Card";

interface LoginPageProps {
  onLoginSuccess: (token: string, user: any) => void;
}

export function LoginPage({ onLoginSuccess }: LoginPageProps) {
  const [mode, setMode] = React.useState<"login" | "forgot" | "reset">("login");
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [token, setToken] = React.useState("");
  const [newPassword, setNewPassword] = React.useState("");
  const [confirmPassword, setConfirmPassword] = React.useState("");
  const [isLoading, setIsLoading] = React.useState(false);
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);
  const [successMessage, setSuccessMessage] = React.useState<string | null>(null);

  // Inspeciona hash da URL na montagem e em hashchange
  React.useEffect(() => {
    const handleHash = () => {
      const hash = window.location.hash || "";
      if (hash.startsWith("#!/reset-password")) {
        const queryIdx = hash.indexOf("?");
        if (queryIdx !== -1) {
          const params = new URLSearchParams(hash.substring(queryIdx));
          const t = params.get("token");
          if (t) {
            setToken(t);
          }
        }
        setMode("reset");
        setErrorMessage(null);
        setSuccessMessage(null);
      }
    };

    handleHash();
    window.addEventListener("hashchange", handleHash);
    return () => window.removeEventListener("hashchange", handleHash);
  }, []);

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      const response = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim(), password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Falha na autenticacao. Verifique e-mail e senha.");
      }

      // Persiste sessao deterministica
      localStorage.setItem("revnault_auth_token", data.access_token);
      localStorage.setItem("revnault_user", JSON.stringify(data.user));
      localStorage.setItem("revnault_user_id", data.user.id);

      onLoginSuccess(data.access_token, data.user);
    } catch (err: any) {
      setErrorMessage(err.message || "Erro de rede ou servidor ao tentar login.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleForgotPasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      const response = await fetch("/api/v1/auth/forgot-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim() }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Falha ao processar solicitacao de recuperacao.");
      }

      setSuccessMessage(
        data.message || "Se o e-mail estiver cadastrado, as instrucoes e o token seguro foram despachados."
      );
    } catch (err: any) {
      setErrorMessage(err.message || "Erro de comunicacao com o servidor.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetPasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    if (newPassword.length < 12) {
      setErrorMessage("A nova senha deve possuir no minimo 12 caracteres.");
      setIsLoading(false);
      return;
    }

    if (confirmPassword && newPassword !== confirmPassword) {
      setErrorMessage("A confirmacao de senha nao confere com a nova senha digitada.");
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch("/api/v1/auth/reset-password-with-token", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          token: token.trim(),
          new_password: newPassword,
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Token invalido ou expirado.");
      }

      setSuccessMessage("Senha redefinida com sucesso. Redirecionando para login...");
      setNewPassword("");
      setConfirmPassword("");
      setToken("");
      setTimeout(() => {
        setMode("login");
        setSuccessMessage(null);
        if (window.location.hash.startsWith("#!/reset-password")) {
          window.location.hash = "";
        }
      }, 2000);
    } catch (err: any) {
      setErrorMessage(err.message || "Erro de comunicacao ao redefinir senha.");
    } finally {
      setIsLoading(false);
    }
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
            RevNault Enterprise
          </h1>
          <p className="text-xs text-text-secondary">
            Revenue Operations, Governanca Cirurgica & CRM Omnichannel
          </p>
        </div>

        {/* Card Principal */}
        <Card className="border-border shadow-card bg-surface-card">
          {mode === "login" && (
            <>
              <CardHeader className="pb-4">
                <CardTitle className="text-base font-semibold text-text-main">Acessar Plataforma</CardTitle>
                <CardDescription className="text-xs text-text-secondary">
                  Informe suas credenciais corporativas com autenticacao criptografica HMAC-SHA256.
                </CardDescription>
              </CardHeader>

              <form onSubmit={handleLoginSubmit}>
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
                      <span className="text-[10px] text-text-muted">Usuario unico / IAM</span>
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
                        placeholder="consultor@revnault.com"
                        className="pl-9 text-xs"
                        disabled={isLoading}
                      />
                    </div>
                  </div>

                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <label className="text-xs font-medium text-text-main">
                        <span>Senha de Acesso</span>
                      </label>
                      <button
                        type="button"
                        onClick={() => {
                          setMode("forgot");
                          setErrorMessage(null);
                          setSuccessMessage(null);
                        }}
                        className="text-[11px] text-brand-primary hover:underline cursor-pointer bg-transparent border-none p-0"
                      >
                        Esqueci minha senha
                      </button>
                    </div>
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
                      <span>Autenticando sessao...</span>
                    ) : (
                      <>
                        <span>Entrar no RevNault</span>
                        <ArrowRight className="h-3.5 w-3.5" />
                      </>
                    )}
                  </Button>

                  <div className="w-full text-center">
                    <button
                      type="button"
                      onClick={() => {
                        setMode("reset");
                        setErrorMessage(null);
                        setSuccessMessage(null);
                      }}
                      className="text-[11px] text-text-muted hover:text-text-main cursor-pointer bg-transparent border-none"
                    >
                      Possui um token? Redefinir com token
                    </button>
                  </div>
                </CardFooter>
              </form>
            </>
          )}

          {mode === "forgot" && (
            <>
              <CardHeader className="pb-4">
                <CardTitle className="text-base font-semibold text-text-main">Recuperacao de Senha</CardTitle>
                <CardDescription className="text-xs text-text-secondary">
                  Enviaremos instrucoes seguras e token temporario para o e-mail corporativo cadastrado.
                </CardDescription>
              </CardHeader>

              <form onSubmit={handleForgotPasswordSubmit}>
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

                  {successMessage && (
                    <div
                      role="status"
                      className="p-3 rounded-lg bg-status-success-subtle border border-status-success/30 text-status-success text-xs flex items-start gap-2"
                    >
                      <CheckCircle2 className="h-4 w-4 shrink-0 mt-0.5" />
                      <span className="flex-1">{successMessage}</span>
                    </div>
                  )}

                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-text-main">
                      <span>E-mail Cadastrado</span>
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
                        placeholder="consultor@revnault.com"
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
                    {isLoading ? <span>Enviando solicitacao...</span> : <span>Solicitar Redefinicao</span>}
                  </Button>

                  <button
                    type="button"
                    onClick={() => {
                      setMode("login");
                      setErrorMessage(null);
                      setSuccessMessage(null);
                    }}
                    className="flex items-center justify-center gap-1.5 text-xs text-text-muted hover:text-text-main cursor-pointer bg-transparent border-none py-1"
                  >
                    <ArrowLeft className="h-3.5 w-3.5" />
                    <span>Voltar para Login</span>
                  </button>
                </CardFooter>
              </form>
            </>
          )}

          {mode === "reset" && (
            <>
              <CardHeader className="pb-4">
                <CardTitle className="text-base font-semibold text-text-main">Nova Senha de Acesso</CardTitle>
                <CardDescription className="text-xs text-text-secondary">
                  Insira o token recebido e defina uma senha forte de no minimo 12 caracteres.
                </CardDescription>
              </CardHeader>

              <form onSubmit={handleResetPasswordSubmit}>
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

                  {successMessage && (
                    <div
                      role="status"
                      className="p-3 rounded-lg bg-status-success-subtle border border-status-success/30 text-status-success text-xs flex items-start gap-2"
                    >
                      <CheckCircle2 className="h-4 w-4 shrink-0 mt-0.5" />
                      <span className="flex-1">{successMessage}</span>
                    </div>
                  )}

                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-text-main">
                      <span>Token de Recuperacao</span>
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-text-muted">
                        <KeyRound className="h-4 w-4" />
                      </div>
                      <Input
                        type="text"
                        required
                        value={token}
                        onChange={(e) => setToken(e.target.value)}
                        placeholder="Cole o token recebido por e-mail"
                        className="pl-9 text-xs"
                        disabled={isLoading}
                      />
                    </div>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-text-main flex items-center justify-between">
                      <span>Nova Senha</span>
                      <span className="text-[10px] text-text-muted">Minimo 12 caracteres</span>
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-text-muted">
                        <Lock className="h-4 w-4" />
                      </div>
                      <Input
                        type="password"
                        required
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        placeholder="••••••••••••"
                        className="pl-9 text-xs"
                        disabled={isLoading}
                      />
                    </div>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-text-main">
                      <span>Confirme a Nova Senha</span>
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-text-muted">
                        <Lock className="h-4 w-4" />
                      </div>
                      <Input
                        type="password"
                        required
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
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
                    {isLoading ? <span>Gravando nova senha...</span> : <span>Redefinir Senha</span>}
                  </Button>

                  <button
                    type="button"
                    onClick={() => {
                      setMode("login");
                      setErrorMessage(null);
                      setSuccessMessage(null);
                    }}
                    className="flex items-center justify-center gap-1.5 text-xs text-text-muted hover:text-text-main cursor-pointer bg-transparent border-none py-1"
                  >
                    <ArrowLeft className="h-3.5 w-3.5" />
                    <span>Voltar para Login</span>
                  </button>
                </CardFooter>
              </form>
            </>
          )}
        </Card>

        {/* Rodape de Governanca e Seguranca */}
        <div className="text-center text-[11px] text-text-muted space-y-1">
          <p>RevNault Enterprise v1.0.0 • SQLite WAL • OpenAPI 3.1</p>
          <p className="flex items-center justify-center gap-1">
            <CheckCircle2 className="h-3 w-3 text-status-success" />
            <span>Sessoes assinadas com HMAC-SHA256 e rate limit anti-forca bruta</span>
          </p>
        </div>
      </div>
    </div>
  );
}
