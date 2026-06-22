import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";
import {
  AUTH_COOKIE_ACCESS,
  AUTH_COOKIE_MODE,
} from "@/lib/auth/cookies";

function isAuthenticated(request: NextRequest): boolean {
  return Boolean(request.cookies.get(AUTH_COOKIE_ACCESS)?.value);
}

function getAuthMode(request: NextRequest): "cs" | "portal" {
  return request.cookies.get(AUTH_COOKIE_MODE)?.value === "portal" ? "portal" : "cs";
}

function redirect(request: NextRequest, pathname: string) {
  const url = request.nextUrl.clone();
  url.pathname = pathname;
  return NextResponse.redirect(url);
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const authed = isAuthenticated(request);
  const mode = getAuthMode(request);

  if (pathname.startsWith("/prestadores")) {
    if (!authed) return redirect(request, "/login");
    if (mode === "portal") return redirect(request, "/portal/perfil");
    return NextResponse.next();
  }

  if (pathname === "/login") {
    if (authed && mode === "cs") return redirect(request, "/prestadores");
    return NextResponse.next();
  }

  if (pathname.startsWith("/portal")) {
    const isPublic =
      pathname === "/portal/login" || pathname.startsWith("/portal/convite");

    if (isPublic) {
      if (authed && mode === "portal") {
        return redirect(request, "/portal/perfil");
      }
      return NextResponse.next();
    }

    if (!authed) return redirect(request, "/portal/login");
    if (mode !== "portal") return redirect(request, "/login");
    return NextResponse.next();
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/prestadores/:path*", "/portal/:path*", "/login"],
};
