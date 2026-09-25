from django.core.management.base import BaseCommand
from django.db import transaction
from catalog.models import Produit, Prix, Activation

CATALOG_DATA = [
    # GOOGLE AI PRO
    {
        "nom": "Google AI Pro (3 mois)",
        "description": "Abonnement Google One AI Premium (Gemini Advanced 1.5 Pro / 2.0) avec 2 To de stockage cloud pendant 3 mois.",
        "prix_vente": 29000,
        "prix_achat": 15000,
        "guide": "1. Rendez-vous sur one.google.com\n2. Connectez-vous avec votre compte Google personnel.\n3. Acceptez l'invitation membre de la famille ou appliquez le lien d'activation fourni par Licence Pro Madagascar."
    },
    {
        "nom": "Google AI Pro (12 mois)",
        "description": "Abonnement 1 an complet à Google AI Pro (Gemini Advanced, intégration Workspace et 2 To de stockage).",
        "prix_vente": 49000,
        "prix_achat": 25000,
        "guide": "1. Connectez-vous sur one.google.com avec votre compte Gmail.\n2. Cliquez sur le lien d'activation sécurisé transmis par notre équipe.\n3. Profitez de Gemini Advanced et des 2 To pendant 1 an."
    },
    {
        "nom": "Google AI Pro (18 mois)",
        "description": "Abonnement longue durée 18 mois à Google AI Pro (Gemini Advanced, 2 To de stockage cloud Google One).",
        "prix_vente": 89000,
        "prix_achat": 45000,
        "guide": "1. Rendez-vous sur one.google.com\n2. Validez le lien d'invitation sécurisé transmis par Licence Pro Madagascar.\n3. Accès garanti pendant 18 mois complets."
    },

    # SYSTEMES D'EXPLOITATION WINDOWS
    {
        "nom": "Windows 11 Home",
        "description": "Licence authentique Microsoft Windows 11 Famille (Home) 64-bit. Clé d'activation officielle à vie pour 1 PC.",
        "prix_vente": 39000,
        "prix_achat": 15000,
        "guide": "1. Ouvrez Paramètres > Système > Activation.\n2. Cliquez sur 'Modifier la clé de produit'.\n3. Saisissez votre clé à 25 caractères (XXXXX-XXXXX-XXXXX-XXXXX-XXXXX).\n4. Cliquez sur 'Activer' en étant connecté à Internet."
    },
    {
        "nom": "Windows 11 Pro",
        "description": "Licence authentique Microsoft Windows 11 Professionnel 64-bit. Inclut BitLocker, Bureau à distance et Hyper-V. Clé perpétuelle à vie pour 1 PC.",
        "prix_vente": 49000,
        "prix_achat": 18000,
        "guide": "1. Allez dans Paramètres Windows > Système > Activation.\n2. Cliquez sur 'Modifier la clé de produit'.\n3. Entrez la clé officielle fournie.\n4. Si vous migrez depuis Windows 11 Home vers Pro, le système redémarrera pour installer les composants Pro automatiquement."
    },

    # SUITE BUREAUTIQUE MICROSOFT OFFICE
    {
        "nom": "Office 2019 Pro Plus",
        "description": "Suite complète Microsoft Office 2019 Professionnel Plus (Word, Excel, PowerPoint, Outlook, Access, Publisher). Licence perpétuelle à vie pour 1 PC.",
        "prix_vente": 39000,
        "prix_achat": 15000,
        "guide": "1. Téléchargez l'installateur officiel Microsoft sur setup.office.com.\n2. Installez la suite bureautique.\n3. Lancez Word ou Excel et entrez la clé de produit à 25 caractères pour valider l'activation en ligne."
    },
    {
        "nom": "Office 2021 Pro Plus",
        "description": "Dernière version sans abonnement de Microsoft Office 2021 Professionnel Plus. Performance accrue, mode sombre et nouvelles formules Excel. Licence à vie pour 1 PC.",
        "prix_vente": 49000,
        "prix_achat": 20000,
        "guide": "1. Téléchargez l'ISO ou installateur officiel via setup.office.com.\n2. Procédez à l'installation complète.\n3. Ouvrez n'importe quelle application Office et saisissez votre clé d'activation officielle."
    },
    {
        "nom": "Office 365",
        "description": "Abonnement Microsoft 365 (Famille / Personnel) 1 an pour jusqu'à 5 appareils (PC, Mac, Tablettes, Mobiles) avec 1 To de stockage cloud OneDrive.",
        "prix_vente": 199000,
        "prix_achat": 110000,
        "guide": "1. Rendez-vous sur microsoft365.com/setup\n2. Connectez-vous avec votre compte Microsoft.\n3. Saisissez votre code d'activation de 25 caractères pour lier l'abonnement d'1 an et télécharger les applications sur vos 5 appareils."
    },

    # CREATION & DESIGN
    {
        "nom": "Canva Pro (1 an)",
        "description": "Abonnement Canva Pro 1 an. Accès illimité à plus de 100 millions de modèles, photos, vidéos, suppression d'arrière-plan en 1 clic et redimensionnement magique.",
        "prix_vente": 69000,
        "prix_achat": 30000,
        "guide": "1. Créez ou connectez-vous à votre compte sur canva.com\n2. Cliquez sur le lien d'invitation d'équipe Canva Pro envoyé par Licence Pro Madagascar.\n3. Votre compte bascule immédiatement en statut Pro avec tous les éléments débloqués."
    },

    # SECURITE & ANTIMALWARE
    {
        "nom": "CCleaner (1 an - 1 appareil)",
        "description": "Licence CCleaner Professional 1 an pour 1 PC. Nettoyage approfondi, mise à jour automatique des pilotes et optimisation du démarrage.",
        "prix_vente": 49000,
        "prix_achat": 20000,
        "guide": "1. Téléchargez CCleaner Professional sur ccleaner.com\n2. Ouvrez l'application, allez dans Options > À propos > Mettre à niveau vers Pro.\n3. Entrez votre nom et la clé d'enregistrement transmise."
    },
    {
        "nom": "McAfee (1 an - 1 appareil)",
        "description": "Antivirus McAfee Total Protection 1 an pour 1 appareil. Protection temps réel contre les virus, ransomwares, chevaux de Troie et navigation sécurisée.",
        "prix_vente": 79000,
        "prix_achat": 35000,
        "guide": "1. Rendez-vous sur mcafee.com/activate\n2. Saisissez votre clé de produit à 25 caractères.\n3. Téléchargez et installez l'agent McAfee sur votre appareil."
    },
    {
        "nom": "Avast Pro (1 an - 1 appareil)",
        "description": "Avast Premium Security 1 an pour 1 appareil. Pare-feu avancé, bouclier anti-ransomware, protection des achats bancaires et de la webcam.",
        "prix_vente": 89000,
        "prix_achat": 40000,
        "guide": "1. Téléchargez Avast Premium Security sur avast.com\n2. Allez dans Menu > Mes abonnements > Saisir un code d'activation valide.\n3. Collez la clé d'activation fournie par Licence Pro Madagascar."
    },

    # VPN & PROTECTION EN LIGNE
    {
        "nom": "Express VPN (12 mois)",
        "description": "Abonnement ExpressVPN 1 an. Serveurs ultra-rapides dans 105 pays, chiffrement de pointe et contournement garanti des restrictions géographiques.",
        "prix_vente": 99000,
        "prix_achat": 50000,
        "guide": "1. Rendez-vous sur expressvpn.com/setup\n2. Connectez-vous avec vos identifiants fournis ou saisissez votre code d'activation.\n3. Téléchargez l'application ExpressVPN sur votre PC ou smartphone et connectez-vous."
    },
    {
        "nom": "Surfshark VPN (12 mois)",
        "description": "Abonnement Surfshark VPN 12 mois. Connexions simultanées illimitées sur tous vos appareils, bloqueur de publicités CleanWeb et politique stricte sans journaux.",
        "prix_vente": 189000,
        "prix_achat": 90000,
        "guide": "1. Téléchargez l'application Surfshark sur surfshark.com/download\n2. Connectez-vous à l'aide du compte pré-activé ou de la clé transmise par Licence Pro Madagascar.\n3. Activez la connexion sur autant d'appareils que souhaité."
    }
]


class Command(BaseCommand):
    help = "Initialise le catalogue officiel des logiciels et licences avec prix actifs et guides d'activation"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Démarrage de l'importation du catalogue officiel..."))
        count_created = 0
        count_updated = 0

        with transaction.atomic():
            for item in CATALOG_DATA:
                produit, created = Produit.objects.update_or_create(
                    nom=item["nom"],
                    defaults={
                        "description": item["description"],
                        "prix_achat": item["prix_achat"],
                        "image": "",
                        "lien_achat": ""
                    }
                )

                # Mise à jour ou création du prix actif
                prix_existant = produit.prix_set.filter(is_active=True).first()
                if not prix_existant or float(prix_existant.prix) != float(item["prix_vente"]):
                    produit.prix_set.filter(is_active=True).update(is_active=False)
                    Prix.objects.create(
                        produit=produit,
                        prix=item["prix_vente"],
                        is_active=True
                    )

                # Mise à jour ou création du guide d'activation
                Activation.objects.update_or_create(
                    produit=produit,
                    defaults={"description_activation": item["guide"]}
                )

                if created:
                    count_created += 1
                    self.stdout.write(self.style.SUCCESS(f"  + Créé: {produit.nom} ({item['prix_vente']:,} Ar)"))
                else:
                    count_updated += 1
                    self.stdout.write(self.style.WARNING(f"  ~ Mis à jour: {produit.nom} ({item['prix_vente']:,} Ar)"))

        self.stdout.write(self.style.SUCCESS(
            f"\nCatalogue synchronisé avec succès ! ({count_created} créés, {count_updated} mis à jour - Total: {len(CATALOG_DATA)} produits)"
        ))
