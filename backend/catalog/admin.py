from django.contrib import admin
from .models import Produit, Prix, Activation


class PrixInline(admin.TabularInline):
    model = Prix
    extra = 1


class ActivationInline(admin.StackedInline):
    model = Activation
    extra = 1


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'prix_achat', 'prix_actif', 'created_at')
    search_fields = ('nom', 'description')
    inlines = [PrixInline, ActivationInline]


@admin.register(Prix)
class PrixAdmin(admin.ModelAdmin):
    list_display = ('id', 'produit', 'prix', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('produit__nom',)


@admin.register(Activation)
class ActivationAdmin(admin.ModelAdmin):
    list_display = ('id', 'produit')
    search_fields = ('produit__nom', 'description_activation')
