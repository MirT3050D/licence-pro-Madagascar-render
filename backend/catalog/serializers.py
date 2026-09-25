from rest_framework import serializers
from django.db import transaction
from .models import Produit, Prix, Activation


class PrixSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prix
        fields = ['id', 'produit', 'prix', 'created_at', 'is_active']
        read_only_fields = ['created_at']


class ActivationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activation
        fields = ['id', 'produit', 'description_activation']


class ProduitSerializer(serializers.ModelSerializer):
    prix_actif = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    prix_initial = serializers.DecimalField(max_digits=12, decimal_places=2, write_only=True, required=False)
    description_activation = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    # Detail fields
    prix_historique = PrixSerializer(source='prix_set', many=True, read_only=True)
    activations = ActivationSerializer(many=True, read_only=True)

    class Meta:
        model = Produit
        fields = [
            'id', 'nom', 'description', 'image', 'lien_achat',
            'prix_achat', 'prix_actif', 'prix_initial', 'description_activation',
            'prix_historique', 'activations', 'created_at'
        ]

    def create(self, validated_data):
        prix_initial = validated_data.pop('prix_initial', None)
        desc_activation = validated_data.pop('description_activation', None)

        with transaction.atomic():
            produit = Produit.objects.create(**validated_data)
            
            # Initial active price
            if prix_initial is not None:
                Prix.objects.create(
                    produit=produit,
                    prix=prix_initial,
                    is_active=True
                )
            
            # Initial activation guide
            if desc_activation:
                Activation.objects.create(
                    produit=produit,
                    description_activation=desc_activation
                )

        return produit
