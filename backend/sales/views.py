from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count, F, DecimalField, ExpressionWrapper, Q
from django.db.models.functions import TruncDate
from .models import MethodePaiement, Vente, Commande
from .serializers import MethodePaiementSerializer, VenteSerializer, VenteCreateSerializer
from accounts.models import Utilisateur


class MethodePaiementViewSet(viewsets.ModelViewSet):
    queryset = MethodePaiement.objects.all().prefetch_related('ventes')
    serializer_class = MethodePaiementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get('search') or self.request.query_params.get('q')
        status_param = self.request.query_params.get('status')

        if search:
            search = search.strip()
            qs = qs.filter(Q(label__icontains=search) | Q(details__icontains=search))

        if status_param == 'active':
            qs = qs.filter(is_active=True)
        elif status_param == 'inactive':
            qs = qs.filter(is_active=False)

        return qs.order_by('-is_active', 'label')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        ventes_count = instance.ventes.count()
        if ventes_count > 0:
            return Response(
                {
                    'error': f"Impossible de supprimer « {instance.label} » car elle est rattachée à {ventes_count} vente(s). Vous pouvez la désactiver à la place."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request, pk=None):
        instance = self.get_object()
        instance.is_active = not instance.is_active
        instance.save(update_fields=['is_active'])
        return Response(self.get_serializer(instance).data)


class VenteViewSet(viewsets.ModelViewSet):
    queryset = Vente.objects.all().select_related(
        'client', 'user_affilie', 'user_affilie__role', 'methode_paiement'
    ).prefetch_related(
        'commandes__produit__activations'
    )
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return VenteCreateSerializer
        return VenteSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        
        # Filtres
        date_debut = self.request.query_params.get('date_debut')
        date_fin = self.request.query_params.get('date_fin')
        user_id = self.request.query_params.get('vendeur') or self.request.query_params.get('user_affilie')
        methode_id = self.request.query_params.get('methode_paiement')
        client_id = self.request.query_params.get('client')
        search = self.request.query_params.get('search') or self.request.query_params.get('q')

        if date_debut:
            qs = qs.filter(date__date__gte=date_debut)
        if date_fin:
            qs = qs.filter(date__date__lte=date_fin)
        if user_id:
            qs = qs.filter(user_affilie_id=user_id)
        if methode_id:
            qs = qs.filter(methode_paiement_id=methode_id)
        if client_id:
            qs = qs.filter(client_id=client_id)
        if search:
            search = search.strip()
            qs = qs.filter(
                Q(client__nom__icontains=search) |
                Q(client__numero__icontains=search) |
                Q(id__icontains=search)
            )

        return qs.order_by('-date')

    def create(self, request, *args, **kwargs):
        user = request.user
        is_admin = (
            user.is_staff or 
            user.is_superuser or 
            (user.role and user.role.point >= 50) or 
            (user.role and user.role.nom == 'admin')
        )
        if not is_admin:
            return Response(
                {"error": "Permission refusée. Seul un administrateur (niveau 50) peut enregistrer de nouvelles ventes."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        vente = serializer.save()
        read_serializer = VenteSerializer(vente)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        is_admin = (
            user.is_staff or 
            user.is_superuser or 
            (user.role and user.role.point >= 50) or 
            (user.role and user.role.nom == 'admin')
        )
        if not is_admin:
            return Response(
                {"error": "Permission refusée. Seul un administrateur (niveau 50) peut supprimer des ventes."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Filtres Dashboard
        vendeur_id = request.query_params.get('vendeur') or request.query_params.get('user_affilie')
        date_debut = request.query_params.get('date_debut')
        date_fin = request.query_params.get('date_fin')
        methode_id = request.query_params.get('methode_paiement')

        ventes_qs = Vente.objects.all().prefetch_related('commandes__produit')
        commandes_qs = Commande.objects.select_related('produit', 'vente')

        if vendeur_id:
            ventes_qs = ventes_qs.filter(user_affilie_id=vendeur_id)
            commandes_qs = commandes_qs.filter(vente__user_affilie_id=vendeur_id)
        if date_debut:
            ventes_qs = ventes_qs.filter(date__date__gte=date_debut)
            commandes_qs = commandes_qs.filter(vente__date__date__gte=date_debut)
        if date_fin:
            ventes_qs = ventes_qs.filter(date__date__lte=date_fin)
            commandes_qs = commandes_qs.filter(vente__date__date__lte=date_fin)
        if methode_id:
            ventes_qs = ventes_qs.filter(methode_paiement_id=methode_id)
            commandes_qs = commandes_qs.filter(vente__methode_paiement_id=methode_id)

        # 1. Total KPI
        total_ventes = ventes_qs.count()

        ca_total = 0.0
        marge_nette = 0.0

        for cmd in commandes_qs:
            st = float(cmd.quantite * cmd.prix_unitaire)
            cout = float(cmd.quantite * cmd.produit.prix_achat)
            ca_total += st
            marge_nette += (st - cout)

        # 2. Évolution des ventes par jour
        evolution_ventes = (
            ventes_qs.annotate(jour=TruncDate('date'))
            .values('jour')
            .annotate(nb_ventes=Count('id'))
            .order_by('jour')
        )

        # 3. Répartition par méthode de paiement
        repartition_paiements = (
            ventes_qs.values('methode_paiement__label')
            .annotate(nb_ventes=Count('id'))
            .order_by('-nb_ventes')
        )

        # 4. Top 5 produits les plus vendus
        top_produits = (
            commandes_qs.values('produit__id', 'produit__nom')
            .annotate(
                total_quantite=Sum('quantite'),
                total_ca=Sum(F('quantite') * F('prix_unitaire'), output_field=DecimalField())
            )
            .order_by('-total_quantite')[:5]
        )

        # 5. Classement des vendeurs
        vendeurs_qs = Utilisateur.objects.select_related('role').filter(is_active=True)
        if vendeur_id:
            vendeurs_qs = vendeurs_qs.filter(id=vendeur_id)

        classement_vendeurs = []
        for v in vendeurs_qs:
            user_ventes = v.ventes.all()
            if date_debut:
                user_ventes = user_ventes.filter(date__date__gte=date_debut)
            if date_fin:
                user_ventes = user_ventes.filter(date__date__lte=date_fin)
            if methode_id:
                user_ventes = user_ventes.filter(methode_paiement_id=methode_id)

            nb_v = user_ventes.count()
            ca_v = sum(vente.total for vente in user_ventes)
            pts = v.role.point if v.role else 0
            classement_vendeurs.append({
                'id': v.id,
                'nom_complet': f"{v.prenom} {v.nom}",
                'email': v.email,
                'role': v.role.label if v.role else 'Sans rôle',
                'points': pts,
                'nombre_ventes': nb_v,
                'chiffre_affaires': ca_v
            })

        classement_vendeurs.sort(key=lambda x: (x['chiffre_affaires'], x['points'], x['nombre_ventes']), reverse=True)

        return Response({
            'kpis': {
                'chiffre_affaires': ca_total,
                'marge_nette': marge_nette,
                'nombre_ventes': total_ventes,
            },
            'evolution_ventes': list(evolution_ventes),
            'repartition_paiements': list(repartition_paiements),
            'top_produits': list(top_produits),
            'classement_vendeurs': classement_vendeurs,
        })
