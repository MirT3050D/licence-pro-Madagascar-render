from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Sum, F
from .models import Role, Utilisateur
from .serializers import (
    RoleSerializer,
    UtilisateurSerializer,
    CustomTokenObtainPairSerializer,
    RegisterSerializer
)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_data = UtilisateurSerializer(user).data

            if user.is_active:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'user': user_data,
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'requires_approval': False,
                    'message': 'Compte Administrateur configuré et activé avec succès !'
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'user': user_data,
                    'requires_approval': True,
                    'message': "Inscription réussie ! Votre compte commercial est en attente d'approbation par l'administrateur."
                }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]


class UtilisateurViewSet(viewsets.ModelViewSet):
    queryset = Utilisateur.objects.all().select_related('role').order_by('-created_at')
    serializer_class = UtilisateurSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        current_user = request.user
        is_admin = current_user.is_staff or current_user.is_superuser or (current_user.role and current_user.role.nom == 'admin')
        if not is_admin:
            return Response({'error': "Action réservée aux administrateurs."}, status=status.HTTP_403_FORBIDDEN)

        target_user = self.get_object()
        if target_user == current_user:
            return Response({'error': "Vous ne pouvez pas désactiver votre propre compte."}, status=status.HTTP_400_BAD_REQUEST)

        target_user.is_active = not target_user.is_active
        target_user.save()
        status_label = "activé" if target_user.is_active else "désactivé"
        return Response({
            'status': 'success',
            'is_active': target_user.is_active,
            'user': UtilisateurSerializer(target_user).data,
            'message': f"Le compte de {target_user.prenom} {target_user.nom} est maintenant {status_label}."
        })


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UtilisateurSerializer(user)

        # Sales statistics for current user
        ventes = user.ventes.all().prefetch_related('commandes')
        total_ventes_count = ventes.count()
        total_ca = sum(v.total for v in ventes)
        points = user.role.point if user.role else 0

        # Recent personal sales
        recent_sales = [
            {
                'id': v.id,
                'date': v.date,
                'client_nom': v.client.nom,
                'total': v.total,
                'methode_paiement': v.methode_paiement.label
            }
            for v in ventes.order_by('-date')[:5]
        ]

        return Response({
            'user': serializer.data,
            'statistiques': {
                'points': points,
                'total_ventes': total_ventes_count,
                'chiffre_affaires': total_ca
            },
            'ventes_recentes': recent_sales
        })
