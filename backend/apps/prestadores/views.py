import logging
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound, ValidationError
from .models import Prestador, Usuario
from .serializers import (
    PrestadorSerializer,
    PrestadorListSerializer,
    MarryMeTokenSerializer,
    PortalPrestadorSerializer,
)
from .services import PrestadorService
from .tokens import validar_token_acesso
from core.permissions import IsCS, IsAdmin, IsEquipeOuPrestadorVinculado, IsPrestador

logger = logging.getLogger('marryme.prestadores')


class MarryMeTokenView(TokenObtainPairView):
    """Login — retorna access + refresh token com role e nome."""
    serializer_class = MarryMeTokenSerializer


class PrestadorViewSet(viewsets.ModelViewSet):
    """
    CRUD completo de prestadores.
    Listagem usa serializer resumido — detalhe usa completo.
    Filtros por fase e categoria via query params.
    """
    queryset = Prestador.objects.select_related('responsavel').all()

    def get_serializer_class(self):
        if self.action == 'list':
            return PrestadorListSerializer
        return PrestadorSerializer

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAdmin()]
        return [IsCS()]

    def get_queryset(self):
        queryset = super().get_queryset()
        fase = self.request.query_params.get('fase')
        categoria = self.request.query_params.get('categoria')
        busca = self.request.query_params.get('busca')

        if fase:
            queryset = queryset.filter(fase=fase)
        if categoria:
            queryset = queryset.filter(categoria=categoria)
        if busca:
            queryset = queryset.filter(
                nome_artistico__icontains=busca
            ) | queryset.filter(
                cidade__icontains=busca
            )
        return queryset

    def perform_create(self, serializer):
        serializer.save(responsavel=self.request.user)
        logger.info(f"Prestador criado: {serializer.instance}")

    @action(detail=True, methods=['post'], url_path='atualizar-fase')
    def atualizar_fase(self, request, pk=None):
        """Atualiza fase do pipeline e dispara automações."""
        prestador = self.get_object()
        nova_fase = request.data.get('fase')

        if not nova_fase:
            return Response(
                {'erro': 'Campo fase é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if nova_fase not in dict(Prestador.FASES):
            return Response(
                {'erro': f'Fase inválida: {nova_fase}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        prestador = PrestadorService().atualizar_fase(prestador, nova_fase)
        return Response(PrestadorSerializer(prestador).data)

    @action(detail=True, methods=['post'], url_path='sync-meta')
    def sync_meta(self, request, pk=None):
        """Dispara sync do Meta Ads em background."""
        prestador = self.get_object()

        if not prestador.meta_ad_account_id:
            return Response(
                {'erro': 'Conta Meta não configurada.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from apps.campanhas.tasks import sincronizar_meta_ads
        sincronizar_meta_ads.delay(str(prestador.id))

        logger.info(f"Sync Meta enfileirado: {prestador}")
        return Response({'status': 'enfileirado'})

    @action(detail=False, methods=['post'], url_path='sync-todos')
    def sync_todos(self, request, pk=None):
        """Dispara sync de todos os clientes ativos — admin only."""
        from apps.campanhas.tasks import sincronizar_todos_clientes
        sincronizar_todos_clientes.delay()
        return Response({'status': 'enfileirado'})


class PortalLoginView(APIView):
    """
    Endpoint de login exclusivo para prestadores.
    Separado do login da equipe interna.
    """
    permission_classes = []

    def post(self, request):
        email = request.data.get('email', '').strip()
        senha = request.data.get('senha', '').strip()

        if not email or not senha:
            return Response(
                {'erro': 'Email e senha são obrigatórios.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            usuario = Usuario.objects.get(email=email, role='prestador')
        except Usuario.DoesNotExist:
            return Response(
                {'erro': 'Credenciais inválidas.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not usuario.check_password(senha):
            return Response(
                {'erro': 'Credenciais inválidas.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not usuario.is_active:
            return Response(
                {'erro': 'Acesso inativo. Entre em contato com a MarryMe.'},
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(usuario)
        refresh['role'] = usuario.role
        refresh['nome'] = (
            usuario.prestador_vinculado.nome_artistico
            if usuario.prestador_vinculado
            else usuario.email
        )

        logger.info(f"Login portal: {usuario.email}")

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'role': usuario.role,
            'nome': (
                usuario.prestador_vinculado.nome_artistico
                if usuario.prestador_vinculado
                else usuario.email
            ),
            'prestador_id': (
                str(usuario.prestador_vinculado.id)
                if usuario.prestador_vinculado
                else None
            ),
        })


class PrimeiroAcessoView(APIView):
    """
    Valida token de primeiro acesso e define senha.
    Prestador recebe link por WhatsApp/email e define senha aqui.
    """
    permission_classes = []

    def post(self, request):
        token_str = request.data.get('token', '').strip()
        nova_senha = request.data.get('senha', '').strip()

        if not token_str or not nova_senha:
            return Response(
                {'erro': 'Token e senha são obrigatórios.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(nova_senha) < 8:
            return Response(
                {'erro': 'Senha deve ter no mínimo 8 caracteres.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        token = validar_token_acesso(token_str)
        if not token:
            return Response(
                {'erro': 'Token inválido ou expirado.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        token.usuario.set_password(nova_senha)
        token.usuario.save()
        token.usado = True
        token.save()

        logger.info(f"Primeiro acesso concluído: {token.usuario.email}")
        return Response({
            'status': 'Senha definida com sucesso. Faça login para continuar.'
        })


class PortalPerfilView(generics.RetrieveAPIView):
    """
    Perfil do prestador no portal.
    Prestador vê apenas o próprio perfil.
    Equipe acessa via ?prestador_id=
    """
    serializer_class = PortalPrestadorSerializer
    permission_classes = [IsEquipeOuPrestadorVinculado]

    def get_object(self):
        user = self.request.user

        if user.role == 'prestador':
            if not user.prestador_vinculado:
                raise NotFound('Nenhum prestador vinculado.')
            return user.prestador_vinculado

        prestador_id = self.request.query_params.get('prestador_id')
        if not prestador_id:
            raise ValidationError('Parâmetro prestador_id é obrigatório.')

        return get_object_or_404(Prestador, id=prestador_id)


class PortalCampanhasView(generics.ListAPIView):
    """
    Health scores e métricas do prestador no portal.
    Prestador vê apenas os próprios dados.
    """
    permission_classes = [IsEquipeOuPrestadorVinculado]

    def get(self, request):
        from apps.campanhas.models import HealthScore, MetricaMeta
        from apps.campanhas.serializers import HealthScoreSerializer, MetricaMetaSerializer

        user = request.user

        if user.role == 'prestador':
            if not user.prestador_vinculado:
                raise NotFound('Nenhum prestador vinculado.')
            prestador = user.prestador_vinculado
        else:
            prestador_id = request.query_params.get('prestador_id')
            if not prestador_id:
                raise ValidationError('Parâmetro prestador_id é obrigatório.')
            prestador = get_object_or_404(Prestador, id=prestador_id)

        # Último health score
        hs = HealthScore.objects.filter(
            prestador=prestador
        ).order_by('-data_calculo').first()

        # Métricas dos últimos 30 dias
        metricas = MetricaMeta.objects.filter(
            prestador=prestador
        ).order_by('-data_referencia')[:30]

        return Response({
            'health_score': HealthScoreSerializer(hs).data if hs else None,
            'metricas': MetricaMetaSerializer(metricas, many=True).data,
        })


class PortalRoteirosView(generics.ListAPIView):
    """
    Roteiros aprovados do prestador no portal.
    Prestador vê apenas os próprios roteiros.
    """
    permission_classes = [IsEquipeOuPrestadorVinculado]

    def get(self, request):
        from apps.roteiros.models import RoteiroFinal, ChatSessao
        from apps.roteiros.serializers import RoteiroFinalSerializer, ChatSessaoListSerializer

        user = request.user

        if user.role == 'prestador':
            if not user.prestador_vinculado:
                raise NotFound('Nenhum prestador vinculado.')
            prestador = user.prestador_vinculado
        else:
            prestador_id = request.query_params.get('prestador_id')
            if not prestador_id:
                raise ValidationError('Parâmetro prestador_id é obrigatório.')
            prestador = get_object_or_404(Prestador, id=prestador_id)

        # Roteiros aprovados
        roteiros = RoteiroFinal.objects.filter(
            prestador=prestador,
            aprovado=True
        ).order_by('-criado_em')

        # Últimas sessões finalizadas
        sessoes = ChatSessao.objects.filter(
            prestador=prestador,
            status='finalizada'
        ).order_by('-atualizado_em')[:5]

        return Response({
            'roteiros': RoteiroFinalSerializer(roteiros, many=True).data,
            'sessoes_recentes': ChatSessaoListSerializer(sessoes, many=True).data,
        })
