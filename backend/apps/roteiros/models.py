from django.db import models
import uuid


class ChatSessao(models.Model):
    TIPOS = [
        ('geral', 'Geral'),
        ('video', 'Vídeo de Apresentação'),
        ('cta', 'CTA / Anúncio'),
        ('direcao', 'Direção Criativa'),
        ('analise', 'Análise Estratégica'),
    ]
    STATUS = [
        ('ativa', 'Ativa'),
        ('finalizada', 'Finalizada'),
        ('arquivada', 'Arquivada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prestador = models.ForeignKey(
        'prestadores.Prestador',
        on_delete=models.CASCADE,
        related_name='sessoes_chat'
    )
    titulo = models.CharField(max_length=200, default='Nova conversa')
    tipo = models.CharField(max_length=20, choices=TIPOS, default='geral')
    status = models.CharField(max_length=20, choices=STATUS, default='ativa')
    roteiro_final = models.JSONField(null=True, blank=True)
    tokens_usados = models.IntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-atualizado_em']
        verbose_name = 'Sessão de Chat'
        verbose_name_plural = 'Sessões de Chat'

    def __str__(self):
        return f"{self.prestador} — {self.titulo}"


class ChatMensagem(models.Model):
    ROLES = [
        ('user', 'Usuário'),
        ('assistant', 'Assistente'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sessao = models.ForeignKey(
        ChatSessao,
        on_delete=models.CASCADE,
        related_name='mensagens'
    )
    role = models.CharField(max_length=20, choices=ROLES)
    content = models.TextField()
    arquivos = models.JSONField(default=list)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['criado_em']
        verbose_name = 'Mensagem'
        verbose_name_plural = 'Mensagens'

    def __str__(self):
        return f"{self.role} — {self.sessao}"


class RoteiroFinal(models.Model):
    TIPOS = [
        ('video', 'Vídeo de Apresentação'),
        ('cta', 'CTA / Anúncio'),
        ('direcao', 'Direção Criativa'),
        ('analise', 'Análise Estratégica'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prestador = models.ForeignKey(
        'prestadores.Prestador',
        on_delete=models.CASCADE,
        related_name='roteiros'
    )
    sessao = models.ForeignKey(
        ChatSessao,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='roteiros'
    )
    tipo = models.CharField(max_length=20, choices=TIPOS)
    conteudo_json = models.JSONField()
    aprovado = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Roteiro Final'
        verbose_name_plural = 'Roteiros Finais'

    def __str__(self):
        return f"{self.prestador} — {self.tipo}"
