import uuid

from django.db import models


class MetricaMeta(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prestador = models.ForeignKey(
        "prestadores.Prestador", on_delete=models.CASCADE, related_name="metricas"
    )
    data_referencia = models.DateField()
    campanha_id = models.CharField(max_length=100)
    campanha_nome = models.CharField(max_length=200)
    impressoes = models.IntegerField(default=0)
    alcance = models.IntegerField(default=0)
    cliques = models.IntegerField(default=0)
    ctr = models.DecimalField(max_digits=6, decimal_places=4, default=0)
    leads = models.IntegerField(default=0)
    gasto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cpl = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-data_referencia"]
        verbose_name = "Métrica Meta"
        verbose_name_plural = "Métricas Meta"

    def __str__(self):
        return f"{self.prestador} — {self.data_referencia}"


class HealthScore(models.Model):
    STATUS = [
        ("saudavel", "Saudável"),
        ("atencao", "Atenção"),
        ("em_risco", "Em Risco"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prestador = models.ForeignKey(
        "prestadores.Prestador", on_delete=models.CASCADE, related_name="health_scores"
    )
    data_calculo = models.DateField()
    score = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS)
    score_cpl = models.IntegerField()
    score_orcamento = models.IntegerField()
    score_leads = models.IntegerField()
    score_ctr = models.IntegerField()
    cpl_real = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    gasto_real = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    leads_real = models.IntegerField(null=True)
    roi = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-data_calculo"]
        verbose_name = "Health Score"
        verbose_name_plural = "Health Scores"

    def __str__(self):
        return f"{self.prestador} — Score {self.score} ({self.status})"


class RelatorioIA(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prestador = models.ForeignKey(
        "prestadores.Prestador", on_delete=models.CASCADE, related_name="relatorios"
    )
    periodo_inicio = models.DateField()
    periodo_fim = models.DateField()
    dados_json = models.JSONField()
    health_score = models.IntegerField(null=True)
    tokens_usados = models.IntegerField(default=0)
    gerado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-gerado_em"]
        verbose_name = "Relatório IA"
        verbose_name_plural = "Relatórios IA"

    def __str__(self):
        return f"{self.prestador} — {self.periodo_inicio} a {self.periodo_fim}"


class ConfiguracaoMeta(models.Model):
    """Armazena configurações dinâmicas — token Meta, etc."""

    chave = models.CharField(max_length=100, unique=True)
    valor = models.TextField()
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuração Meta"
        verbose_name_plural = "Configurações Meta"

    def __str__(self):
        return self.chave

    @classmethod
    def get(cls, chave: str):
        try:
            return cls.objects.get(chave=chave).valor
        except cls.DoesNotExist:
            return None

    @classmethod
    def set(cls, chave: str, valor: str):
        cls.objects.update_or_create(chave=chave, defaults={"valor": valor})
