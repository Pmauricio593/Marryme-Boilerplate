import factory

from apps.prestadores.factories import PrestadorFactory

from .models import ChatSessao, RoteiroFinal


class ChatSessaoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ChatSessao

    prestador = factory.SubFactory(PrestadorFactory)
    titulo = "Nova conversa"
    tipo = "geral"
    status = "ativa"


class RoteiroFinalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RoteiroFinal

    prestador = factory.SubFactory(PrestadorFactory)
    tipo = "video"
    conteudo_json = factory.LazyFunction(lambda: {"texto": "Roteiro de teste"})
