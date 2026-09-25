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


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all().order_by('-point', 'label')
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def _check_admin(self, user):
        return (
            user.is_staff or 
            user.is_superuser or 
            (user.role and user.role.point >= 50) or 
            (user.role and user.role.nom == 'admin')
        )

    def create(self, request, *args, **kwargs):
        if not self._check_admin(request.user):
            return Response({'error': "Action réservée aux administrateurs."}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if not self._check_admin(request.user):
            return Response({'error': "Action réservée aux administrateurs."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not self._check_admin(request.user):
            return Response({'error': "Action réservée aux administrateurs."}, status=status.HTTP_403_FORBIDDEN)
        role = self.get_object()
        if role.nom in ['admin', 'media_buyer']:
            return Response({'error': f"Le rôle système '{role.label}' est protégé et ne peut pas être supprimé."}, status=status.HTTP_400_BAD_REQUEST)
        if role.utilisateurs.count() > 0:
            return Response({'error': f"Impossible de supprimer ce rôle : {role.utilisateurs.count()} utilisateur(s) lui sont assigné(s)."}, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)


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

    def get_queryset(self):
        qs = Utilisateur.objects.all().select_related('role')
        search = self.request.query_params.get('search')
        if search:
            query = search.strip()
            qs = qs.filter(nom__icontains=query) | qs.filter(prenom__icontains=query) | qs.filter(email__icontains=query)
        role_id = self.request.query_params.get('role')
        if role_id:
            qs = qs.filter(role_id=role_id)
        is_active = self.request.query_params.get('is_active')
        if is_active is not None and is_active != '':
            qs = qs.filter(is_active=is_active.lower() in ('true', '1'))
        return qs.order_by('-created_at')

    def create(self, request, *args, **kwargs):
        if not self._check_admin(request.user):
            return Response({'error': "Action réservée aux administrateurs."}, status=status.HTTP_403_FORBIDDEN)
        
        email = request.data.get('email', '').strip().lower()
        if not email:
            return Response({'error': "L'adresse email est obligatoire."}, status=status.HTTP_400_BAD_REQUEST)
        if Utilisateur.objects.filter(email__iexact=email).exists():
            return Response({'error': f"Un utilisateur avec l'adresse '{email}' existe déjà."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Configurer automatiquement is_staff si rôle admin
        if user.role and (user.role.point >= 50 or user.role.nom == 'admin'):
            user.is_staff = True
            user.save()

        headers = self.get_success_headers(serializer.data)
        return Response(UtilisateurSerializer(user).data, status=status.HTTP_201_CREATED, headers=headers)

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
        if target_user.ventes.count() > 0:
            return Response(
                {'error': f"Impossible de supprimer cet utilisateur : {target_user.ventes.count()} vente(s) lui sont associées. Vous pouvez plutôt désactiver son compte."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if target_user.role and target_user.role.point >= 50:
            other_admins = Utilisateur.objects.filter(is_active=True, role__point__gte=50).exclude(id=target_user.id).exists()
            if not other_admins:
                return Response({'error': "Action impossible : il s'agit du dernier administrateur actif."}, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='reset-password')
    def reset_password(self, request, pk=None):
        if not self._check_admin(request.user):
            return Response({'error': "Action réservée aux administrateurs."}, status=status.HTTP_403_FORBIDDEN)
        target_user = self.get_object()
        password = request.data.get('password', '').strip()
        if not password or len(password) < 6:
            return Response({'error': "Le mot de passe doit comporter au moins 6 caractères."}, status=status.HTTP_400_BAD_REQUEST)
        target_user.set_password(password)
        target_user.save()
        return Response({
            'status': 'success',
            'message': f"Le mot de passe de {target_user.prenom} {target_user.nom} a été réinitialisé avec succès."
        })

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
