from django.db import migrations

PERMISSOES_TITULAR = {
    'perfil': True,
    'campanhas': True,
    'health_score': True,
    'roteiros': True,
}


def migrar_prestador_vinculado(apps, schema_editor):
    Usuario = apps.get_model('prestadores', 'Usuario')
    VinculoPrestador = apps.get_model('contas', 'VinculoPrestador')

    for usuario in Usuario.objects.exclude(prestador_vinculado_id=None):
        VinculoPrestador.objects.get_or_create(
            usuario_id=usuario.id,
            prestador_id=usuario.prestador_vinculado_id,
            defaults={
                'tipo': 'titular',
                'permissoes_portal': PERMISSOES_TITULAR,
                'ativo': True,
            },
        )


def reverter_migracao(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('contas', '0001_initial'),
        ('prestadores', '0004_alter_usuario_role'),
    ]

    operations = [
        migrations.RunPython(migrar_prestador_vinculado, reverter_migracao),
    ]
