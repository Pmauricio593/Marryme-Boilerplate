import {
  AUTH_COOKIE_ACCESS,
  AUTH_COOKIE_MODE,
  AUTH_COOKIE_REFRESH,
  clearAuthCookies,
  readDocumentCookie,
  setAccessRefreshCookies,
  setAuthCookies,
  setAuthModeCookie,
} from "@/lib/auth/cookies";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
export class ApiError extends Error {
  status: number;
  detalhes?: Record<string, unknown>;

  constructor(message: string, status: number, detalhes?: Record<string, unknown>) {
    super(message);
    this.status = status;
    this.detalhes = detalhes;
  }
}

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return (
    localStorage.getItem(AUTH_COOKIE_ACCESS) ?? readDocumentCookie(AUTH_COOKIE_ACCESS)
  );
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return (
    localStorage.getItem(AUTH_COOKIE_REFRESH) ?? readDocumentCookie(AUTH_COOKIE_REFRESH)
  );
}

export function setTokens(access: string, refresh: string) {
  localStorage.setItem(AUTH_COOKIE_ACCESS, access);
  localStorage.setItem(AUTH_COOKIE_REFRESH, refresh);
  setAccessRefreshCookies(access, refresh);
}

export function clearTokens() {
  localStorage.removeItem(AUTH_COOKIE_ACCESS);
  localStorage.removeItem(AUTH_COOKIE_REFRESH);
  localStorage.removeItem("marryme_user");
  localStorage.removeItem(AUTH_COOKIE_MODE);
  clearAuthCookies();
}

export function setAuthMode(mode: "cs" | "portal") {
  localStorage.setItem(AUTH_COOKIE_MODE, mode);
  setAuthModeCookie(mode);
  const access = localStorage.getItem(AUTH_COOKIE_ACCESS);
  const refresh = localStorage.getItem(AUTH_COOKIE_REFRESH);
  if (access && refresh) {
    setAuthCookies(access, refresh, mode);
  }
}

export function getAuthMode(): "cs" | "portal" {
  if (typeof window === "undefined") return "cs";
  const mode =
    localStorage.getItem(AUTH_COOKIE_MODE) ?? readDocumentCookie(AUTH_COOKIE_MODE);
  return mode === "portal" ? "portal" : "cs";
}

export function redirectToLogin() {
  if (typeof window === "undefined") return;
  const path = getAuthMode() === "portal" ? "/portal/login" : "/login";
  if (!window.location.pathname.startsWith(path)) {
    window.location.href = path;
  }
}

export function setUserMeta(meta: Record<string, unknown>) {
  localStorage.setItem("marryme_user", JSON.stringify(meta));
}

export function getUserMeta<T = Record<string, unknown>>(): T | null {
  const raw = localStorage.getItem("marryme_user");
  if (!raw) return null;
  try {
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}

async function refreshAccessToken(): Promise<string | null> {
  const refresh = getRefreshToken();
  if (!refresh) return null;

  const res = await fetch(`${API_URL}/api/v1/auth/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh }),
  });

  if (!res.ok) {
    clearTokens();
    return null;
  }

  const data = await res.json();
  setTokens(data.access, data.refresh ?? refresh);
  return data.access as string;
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
  retry = true,
): Promise<T> {
  let token = getAccessToken();
  const headers: Record<string, string> = {
    ...(options.body ? { "Content-Type": "application/json" } : {}),
    ...(options.headers as Record<string, string>),
  };
  if (token) headers.Authorization = `Bearer ${token}`;

  let res = await fetch(`${API_URL}${path}`, { ...options, headers });

  if (res.status === 401 && retry) {
    token = await refreshAccessToken();
    if (token) {
      headers.Authorization = `Bearer ${token}`;
      res = await fetch(`${API_URL}${path}`, { ...options, headers });
    } else {
      redirectToLogin();
    }
  }

  const contentType = res.headers.get("content-type") || "";
  if (contentType.includes("text/event-stream")) {
    return res as unknown as T;
  }

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw new ApiError(
      data.erro || "Erro na requisição.",
      data.status || res.status,
      data.detalhes,
    );
  }

  return data as T;
}

export async function streamSessaoChat(
  sessaoId: string,
  mensagem: string,
  onChunk: (chunk: string) => void,
): Promise<void> {
  const token = getAccessToken();
  const res = await fetch(`${API_URL}/api/v1/sessoes/${sessaoId}/stream/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ mensagem }),
  });

  if (!res.ok || !res.body) {
    const err = await res.json().catch(() => ({}));
    throw new ApiError(err.erro || "Erro no stream.", res.status);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";
    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const chunk = line.slice(6);
        if (chunk === "[DONE]") return;
        onChunk(chunk);
      }
    }
  }
}
