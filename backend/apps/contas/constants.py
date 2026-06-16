class NivelAcesso:
    ADMIN = 'admin'
    EQUIPE = 'equipe'
    PRESTADOR = 'prestador'
    ASSESSORIA = 'assessoria'


ROLES_EQUIPE = ('cs', 'sdr', 'dev')
ROLES_PORTAL = ('prestador', 'assessoria')
ROLES_INTERNOS = ('admin',) + ROLES_EQUIPE

ROLE_PARA_NIVEL = {
    'admin': NivelAcesso.ADMIN,
    'cs': NivelAcesso.EQUIPE,
    'sdr': NivelAcesso.EQUIPE,
    'dev': NivelAcesso.EQUIPE,
    'prestador': NivelAcesso.PRESTADOR,
    'assessoria': NivelAcesso.ASSESSORIA,
}

PERMISSOES_TITULAR = {
    'perfil': True,
    'campanhas': True,
    'health_score': True,
    'roteiros': True,
}

PERMISSOES_ASSESSORIA_DEFAULT = {
    'perfil': True,
    'campanhas': True,
    'health_score': True,
    'roteiros': False,
}


def role_para_nivel(role: str) -> str:
    return ROLE_PARA_NIVEL.get(role, NivelAcesso.EQUIPE)


def eh_portal(role: str) -> bool:
    return role in ROLES_PORTAL


def eh_equipe_interna(role: str) -> bool:
    return role in ROLES_INTERNOS
