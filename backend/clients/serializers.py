from rest_framework import serializers
from .models import Provenance, Client


class ProvenanceSerializer(serializers.ModelSerializer):
    clients_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Provenance
        fields = ['id', 'label', 'clients_count']

    def get_clients_count(self, obj):
        if hasattr(obj, 'annotated_clients_count'):
            return obj.annotated_clients_count
        return obj.clients.count()



class ClientSerializer(serializers.ModelSerializer):
    provenance = ProvenanceSerializer(read_only=True)
    provenance_id = serializers.PrimaryKeyRelatedField(
        queryset=Provenance.objects.all(),
        source='provenance',
        write_only=True,
        required=False,
        allow_null=True
    )
    ventes_count = serializers.SerializerMethodField()
    total_achats = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = [
            'id', 'nom', 'numero', 'provenance', 'provenance_id',
            'created_at', 'ventes_count', 'total_achats'
        ]

    def get_ventes_count(self, obj):
        return obj.ventes.count()

    def get_total_achats(self, obj):
        return sum(v.total for v in obj.ventes.all())
