from django.core.management.base import BaseCommand
from django.db import transaction, connection
from django.contrib.admin.models import LogEntry
from accounts.models import Role, Utilisateur
from catalog.models import Produit, Prix, Activation
from clients.models import Client, Provenance
from sales.models import Vente, Commande, MethodePaiement


class Command(BaseCommand):
    help = (
        "Remet à zéro toutes les données (ventes, commandes, clients, catalogue, "
        "méthodes de paiement, provenances) en conservant les rôles et l'utilisateur principal."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help="Exécuter la réinitialisation sans confirmation interactive"
        )
        parser.add_argument(
            '--preserve-email',
            type=str,
            default='rahajarijaonamir@gmail.com',
            help="Email du compte utilisateur principal à conserver (défaut: rahajarijaonamir@gmail.com)"
        )

    def handle(self, *args, **options):
        preserve_email = options['preserve_email'].strip().lower()
        force = options.get('force', False)

        self.stdout.write(self.style.MIGRATE_HEADING("\n=== RÉINITIALISATION COMPLÈTE DES DONNÉES ==="))

        # Vérification des utilisateurs
        main_user = Utilisateur.objects.filter(email__iexact=preserve_email).first()
        if not main_user:
            self.stdout.write(self.style.ERROR(
                f"ERREUR : L'utilisateur principal '{preserve_email}' est introuvable !\n"
                f"Opération annulée par sécurité pour éviter de supprimer tous les comptes."
            ))
            return

        demo_users = Utilisateur.objects.exclude(id=main_user.id)

        # Comptages actuels
        counts = {
            'commandes': Commande.objects.count(),
            'ventes': Vente.objects.count(),
            'clients': Client.objects.count(),
            'activations': Activation.objects.count(),
            'prix': Prix.objects.count(),
            'produits': Produit.objects.count(),
            'methodes': MethodePaiement.objects.count(),
            'provenances': Provenance.objects.count(),
            'demo_users': demo_users.count(),
            'roles': Role.objects.count(),
        }

        self.stdout.write("\nDonnées à supprimer :")
        self.stdout.write(f"- Lignes de commande : {counts['commandes']}")
        self.stdout.write(f"- Ventes : {counts['ventes']}")
        self.stdout.write(f"- Clients : {counts['clients']}")
        self.stdout.write(f"- Activations produits : {counts['activations']}")
        self.stdout.write(f"- Prix produits : {counts['prix']}")
        self.stdout.write(f"- Produits : {counts['produits']}")
        self.stdout.write(f"- Méthodes de paiement : {counts['methodes']}")
        self.stdout.write(f"- Provenances clients : {counts['provenances']}")
        self.stdout.write(f"- Comptes démo / secondaires : {counts['demo_users']} ({', '.join(u.email for u in demo_users)})")

        self.stdout.write("\nDonnées conservées :")
        self.stdout.write(f"- Utilisateur principal : {main_user.email} ({main_user.prenom} {main_user.nom})")
        self.stdout.write(f"- Rôles système : {counts['roles']} ({', '.join(r.nom for r in Role.objects.all())})")

        if not force:
            rep = input("\nÊtes-vous sûr de vouloir remettre ces données à zéro ? (o/N) : ").strip().lower()
            if rep not in ['o', 'oui', 'y', 'yes']:
                self.stdout.write(self.style.WARNING("Opération annulée."))
                return

        with transaction.atomic():
            # 1. Nettoyage de l'historique admin
            LogEntry.objects.all().delete()

            # 2. Suppression dans l'ordre strict des dépendances
            del_commandes = Commande.objects.all().delete()[0]
            del_ventes = Vente.objects.all().delete()[0]
            del_clients = Client.objects.all().delete()[0]
            del_activations = Activation.objects.all().delete()[0]
            del_prix = Prix.objects.all().delete()[0]
            del_produits = Produit.objects.all().delete()[0]
            del_methodes = MethodePaiement.objects.all().delete()[0]
            del_provenances = Provenance.objects.all().delete()[0]
            del_users = demo_users.delete()[0]

            # 3. S'assurer que le compte principal conserve les privilèges staff / superuser
            main_user.is_staff = True
            main_user.is_superuser = True
            main_user.save()

            # 4. Réinitialisation des séquences (IDs recommenceront à 1)
            tables_to_reset = [
                'commande',
                'vente',
                'client',
                'activation',
                'prix',
                'produit',
                'methode_paiement',
                'provenance',
            ]

            vendor = connection.vendor
            with connection.cursor() as cursor:
                if vendor == 'postgresql':
                    for table in tables_to_reset:
                        seq_name = f"{table}_id_seq"
                        try:
                            cursor.execute(f"ALTER SEQUENCE {seq_name} RESTART WITH 1;")
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f"Note séquence {seq_name}: {e}"))
                elif vendor == 'sqlite':
                    for table in tables_to_reset:
                        try:
                            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name = '{table}';")
                        except Exception:
                            pass

        self.stdout.write(self.style.SUCCESS(
            "\n Réinitialisation terminée avec succès !\n"
            f"- {del_commandes} ligne(s) de commande supprimée(s)\n"
            f"- {del_ventes} vente(s) supprimée(s)\n"
            f"- {del_clients} client(s) supprimé(s)\n"
            f"- {del_activations} activation(s) supprimée(s)\n"
            f"- {del_prix} tarif(s) supprimé(s)\n"
            f"- {del_produits} produit(s) supprimé(s)\n"
            f"- {del_methodes} méthode(s) de paiement supprimée(s)\n"
            f"- {del_provenances} provenance(s) supprimée(s)\n"
            f"- {del_users} utilisateur(s) démo supprimé(s)\n"
            f"Les séquences d'identifiants ont été réinitialisées à 1.\n"
            f"Utilisateur actif conservé : {main_user.email} (Administrateur)"
        ))
