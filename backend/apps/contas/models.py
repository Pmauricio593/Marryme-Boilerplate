import uuid
from django.db import models
from django.utils import timezone

from apps.contas.constants import PERMISSOES_ASSESSORIA_DEFAULT, PERMISSOES_TITULAR


class ConviteAcesso(models.Model):
    TIPOS = [
        ('titular', 'Titular'),
        ('assessoria', 'Assessoria'),
    ]
    STATUS = [
        ('pendente', 'Pendente'),
        ('usado', 'Usado'),
        ('expirado', 'Expirado'),
        ('revogado', 'Revogado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prestador = models.ForeignKey(
        'prestadores.Prestador',
        on_delete=models.CASCADE,
        related_name='convites',
    )
    email = models.EmailField()
    tipo = models.CharField(max_length=20, choices=TIPOS)
    permissoes_portal = models.JSONField(default=dict, blank=True)
    token_hash = models.CharField(max_length=64, unique=True)
    status = models.CharField(max_length=20, choices=STATUS, default='pendente')
    criado_por = models.ForeignKey(
        'prestadores.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='convites_emitidos',
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    expira_em = models.DateTimeField()
    usado_em = models.DateTimeField(null=True, blank=True)
    usuario_criado = models.ForeignKey(
        'prestadores.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='convites_aceitos',
    )

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Convite de Acesso'
        verbose_name_plural = 'Convites de Acesso'

    def __str__(self):
        return f'{self.email} — {self.prestador} ({self.tipo})'

    @property
    def expirado(self) -> bool:
        return timezone.now() > self.expira_em

    @property
    def valido(self) -> bool:
        return self.status == 'pendente' and not self.expirado

    def permissoes_efetivas(self) -> dict:
        if self.tipo == 'titular':
            return PERMISSOES_TITULAR.copy()
        return self.permissoes_portal or PERMISSOES_ASSESSORIA_DEFAULT.copy()


class VinculoPrestador(models.Model):
    TIPOS = [
        ('titular', 'Titular'),
        ('assessoria', 'Assessoria'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        'prestadores.Usuario',
        on_delete=models.CASCADE,
        related_name='vinculos_prestador',
    )
    prestador = models.ForeignKey(
        'prestadores.Prestador',
        on_delete=models.CASCADE,
        related_name='membros',
    )
    tipo = models.CharField(max_length=20, choices=TIPOS)
    permissoes_portal = models.JSONField(default=dict, blank=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('usuario', 'prestador')]
        verbose_name = 'Vínculo com Prestador'
        verbose_name_plural = 'Vínculos com Prestador'

    def __str__(self):
        return f'{self.usuario.email} → {self.prestador} ({self.tipo})'

    def permissoes_efetivas(self) -> dict:
        if self.tipo == 'titular':
            return PERMISSOES_TITULAR.copy()
        return self.permissoes_portal or PERMISSOES_ASSESSORIA_DEFAULT.copy()
