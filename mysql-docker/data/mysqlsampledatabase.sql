-- =========================
-- BASE DE DONNÉES
-- =========================
CREATE DATABASE IF NOT EXISTS hotel_db;
USE hotel_db;

-- =========================
-- TABLE VILLE
-- =========================
CREATE TABLE VILLE (
    Id_ville INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    latitude DECIMAL(9,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL,
    region VARCHAR(100) NOT NULL,
    pays VARCHAR(100) NOT NULL
);

INSERT INTO VILLE (nom, latitude, longitude, region, pays) VALUES
('Casablanca', 33.573110, -7.589843, 'Casablanca-Settat', 'Maroc'),
('Rabat', 34.020882, -6.841650, 'Rabat-Salé-Kénitra', 'Maroc');

-- =========================
-- TABLE CHAMBRE
-- =========================
CREATE TABLE CHAMBRE (
    Cod_C INT AUTO_INCREMENT PRIMARY KEY,
    numero_etage SMALLINT NOT NULL,
    surface DECIMAL(6,2) NOT NULL
);

INSERT INTO CHAMBRE (numero_etage, surface) VALUES
(1, 25.50),
(2, 40.00),
(3, 60.75);

-- =========================
-- TABLE AGENCE
-- =========================
CREATE TABLE AGENCE (
    Cod_A VARCHAR(100) PRIMARY KEY,
    telephone VARCHAR(30) NOT NULL,
    site_web VARCHAR(255),
    Adresse_Code_Postal VARCHAR(20) NOT NULL,
    Adresse_Rue_A VARCHAR(255) NOT NULL,
    Adresse_Num_A VARCHAR(20) NOT NULL,
    Adresse_Pays_A VARCHAR(100) NOT NULL,
    VILLE_Id_ville INT NOT NULL,
    FOREIGN KEY (VILLE_Id_ville)
        REFERENCES VILLE(Id_ville)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

INSERT INTO AGENCE VALUES
('AG001', '0522000001', 'www.agence-casa.ma', '20000', 'Bd Zerktouni', '12', 'Maroc', 1),
('AG002', '0537000002', 'www.agence-rabat.ma', '10000', 'Av Mohammed V', '45', 'Maroc', 2);

-- =========================
-- TABLE SUITE
-- =========================
CREATE TABLE SUITE (
    CHAMBRE_Cod_C INT PRIMARY KEY,
    FOREIGN KEY (CHAMBRE_Cod_C)
        REFERENCES CHAMBRE(Cod_C)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

INSERT INTO SUITE VALUES
(2),
(3);

-- =========================
-- TABLE HAS_EQUIPEMENT
-- =========================
CREATE TABLE HAS_EQUIPEMENT (
    CHAMBRE_Cod_C INT,
    EQUIPEMENT_equipement VARCHAR(100),
    PRIMARY KEY (CHAMBRE_Cod_C, EQUIPEMENT_equipement),
    FOREIGN KEY (CHAMBRE_Cod_C)
        REFERENCES CHAMBRE(Cod_C)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

INSERT INTO HAS_EQUIPEMENT VALUES
(2, 'Minibar'),
(2, 'Balcon'),
(3, 'Minibar'),
(3, 'Jacuzzi'),
(3, 'Climatisation');

-- =========================
-- TABLE HAS_ESPACES_DISPO
-- =========================
CREATE TABLE HAS_ESPACES_DISPO (
    ESPACES_DISPO_Espaces_Dispo VARCHAR(100),
    SUITE_CHAMBRE_Cod_C INT,
    PRIMARY KEY (ESPACES_DISPO_Espaces_Dispo, SUITE_CHAMBRE_Cod_C),
    FOREIGN KEY (SUITE_CHAMBRE_Cod_C)
        REFERENCES SUITE(CHAMBRE_Cod_C)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

INSERT INTO HAS_ESPACES_DISPO VALUES
('Chambre', 2),
('Salon', 2),
('Chambre', 3),
('Salon', 3),
('Salle à manger', 3);

-- =========================
-- TABLE RESERVATION
-- =========================
CREATE TABLE RESERVATION (
    CHAMBRE_Cod_C INT NOT NULL,
    date_debut DATE NOT NULL,
    date_fin DATE NOT NULL,
    prix DECIMAL(10,2) NOT NULL,
    AGENCE_Cod_A VARCHAR(100) NOT NULL,
    PRIMARY KEY (CHAMBRE_Cod_C, date_debut),
    FOREIGN KEY (CHAMBRE_Cod_C)
        REFERENCES CHAMBRE(Cod_C)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    FOREIGN KEY (AGENCE_Cod_A)
        REFERENCES AGENCE(Cod_A)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CHECK (date_fin > date_debut)
);

INSERT INTO RESERVATION VALUES
(2, '2025-06-01', '2025-06-05', 1200.00, 'AG001'),
(3, '2025-07-10', '2025-07-15', 2500.00, 'AG002');

-- =========================
-- INDEX
-- =========================
CREATE INDEX idx_agence_ville ON AGENCE(VILLE_Id_ville);
CREATE INDEX idx_reservation_chambre ON RESERVATION(CHAMBRE_Cod_C);
CREATE INDEX idx_reservation_agence ON RESERVATION(AGENCE_Cod_A);
