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

    def _check_admin(self, user):
        return (
            user.is_staff or 
            user.is_superuser or 
            (user.role and user.role.point >= 50) or 
            (user.role and user.role.nom == 'admin')
        )

    def update(self, request, *args, **kwargs):
        if not self._check_admin(request.user):
            return Response({'error': "Action réservée aux administrateurs."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if not self._check_admin(request.user):
            return Response({'error': "Action réservée aux administrateurs."}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not self._check_admin(request.user):
            return Response({'error': "Action réservée aux administrateurs."}, status=status.HTTP_403_FORBIDDEN)
        target_user = self.get_object()
        if target_user == request.user:
            return Response({'error': "Vous ne pouvez pas supprimer votre propre compte."}, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        if not self._check_admin(request.user):
            return Response({'error': "Action réservée aux administrateurs."}, status=status.HTTP_403_FORBIDDEN)

        target_user = self.get_object()
        if target_user == request.user:
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

    @action(detail=True, methods=['post'], url_path='change-role')
    def change_role(self, request, pk=None):
        if not self._check_admin(request.user):
            return Response({'error': "Action réservée aux administrateurs (niveau 50)."}, status=status.HTTP_403_FORBIDDEN)

        target_user = self.get_object()
        role_id = request.data.get('role_id')
        if not role_id:
            return Response({'error': "Le champ role_id est obligatoire."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return Response({'error': "Le rôle sélectionné n'existe pas."}, status=status.HTTP_404_NOT_FOUND)

        # Si l'admin modifie son propre rôle et tente de se rétrograder, vérifier qu'un autre admin actif existe
        if target_user == request.user and new_role.point < 50:
            other_admins = Utilisateur.objects.filter(is_active=True, role__point__gte=50).exclude(id=request.user.id).exists()
            if not other_admins:
                return Response({'error': "Action impossible : vous êtes le seul administrateur actif."}, status=status.HTTP_400_BAD_REQUEST)

        target_user.role = new_role
        if new_role.point >= 50 or new_role.nom == 'admin':
            target_user.is_staff = True
        else:
            target_user.is_staff = False
        target_user.save()

        return Response({
            'status': 'success',
            'user': UtilisateurSerializer(target_user).data,
            'message': f"Le rôle de {target_user.prenom} {target_user.nom} a été modifié en {new_role.label} ({new_role.point} pts)."
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
