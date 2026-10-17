/**
 * Revnaut Dental Ops — Centralized API Client (ES Module)
 * Gerencia tokens de sessão, injeção de headers e interceptação de 401/403.
 */

const API_BASE = (typeof window !== 'undefined' && window.location.origin && window.location.origin !== 'null' && window.location.protocol !== 'file:')
  ? `${window.location.origin}/api/v1`
  : 'http://localhost:8000/api/v1';

export function getAuthToken() {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('revnaut_auth_token') || sessionStorage.getItem('revnaut_auth_token') || window.AUTH_TOKEN || null;
}

export function setAuthToken(token, persist = true) {
  if (typeof window === 'undefined') return;
  window.AUTH_TOKEN = token;
  if (persist) {
    localStorage.setItem('revnaut_auth_token', token);
  } else {
    sessionStorage.setItem('revnaut_auth_token', token);
  }
}

export function clearAuthToken() {
  if (typeof window === 'undefined') return;
  window.AUTH_TOKEN = null;
  localStorage.removeItem('revnaut_auth_token');
  sessionStorage.removeItem('revnaut_auth_token');
}

export async function apiRequest(endpoint, options = {}) {
  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint.startsWith('/') ? endpoint : '/' + endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  const token = getAuthToken();
  if (token && !headers['Authorization']) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const userId = window.CURRENT_USER_ID || (window.CURRENT_USER && window.CURRENT_USER.id);
  if (userId && !headers['X-User-Id']) {
    headers['X-User-Id'] = userId;
  }

  const response = await fetch(url, {
    ...options,
    headers
  });

  if (response.status === 401) {
    console.warn('[ApiClient] Sessão expirada ou não autorizada (HTTP 401).');
    if (typeof window !== 'undefined' && window.handleSessionExpired) {
      window.handleSessionExpired();
    }
  }

  return response;
}

export const api = {
  get: (url, opts) => apiRequest(url, { ...opts, method: 'GET' }),
  post: (url, data, opts) => apiRequest(url, { ...opts, method: 'POST', body: JSON.stringify(data) }),
  put: (url, data, opts) => apiRequest(url, { ...opts, method: 'PUT', body: JSON.stringify(data) }),
  patch: (url, data, opts) => apiRequest(url, { ...opts, method: 'PATCH', body: JSON.stringify(data) }),
  delete: (url, opts) => apiRequest(url, { ...opts, method: 'DELETE' })
};
