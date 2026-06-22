export const AUTH_COOKIE_ACCESS = "marryme_access";
export const AUTH_COOKIE_REFRESH = "marryme_refresh";
export const AUTH_COOKIE_MODE = "marryme_auth_mode";

/** 7 dias — alinhado ao refresh JWT típico */
export const AUTH_COOKIE_MAX_AGE = 60 * 60 * 24 * 7;

function cookieFlags(maxAge: number): string {
  const secure =
    typeof window !== "undefined" && window.location.protocol === "https:" ? "; Secure" : "";
  return `path=/; SameSite=Lax; max-age=${maxAge}${secure}`;
}

export function setAccessRefreshCookies(access: string, refresh: string) {
  if (typeof document === "undefined") return;
  document.cookie = `${AUTH_COOKIE_ACCESS}=${encodeURIComponent(access)}; ${cookieFlags(AUTH_COOKIE_MAX_AGE)}`;
  document.cookie = `${AUTH_COOKIE_REFRESH}=${encodeURIComponent(refresh)}; ${cookieFlags(AUTH_COOKIE_MAX_AGE)}`;
}

export function setAuthCookies(access: string, refresh: string, mode: "cs" | "portal") {
  setAccessRefreshCookies(access, refresh);
  setAuthModeCookie(mode);
}

export function setAuthModeCookie(mode: "cs" | "portal") {
  if (typeof document === "undefined") return;
  document.cookie = `${AUTH_COOKIE_MODE}=${mode}; ${cookieFlags(AUTH_COOKIE_MAX_AGE)}`;
}

export function clearAuthCookies() {
  if (typeof document === "undefined") return;
  const expire = "path=/; max-age=0";
  document.cookie = `${AUTH_COOKIE_ACCESS}=; ${expire}`;
  document.cookie = `${AUTH_COOKIE_REFRESH}=; ${expire}`;
  document.cookie = `${AUTH_COOKIE_MODE}=; ${expire}`;
}

export function readDocumentCookie(name: string): string | null {
  if (typeof document === "undefined") return null;
  const prefix = `${name}=`;
  for (const part of document.cookie.split(";")) {
    const trimmed = part.trim();
    if (trimmed.startsWith(prefix)) {
      return decodeURIComponent(trimmed.slice(prefix.length));
    }
  }
  return null;
}

export function hydrateAuthFromCookies(): boolean {
  if (typeof window === "undefined") return false;
  if (localStorage.getItem(AUTH_COOKIE_ACCESS)) return false;

  const access = readDocumentCookie(AUTH_COOKIE_ACCESS);
  if (!access) return false;

  localStorage.setItem(AUTH_COOKIE_ACCESS, access);
  const refresh = readDocumentCookie(AUTH_COOKIE_REFRESH);
  if (refresh) localStorage.setItem(AUTH_COOKIE_REFRESH, refresh);
  const mode = readDocumentCookie(AUTH_COOKIE_MODE);
  if (mode === "portal" || mode === "cs") {
    localStorage.setItem(AUTH_COOKIE_MODE, mode);
  }
  return true;
}
