import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4 text-center">
      <div className="card max-w-md space-y-4">
        <h1 className="font-display text-2xl text-primary">Página não encontrada</h1>
        <p className="text-sm text-text-mid">O endereço que você acessou não existe.</p>
        <div className="flex flex-wrap justify-center gap-3 pt-2">
          <Link href="/login" className="btn-primary inline-block">
            Login CS
          </Link>
          <Link href="/portal/login" className="btn-secondary inline-block">
            Portal
          </Link>
        </div>
      </div>
    </div>
  );
}
