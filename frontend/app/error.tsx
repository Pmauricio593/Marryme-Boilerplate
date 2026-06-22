"use client";

import { useEffect } from "react";
import { ErrorFallback, logClientError, safeMessage } from "@/components/errors/ErrorFallback";

export default function GlobalAppError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    logClientError(error, "app");
  }, [error]);

  return (
    <ErrorFallback
      message={safeMessage(error)}
      reset={reset}
      homeHref="/login"
      homeLabel="Ir para login"
    />
  );
}
