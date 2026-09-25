from rest_framework import serializers
from django.db import transaction
from .models import MethodePaiement, Vente, Commande, MediaBuyerCommission
from clients.models import Client, Provenance
from catalog.models import Produit
from clients.serializers import ClientSerializer, ProvenanceSerializer
from accounts.models import Utilisateur
from accounts.serializers import UtilisateurSerializer


class MethodePaiementSerializer(serializers.ModelSerializer):
    ventes_count = serializers.IntegerField(source='ventes.count', read_only=True)

    class Meta:
        model = MethodePaiement
        fields = ['id', 'label', 'details', 'is_active', 'ventes_count']


class CommandeSerializer(serializers.ModelSerializer):
    produit_nom = serializers.CharField(source='produit.nom', read_only=True)
    produit_prix_achat = serializers.DecimalField(source='produit.prix_achat', max_digits=12, decimal_places=2, read_only=True)
    produit_image = serializers.CharField(source='produit.image', read_only=True)
    sous_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Commande
        fields = ['id', 'produit', 'produit_nom', 'produit_prix_achat', 'produit_image', 'quantite', 'prix_unitaire', 'sous_total', 'date']


class CommandeItemInputSerializer(serializers.Serializer):
    produit_id = serializers.IntegerField()
    quantite = serializers.IntegerField(min_value=1, default=1)
    prix_unitaire = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)


class VenteSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only=True)
    user_affilie = UtilisateurSerializer(read_only=True)
    methode_paiement = MethodePaiementSerializer(read_only=True)
    commandes = CommandeSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    guides_activation = serializers.SerializerMethodField()

    class Meta:
        model = Vente
        fields = [
            'id', 'date', 'client', 'user_affilie', 'methode_paiement',
            'commandes', 'total', 'guides_activation'
        ]

    def get_guides_activation(self, obj):
        guides = []
        for cmd in obj.commandes.all():
            activation = cmd.produit.activations.first()
            if activation and activation.description_activation:
                guides.append({
                    'produit_id': cmd.produit.id,
                    'produit_nom': cmd.produit.nom,
                    'guide': activation.description_activation
                })
        return guides


class VenteCreateSerializer(serializers.Serializer):
    client_id = serializers.IntegerField()
    user_affilie_id = serializers.IntegerField(required=False, allow_null=True)
    methode_paiement_id = serializers.IntegerField()
    date = serializers.DateTimeField(required=False, allow_null=True)
    articles = CommandeItemInputSerializer(many=True)

    def validate_client_id(self, value):
        if not Client.objects.filter(id=value).exists():
            raise serializers.ValidationError("Client introuvable.")
        return value

    def validate_methode_paiement_id(self, value):
        if not MethodePaiement.objects.filter(id=value).exists():
            raise serializers.ValidationError("Méthode de paiement introuvable.")
        return value

    def validate_articles(self, value):
        if not value:
            raise serializers.ValidationError("La vente doit contenir au moins un article.")
        return value

    def create(self, validated_data):
        request_user = self.context['request'].user
        user_affilie_id = validated_data.get('user_affilie_id')
        if user_affilie_id:
            user_affilie = Utilisateur.objects.filter(id=user_affilie_id).first() or request_user
        else:
            user_affilie = request_user

        client = Client.objects.get(id=validated_data['client_id'])
        methode = MethodePaiement.objects.get(id=validated_data['methode_paiement_id'])
        articles_data = validated_data['articles']
        sale_date = validated_data.get('date')

        with transaction.atomic():
            vente_kwargs = {
                'client': client,
                'user_affilie': user_affilie,
                'methode_paiement': methode,
            }
            if sale_date:
                vente_kwargs['date'] = sale_date

            vente = Vente.objects.create(**vente_kwargs)

            for item in articles_data:
                produit = Produit.objects.get(id=item['produit_id'])
                # Si prix unitaire non spécifié, prendre le prix actif
                prix = item.get('prix_unitaire')
                if prix is None:
                    prix = produit.prix_actif
                    if prix is None:
                        raise serializers.ValidationError(f"Aucun prix actif défini pour le produit '{produit.nom}'.")

                Commande.objects.create(
                    vente=vente,
                    produit=produit,
                    quantite=item['quantite'],
                    prix_unitaire=prix,
                    date=vente.date
                )

        return vente

    def update(self, instance, validated_data):
        user_affilie_id = validated_data.get('user_affilie_id')
        if user_affilie_id is not None:
            instance.user_affilie = Utilisateur.objects.filter(id=user_affilie_id).first() or instance.user_affilie

        if 'client_id' in validated_data:
            instance.client = Client.objects.get(id=validated_data['client_id'])
        if 'methode_paiement_id' in validated_data:
            instance.methode_paiement = MethodePaiement.objects.get(id=validated_data['methode_paiement_id'])
        if 'date' in validated_data and validated_data['date'] is not None:
            instance.date = validated_data['date']

        articles_data = validated_data.get('articles')

        with transaction.atomic():
            instance.save()

            if articles_data is not None:
                instance.commandes.all().delete()
                for item in articles_data:
                    produit = Produit.objects.get(id=item['produit_id'])
                    prix = item.get('prix_unitaire')
                    if prix is None:
                        prix = produit.prix_actif
                        if prix is None:
                            raise serializers.ValidationError(f"Aucun prix actif défini pour le produit '{produit.nom}'.")

                    Commande.objects.create(
                        vente=instance,
                        produit=produit,
                        quantite=item['quantite'],
                        prix_unitaire=prix,
                        date=instance.date
                    )

        return instance


class MediaBuyerCommissionSerializer(serializers.ModelSerializer):
    provenances_details = ProvenanceSerializer(source='provenances', many=True, read_only=True)
    provenances = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Provenance.objects.all(),
        required=False
    )

    class Meta:
        model = MediaBuyerCommission
        fields = [
            'id', 'cout_pub', 'regle_ca', 'regle_benefice', 'seuil_marge',
            'base_recouvrement', 'provenances', 'provenances_details',
            'is_active', 'created_at', 'updated_at'
        ]
