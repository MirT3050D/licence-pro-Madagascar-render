from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count, F, DecimalField, ExpressionWrapper
from django.db.models.functions import TruncDate
from .models import MethodePaiement, Vente, Commande
from .serializers import MethodePaiementSerializer, VenteSerializer, VenteCreateSerializer
from accounts.models import Utilisateur


class MethodePaiementViewSet(viewsets.ModelViewSet):
    queryset = MethodePaiement.objects.all()
    serializer_class = MethodePaiementSerializer
    permission_classes = [permissions.IsAuthenticated]


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
        user_id = self.request.query_params.get('vendeur')
        methode_id = self.request.query_params.get('methode_paiement')
        client_id = self.request.query_params.get('client')

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

        return qs.order_by('-date')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        vente = serializer.save()
        read_serializer = VenteSerializer(vente)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)


class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # 1. Total KPI
        ventes = Vente.objects.all().prefetch_related('commandes__produit')
        total_ventes = ventes.count()

        # Calcul Chiffre d'Affaires et Marge Nette
        commandes = Commande.objects.select_related('produit')
        ca_total = 0.0
        marge_nette = 0.0

        for cmd in commandes:
            st = float(cmd.quantite * cmd.prix_unitaire)
            cout = float(cmd.quantite * cmd.produit.prix_achat)
            ca_total += st
            marge_nette += (st - cout)

        # 2. Évolution des ventes par jour (30 derniers jours)
        evolution_ventes = (
            Vente.objects.annotate(jour=TruncDate('date'))
            .values('jour')
            .annotate(nb_ventes=Count('id'))
            .order_by('jour')
        )

        # 3. Répartition par méthode de paiement
        repartition_paiements = (
            Vente.objects.values('methode_paiement__label')
            .annotate(nb_ventes=Count('id'))
            .order_by('-nb_ventes')
        )

        # 4. Top 5 produits les plus vendus
        top_produits = (
            Commande.objects.values('produit__id', 'produit__nom')
            .annotate(
                total_quantite=Sum('quantite'),
                total_ca=Sum(F('quantite') * F('prix_unitaire'), output_field=DecimalField())
            )
            .order_by('-total_quantite')[:5]
        )

        # 5. Classement des points par vendeur
        vendeurs = Utilisateur.objects.select_related('role').all()
        classement_vendeurs = []
        for v in vendeurs:
            nb_v = v.ventes.count()
            ca_v = sum(vente.total for vente in v.ventes.all())
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
        
        classement_vendeurs.sort(key=lambda x: (x['points'], x['nombre_ventes']), reverse=True)

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
