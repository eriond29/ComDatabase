-- MySQL dump 10.13  Distrib 8.0.39, for Linux (x86_64)
--
-- Host: localhost    Database: ComicDatabase
-- ------------------------------------------------------
-- Server version	8.0.39-0ubuntu0.24.04.2

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Artist`
--

DROP TABLE IF EXISTS `Artist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Artist` (
  `PersonID` varchar(10) NOT NULL,
  `Inker` varchar(3) DEFAULT NULL,
  PRIMARY KEY (`PersonID`),
  CONSTRAINT `Artist_ibfk_1` FOREIGN KEY (`PersonID`) REFERENCES `Person` (`PersonID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Artist`
--

LOCK TABLES `Artist` WRITE;
/*!40000 ALTER TABLE `Artist` DISABLE KEYS */;
INSERT INTO `Artist` VALUES ('OCCJAKI','No'),('OCCJILE','Yes'),('OCCJOBY','Yes'),('OCCSTDI','No'),('OCCTOMC','Yes');
/*!40000 ALTER TABLE `Artist` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Author`
--

DROP TABLE IF EXISTS `Author`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Author` (
  `PersonID` varchar(10) NOT NULL,
  `StartingCompany` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`PersonID`),
  CONSTRAINT `Author_ibfk_1` FOREIGN KEY (`PersonID`) REFERENCES `Person` (`PersonID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `Author_ibfk_2` FOREIGN KEY (`PersonID`) REFERENCES `Person` (`PersonID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `Author_ibfk_3` FOREIGN KEY (`PersonID`) REFERENCES `Person` (`PersonID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Author`
--

LOCK TABLES `Author` WRITE;
/*!40000 ALTER TABLE `Author` DISABLE KEYS */;
INSERT INTO `Author` VALUES ('OCCDAMI','DC'),('OCCJOBY','Marvel'),('OCCSTALE','Marvel');
/*!40000 ALTER TABLE `Author` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ComicCharacter`
--

DROP TABLE IF EXISTS `ComicCharacter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ComicCharacter` (
  `CharacterID` varchar(20) NOT NULL,
  `FirstName` varchar(50) DEFAULT NULL,
  `LastName` varchar(50) DEFAULT NULL,
  `Monicker` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`CharacterID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ComicCharacter`
--

LOCK TABLES `ComicCharacter` WRITE;
/*!40000 ALTER TABLE `ComicCharacter` DISABLE KEYS */;
INSERT INTO `ComicCharacter` VALUES ('CHIDJEGR','Jean','Grey','Marvel Girl'),('CHIDSCSU','Scott','Summers','Cyclops');
/*!40000 ALTER TABLE `ComicCharacter` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Issue`
--

DROP TABLE IF EXISTS `Issue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Issue` (
  `IssueID` varchar(20) NOT NULL,
  `SeriesID` varchar(20) DEFAULT NULL,
  `Year` smallint DEFAULT NULL,
  `Author` varchar(50) DEFAULT NULL,
  `Artist` varchar(50) DEFAULT NULL,
  `IssueNumber` smallint DEFAULT NULL,
  PRIMARY KEY (`IssueID`),
  KEY `SeriesID` (`SeriesID`),
  KEY `Author` (`Author`),
  KEY `Artist` (`Artist`),
  CONSTRAINT `Issue_ibfk_1` FOREIGN KEY (`SeriesID`) REFERENCES `Series` (`SeriesID`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `Issue_ibfk_2` FOREIGN KEY (`Author`) REFERENCES `Author` (`PersonID`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `Issue_ibfk_3` FOREIGN KEY (`Artist`) REFERENCES `Artist` (`PersonID`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Issue`
--

LOCK TABLES `Issue` WRITE;
/*!40000 ALTER TABLE `Issue` DISABLE KEYS */;
INSERT INTO `Issue` VALUES ('IIDXMVOL1I1',NULL,1963,NULL,NULL,1),('IIDXMVOL2I1',NULL,1992,NULL,NULL,1);
/*!40000 ALTER TABLE `Issue` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Issue_Character`
--

DROP TABLE IF EXISTS `Issue_Character`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Issue_Character` (
  `CharacterID` varchar(20) NOT NULL,
  `IssueID` varchar(20) NOT NULL,
  PRIMARY KEY (`CharacterID`,`IssueID`),
  KEY `IssueID` (`IssueID`),
  CONSTRAINT `Issue_Character_ibfk_1` FOREIGN KEY (`CharacterID`) REFERENCES `ComicCharacter` (`CharacterID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `Issue_Character_ibfk_2` FOREIGN KEY (`IssueID`) REFERENCES `Issue` (`IssueID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Issue_Character`
--

LOCK TABLES `Issue_Character` WRITE;
/*!40000 ALTER TABLE `Issue_Character` DISABLE KEYS */;
/*!40000 ALTER TABLE `Issue_Character` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Person`
--

DROP TABLE IF EXISTS `Person`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Person` (
  `PersonID` varchar(10) NOT NULL,
  `FirstName` varchar(50) DEFAULT NULL,
  `LastName` varchar(50) DEFAULT NULL,
  `Nationality` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`PersonID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Person`
--

LOCK TABLES `Person` WRITE;
/*!40000 ALTER TABLE `Person` DISABLE KEYS */;
INSERT INTO `Person` VALUES ('OCCALMO',NULL,NULL,NULL),('OCCDAMI',NULL,NULL,NULL),('OCCHCL','Chris','Claremont','US'),('OCCJAKI',NULL,NULL,NULL),('OCCJILE',NULL,NULL,NULL),('OCCJOBY',NULL,NULL,NULL),('OCCSTALE','Stan','Lee','US'),('OCCSTDI',NULL,NULL,NULL),('OCCTOMC',NULL,NULL,NULL);
/*!40000 ALTER TABLE `Person` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Series`
--

DROP TABLE IF EXISTS `Series`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Series` (
  `SeriesID` varchar(10) NOT NULL,
  `Title` varchar(50) DEFAULT NULL,
  `VolumeNumber` smallint NOT NULL,
  `StartYear` smallint DEFAULT NULL,
  PRIMARY KEY (`SeriesID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Series`
--

LOCK TABLES `Series` WRITE;
/*!40000 ALTER TABLE `Series` DISABLE KEYS */;
INSERT INTO `Series` VALUES ('SIDXM1','X-Men',1,1963),('SIDXM2','X-Men',2,1992);
/*!40000 ALTER TABLE `Series` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `SeriesTitle`
--

DROP TABLE IF EXISTS `SeriesTitle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `SeriesTitle` (
  `SeriesID` varchar(10) NOT NULL,
  `Title` varchar(50) NOT NULL,
  PRIMARY KEY (`SeriesID`,`Title`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `SeriesTitle`
--

LOCK TABLES `SeriesTitle` WRITE;
/*!40000 ALTER TABLE `SeriesTitle` DISABLE KEYS */;
INSERT INTO `SeriesTitle` VALUES ('SIDXM1','Uncanny X-Men'),('SIDXM2','X-Men');
/*!40000 ALTER TABLE `SeriesTitle` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-10-14  3:31:21
