from django.db import models


class Provenance(models.Model):
    label = models.CharField(max_length=100)

    class Meta:
        db_table = 'provenance'
        verbose_name = 'Provenance'
        verbose_name_plural = 'Provenances'

    def __str__(self):
        return self.label


class Client(models.Model):
    nom = models.CharField(max_length=150)
    numero = models.CharField(max_length=30, blank=True, null=True)
    provenance = models.ForeignKey(
        Provenance,
        on_delete=models.SET_NULL,
        db_column='id_provenance',
        null=True,
        blank=True,
        related_name='clients'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'client'
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

    def __str__(self):
        return self.nom
