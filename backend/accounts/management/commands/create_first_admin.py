from django.core.management.base import BaseCommand
import getpass
from accounts.models import Role, Utilisateur


class Command(BaseCommand):
    help = "Crée ou met à jour le premier compte Administrateur de production pour Licence Pro Madagascar."

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help="Adresse email de l'administrateur")
        parser.add_argument('--password', type=str, help="Mot de passe de l'administrateur")
        parser.add_argument('--nom', type=str, help="Nom de famille")
        parser.add_argument('--prenom', type=str, help="Prénom")
        parser.add_argument('--numero', type=str, default='', help="Numéro de téléphone")

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("=== Création du premier Administrateur (Production) ==="))

        email = options.get('email')
        while not email:
            email = input("Adresse email: ").strip()

        nom = options.get('nom')
        while not nom:
            nom = input("Nom: ").strip()

        prenom = options.get('prenom')
        while not prenom:
            prenom = input("Prénom: ").strip()

        numero = options.get('numero')
        if numero is None or numero == '':
            numero = input("Numéro de téléphone (optionnel): ").strip()

        password = options.get('password')
        while not password:
            password = getpass.getpass("Mot de passe: ").strip()
            password_confirm = getpass.getpass("Confirmez le mot de passe: ").strip()
            if password != password_confirm:
                self.stdout.write(self.style.ERROR("Les mots de passe ne correspondent pas. Réessayez."))
                password = None
            elif len(password) < 6:
                self.stdout.write(self.style.WARNING("Le mot de passe doit comporter au moins 6 caractères."))
                password = None

        # 1. S'assurer que le rôle 'admin' existe
        role_admin, _ = Role.objects.get_or_create(
            nom='admin',
            defaults={'label': 'Administrateur', 'point': 100}
        )

        # 2. Créer ou mettre à jour l'utilisateur
        user, created = Utilisateur.objects.get_or_create(
            email__iexact=email,
            defaults={
                'email': email.lower(),
                'nom': nom,
                'prenom': prenom,
                'numero': numero,
                'role': role_admin,
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            }
        )

        if not created:
            user.nom = nom
            user.prenom = prenom
            user.numero = numero
            user.role = role_admin
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            self.stdout.write(self.style.WARNING(f"Le compte {email} existait déjà. Mise à jour de ses droits d'administrateur."))

        user.set_password(password)
        user.save()

        self.stdout.write(self.style.SUCCESS(
            f"\n Succès ! Le compte Administrateur '{user.email}' a été enregistré dans la base de données.\n"
            f"Vous pouvez vous connecter directement sur l'application avec ces identifiants."
        ))
