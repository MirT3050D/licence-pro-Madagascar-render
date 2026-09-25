from django.contrib import admin
from .models import Provenance, Client


@admin.register(Provenance)
class ProvenanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'label')
    search_fields = ('label',)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'numero', 'provenance', 'created_at')
    list_filter = ('provenance', 'created_at')
    search_fields = ('nom', 'numero')
