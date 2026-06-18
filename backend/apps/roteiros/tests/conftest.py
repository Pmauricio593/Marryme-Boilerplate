import pytest

from apps.roteiros.factories import ChatSessaoFactory, RoteiroFinalFactory


@pytest.fixture
def chat_sessao_factory(prestador_factory):
    def factory(**kwargs):
        if "prestador" not in kwargs:
            kwargs["prestador"] = prestador_factory()
        return ChatSessaoFactory(**kwargs)

    return factory


@pytest.fixture
def roteiro_final_factory(prestador_factory):
    def factory(**kwargs):
        if "prestador" not in kwargs:
            kwargs["prestador"] = prestador_factory()
        return RoteiroFinalFactory(**kwargs)

    return factory
