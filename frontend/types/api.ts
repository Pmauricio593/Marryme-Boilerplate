export type Paginated<T> = {
  total: number;
  paginas: number;
  pagina_atual: number;
  proxima: string | null;
  anterior: string | null;
  resultados: T[];
};

export type LoginEquipeResponse = {
  access: string;
  refresh: string;
  role: string;
  nivel_acesso: string;
  nome: string;
};

export type PortalLoginResponse = LoginEquipeResponse & {
  prestador_id?: string;
  permissoes_portal?: Record<string, boolean>;
  tipo_portal?: string;
};

export type PrestadorListItem = {
  id: string;
  nome_artistico: string;
  categoria: string;
  fase: string;
  cidade: string;
  estado: string;
  health_score: number | null;
  health_status: string | null;
  responsavel_nome: string;
  atualizado_em: string;
};

export type PrestadorDetail = PrestadorListItem & {
  nome_completo: string;
  email: string;
  whatsapp: string;
  instagram: string;
  meta_ad_account_id: string;
  meta_ultima_sync: string | null;
  meta_cpl_alvo?: string | null;
  meta_orcamento_mensal?: string | null;
  meta_leads_alvo_mensal?: number | null;
  ticket_medio_estimado: number | null;
  dados_entrevista: Record<string, unknown>;
};

export type HealthScore = {
  id: string;
  score: number;
  status: string;
  data_calculo: string;
  score_cpl: number;
  score_orcamento: number;
  score_leads: number;
  score_ctr: number;
};

export type Convite = {
  id: string;
  email: string;
  tipo: string;
  status: string;
  expira_em: string;
  criado_em?: string;
  link_portal?: string;
};

export type MembroPortal = {
  id: string;
  usuario: string;
  usuario_email: string;
  tipo: string;
  ativo: boolean;
  criado_em: string;
};

export type RelatorioIA = {
  id: string;
  prestador: string;
  periodo_inicio: string;
  periodo_fim: string;
  dados_json: {
    analise?: string;
    pauta_reuniao?: string[];
    acoes_cs?: string[];
    metricas_resumo?: Record<string, unknown>;
  };
  health_score: number | null;
  tokens_usados: number;
  gerado_em: string;
};

export type ChatMensagemApi = {
  id: string;
  role: string;
  content: string;
  criado_em: string;
};

export type ChatSessao = {
  id: string;
  titulo: string;
  tipo: string;
  status: string;
  prestador?: string;
  total_mensagens?: number;
  atualizado_em?: string;
};

export type PortalPerfil = {
  id: string;
  nome_artistico: string;
  categoria: string;
  fase: string;
  cidade?: string;
  estado?: string;
  instagram?: string;
  health_score: number | null;
  health_status: string | null;
  health_score_atual?: {
    score: number;
    status: string;
    data: string;
    breakdown: { cpm: number; hook_rate: number; retencao: number; ctr: number };
  } | null;
  total_sessoes?: number;
  roteiros_aprovados?: number;
  atualizado_em?: string;
  permissoes_portal?: Record<string, boolean>;
};

export type RoteiroFinal = {
  id: string;
  prestador: string;
  sessao: string | null;
  tipo: string;
  conteudo_json: Record<string, unknown>;
  aprovado: boolean;
  criado_em: string;
};
