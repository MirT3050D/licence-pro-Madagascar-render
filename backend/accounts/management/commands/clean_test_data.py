from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import Utilisateur
from sales.models import Vente, Commande
from clients.models import Client


class Command(BaseCommand):
    help = "Nettoie les données de test (ventes fictives, clients de test, comptes de démo admin@/vendeur@licencepro.mg)."

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help="Exécuter le nettoyage sans confirmation interactive"
        )
        parser.add_argument(
            '--keep-demo-accounts',
            action='store_true',
            help="Conserver les comptes admin@licencepro.mg et vendeur@licencepro.mg"
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("=== Nettoyage des données de test de production ==="))

        test_emails = ['admin@licencepro.mg', 'vendeur@licencepro.mg']
        demo_users = Utilisateur.objects.filter(email__in=test_emails)
        demo_clients = Client.objects.filter(nom__in=['Société ABC Tech', 'Andry Rasolofo'])

        self.stdout.write("Éléments de test détectés :")
        self.stdout.write(f"- Utilisateurs démo : {demo_users.count()} ({', '.join(u.email for u in demo_users)})")
        self.stdout.write(f"- Clients démo : {demo_clients.count()} ({', '.join(c.nom for c in demo_clients)})")
        self.stdout.write(f"- Total des ventes existantes : {Vente.objects.count()}")
        self.stdout.write(f"- Total des lignes de commande : {Commande.objects.count()}")

        if not options.get('force'):
            rep = input("\nÊtes-vous sûr de vouloir supprimer ces données de test ? (o/N) : ").strip().lower()
            if rep not in ['o', 'oui', 'y', 'yes']:
                self.stdout.write(self.style.WARNING("Opération annulée."))
                return

        with transaction.atomic():
            # 1. Supprimer les commandes et les ventes associées
            nb_commandes = Commande.objects.all().delete()[0]
            nb_ventes = Vente.objects.all().delete()[0]

            # 2. Supprimer les clients démo
            nb_clients = demo_clients.delete()[0]

            # 3. Supprimer les comptes démo si non protégés
            nb_users = 0
            if not options.get('keep_demo_accounts'):
                nb_users = demo_users.delete()[0]

        self.stdout.write(self.style.SUCCESS(
            f"\n Nettoyage terminé avec succès !\n"
            f"- {nb_commandes} ligne(s) de commande supprimée(s)\n"
            f"- {nb_ventes} vente(s) test supprimée(s)\n"
            f"- {nb_clients} client(s) démo supprimé(s)\n"
            f"- {nb_users} utilisateur(s) test supprimé(s)\n"
            f"La base de données est maintenant prête pour votre exploitation commerciale réelle."
        ))
