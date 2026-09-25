from django.db import models
from django.conf import settings
from django.utils import timezone
from clients.models import Client, Provenance
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
    date = models.DateTimeField(default=timezone.now)
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
    date = models.DateTimeField(default=timezone.now)

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


class MediaBuyerCommission(models.Model):
    cout_pub = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name="Coût de publicité (Ar)"
    )
    regle_ca = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.00,
        verbose_name="Taux com sur CA si marge > seuil (%)"
    )
    regle_benefice = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=30.00,
        verbose_name="Taux com sur Bénéfice si marge <= seuil (%)"
    )
    seuil_marge = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=40.00,
        verbose_name="Seuil de marge bénéficiaire (%)"
    )
    base_recouvrement = models.CharField(
        max_length=20,
        default='benefice',
        choices=[
            ('benefice', 'Bénéfice brut'),
            ('ca', "Chiffre d'affaires"),
        ],
        verbose_name="Base de recouvrement du coût pub"
    )
    provenances = models.ManyToManyField(
        Provenance,
        blank=True,
        related_name='media_buyer_commissions',
        verbose_name="Provenances éligibles"
    )
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'media_buyer_commission'
        verbose_name = 'Commission Media Buyer'
        verbose_name_plural = 'Commissions Media Buyer'

    def __str__(self):
        return f"Commission MB #{self.id} (Coût pub: {self.cout_pub} Ar, CA: {self.regle_ca}%, Marge: {self.regle_benefice}%)"
