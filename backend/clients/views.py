from django.db.models import Count
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Provenance, Client
from .serializers import ProvenanceSerializer, ClientSerializer


class ProvenanceViewSet(viewsets.ModelViewSet):
    queryset = Provenance.objects.annotate(annotated_clients_count=Count('clients')).order_by('label')
    serializer_class = ProvenanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Provenance.objects.annotate(annotated_clients_count=Count('clients'))
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(label__icontains=search.strip())
        return qs.order_by('-annotated_clients_count', 'label')

    def destroy(self, request, *args, **kwargs):
        provenance = self.get_object()
        client_count = provenance.clients.count()
        force = request.query_params.get('force', 'false').lower() in ('true', '1')

        if client_count > 0 and not force:
            return Response(
                {
                    'error': f"Impossible de supprimer '{provenance.label}' : {client_count} client(s) y sont rattaché(s).",
                    'client_count': client_count,
                    'can_force': True
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)



class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all().select_related('provenance').prefetch_related('ventes__commandes', 'ventes__methode_paiement')
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['nom', 'numero']

    def get_queryset(self):
        qs = super().get_queryset()
        query = self.request.query_params.get('search')
        if query:
            qs = qs.filter(nom__icontains=query) | qs.filter(numero__icontains=query)
        provenance_id = self.request.query_params.get('provenance')
        if provenance_id:
            qs = qs.filter(provenance_id=provenance_id)
        return qs.order_by('-created_at')

    @action(detail=True, methods=['get'])
    def historique(self, request, pk=None):
        client = self.get_object()
        ventes = client.ventes.all().order_by('-date').prefetch_related('commandes__produit', 'methode_paiement', 'user_affilie')

        data = [
            {
                'id': v.id,
                'date': v.date,
                'vendeur': f"{v.user_affilie.prenom} {v.user_affilie.nom}",
                'methode_paiement': v.methode_paiement.label,
                'total': v.total,
                'commandes': [
                    {
                        'produit_id': cmd.produit.id,
                        'produit_nom': cmd.produit.nom,
                        'quantite': cmd.quantite,
                        'prix_unitaire': cmd.prix_unitaire,
                        'sous_total': cmd.sous_total
                    }
                    for cmd in v.commandes.all()
                ]
            }
            for v in ventes
        ]

        return Response({
            'client_id': client.id,
            'client_nom': client.nom,
            'historique_achats': data
        })
