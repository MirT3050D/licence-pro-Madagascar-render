from django.contrib import admin
from .models import MethodePaiement, Vente, Commande, MediaBuyerCommission


class CommandeInline(admin.TabularInline):
    model = Commande
    extra = 1


@admin.register(MethodePaiement)
class MethodePaiementAdmin(admin.ModelAdmin):
    list_display = ('id', 'label', 'details', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('label', 'details')


@admin.register(Vente)
class VenteAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'client', 'user_affilie', 'methode_paiement', 'get_total')
    list_filter = ('date', 'methode_paiement', 'user_affilie')
    search_fields = ('client__nom', 'user_affilie__email', 'user_affilie__nom')
    inlines = [CommandeInline]

    @admin.display(description='Total')
    def get_total(self, obj):
        return f"{obj.total} Ar"


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'vente', 'produit', 'quantite', 'prix_unitaire', 'get_sous_total', 'date')
    list_filter = ('date', 'produit')
    search_fields = ('produit__nom', 'vente__client__nom')

    @admin.display(description='Sous-total')
    def get_sous_total(self, obj):
        return f"{obj.sous_total} Ar"


@admin.register(MediaBuyerCommission)
class MediaBuyerCommissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'cout_pub', 'regle_ca', 'regle_benefice', 'seuil_marge', 'base_recouvrement', 'is_active', 'updated_at')
    filter_horizontal = ('provenances',)
