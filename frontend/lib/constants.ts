export const FASES = [
  { value: "onboarding", label: "Onboarding" },
  { value: "planejamento", label: "Planejamento de metas" },
  { value: "growth", label: "Growth" },
  { value: "voo_cruzeiro", label: "Voo de cruzeiro" },
  { value: "renovacao", label: "Renovação" },
  { value: "pausado", label: "Pausado" },
  { value: "churn", label: "Churn" },
] as const;

export const CATEGORIAS = [
  { value: "musico", label: "Músico / Banda" },
  { value: "fotografo", label: "Fotógrafo / Videomaker" },
  { value: "celebrante", label: "Celebrante" },
  { value: "dj", label: "DJ" },
  { value: "cerimonialista", label: "Cerimonialista" },
] as const;

export const CONVITE_TIPOS = [
  { value: "titular", label: "Titular (prestador)" },
  { value: "assessoria", label: "Assessoria" },
] as const;

export function labelFase(fase: string): string {
  return FASES.find((f) => f.value === fase)?.label ?? fase.replace(/_/g, " ");
}

export function labelCategoria(categoria: string): string {
  return CATEGORIAS.find((c) => c.value === categoria)?.label ?? categoria;
}

export const ROTEIRO_TIPOS = [
  { value: "video", label: "Vídeo de apresentação" },
  { value: "cta", label: "CTA / Anúncio" },
  { value: "direcao", label: "Direção criativa" },
  { value: "analise", label: "Análise estratégica" },
] as const;

export const CONVITE_STATUS: Record<string, string> = {
  pendente: "Pendente",
  aceito: "Aceito",
  expirado: "Expirado",
  revogado: "Revogado",
};

export function labelHsStatus(status: string | null | undefined): string {
  if (status === "saudavel") return "Saudável";
  if (status === "atencao") return "Atenção";
  if (status === "em_risco") return "Em risco";
  return status?.replace(/_/g, " ") ?? "—";
}

export function labelRoteiroTipo(tipo: string): string {
  return ROTEIRO_TIPOS.find((t) => t.value === tipo)?.label ?? tipo.replace(/_/g, " ");
}

export function labelConviteStatus(status: string): string {
  return CONVITE_STATUS[status] ?? status.replace(/_/g, " ");
}
