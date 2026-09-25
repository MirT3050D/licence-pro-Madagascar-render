from django.db import models


class Produit(models.Model):
    nom = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    image = models.TextField(blank=True, null=True)
    lien_achat = models.TextField(blank=True, null=True)
    prix_achat = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'produit'
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'

    def __str__(self):
        return self.nom

    @property
    def prix_actif(self):
        prix_obj = self.prix_set.filter(is_active=True).order_by('-created_at').first()
        return prix_obj.prix if prix_obj else None


class Prix(models.Model):
    produit = models.ForeignKey(
        Produit,
        on_delete=models.CASCADE,
        db_column='id_produit',
        related_name='prix_set'
    )
    prix = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'prix'
        verbose_name = 'Prix'
        verbose_name_plural = 'Prix'
        indexes = [
            models.Index(fields=['produit', 'is_active'], name='idx_prix_produit_active'),
        ]

    def __str__(self):
        return f"{self.produit.nom} - {self.prix} (Actif: {self.is_active})"


class Activation(models.Model):
    produit = models.ForeignKey(
        Produit,
        on_delete=models.CASCADE,
        db_column='id_produit',
        related_name='activations'
    )
    description_activation = models.TextField()

    class Meta:
        db_table = 'activation'
        verbose_name = 'Activation'
        verbose_name_plural = 'Activations'

    def __str__(self):
        return f"Activation: {self.produit.nom}"
