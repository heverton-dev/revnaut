// -*- coding: utf-8 -*-
/**
 * Global API Client & Fetch Interceptor
 * Intercepta chamadas /api/v1/*, injeta credenciais RBAC (X-User-Id, Bearer token),
 * e dispara notificações determinísticas (revnaut:toast) para operações mutantes.
 */

export interface ToastPayload {
  type: "success" | "error" | "info" | "warning";
  title: string;
  message: string;
  status?: number;
}

export function getActiveUserId(): string {
  if (typeof window === "undefined") return "usr-director-br";
  return localStorage.getItem("revnaut_active_user_id") || "usr-director-br";
}

export function setActiveUserId(userId: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem("revnaut_active_user_id", userId);
  window.dispatchEvent(new CustomEvent("revnaut:user_changed", { detail: { userId } }));
}

export function dispatchToast(toast: ToastPayload): void {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new CustomEvent("revnaut:toast", { detail: toast }));
}

// Inicializa interceptor global de fetch
export function setupGlobalFetchInterceptor(): void {
  if (typeof window === "undefined" || (window as any).__revnaut_fetch_intercepted) {
    return;
  }

  const originalFetch = window.fetch.bind(window);

  window.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
    const urlString = typeof input === "string" ? input : input instanceof URL ? input.toString() : input.url;
    const isApiRequest = urlString.includes("/api/v1/");

    if (!isApiRequest) {
      return originalFetch(input, init);
    }

    const activeUserId = getActiveUserId();
    // LoginPage grava o token em "revnaut_auth_token"; chaves antigas mantidas por compatibilidade
    const token =
      localStorage.getItem("revnaut_auth_token") || localStorage.getItem("auth_token") || localStorage.getItem("revnaut_token");

    const modifiedInit: RequestInit = { ...(init || {}) };
    const headers = new Headers(modifiedInit.headers || (input instanceof Request ? input.headers : {}));

    if (!headers.has("X-User-Id")) {
      headers.set("X-User-Id", activeUserId);
    }

    if (token && !headers.has("Authorization")) {
      headers.set("Authorization", `Bearer ${token}`);
    }

    const method = (modifiedInit.method || (input instanceof Request ? input.method : "GET")).toUpperCase();

    // Se houver body e for string sem Content-Type especificado, define como application/json
    if (
      modifiedInit.body &&
      typeof modifiedInit.body === "string" &&
      !headers.has("Content-Type") &&
      (modifiedInit.body.startsWith("{") || modifiedInit.body.startsWith("["))
    ) {
      headers.set("Content-Type", "application/json");
    }

    modifiedInit.headers = headers;

    try {
      const response = await originalFetch(input, modifiedInit);

      // Token de sessão rejeitado (expirado ou inválido): encerra a sessão local e volta ao login
      if (response.status === 401 && token && !urlString.includes("/api/v1/auth/login")) {
        localStorage.removeItem("revnaut_auth_token");
        localStorage.removeItem("auth_token");
        localStorage.removeItem("revnaut_token");
        window.dispatchEvent(new CustomEvent("revnaut:session_expired"));
      }

      // Dispara toast para métodos de mutação (POST, PUT, PATCH, DELETE)
      if (["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
        try {
          const clone = response.clone();
          const contentType = clone.headers.get("content-type") || "";
          let data: any = null;
          if (contentType.includes("application/json")) {
            data = await clone.json().catch(() => null);
          } else {
            data = await clone.text().catch(() => null);
          }

          if (response.ok) {
            const successMsg =
              (typeof data === "object" && (data?.message || data?.detail || data?.feedback || data?.title)) ||
              (response.status === 201 ? "Registro criado com sucesso!" : "Operação concluída com sucesso!");
            dispatchToast({
              type: "success",
              title: "Sucesso",
              message: String(successMsg),
              status: response.status,
            });
          } else {
            const rawDetail = (typeof data === "object" && data?.detail) || data || "Falha na requisição ao servidor.";
            const errorMsg = typeof rawDetail === "object" ? JSON.stringify(rawDetail) : String(rawDetail);
            dispatchToast({
              type: "error",
              title: `Erro (${response.status})`,
              message: errorMsg,
              status: response.status,
            });
          }
        } catch {
          // Garante que o interceptor não bloqueia a resposta se a extração falhar
        }
      }

      return response;
    } catch (err: any) {
      if (["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
        dispatchToast({
          type: "error",
          title: "Erro de Conexão",
          message: err?.message || "Não foi possível conectar ao servidor.",
        });
      }
      throw err;
    }
  };

  (window as any).__revnaut_fetch_intercepted = true;
}
