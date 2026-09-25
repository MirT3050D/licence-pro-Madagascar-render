-- Nettoyage préalable (ordre inverse des dépendances)
DROP TABLE IF EXISTS commande CASCADE;
DROP TABLE IF EXISTS vente CASCADE;
DROP TABLE IF EXISTS activation CASCADE;
DROP TABLE IF EXISTS prix CASCADE;
DROP TABLE IF EXISTS produit CASCADE;
DROP TABLE IF EXISTS client CASCADE;
DROP TABLE IF EXISTS methode_paiement CASCADE;
DROP TABLE IF EXISTS provenance CASCADE;
DROP TABLE IF EXISTS utilisateur CASCADE;
DROP TABLE IF EXISTS role CASCADE;

-- 1. Table Provenance (Canal d'acquisition client)
CREATE TABLE provenance (
    id SERIAL PRIMARY KEY,
    label VARCHAR(100) NOT NULL
);

-- 2. Table Methode_Paiement (Comptes de réception / Mode de règlement)
CREATE TABLE methode_paiement (
    id SERIAL PRIMARY KEY,
    label VARCHAR(100) NOT NULL,
    details VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- 3. Table Role
CREATE TABLE role (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(50) NOT NULL UNIQUE,
    label VARCHAR(100) NOT NULL,
    point INTEGER DEFAULT 0
);

-- 4. Table Utilisateur
CREATE TABLE utilisateur (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    numero VARCHAR(30),
    email VARCHAR(150) NOT NULL UNIQUE,
    mot_de_passe VARCHAR(255) NOT NULL,
    id_role INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_utilisateur_role FOREIGN KEY (id_role) 
        REFERENCES role(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- 5. Table Client
CREATE TABLE client (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(150) NOT NULL,
    numero VARCHAR(30),
    id_provenance INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_client_provenance FOREIGN KEY (id_provenance) 
        REFERENCES provenance(id) ON UPDATE CASCADE ON DELETE SET NULL
);

-- 6. Table Produit
CREATE TABLE produit (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(150) NOT NULL,
    description TEXT,
    image VARCHAR(255),
    lien_achat TEXT,
    prix_achat NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. Table Prix (Catalogue des tarifs de vente)
CREATE TABLE prix (
    id SERIAL PRIMARY KEY,
    id_produit INTEGER NOT NULL,
    prix NUMERIC(12, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_prix_produit FOREIGN KEY (id_produit) 
        REFERENCES produit(id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- 8. Table Activation (Guide / Procédure technique)
CREATE TABLE activation (
    id SERIAL PRIMARY KEY,
    id_produit INTEGER NOT NULL,
    description_activation TEXT NOT NULL,
    CONSTRAINT fk_activation_produit FOREIGN KEY (id_produit) 
        REFERENCES produit(id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- 9. Table Vente (En-tête de la transaction)
CREATE TABLE vente (
    id SERIAL PRIMARY KEY,
    date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    id_client INTEGER NOT NULL,
    id_user_affilie INTEGER NOT NULL,
    id_methode_paiement INTEGER NOT NULL,
    CONSTRAINT fk_vente_client FOREIGN KEY (id_client) 
        REFERENCES client(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_vente_user FOREIGN KEY (id_user_affilie) 
        REFERENCES utilisateur(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_vente_methode_paiement FOREIGN KEY (id_methode_paiement) 
        REFERENCES methode_paiement(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- 10. Table Commande (Articles / Lignes de la vente)
CREATE TABLE commande (
    id SERIAL PRIMARY KEY,
    id_vente INTEGER NOT NULL,
    id_produit INTEGER NOT NULL,
    quantite INTEGER NOT NULL DEFAULT 1 CHECK (quantite > 0),
    prix_unitaire NUMERIC(12, 2) NOT NULL,
    date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_commande_vente FOREIGN KEY (id_vente) 
        REFERENCES vente(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_commande_produit FOREIGN KEY (id_produit) 
        REFERENCES produit(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- Index pour optimiser les requêtes du Dashboard, calculs de trésorerie et statistiques
CREATE INDEX idx_vente_date ON vente(date);
CREATE INDEX idx_vente_client ON vente(id_client);
CREATE INDEX idx_vente_user ON vente(id_user_affilie);
CREATE INDEX idx_vente_paiement ON vente(id_methode_paiement);
CREATE INDEX idx_commande_vente ON commande(id_vente);
CREATE INDEX idx_commande_produit ON commande(id_produit);
CREATE INDEX idx_prix_produit_active ON prix(id_produit, is_active);