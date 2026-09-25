from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import Produit, Prix, Activation
from .serializers import ProduitSerializer, PrixSerializer, ActivationSerializer


class ProduitViewSet(viewsets.ModelViewSet):
    queryset = Produit.objects.all().prefetch_related('prix_set', 'activations')
    serializer_class = ProduitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        query = self.request.query_params.get('search')
        if query:
            qs = qs.filter(nom__icontains=query) | qs.filter(description__icontains=query)
        return qs.order_by('-created_at')

    @action(detail=True, methods=['post'], url_path='changer-prix')
    def changer_prix(self, request, pk=None):
        produit = self.get_object()
        nouveau_prix = request.data.get('prix')

        if nouveau_prix is None:
            return Response({'error': 'Le champ prix est obligatoire.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            val_prix = float(nouveau_prix)
            if val_prix < 0:
                raise ValueError()
        except ValueError:
            return Response({'error': 'Prix invalide.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # Désactiver tous les prix précédents pour ce produit
            Prix.objects.filter(produit=produit, is_active=True).update(is_active=False)

            # Créer le nouveau prix actif
            prix_obj = Prix.objects.create(
                produit=produit,
                prix=val_prix,
                is_active=True
            )

        return Response(PrixSerializer(prix_obj).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'post'], url_path='activation')
    def guide_activation(self, request, pk=None):
        produit = self.get_object()
        if request.method == 'GET':
            activation = produit.activations.first()
            if not activation:
                return Response({'description_activation': ''})
            return Response(ActivationSerializer(activation).data)

        desc = request.data.get('description_activation', '')
        activation, _ = Activation.objects.update_or_create(
            produit=produit,
            defaults={'description_activation': desc}
        )
        return Response(ActivationSerializer(activation).data)


class PrixViewSet(viewsets.ModelViewSet):
    queryset = Prix.objects.all()
    serializer_class = PrixSerializer
    permission_classes = [permissions.IsAuthenticated]


class ActivationViewSet(viewsets.ModelViewSet):
    queryset = Activation.objects.all()
    serializer_class = ActivationSerializer
    permission_classes = [permissions.IsAuthenticated]
