import factory
from django.contrib.auth import get_user_model

from apps.prestadores.models import Prestador

Usuario = get_user_model()


class UsuarioFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Usuario
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"user{n}@test.com")
    email = factory.LazyAttribute(lambda obj: obj.username)
    role = "cs"

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        raw_password = extracted or "senha123dev"
        self.set_password(raw_password)
        if create:
            self.save()


class PrestadorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Prestador

    nome_artistico = factory.Sequence(lambda n: f"Artista Teste {n}")
    nome_completo = factory.Sequence(lambda n: f"Artista Teste {n} Silva")
    categoria = "musico"
    fase = "onboarding"
    cidade = "São Paulo"
    estado = "SP"
    whatsapp = "11999999999"
    email = factory.Sequence(lambda n: f"artista{n}@test.com")
