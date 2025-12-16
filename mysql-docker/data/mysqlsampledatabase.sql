-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: db
-- Cree le: Mai 17, 2023 ‡ 10:02
-- Version du server: 8.0.33
-- Version PHP: 8.1.18

--
-- Database: `hotel`
--
CREATE DATABASE IF NOT EXISTS `hotel`;
USE `hotel`;

-- --------------------------------------------------------

--
-- Structure de la table `CITY`
--

CREATE TABLE `CITY` (
  `Name` varchar(32) NOT NULL,
  `Latitude` float DEFAULT NULL,
  `Longitude` float DEFAULT NULL,
  `Country` varchar(32) DEFAULT NULL,
  `Region` varchar(32) NOT NULL,
  PRIMARY KEY (`Name`)
);

--
-- Dump des donnÈes pour la table `CITY`
--

INSERT INTO `CITY` (`Name`, `Latitude`, `Longitude`, `Country`, `Region`) VALUES
('Ville1', 41.1253, 16.8667, 'Maroc', 'Region-3'),
('Ville2', 44.4939, 11.3428, 'Maroc', 'Region-2'),
('Ville3', 45.5389, 10.2203, 'Maroc', 'Region1'),
('Ville4', 37.5, 15.0903, 'Maroc', 'Region-4'),
('Ville5', 39.3, 16.25, 'Maroc', 'Region-5'),
('Ville6', 43.7714, 11.2542, 'Maroc', 'Region-6'),
('Ville7', 44.4111, 8.9328, 'Maroc', 'Region-7'),
('Ville8', 38.1936, 15.5542, 'Maroc', 'Region-4'),
('Ville9', 45.4669, 9.19, 'Maroc', 'Region1'),
('Ville10', 44.6458, 10.9257, 'Maroc', 'Region-2'),
('Ville11', 40.8333, 14.25, 'Maroc', 'Region-9'),
('Ville12', 45.4064, 11.8778, 'Maroc', 'Region-10'),
('Ville13', 38.1157, 13.3613, 'Maroc', 'Region-4'),
('Ville14', 44.8015, 10.328, 'Maroc', 'Region-2'),
('Ville15', 43.8808, 11.0966, 'Maroc', 'Region-6'),
('Ville16', 41.8931, 12.4828, 'Maroc', 'Region-11'),
('Ville17', 40.4711, 17.2431, 'Maroc', 'Region-3'),
('Ville18', 45.0792, 7.6761, 'Maroc', 'Region-12'),
('Ville19', 45.6503, 13.7703, 'Maroc', 'Region-13'),
('Ville20', 45.4397, 12.3319, 'Maroc', 'Region-10'),
('Ville21', 45.4386, 10.9928, 'Maroc', 'Region-10');

-- --------------------------------------------------------

CREATE TABLE `TRAVEL_AGENCY` (
  `CodA` int NOT NULL,
  `WebSite` varchar(32) DEFAULT NULL,
  `Tel` varchar(32) NOT NULL,
  `Street_Address` varchar(32) NOT NULL,
  `ZIP_Address` int NOT NULL,
  `City_Address` varchar(32) NOT NULL,
  `Num_Address` int NOT NULL,
  `Country_Address` varchar(32) NOT NULL,
  PRIMARY KEY (`CodA`),
  FOREIGN KEY (`City_Address`) REFERENCES `CITY` (`Name`)
);

--
-- Dump des donnÈes pour la table`TRAVEL_AGENCY`
--

INSERT INTO `TRAVEL_AGENCY` (`CodA`, `WebSite`, `Tel`, `Street_Address`, `ZIP_Address`, `City_Address`, `Num_Address`, `Country_Address`) VALUES
(1, 'www.ag1.ma', '060-123456', 'Rue- Stre', 1234, 'Ville1', 12, 'Maroc'),
(2, 'www.ag2.ma', '060-234567', 'Rue- Cora', 2345, 'Ville2', 24, 'Maroc'),
(3, NULL, '060-345678', 'Rue- Lun', 3456, 'Ville3', 38, 'Maroc'),
(4, 'www.ag4.ma', '050-23232', 'Rue- Lend', 2345, 'Ville2', 11, 'Maroc'),
(5, 'www.ag5.ma', '060-89821', 'Rue- Rim', 1234, 'Ville1', 5, 'Maroc'),
(6, 'www.ag6.ma', '060-77623', 'Rue- Cavr', 1234, 'Ville1', 89, 'Maroc'),
(7, 'www.ag7.ma', '060-14521', 'Rue- Mart', 1234, 'Ville1', 43, 'Maroc'),
(8, 'www.ag8.ma', '060-22121', 'Rue- UFoscol', 7777, 'Ville4', 130, 'Maroc'),
(9, 'www.ag9.ma', '060-34012', 'Rue- Milop', 8989, 'Ville5', 77, 'Maroc'),
(10, 'www.ag10.ma', '060-99881', 'Rue- Trent', 8989, 'Ville5', 10, 'Maroc'),
(11, 'www.ag11.ma', '060-01001', 'Rue- Liat', 9876, 'Ville6', 10, 'Maroc');

-- --------------------------------------------------------

--
-- Structure de la table `ROOM`
--

CREATE TABLE `ROOM` (
  `CodR` int NOT NULL,
  `Floor` int NOT NULL,
  `SurfaceArea` int NOT NULL,
  `Type` varchar(32) NOT NULL,
  PRIMARY KEY (`CodR`)
);
--
-- Dump des donnÈes pour la table `ROOM`
--

INSERT INTO `ROOM` (`CodR`, `Floor`, `SurfaceArea`, `Type`) VALUES
(1, 1, 20, 'single'),
(2, 2, 30, 'double'),
(3, 3, 40, 'suite'),
(4, 2, 20, 'single'),
(5, 4, 17, 'single'),
(6, 5, 25, 'double'),
(7, 4, 25, 'double'),
(8, 2, 45, 'suite'),
(9, 6, 45, 'suite'),
(10, 2, 35, 'suite'),
(11, 4, 15, 'single'),
(12, 8, 25, 'single'),
(13, 3, 30, 'double');

--
-- Structure de la table `HAS_AMENITIES`
--

CREATE TABLE `HAS_AMENITIES` (
  `AMENITIES_Amenity` varchar(32) NOT NULL,
  `ROOM_CodR` int NOT NULL,
  PRIMARY KEY (AMENITIES_Amenity, ROOM_CodR),
  FOREIGN KEY (ROOM_CodR) REFERENCES ROOM(CodR)
);
--
-- Dump des donnÈes pour la table`HAS_AMENITIES`
--

INSERT INTO `HAS_AMENITIES` (`AMENITIES_Amenity`, `ROOM_CodR`) VALUES
('balcony', 1),
('balcony', 2),
('jacuzzi', 2),
('minibar', 2),
('minibar', 3),
('balcony', 4),
('pay-tv', 5),
('minibar', 11),
('balcony', 11),
('balcony', 6),
('jacuzzi', 6),
('balcony', 8),
('jacuzzi', 8),
('jacuzzi', 9),
('minibar', 12),
('minibar', 10),
('pay-tv', 10),
('balcony', 7),
('pay-tv', 13);

-- --------------------------------------------------------

--
-- Structure de la table `HAS_SPACES`
--

CREATE TABLE `HAS_SPACES` (
  `SPACES_Space` varchar(32) NOT NULL,
  `ROOM_CodR` int NOT NULL,
  PRIMARY KEY (SPACES_Space, ROOM_CodR),
  FOREIGN KEY (ROOM_CodR) REFERENCES ROOM(CodR)
);

--
-- Dump des donnÈes pour la table `HAS_SPACES`
--

INSERT INTO `HAS_SPACES` (`SPACES_Space`, `ROOM_CodR`) VALUES
('bathroom', 3),
('chambre ‡ choucher', 3),
('kitchen', 3),
('kitchen', 4),
('kitchen', 6),
('kitchen', 13),
('dining room', 3),
('dining room', 7),
('dining room', 5);

-- --------------------------------------------------------

--
-- Structure de la table `BOOKING`
--

CREATE TABLE `BOOKING` (
  `ROOM_CodR` int NOT NULL,
  `StartDate` varchar(32) NOT NULL,
  `EndDate` varchar(32) NOT NULL,
  `Cost` double NOT NULL,
  `TRAVEL_AGENCY_CodA` int NOT NULL,
  PRIMARY KEY (ROOM_CodR, StartDate),
  FOREIGN KEY (ROOM_CodR) REFERENCES ROOM(CodR),
  FOREIGN KEY (TRAVEL_AGENCY_CodA) REFERENCES TRAVEL_AGENCY(CodA)
);

--
-- Dump des donnÈes pour la table `BOOKING`
--

INSERT INTO `BOOKING` (`ROOM_CodR`, `StartDate`, `EndDate`, `Cost`, `TRAVEL_AGENCY_CodA`) VALUES
(1, '2023-01-01', '2023-01-10', 1000, 1),
(2, '2023-01-01', '2023-01-10', 1500, 2),
(3, '2023-02-01', '2023-02-10', 800, 2),
(13, '2023-03-01', '2023-03-10', 800, 2),
(2, '2023-01-12', '2023-01-17', 560, 2),
(3, '2023-03-13', '2023-03-17', 270, 2),
(4, '2023-02-01', '2023-02-05', 300, 3),
(3, '2023-02-06', '2023-02-07', 90, 3),
(7, '2023-09-06', '2023-09-17', 1250, 3),
(10, '2023-08-06', '2023-08-09', 950, 3),
(10, '2023-04-16', '2023-04-19', 660, 5),
(10, '2023-07-13', '2023-07-20', 1185, 5),
(8, '2023-12-11', '2023-12-14', 710, 4);

-- --------------------------------------------------------
