"use client";

import { useEffect } from "react";
import { hydrateAuthFromCookies } from "@/lib/auth/cookies";

/** Restaura localStorage a partir dos cookies quando a aba perdeu o storage. */
export function AuthHydrate() {
  useEffect(() => {
    hydrateAuthFromCookies();
  }, []);
  return null;
}
