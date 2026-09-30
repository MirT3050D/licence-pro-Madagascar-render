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


class Fournisseur(models.Model):
    nom = models.CharField(max_length=150, unique=True, verbose_name="Nom du fournisseur")
    contact = models.CharField(max_length=255, blank=True, null=True, verbose_name="Contact / Référence")
    site_web = models.CharField(max_length=500, blank=True, null=True, verbose_name="Site web / Lien portail")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes / Informations")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fournisseur'
        verbose_name = 'Fournisseur'
        verbose_name_plural = 'Fournisseurs'
        ordering = ['nom']

    def __str__(self):
        return self.nom


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
    fournisseur = models.ForeignKey(
        Fournisseur,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        db_column='id_fournisseur',
        related_name='ventes',
        verbose_name="Fournisseur"
    )
    numero_commande_fournisseur = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_column='numero_commande_fournisseur',
        verbose_name="Numéro de commande fournisseur"
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
            models.Index(fields=['fournisseur'], name='idx_vente_fournisseur'),
            models.Index(fields=['numero_commande_fournisseur'], name='idx_vente_num_cmd_fourn'),
        ]

    def __str__(self):
        cmd_info = f" [Cmd: {self.numero_commande_fournisseur}]" if self.numero_commande_fournisseur else ""
        fourn_info = f" [{self.fournisseur.nom}]" if self.fournisseur else ""
        return f"Vente #{self.id}{fourn_info}{cmd_info} - {self.client.nom} ({self.date.strftime('%d/%m/%Y %H:%M')})"

    @property
    def numero_commande(self):
        return self.numero_commande_fournisseur

    @numero_commande.setter
    def numero_commande(self, value):
        self.numero_commande_fournisseur = value

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
