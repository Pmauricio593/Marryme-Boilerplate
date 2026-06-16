from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.contas.models import ConviteAcesso, VinculoPrestador
from apps.contas.services.convite_service import ConviteService
from apps.prestadores.models import Prestador

Usuario = get_user_model()


class ConviteServiceTest(TestCase):

    def setUp(self):
        self.prestador = Prestador.objects.create(
            nome_artistico='Airton Sax',
            nome_completo='Airton Silva',
            categoria='musico',
            cidade='São Paulo',
            estado='SP',
            whatsapp='11999999999',
            email='airton@test.com',
        )
        self.admin = Usuario.objects.create_user(
            username='admin@test.com',
            email='admin@test.com',
            password='admin123dev',
            role='admin',
        )

    def test_emitir_convite_titular_sem_criar_usuario(self):
        _, token = ConviteService().emitir(
            prestador=self.prestador,
            email=self.prestador.email,
            tipo='titular',
            criado_por=self.admin,
        )

        self.assertFalse(
            Usuario.objects.filter(email=self.prestador.email).exists()
        )
        self.assertEqual(ConviteAcesso.objects.count(), 1)
        self.assertTrue(token)

    def test_aceitar_convite_cria_usuario_e_vinculo(self):
        _, token = ConviteService().emitir(
            prestador=self.prestador,
            email=self.prestador.email,
            tipo='titular',
            criado_por=self.admin,
        )

        resultado = ConviteService().aceitar(
            token=token,
            senha='senha12345',
            nome='Airton Sax',
        )

        self.assertTrue(
            Usuario.objects.filter(email=self.prestador.email, role='prestador').exists()
        )
        self.assertEqual(VinculoPrestador.objects.count(), 1)
        self.assertIn('access', resultado)
        self.assertEqual(resultado['nivel_acesso'], 'prestador')

    def test_login_equipe_bloqueia_portal(self):
        _, token = ConviteService().emitir(
            prestador=self.prestador,
            email=self.prestador.email,
            tipo='titular',
        )
        ConviteService().aceitar(token=token, senha='senha12345')

        client = APIClient()
        response = client.post('/api/v1/auth/login/', {
            'username': self.prestador.email,
            'password': 'senha12345',
        }, format='json')

        self.assertEqual(response.status_code, 400)

    def test_validar_convite(self):
        _, token = ConviteService().emitir(
            prestador=self.prestador,
            email=self.prestador.email,
            tipo='titular',
        )

        client = APIClient()
        response = client.get(f'/api/v1/portal/convites/validar/?token={token}')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['valido'])
        self.assertIn('***', response.data['email_mascarado'])
