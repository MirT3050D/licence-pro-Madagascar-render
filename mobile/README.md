# Licence Pro Madagascar — Application Mobile (Ionic + Vue 3 + Capacitor)

Application mobile officielle de **Licence Pro Madagascar**, développée avec **Vue 3**, **Ionic Framework 8**, **Capacitor 6** et **Vite**.

---

## 📱 Fonctionnalités Incluses

1. **Tableau de Bord & KPIs en Temps Réel** :
   - Chiffre d'affaires total encaissé
   - Marge nette estimée
   - Nombre de ventes conclues & licences écoulées
   - Top logiciels vendus
   - Ventes récentes & solde de points de commission

2. **Gestion des Ventes (CRUD Vente)** :
   - Recherche instantanée par nom, téléphone, identifiant
   - Filtres temporels rapides (*Tout, Aujourd'hui, 7 jours, 30 jours*)
   - **Nouvelle Vente** : modal tactile optimisé avec sélection client (ou création rapide), multi-articles, ajustement des quantités (+/-), calcul dynamique du total en Ariary (Ar) et choix du mode de paiement (MVola, Orange Money, Airtel, Cash).
   - Bouton de copie du **guide d'activation** prêt à envoyer directement au client par WhatsApp / SMS.

3. **Répertoire Clients (CRUD Client)** :
   - Fiche client avec initiales stylisées et provenance (Facebook, Recommandation, Direct...)
   - Raccourcis directs d'appel téléphonique (`tel:`) et de contact **WhatsApp** en un clic.
   - Statistiques par client (nombre d'achats et montant total cumulé).

4. **Catalogue Logiciels & Licences (CRUD Produit)** :
   - Liste des logiciels avec tarifs actifs et prix de revient
   - Modification express du prix de vente sans recharger
   - Consultation et copie rapide du guide d'activation technique pour chaque licence.

5. **Assistant Virtuel IA Flottant (Bouton FAB)** :
   - Accessible sur tous les onglets via le bouton flottant étincelant.
   - **Chatbot interactif** : conseils sur les logiciels, activation, tarifs.
   - **Extracteur automatique** : collez un message WhatsApp brut du client, l'IA détecte le client, les logiciels et ouvre directement le formulaire de vente pré-rempli.

6. **Espace Compte & Console Administrateur** :
   - Fiche vendeur avec habilitation, ventes associées et CA personnel
   - Pour les administrateurs (Niveau 50) : console de validation des nouveaux vendeurs inscrits.

---

## 🚀 Démarrage Rapide

### 1. Développement Local (Navigateur / Wi-Fi)

Pour lancer le serveur de développement local avec rechargement à chaud :

```bash
cd mobile
npm run dev
```

L'application s'ouvre par défaut sur `http://localhost:5174/`.
> 💡 *Astuce* : Ouvrez l'inspecteur de votre navigateur (F12) et basculez en **Mode Appareil Mobile** (Ctrl+Shift+M) pour apprécier la fluidité tactile et le design iOS/Android.

### 2. Compilation & Synchronisation Capacitor

Pour compiler la version de production et synchroniser les fichiers vers le dossier Android natif :

```bash
npm run cap:sync
```

### 3. Ouvrir dans Android Studio

Pour compiler l'APK final ou lancer l'application sur un smartphone Android connecté en USB ou un émulateur :

```bash
npm run cap:open:android
```
