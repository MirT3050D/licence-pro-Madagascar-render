from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import Role, Utilisateur
from clients.models import Provenance, Client
from catalog.models import Produit, Prix, Activation
from sales.models import MethodePaiement, Vente, Commande


class Command(BaseCommand):
    help = 'Peuple la base de données avec des données de test initiales.'

    def handle(self, *args, **options):
        self.stdout.write("Génération des données initiales...")

        with transaction.atomic():
            # 1. Rôles
            role_admin, _ = Role.objects.get_or_create(
                nom='admin',
                defaults={'label': 'Administrateur', 'point': 100}
            )
            role_vendeur, _ = Role.objects.get_or_create(
                nom='vendeur',
                defaults={'label': 'Affilié / Vendeur', 'point': 10}
            )

            # 2. Utilisateurs
            if not Utilisateur.objects.filter(email='admin@licencepro.mg').exists():
                admin_user = Utilisateur.objects.create_superuser(
                    email='admin@licencepro.mg',
                    password='adminpassword123',
                    nom='Rakoto',
                    prenom='Admin',
                    numero='0340000001',
                    role=role_admin
                )
                self.stdout.write(self.style.SUCCESS("Superadmin créé: admin@licencepro.mg / adminpassword123"))

            vendeur_user, created = Utilisateur.objects.get_or_create(
                email='vendeur@licencepro.mg',
                defaults={
                    'nom': 'Rabe',
                    'prenom': 'Jean',
                    'numero': '0340000002',
                    'role': role_vendeur
                }
            )
            if created:
                vendeur_user.set_password('vendeurpassword123')
                vendeur_user.save()
                self.stdout.write(self.style.SUCCESS("Vendeur créé: vendeur@licencepro.mg / vendeurpassword123"))

            # 3. Provenances
            prov_fb, _ = Provenance.objects.get_or_create(label='Facebook')
            prov_wa, _ = Provenance.objects.get_or_create(label='WhatsApp')
            prov_bouche, _ = Provenance.objects.get_or_create(label='Bouche à oreille')
            prov_web, _ = Provenance.objects.get_or_create(label='Site Web')

            # 4. Méthodes de paiement
            mp_mvola, _ = MethodePaiement.objects.get_or_create(
                label='MVola',
                defaults={'details': '034 11 222 33 (RAKOTO)', 'is_active': True}
            )
            mp_orange, _ = MethodePaiement.objects.get_or_create(
                label='Orange Money',
                defaults={'details': '032 44 555 66 (RAKOTO)', 'is_active': True}
            )
            mp_airtel, _ = MethodePaiement.objects.get_or_create(
                label='Airtel Money',
                defaults={'details': '033 77 888 99 (RAKOTO)', 'is_active': True}
            )
            mp_cash, _ = MethodePaiement.objects.get_or_create(
                label='Espèces',
                defaults={'details': 'Paiement en boutique / comptoir', 'is_active': True}
            )

            # 5. Clients
            c1, _ = Client.objects.get_or_create(
                nom='Société ABC Tech',
                defaults={'numero': '0341234567', 'provenance': prov_fb}
            )
            c2, _ = Client.objects.get_or_create(
                nom='Andry Rasolofo',
                defaults={'numero': '0329876543', 'provenance': prov_wa}
            )

            # 6. Produits, Prix et Activations
            prods_data = [
                {
                    'nom': 'Windows 11 Pro',
                    'description': 'Licence officielle OEM / Retail à vie pour 1 PC',
                    'prix_achat': 15000.00,
                    'prix_vente': 35000.00,
                    'activation': '1. Allez dans Paramètres > Système > Activation.\n2. Cliquez sur "Modifier la clé de produit".\n3. Entrez la clé fournie et validez en étant connecté à Internet.'
                },
                {
                    'nom': 'Microsoft Office 365 Pro Plus',
                    'description': 'Abonnement 1 an pour 5 appareils (PC, Mac, Mobile) avec 1 To OneDrive',
                    'prix_achat': 25000.00,
                    'prix_vente': 55000.00,
                    'activation': '1. Rendez-vous sur https://portal.office.com\n2. Connectez-vous avec l\'identifiant et mot de passe temporaire fournis.\n3. Changez votre mot de passe et téléchargez le pack Office.'
                },
                {
                    'nom': 'Kaspersky Total Security 1 An',
                    'description': 'Antivirus complet pour 1 appareil pendant 12 mois',
                    'prix_achat': 20000.00,
                    'prix_vente': 45000.00,
                    'activation': '1. Téléchargez Kaspersky depuis le site officiel.\n2. Ouvrez l\'application et entrez le code d\'activation.\n3. Associez à votre compte My Kaspersky.'
                },
                {
                    'nom': 'Canva Pro 1 An',
                    'description': 'Accès à toutes les fonctionnalités premium, modèles et banques d\'images',
                    'prix_achat': 10000.00,
                    'prix_vente': 25000.00,
                    'activation': '1. Ouvrez l\'email d\'invitation reçu sur votre boîte mail.\n2. Cliquez sur "Rejoindre l\'équipe".\n3. Connectez-vous ou créez votre compte Canva.'
                },
            ]

            created_prods = []
            for p_info in prods_data:
                prod, p_created = Produit.objects.get_or_create(
                    nom=p_info['nom'],
                    defaults={
                        'description': p_info['description'],
                        'prix_achat': p_info['prix_achat'],
                    }
                )
                if p_created:
                    Prix.objects.create(
                        produit=prod,
                        prix=p_info['prix_vente'],
                        is_active=True
                    )
                    Activation.objects.create(
                        produit=prod,
                        description_activation=p_info['activation']
                    )
                created_prods.append(prod)

            # 7. Ventes de test
            if not Vente.objects.exists():
                v1 = Vente.objects.create(
                    client=c1,
                    user_affilie=vendeur_user,
                    methode_paiement=mp_mvola
                )
                Commande.objects.create(
                    vente=v1,
                    produit=created_prods[0],
                    quantite=2,
                    prix_unitaire=created_prods[0].prix_actif
                )
                Commande.objects.create(
                    vente=v1,
                    produit=created_prods[1],
                    quantite=1,
                    prix_unitaire=created_prods[1].prix_actif
                )

                v2 = Vente.objects.create(
                    client=c2,
                    user_affilie=vendeur_user,
                    methode_paiement=mp_orange
                )
                Commande.objects.create(
                    vente=v2,
                    produit=created_prods[2],
                    quantite=1,
                    prix_unitaire=created_prods[2].prix_actif
                )

        self.stdout.write(self.style.SUCCESS("Base de données initialisée avec succès !"))
