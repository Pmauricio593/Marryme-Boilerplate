from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class Usuario(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(
        max_length=20,
        choices=[
            ('admin', 'Admin'),
            ('cs', 'CS'),
            ('sdr', 'SDR'),
            ('dev', 'Dev'),
            ('prestador', 'Prestador'),
        ],
        default='cs'
    )
    prestador_vinculado = models.OneToOneField(
        'Prestador',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuario_acesso',
    )

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='usuario_set',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='usuario_permission_set',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

class Prestador(models.Model):
    FASES = [
        ('onboarding', 'Onboarding'),
        ('planejamento', 'Planejamento de Metas'),
        ('growth', 'Growth'),
        ('voo_cruzeiro', 'Voo de Cruzeiro'),
        ('renovacao', 'Renovação'),
        ('pausado', 'Pausado'),
        ('churn', 'Churn'),
    ]
    CATEGORIAS = [
        ('musico', 'Músico / Banda'),
        ('fotografo', 'Fotógrafo / Videomaker'),
        ('celebrante', 'Celebrante'),
        ('dj', 'DJ'),
        ('cerimonialista', 'Cerimonialista'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome_artistico = models.CharField(max_length=200)
    nome_completo = models.CharField(max_length=200)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    fase = models.CharField(max_length=20, choices=FASES, default='onboarding')
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    whatsapp = models.CharField(max_length=20)
    instagram = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    meta_ad_account_id = models.CharField(max_length=50, blank=True)
    meta_cpl_alvo = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True)
    meta_orcamento_mensal = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    meta_leads_alvo_mensal = models.IntegerField(null=True, blank=True)
    ticket_medio_estimado = models.DecimalField(
        max_digits=10, decimal_places=2, default=3000)
    health_score = models.IntegerField(null=True, blank=True)
    health_status = models.CharField(max_length=20, null=True, blank=True)
    meta_ultima_sync = models.DateTimeField(null=True, blank=True)
    dados_entrevista = models.JSONField(default=dict)
    analise_estrategica = models.JSONField(default=dict)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    responsavel = models.ForeignKey(
        'prestadores.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prestadores'
    )

    class Meta:
        ordering = ['-atualizado_em']
        verbose_name = 'Prestador'
        verbose_name_plural = 'Prestadores'

    def __str__(self):
        return f"{self.nome_artistico} ({self.categoria})"


class TokenPrimeiroAcesso(models.Model):
    """
    Token temporário gerado no cadastro do prestador.
    Usado para o primeiro acesso e definição de senha.
    Expira em 48h.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='tokens_acesso'
    )
    token = models.CharField(max_length=64, unique=True)
    usado = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)
    expira_em = models.DateTimeField()

    class Meta:
        verbose_name = 'Token de Primeiro Acesso'
        verbose_name_plural = 'Tokens de Primeiro Acesso'

    def __str__(self):
        return f"{self.usuario.email} — {'usado' if self.usado else 'pendente'}"

    @property
    def expirado(self):
        from django.utils import timezone
        return timezone.now() > self.expira_em

    @property
    def valido(self):
        return not self.usado and not self.expirado
