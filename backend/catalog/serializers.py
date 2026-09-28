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
    prix_vente = serializers.DecimalField(max_digits=12, decimal_places=2, write_only=True, required=False)
    description_activation = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    # Detail fields
    prix_historique = PrixSerializer(source='prix_set', many=True, read_only=True)
    activations = ActivationSerializer(many=True, read_only=True)

    class Meta:
        model = Produit
        fields = [
            'id', 'nom', 'description', 'image', 'lien_achat',
            'prix_achat', 'prix_actif', 'prix_initial', 'prix_vente', 'description_activation',
            'prix_historique', 'activations', 'created_at'
        ]

    def create(self, validated_data):
        prix_initial = validated_data.pop('prix_vente', None)
        if prix_initial is None:
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

    def update(self, instance, validated_data):
        prix_nouveau = validated_data.pop('prix_vente', None)
        if prix_nouveau is None:
            prix_nouveau = validated_data.pop('prix_initial', None)
        desc_activation = validated_data.pop('description_activation', None)

        with transaction.atomic():
            # Update Produit scalar fields
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            # Update active selling price if provided and different
            if prix_nouveau is not None:
                current_price = instance.prix_actif
                if current_price is None or float(current_price) != float(prix_nouveau):
                    Prix.objects.filter(produit=instance, is_active=True).update(is_active=False)
                    Prix.objects.create(
                        produit=instance,
                        prix=prix_nouveau,
                        is_active=True
                    )

            # Update or create activation guide if provided
            if desc_activation is not None:
                Activation.objects.update_or_create(
                    produit=instance,
                    defaults={'description_activation': desc_activation}
                )

        # Clear prefetched cache to return fresh relations
        if hasattr(instance, '_prefetched_objects_cache'):
            instance._prefetched_objects_cache.clear()

        return instance
