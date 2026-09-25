from django.db import models
from django.conf import settings
from clients.models import Client
from catalog.models import Produit


class MethodePaiement(models.Model):
    label = models.CharField(max_length=100)
    details = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'methode_paiement'
        verbose_name = 'Méthode de paiement'
        verbose_name_plural = 'Méthodes de paiement'

    def __str__(self):
        return self.label


class Vente(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(
        Client,
        on_delete=models.RESTRICT,
        db_column='id_client',
        related_name='ventes'
    )
    user_affilie = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        db_column='id_user_affilie',
        related_name='ventes'
    )
    methode_paiement = models.ForeignKey(
        MethodePaiement,
        on_delete=models.RESTRICT,
        db_column='id_methode_paiement',
        related_name='ventes'
    )

    class Meta:
        db_table = 'vente'
        verbose_name = 'Vente'
        verbose_name_plural = 'Ventes'
        indexes = [
            models.Index(fields=['date'], name='idx_vente_date'),
            models.Index(fields=['client'], name='idx_vente_client'),
            models.Index(fields=['user_affilie'], name='idx_vente_user'),
            models.Index(fields=['methode_paiement'], name='idx_vente_paiement'),
        ]

    def __str__(self):
        return f"Vente #{self.id} - {self.client.nom} ({self.date.strftime('%d/%m/%Y %H:%M')})"

    @property
    def total(self):
        return sum(cmd.quantite * cmd.prix_unitaire for cmd in self.commandes.all())


class Commande(models.Model):
    vente = models.ForeignKey(
        Vente,
        on_delete=models.CASCADE,
        db_column='id_vente',
        related_name='commandes'
    )
    produit = models.ForeignKey(
        Produit,
        on_delete=models.RESTRICT,
        db_column='id_produit',
        related_name='commandes'
    )
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'commande'
        verbose_name = 'Ligne de commande'
        verbose_name_plural = 'Lignes de commande'
        indexes = [
            models.Index(fields=['vente'], name='idx_commande_vente'),
            models.Index(fields=['produit'], name='idx_commande_produit'),
        ]

    def __str__(self):
        return f"{self.quantite}x {self.produit.nom} @ {self.prix_unitaire}"

    @property
    def sous_total(self):
        return self.quantite * self.prix_unitaire
