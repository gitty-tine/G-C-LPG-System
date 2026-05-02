-- MySQL dump 10.13  Distrib 8.4.3, for Win64 (x86_64)
--
-- Host: localhost    Database: gnclpgdb
-- ------------------------------------------------------
-- Server version	8.4.3

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
-- Current Database: `gnclpgdb`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `gnclpgdb` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `gnclpgdb`;

--
-- Table structure for table `audit_logs`
--

DROP TABLE IF EXISTS `audit_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `audit_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `action` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `table_name` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `record_id` int NOT NULL,
  `old_value` text COLLATE utf8mb4_general_ci,
  `new_value` text COLLATE utf8mb4_general_ci,
  `changed_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `idx_audit_logs_table_name` (`table_name`),
  KEY `idx_audit_logs_changed_at_id` (`changed_at`,`id`),
  CONSTRAINT `audit_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=160 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `audit_logs`
--

LOCK TABLES `audit_logs` WRITE;
/*!40000 ALTER TABLE `audit_logs` DISABLE KEYS */;
INSERT INTO `audit_logs` VALUES (1,2,'INSERT','customers',26,'-','Jherode Aaron Petate, Rillo, Tuy, Batangas, 09956190545','2026-04-27 01:24:25'),(2,2,'INSERT','customers',27,'-','Kristine Katigbak, Burgos, Tuy, Batangas, 09919899657','2026-04-27 01:25:02'),(3,2,'INSERT','customers',28,'-','Fatima Suzzane Solis, Ermita, Balayan, Batangas, 09643421255','2026-04-27 01:25:59'),(4,2,'INSERT','customers',29,'-','Francine Kim Flores, Lian, Batangas, 09987341213','2026-04-27 01:26:36'),(5,2,'INSERT','customers',30,'-','Janine Cedilla, Magahis, Tuy, Batangas, 09123456789','2026-04-27 01:27:31'),(6,2,'INSERT','customers',31,'-','Ron Ace De Taza, Luna, Tuy, Batangas, 09127164852','2026-04-27 01:28:38'),(7,2,'INSERT','customers',32,'-','Erez Shore, Dao, Tuy, Batangas, 09983758232','2026-04-27 01:29:10'),(8,2,'INSERT','customers',33,'-','Lucerys Velaryon, Putol, Tuy, Batangas, 09675829121','2026-04-27 01:30:05'),(9,2,'INSERT','customers',34,'-','Rhaenyra Targaryen, Luna, Tuy, Batangas, 09182748211','2026-04-27 01:30:49'),(10,2,'INSERT','customers',35,'-','Anghelica Fajardo, Toong, Tuy, Batangas, 09759951254','2026-04-27 01:31:48'),(11,1,'INSERT','lpg_products',23,'-','Town Gaz 11kg, Refill: 930.00, New Tank: 2630.00','2026-04-27 01:34:13'),(12,1,'INSERT','lpg_products',24,'-','Superkalan 2.7kg, Refill: 310.00, New Tank: 1.31','2026-04-27 01:37:58'),(13,1,'UPDATE','lpg_products',24,'Superkalan 2.7kg, Refill: 310.00, New Tank: 1310.00','Town   Gaz 11kg, Refill: 310.00, New Tank: 1310.00','2026-04-27 01:38:10'),(14,1,'INSERT','lpg_products',25,'-','Town, Gaz 11kg, Refill: 930.00, New Tank: 2630.00','2026-04-27 01:39:06'),(15,1,'INSERT','lpg_products',1,'-','Town Gaz 11kg, Refill: 930.00, New Tank: 2630.00','2026-04-27 02:04:51'),(16,1,'INSERT','lpg_products',2,'-','Town     Gaz 11kg, Refill: 930.00, New Tank: 2630.00','2026-04-27 02:05:12'),(17,1,'INSERT','lpg_products',3,'-','Town, Gaz 11kg, Refill: 930.00, New Tank: 2630.00','2026-04-27 02:05:40'),(18,1,'INSERT','lpg_products',4,'-','Superkalan 2.7kg, Refill: 310.00, New Tank: 1310.00','2026-04-27 02:06:23'),(19,1,'UPDATE','lpg_products',4,'Superkalan 2.7kg, Refill: 310.00, New Tank: 1310.00','Town    Gaz 2.7kg, Refill: 310.00, New Tank: 1310.00','2026-04-27 02:07:00'),(20,1,'INSERT','lpg_products',8,'-','Town     Gaz 11kg, Refill: 930.00, New Tank: 2630.00','2026-04-27 11:20:01'),(21,1,'INSERT','lpg_products',14,'-','Town Gaz 11kg, Refill: 930.00, New Tank: 2630.00','2026-04-27 11:48:33'),(22,1,'INSERT','lpg_products',15,'-','Superkalan 2.7kg, Refill: 310.00, New Tank: 1310.00','2026-04-27 11:48:58'),(23,1,'INSERT','lpg_products',16,'-','Regasco 22kg, Refill: 646.00, New Tank: 2650.00','2026-04-27 11:50:29'),(24,1,'DELETE','lpg_products',16,'Regasco 22kg, Refill: 646.00, New Tank: 2650.00','-','2026-04-27 11:50:43'),(25,2,'INSERT','deliveries',7,'-','Customer: Anghelica Fajardo, Date: Apr 27, 2026, Status: pending','2026-04-27 12:40:54'),(26,2,'INSERT','deliveries',8,'-','Customer: Jherode Aaron Petate, Date: Apr 27, 2026, Status: pending','2026-04-27 12:52:24'),(27,2,'INSERT','deliveries',9,'-','Customer: Janine Cedilla, Date: Apr 27, 2026, Status: pending','2026-04-27 12:53:08'),(28,2,'INSERT','deliveries',10,'-','Customer: Kristine Katigbak, Date: Apr 27, 2026, Status: pending','2026-04-27 12:53:36'),(29,2,'INSERT','deliveries',11,'-','Customer: Rhaenyra Targaryen, Date: Apr 27, 2026, Status: pending','2026-04-27 12:54:03'),(30,2,'INSERT','customers',36,'-','Keira Parvis, Guinhawa, Tuy, Batangas, 0998367dfu7','2026-04-27 13:29:22'),(31,2,'DELETE','customers',36,'Keira Parvis, Guinhawa, Tuy, Batangas, 0998367dfu7','-','2026-04-27 13:45:15'),(32,2,'UPDATE','deliveries',11,'Customer: Rhaenyra Targaryen, Date: Apr 27, 2026, Status: in_transit','Customer: Rhaenyra Targaryen, Date: Apr 27, 2026, Status: delivered','2026-04-27 15:48:58'),(33,2,'UPDATE','deliveries',10,'Customer: Kristine Katigbak, Date: Apr 27, 2026, Status: in_transit','Customer: Kristine Katigbak, Date: Apr 27, 2026, Status: delivered','2026-04-27 15:49:05'),(34,2,'UPDATE','deliveries',8,'Customer: Jherode Aaron Petate, Date: Apr 27, 2026, Status: in_transit','Customer: Jherode Aaron Petate, Date: Apr 27, 2026, Status: delivered','2026-04-27 15:49:10'),(35,2,'UPDATE','deliveries',9,'Customer: Janine Cedilla, Date: Apr 27, 2026, Status: pending','Customer: Janine Cedilla, Date: Apr 27, 2026, Status: cancelled','2026-04-27 15:49:15'),(36,2,'UPDATE','deliveries',7,'Customer: Anghelica Fajardo, Date: Apr 27, 2026, Status: in_transit','Customer: Anghelica Fajardo, Date: Apr 27, 2026, Status: cancelled','2026-04-27 15:49:21'),(37,2,'UPDATE','transactions',5,'Payment Status: unpaid','Payment Status: paid','2026-04-27 16:14:43'),(38,2,'INSERT','customers',37,NULL,'Name: kjkjkkj, Address: jkjk, Contact: 09999989789','2026-04-28 02:42:26'),(39,2,'UPDATE','customers',37,'Name: kjkjkkj, Address: jkjk, Contact: 09999989789','Name: ok oko ok, Address: jkjk, Contact: 09999989789','2026-04-28 02:43:11'),(40,2,'UPDATE','customers',37,'Name: ok oko ok, Address: jkjk, Contact: 09999989789','Name: mkijijij, Address: jkjk, Contact: 09999989789','2026-04-28 02:43:34'),(41,2,'DELETE','customers',37,'Name: mkijijij, Address: jkjk, Contact: 09999989789',NULL,'2026-04-28 02:43:47'),(42,1,'UPDATE','lpg_products',15,'Refill: 310.00, New Tank: 1310.00','Refill: 330.00, New Tank: 1310.00','2026-04-28 02:45:29'),(43,1,'UPDATE','lpg_products',15,'Refill: 330.00, New Tank: 1310.00','Refill: 310.00, New Tank: 1310.00','2026-04-28 02:45:50'),(44,1,'INSERT','lpg_products',17,NULL,'Name: okok, Size: 60kg, Refill: 80.00, New Tank: 90.00','2026-04-28 02:46:09'),(45,1,'DELETE','lpg_products',17,'Name: okok, Size: 60kg, Refill: 80.00, New Tank: 90.00',NULL,'2026-04-28 02:46:25'),(46,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Adminy, Username: admin','2026-04-28 03:40:42'),(47,2,'UPDATE','users',2,'Full Name: G&C Adminy, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-28 03:41:03'),(48,2,'UPDATE','transactions',4,'Payment Status: unpaid','Payment Status: paid','2026-04-28 03:50:31'),(49,2,'UPDATE','transactions',3,'Payment Status: unpaid, Customer: Rhaenyra Targaryen, Total Amount: 930.00, Delivery ID: 11','Payment Status: paid, Customer: Rhaenyra Targaryen, Total Amount: 930.00, Delivery ID: 11','2026-04-28 03:56:27'),(50,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-28 12:46:35'),(51,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-28 12:47:08'),(52,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-28 12:48:27'),(53,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-28 12:49:28'),(54,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-28 18:27:17'),(55,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-28 22:03:32'),(56,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-28 22:04:57'),(57,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-28 22:41:29'),(58,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-28 22:42:05'),(59,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-28 22:43:34'),(60,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-28 22:45:57'),(61,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-28 22:48:06'),(62,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-28 22:52:35'),(63,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-28 22:53:20'),(64,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-28 22:54:29'),(65,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-28 23:10:48'),(66,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-28 23:12:11'),(67,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-28 23:12:58'),(68,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-29 00:19:53'),(69,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-29 00:20:30'),(70,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-29 00:21:01'),(71,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-29 00:24:13'),(72,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-29 00:24:19'),(73,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-29 00:28:04'),(74,1,'UPDATE','users',1,'Full Name: G&C Owner, Username: owner','Full Name: G&C Admin, Username: adminy','2026-04-29 00:28:43'),(75,1,'UPDATE','users',1,'Full Name: G&C Admin, Username: adminy','Full Name: G&C Admin, Username: adminy','2026-04-29 00:29:26'),(76,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-29 00:30:40'),(77,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-29 00:30:46'),(78,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-29 00:41:44'),(79,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-29 00:41:56'),(80,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-29 00:42:21'),(81,1,'UPDATE','users',1,'Full Name: G&C Admin, Username: adminy','Full Name: G&C Owner, Username: owner','2026-04-29 00:44:34'),(82,1,'UPDATE','users',1,'Full Name: G&C Owner, Username: owner','Full Name: G&C Owner, Username: owner','2026-04-29 00:44:51'),(83,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-29 00:45:03'),(84,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-29 00:45:39'),(85,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-29 00:47:58'),(86,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: adm   in','2026-04-29 00:52:51'),(87,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: adm   in','Full Name: G&C Admin, Username: admin','2026-04-29 00:53:01'),(88,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-29 00:54:07'),(89,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-29 01:06:34'),(90,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-29 01:10:33'),(91,1,'UPDATE','users',1,'Full Name: G&C Owner, Username: owner','Full Name: G&C Owner, Username: owner','2026-04-29 01:11:14'),(92,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-29 11:26:35'),(93,1,'UPDATE','users',1,'Full Name: G&C Owner, Username: owner','Full Name: G&C Owner, Username: owner','2026-04-29 11:35:25'),(94,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-29 11:35:41'),(95,2,'INSERT','deliveries',12,NULL,'Customer: Jherode Aaron Petate, Date: 2026-04-29, Status: pending','2026-04-29 11:36:29'),(96,2,'INSERT','deliveries',13,NULL,'Customer: Janine Cedilla, Date: 2026-04-29, Status: pending','2026-04-29 11:36:47'),(97,2,'INSERT','deliveries',14,NULL,'Customer: Francine Kim Flores, Date: 2026-04-29, Status: pending','2026-04-29 11:37:25'),(98,2,'UPDATE','transactions',8,'Payment Status: unpaid, Customer: Jherode Aaron Petate, Total Amount: 2550.00, Delivery ID: 12','Payment Status: paid, Customer: Jherode Aaron Petate, Total Amount: 2550.00, Delivery ID: 12','2026-04-29 11:44:05'),(99,2,'UPDATE','transactions',7,'Payment Status: unpaid, Customer: Janine Cedilla, Total Amount: 4240.00, Delivery ID: 13','Payment Status: paid, Customer: Janine Cedilla, Total Amount: 4240.00, Delivery ID: 13','2026-04-29 11:44:08'),(100,2,'UPDATE','transactions',6,'Payment Status: unpaid, Customer: Francine Kim Flores, Total Amount: 1860.00, Delivery ID: 14','Payment Status: paid, Customer: Francine Kim Flores, Total Amount: 1860.00, Delivery ID: 14','2026-04-29 11:44:11'),(101,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-29 12:11:45'),(102,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-29 12:18:15'),(103,2,'INSERT','deliveries',15,NULL,'Customer: Anghelica Fajardo, Date: 2026-04-29, Status: pending','2026-04-29 14:09:58'),(104,2,'INSERT','deliveries',16,NULL,'Customer: Kristine Katigbak, Date: 2026-04-29, Status: pending','2026-04-29 15:25:27'),(105,2,'INSERT','deliveries',17,NULL,'Customer: Jherode Aaron Petate, Date: 2026-04-29, Status: pending','2026-04-29 15:25:42'),(106,2,'INSERT','deliveries',18,NULL,'Customer: Lucerys Velaryon, Date: 2026-04-29, Status: pending','2026-04-29 15:26:14'),(107,2,'UPDATE','transactions',10,'Payment Status: unpaid, Customer: Jherode Aaron Petate, Total Amount: 4650.00, Delivery ID: 17','Payment Status: paid, Customer: Jherode Aaron Petate, Total Amount: 4650.00, Delivery ID: 17','2026-04-29 15:33:37'),(108,2,'UPDATE','transactions',9,'Payment Status: unpaid, Customer: Lucerys Velaryon, Total Amount: 9180.00, Delivery ID: 18','Payment Status: paid, Customer: Lucerys Velaryon, Total Amount: 9180.00, Delivery ID: 18','2026-04-29 15:33:39'),(109,2,'INSERT','deliveries',19,NULL,'Customer: Janine Cedilla, Date: 2026-04-30, Status: pending','2026-04-30 00:03:42'),(110,2,'INSERT','deliveries',20,NULL,'Customer: Rhaenyra Targaryen, Date: 2026-04-30, Status: pending','2026-04-30 00:03:58'),(111,2,'INSERT','deliveries',21,NULL,'Customer: Fatima Suzzane Solis, Date: 2026-04-30, Status: pending','2026-04-30 00:04:18'),(112,2,'UPDATE','users',2,'Full Name: G&C Admin, Username: admin','Full Name: G&C Admin, Username: admin','2026-04-30 01:27:37'),(114,2,'UPDATE','users',2,'Email: katigbakkristine31@gmail.com','Email: katigbakkristine88@gmail.com','2026-04-30 01:34:23'),(116,2,'INSERT','transactions',12,NULL,'Payment Status: unpaid, Customer: Fatima Suzzane Solis, Total Amount: 2940.00, Delivery ID: 21','2026-04-30 07:16:14'),(117,2,'INSERT','transactions',13,NULL,'Payment Status: unpaid, Customer: Rhaenyra Targaryen, Total Amount: 2630.00, Delivery ID: 20','2026-04-30 07:16:18'),(118,2,'UPDATE','transactions',13,'Payment Status: unpaid, Customer: Rhaenyra Targaryen, Total Amount: 2630.00, Delivery ID: 20','Payment Status: paid, Customer: Rhaenyra Targaryen, Total Amount: 2630.00, Delivery ID: 20','2026-04-30 07:16:33'),(125,2,'UPDATE','transactions',12,'Payment Status: unpaid, Customer: Fatima Suzzane Solis, Total Amount: 2940.00, Delivery ID: 21','Payment Status: paid, Customer: Fatima Suzzane Solis, Total Amount: 2940.00, Delivery ID: 21','2026-04-30 22:51:00'),(126,2,'INSERT','deliveries',25,NULL,'Customer: Kristine Katigbak, Date: 2026-05-01, Status: pending','2026-04-30 22:51:49'),(127,2,'INSERT','deliveries',26,NULL,'Customer: Francine Kim Flores, Date: 2026-05-01, Status: pending','2026-04-30 22:52:07'),(129,1,'UPDATE','lpg_products',15,'Name: Superkalan, Size: 2.7kg, Refill: 310.00, New Tank: 1310.00, Active: Yes','Name: Superkalan, Size: 2.7kg, Refill: 310.00, New Tank: 1310.00, Active: No','2026-04-30 23:32:38'),(130,1,'UPDATE','lpg_products',14,'Name: Town Gaz, Size: 11kg, Refill: 930.00, New Tank: 2630.00, Active: Yes','Name: Town Gaz, Size: 11kg, Refill: 930.00, New Tank: 2630.00, Active: No','2026-04-30 23:32:53'),(131,1,'UPDATE','lpg_products',14,'Name: Town Gaz, Size: 11kg, Refill: 930.00, New Tank: 2630.00, Active: No','Name: Town Gaz, Size: 11kg, Refill: 930.00, New Tank: 2630.00, Active: Yes','2026-04-30 23:45:58'),(132,1,'UPDATE','lpg_products',15,'Name: Superkalan, Size: 2.7kg, Refill: 310.00, New Tank: 1310.00, Active: No','Name: Superkalan, Size: 2.7kg, Refill: 310.00, New Tank: 1310.00, Active: Yes','2026-04-30 23:45:58'),(133,1,'UPDATE','lpg_products',15,'Name: Superkalan, Size: 2.7kg, Refill: 310.00, New Tank: 1310.00, Active: Yes','Name: Superkalan, Size: 2.7kg, Refill: 310.00, New Tank: 1310.00, Active: No','2026-05-01 04:01:53'),(134,1,'UPDATE','lpg_products',15,'Name: Superkalan, Size: 2.7kg, Refill: 310.00, New Tank: 1310.00, Active: No','Name: Superkalan, Size: 2.7kg, Refill: 310.00, New Tank: 1310.00, Active: Yes','2026-05-01 04:01:57'),(135,2,'INSERT','deliveries',27,NULL,'Customer: Ron Ace De Taza, Date: 2026-05-01, Status: pending','2026-05-01 04:02:49'),(136,2,'INSERT','transactions',15,NULL,'Payment Status: unpaid, Customer: Ron Ace De Taza, Total Amount: 310.00, Delivery ID: 27','2026-05-01 04:03:26'),(137,2,'UPDATE','transactions',15,'Payment Status: unpaid, Customer: Ron Ace De Taza, Total Amount: 310.00, Delivery ID: 27','Payment Status: paid, Customer: Ron Ace De Taza, Total Amount: 310.00, Delivery ID: 27','2026-05-01 04:03:53'),(138,2,'UPDATE','users',2,'Email: katigbakkristine88@gmail.com','Email: katigbakkristine04@gmail.com','2026-05-01 04:33:36'),(139,2,'UPDATE','users',2,'Password: Previous password','Password: New password','2026-05-01 04:34:17'),(140,1,'UPDATE','users',1,'Username: owner','Username: ownery','2026-05-01 05:02:18'),(141,1,'UPDATE','users',1,'Username: ownery','Username: owner','2026-05-01 05:02:29'),(142,1,'UPDATE','users',1,'Username: owner','Username: ownery','2026-05-01 05:10:18'),(143,1,'UPDATE','users',1,'Password: Previous password','Password: New password','2026-05-01 05:11:26'),(144,2,'UPDATE','users',2,'Username: admin','Username: adminy','2026-05-01 05:14:46'),(145,1,'UPDATE','users',1,'Password: Previous password','Password: New password','2026-05-01 05:38:47'),(146,1,'UPDATE','users',1,'Username: ownery, Password: Previous password','Username: owner, Password: New password','2026-05-01 05:40:45'),(147,2,'UPDATE','users',2,'Username: adminy, Password: Previous password','Username: admin, Password: New password','2026-05-01 05:41:12'),(148,1,'UPDATE','users',1,'Password: Previous password','Password: New password','2026-05-01 05:41:35'),(149,2,'UPDATE','users',2,'Password: Previous password','Password: New password','2026-05-01 05:42:04'),(150,1,'INSERT','lpg_products',19,NULL,'Name: try, Size: 11kg, Refill: 60.00, New Tank: 60.00, Active: Yes','2026-05-01 05:43:06'),(151,1,'DELETE','lpg_products',19,'Name: try, Size: 11kg, Refill: 60.00, New Tank: 60.00, Active: Yes',NULL,'2026-05-01 06:01:37'),(152,2,'INSERT','deliveries',28,NULL,'Customer: Kristine Katigbak, Date: 2026-05-01, Status: pending','2026-05-01 06:16:42'),(153,3,'UPDATE','users',3,'Password: Previous password','Password: New password','2026-05-01 07:28:50'),(154,2,'INSERT','transactions',16,NULL,'Payment Status: unpaid, Customer: Kristine Katigbak, Total Amount: 930.00, Delivery ID: 28','2026-05-01 07:38:51'),(155,2,'INSERT','transactions',17,NULL,'Payment Status: unpaid, Customer: Francine Kim Flores, Total Amount: 310.00, Delivery ID: 26','2026-05-01 07:38:55'),(156,2,'INSERT','transactions',18,NULL,'Payment Status: unpaid, Customer: Kristine Katigbak, Total Amount: 6500.00, Delivery ID: 25','2026-05-01 07:38:59'),(157,2,'UPDATE','transactions',18,'Payment Status: unpaid, Customer: Kristine Katigbak, Total Amount: 6500.00, Delivery ID: 25','Payment Status: paid, Customer: Kristine Katigbak, Total Amount: 6500.00, Delivery ID: 25','2026-05-01 07:39:14'),(158,2,'UPDATE','transactions',17,'Payment Status: unpaid, Customer: Francine Kim Flores, Total Amount: 310.00, Delivery ID: 26','Payment Status: paid, Customer: Francine Kim Flores, Total Amount: 310.00, Delivery ID: 26','2026-05-01 07:39:16'),(159,2,'UPDATE','transactions',16,'Payment Status: unpaid, Customer: Kristine Katigbak, Total Amount: 930.00, Delivery ID: 28','Payment Status: paid, Customer: Kristine Katigbak, Total Amount: 930.00, Delivery ID: 28','2026-05-01 07:39:18');
/*!40000 ALTER TABLE `audit_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customers`
--

DROP TABLE IF EXISTS `customers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `full_name` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `address` text COLLATE utf8mb4_general_ci NOT NULL,
  `contact_number` varchar(20) COLLATE utf8mb4_general_ci NOT NULL,
  `notes` text COLLATE utf8mb4_general_ci,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_customers_created_at_id` (`created_at`,`id`),
  KEY `idx_customers_full_name` (`full_name`)
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customers`
--

LOCK TABLES `customers` WRITE;
/*!40000 ALTER TABLE `customers` DISABLE KEYS */;
INSERT INTO `customers` VALUES (26,'Jherode Aaron Petate','Rillo, Tuy, Batangas','09956190545',NULL,'2026-04-27 01:24:25'),(27,'Kristine Katigbak','Burgos, Tuy, Batangas','09919899657',NULL,'2026-04-27 01:25:02'),(28,'Fatima Suzzane Solis','Ermita, Balayan, Batangas','09643421255',NULL,'2026-04-27 01:25:59'),(29,'Francine Kim Flores','Lian, Batangas','09987341213','secret ang baranggay','2026-04-27 01:26:36'),(30,'Janine Cedilla','Magahis, Tuy, Batangas','09123456789',NULL,'2026-04-27 01:27:31'),(31,'Ron Ace De Taza','Luna, Tuy, Batangas','09127164852',NULL,'2026-04-27 01:28:38'),(32,'Erez Shore','Dao, Tuy, Batangas','09983758232',NULL,'2026-04-27 01:29:10'),(33,'Lucerys Velaryon','Putol, Tuy, Batangas','09675829121',NULL,'2026-04-27 01:30:05'),(34,'Rhaenyra Targaryen','Luna, Tuy, Batangas','09182748211',NULL,'2026-04-27 01:30:49'),(35,'Anghelica Fajardo','Toong, Tuy, Batangas','09759951254',NULL,'2026-04-27 01:31:48');
/*!40000 ALTER TABLE `customers` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `before_customer_insert` BEFORE INSERT ON `customers` FOR EACH ROW BEGIN
    SET NEW.full_name = TRIM(COALESCE(NEW.full_name, ''));
    SET NEW.address = TRIM(COALESCE(NEW.address, ''));
    SET NEW.contact_number = TRIM(COALESCE(NEW.contact_number, ''));
    SET NEW.notes = NULLIF(TRIM(COALESCE(NEW.notes, '')), '');

    IF NEW.full_name = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Full name cannot be empty.';
    END IF;

    IF NEW.address = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Address cannot be empty.';
    END IF;

    IF NEW.contact_number = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Contact number cannot be empty.';
    END IF;

    IF NEW.contact_number NOT REGEXP '^(09[0-9]{9}|63[0-9]{10}|\\+63[0-9]{10})$' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Contact number must be a valid PH number (09XXXXXXXXX, 639XXXXXXXXX, or +639XXXXXXXXX).';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM customers c
        WHERE REGEXP_REPLACE(LOWER(TRIM(c.full_name)), '[^a-z0-9 ]', '')
            = REGEXP_REPLACE(LOWER(NEW.full_name), '[^a-z0-9 ]', '')
          AND LOWER(TRIM(c.address)) = LOWER(NEW.address)
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A customer with the same name and address already exists.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM customers c
        WHERE REGEXP_REPLACE(LOWER(TRIM(c.full_name)), '[^a-z0-9 ]', '')
            = REGEXP_REPLACE(LOWER(NEW.full_name), '[^a-z0-9 ]', '')
          AND TRIM(c.contact_number) = NEW.contact_number
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A customer with the same name and contact number already exists.';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `after_customer_insert` AFTER INSERT ON `customers` FOR EACH ROW BEGIN
    INSERT INTO audit_logs (user_id, action, table_name, record_id, old_value, new_value)
    VALUES (
        COALESCE(NULLIF(@current_user_id, 0), 1),
        'INSERT',
        'customers',
        NEW.id,
        NULL,
        CONCAT_WS(', ',
            CONCAT('Full Name: ', NEW.full_name),
            CONCAT('Address: ', NEW.address),
            CONCAT('Contact Number: ', NEW.contact_number),
            CONCAT('Notes: ', COALESCE(NULLIF(NEW.notes, ''), '-'))
        )
    );
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `before_customer_update` BEFORE UPDATE ON `customers` FOR EACH ROW BEGIN
    IF NOT (OLD.id <=> NEW.id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Customer ID cannot be changed.';
    END IF;

    SET NEW.full_name = TRIM(COALESCE(NEW.full_name, ''));
    SET NEW.address = TRIM(COALESCE(NEW.address, ''));
    SET NEW.contact_number = TRIM(COALESCE(NEW.contact_number, ''));
    SET NEW.notes = NULLIF(TRIM(COALESCE(NEW.notes, '')), '');

    IF NEW.full_name = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Full name cannot be empty.';
    END IF;

    IF NEW.address = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Address cannot be empty.';
    END IF;

    IF NEW.contact_number = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Contact number cannot be empty.';
    END IF;

    IF NEW.contact_number NOT REGEXP '^(09[0-9]{9}|63[0-9]{10}|\\+63[0-9]{10})$' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Contact number must be a valid PH number (09XXXXXXXXX, 639XXXXXXXXX, or +639XXXXXXXXX).';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM customers c
        WHERE c.id <> OLD.id
          AND REGEXP_REPLACE(LOWER(TRIM(c.full_name)), '[^a-z0-9 ]', '')
            = REGEXP_REPLACE(LOWER(NEW.full_name), '[^a-z0-9 ]', '')
          AND LOWER(TRIM(c.address)) = LOWER(NEW.address)
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A customer with the same name and address already exists.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM customers c
        WHERE c.id <> OLD.id
          AND REGEXP_REPLACE(LOWER(TRIM(c.full_name)), '[^a-z0-9 ]', '')
            = REGEXP_REPLACE(LOWER(NEW.full_name), '[^a-z0-9 ]', '')
          AND TRIM(c.contact_number) = NEW.contact_number
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A customer with the same name and contact number already exists.';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `after_customer_update` AFTER UPDATE ON `customers` FOR EACH ROW BEGIN
    IF NOT (OLD.full_name <=> NEW.full_name)
       OR NOT (OLD.address <=> NEW.address)
       OR NOT (OLD.contact_number <=> NEW.contact_number)
       OR NOT (OLD.notes <=> NEW.notes)
    THEN
        INSERT INTO audit_logs (user_id, action, table_name, record_id, old_value, new_value)
        VALUES (
            COALESCE(NULLIF(@current_user_id, 0), 1),
            'UPDATE',
            'customers',
            NEW.id,
            CONCAT_WS(', ',
                IF(NOT (OLD.full_name <=> NEW.full_name), CONCAT('Full Name: ', OLD.full_name), NULL),
                IF(NOT (OLD.address <=> NEW.address), CONCAT('Address: ', OLD.address), NULL),
                IF(NOT (OLD.contact_number <=> NEW.contact_number), CONCAT('Contact Number: ', OLD.contact_number), NULL),
                IF(NOT (OLD.notes <=> NEW.notes), CONCAT('Notes: ', COALESCE(NULLIF(OLD.notes, ''), '-')), NULL)
            ),
            CONCAT_WS(', ',
                IF(NOT (OLD.full_name <=> NEW.full_name), CONCAT('Full Name: ', NEW.full_name), NULL),
                IF(NOT (OLD.address <=> NEW.address), CONCAT('Address: ', NEW.address), NULL),
                IF(NOT (OLD.contact_number <=> NEW.contact_number), CONCAT('Contact Number: ', NEW.contact_number), NULL),
                IF(NOT (OLD.notes <=> NEW.notes), CONCAT('Notes: ', COALESCE(NULLIF(NEW.notes, ''), '-')), NULL)
            )
        );
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `after_customer_delete` AFTER DELETE ON `customers` FOR EACH ROW BEGIN
    INSERT INTO audit_logs (user_id, action, table_name, record_id, old_value, new_value)
    VALUES (
        COALESCE(NULLIF(@current_user_id, 0), 1),
        'DELETE',
        'customers',
        OLD.id,
        CONCAT_WS(', ',
            CONCAT('Full Name: ', OLD.full_name),
            CONCAT('Address: ', OLD.address),
            CONCAT('Contact Number: ', OLD.contact_number),
            CONCAT('Notes: ', COALESCE(NULLIF(OLD.notes, ''), '-'))
        ),
        NULL
    );
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `daily_reports`
--

DROP TABLE IF EXISTS `daily_reports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `daily_reports` (
  `id` int NOT NULL AUTO_INCREMENT,
  `report_date` date NOT NULL,
  `total_deliveries` int NOT NULL DEFAULT '0',
  `total_delivered` int NOT NULL DEFAULT '0',
  `total_cancelled` int NOT NULL DEFAULT '0',
  `total_pending` int NOT NULL DEFAULT '0',
  `total_in_transit` int NOT NULL DEFAULT '0',
  `total_sales` decimal(10,2) NOT NULL DEFAULT '0.00',
  `total_paid` decimal(10,2) NOT NULL DEFAULT '0.00',
  `total_unpaid` decimal(10,2) NOT NULL DEFAULT '0.00',
  `generated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `report_date` (`report_date`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `daily_reports`
--

LOCK TABLES `daily_reports` WRITE;
/*!40000 ALTER TABLE `daily_reports` DISABLE KEYS */;
INSERT INTO `daily_reports` VALUES (1,'2026-04-26',0,0,0,0,0,0.00,0.00,0.00,'2026-04-27 02:38:51'),(2,'2026-04-27',5,3,2,0,0,8740.00,8740.00,0.00,'2026-04-29 15:13:51'),(3,'2026-04-29',7,5,2,0,0,22480.00,22480.00,0.00,'2026-04-29 16:00:00');
/*!40000 ALTER TABLE `daily_reports` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `deliveries`
--

DROP TABLE IF EXISTS `deliveries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `deliveries` (
  `id` int NOT NULL AUTO_INCREMENT,
  `customer_id` int NOT NULL,
  `user_id` int NOT NULL,
  `schedule_date` date NOT NULL,
  `status` enum('pending','in_transit','delivered','cancelled') COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'pending',
  `notes` text COLLATE utf8mb4_general_ci,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `idx_deliveries_schedule_date` (`schedule_date`),
  KEY `idx_deliveries_status` (`status`),
  KEY `idx_deliveries_customer_id` (`customer_id`),
  KEY `idx_deliveries_status_date` (`status`,`schedule_date`,`id`),
  KEY `idx_deliveries_customer_schedule_date` (`customer_id`,`schedule_date`),
  CONSTRAINT `deliveries_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`),
  CONSTRAINT `deliveries_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `deliveries`
--

LOCK TABLES `deliveries` WRITE;
/*!40000 ALTER TABLE `deliveries` DISABLE KEYS */;
INSERT INTO `deliveries` VALUES (7,35,2,'2026-04-27','cancelled',NULL,'2026-04-27 12:40:54','2026-04-27 15:49:45'),(8,26,2,'2026-04-27','delivered',NULL,'2026-04-27 12:52:24','2026-04-27 15:49:40'),(9,30,2,'2026-04-27','cancelled',NULL,'2026-04-27 12:53:08','2026-04-27 15:49:15'),(10,27,2,'2026-04-27','delivered',NULL,'2026-04-27 12:53:36','2026-04-27 15:49:33'),(11,34,2,'2026-04-27','delivered',NULL,'2026-04-27 12:54:03','2026-04-27 15:49:26'),(12,26,2,'2026-04-29','delivered',NULL,'2026-04-29 11:36:29','2026-04-29 11:43:32'),(13,30,2,'2026-04-29','delivered',NULL,'2026-04-29 11:36:47','2026-04-29 11:43:28'),(14,29,2,'2026-04-29','delivered',NULL,'2026-04-29 11:37:25','2026-04-29 11:43:24'),(15,35,2,'2026-04-29','cancelled',NULL,'2026-04-29 14:09:58','2026-04-29 14:10:14'),(16,27,2,'2026-04-29','cancelled',NULL,'2026-04-29 15:25:27','2026-04-29 15:33:49'),(17,26,2,'2026-04-29','delivered',NULL,'2026-04-29 15:25:42','2026-04-29 15:28:37'),(18,33,2,'2026-04-29','delivered',NULL,'2026-04-29 15:26:14','2026-04-29 15:28:34'),(19,30,2,'2026-04-30','cancelled',NULL,'2026-04-30 00:03:42','2026-04-30 07:16:23'),(20,34,2,'2026-04-30','delivered',NULL,'2026-04-30 00:03:58','2026-04-30 07:16:18'),(21,28,2,'2026-04-30','delivered',NULL,'2026-04-30 00:04:18','2026-04-30 07:16:14'),(25,27,2,'2026-05-01','delivered',NULL,'2026-04-30 22:51:49','2026-05-01 07:38:59'),(26,29,2,'2026-05-01','delivered',NULL,'2026-04-30 22:52:07','2026-05-01 07:38:55'),(27,31,2,'2026-05-01','delivered',NULL,'2026-05-01 04:02:49','2026-05-01 04:03:26'),(28,27,2,'2026-05-01','delivered',NULL,'2026-05-01 06:16:42','2026-05-01 07:38:51');
/*!40000 ALTER TABLE `deliveries` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `before_delivery_insert` BEFORE INSERT ON `deliveries` FOR EACH ROW BEGIN
    SET NEW.notes = NULLIF(TRIM(COALESCE(NEW.notes, '')), '');

    IF NEW.customer_id IS NULL
       OR NOT EXISTS (SELECT 1 FROM customers WHERE id = NEW.customer_id)
    THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid customer.';
    END IF;

    IF NEW.user_id IS NULL
       OR NOT EXISTS (SELECT 1 FROM users WHERE id = NEW.user_id AND role = 'admin')
    THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Only administrators can create deliveries.';
    END IF;

    IF NEW.schedule_date IS NULL OR NEW.schedule_date < CURDATE() THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Schedule date cannot be in the past.';
    END IF;

    IF NEW.status IS NULL THEN
        SET NEW.status = 'pending';
    END IF;

    IF NEW.status <> 'pending' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'New deliveries must start as pending.';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `after_delivery_insert` AFTER INSERT ON `deliveries` FOR EACH ROW BEGIN
  INSERT INTO audit_logs (user_id, action, table_name, record_id, old_value, new_value)
  VALUES (
    NEW.user_id, 'INSERT', 'deliveries', NEW.id, NULL,
    CONCAT(
      'Customer: ', (SELECT full_name FROM customers WHERE id = NEW.customer_id),
      ', Date: ', NEW.schedule_date,
      ', Status: ', NEW.status
    )
  );
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `before_delivery_update` BEFORE UPDATE ON `deliveries` FOR EACH ROW BEGIN
    DECLARE v_paid_transaction_count INT DEFAULT 0;

    SET NEW.notes = NULLIF(TRIM(COALESCE(NEW.notes, '')), '');

    IF NOT (OLD.id <=> NEW.id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Delivery ID cannot be changed.';
    END IF;

    IF NEW.customer_id IS NULL
       OR NOT EXISTS (SELECT 1 FROM customers WHERE id = NEW.customer_id)
    THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid customer.';
    END IF;

    IF NEW.user_id IS NULL
       OR NOT EXISTS (SELECT 1 FROM users WHERE id = NEW.user_id AND role = 'admin')
    THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid delivery user.';
    END IF;

    IF NOT (OLD.schedule_date <=> NEW.schedule_date)
       AND (NEW.schedule_date IS NULL OR NEW.schedule_date < CURDATE())
    THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Schedule date cannot be in the past.';
    END IF;

    IF NEW.status NOT IN ('pending', 'in_transit', 'delivered', 'cancelled') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid delivery status.';
    END IF;

    IF OLD.status <> NEW.status THEN
        IF OLD.status = 'pending'
           AND NEW.status NOT IN ('in_transit', 'delivered', 'cancelled')
        THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Pending deliveries can only move to in transit, delivered, or cancelled.';
        END IF;

        IF OLD.status = 'in_transit'
           AND NEW.status NOT IN ('delivered', 'cancelled')
        THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'In-transit deliveries can only move to delivered or cancelled.';
        END IF;

        IF OLD.status = 'cancelled' THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Cancelled deliveries cannot be changed.';
        END IF;

        IF OLD.status = 'delivered'
           AND NEW.status <> 'cancelled'
        THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Delivered deliveries can only be cancelled when unpaid.';
        END IF;

        IF NEW.status = 'delivered'
           AND NOT EXISTS (SELECT 1 FROM delivery_items WHERE delivery_id = OLD.id)
        THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'A delivery must have at least one item before it can be delivered.';
        END IF;

        IF NEW.status = 'delivered'
           AND EXISTS (SELECT 1 FROM transactions WHERE delivery_id = OLD.id)
        THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'This delivery already has a transaction record.';
        END IF;

        IF NEW.status <> 'delivered' THEN
            SELECT COUNT(*)
            INTO v_paid_transaction_count
            FROM transactions
            WHERE delivery_id = OLD.id
              AND payment_status = 'paid';

            IF v_paid_transaction_count > 0 THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Paid deliveries cannot be cancelled.';
            END IF;
        END IF;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'NO_AUTO_VALUE_ON_ZERO' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `after_delivery_completed` AFTER UPDATE ON `deliveries` FOR EACH ROW BEGIN
  IF NEW.status = 'delivered' AND OLD.status != 'delivered' THEN
    INSERT INTO transactions (delivery_id, total_amount, payment_status)
    SELECT
      NEW.id,
      SUM(quantity * price_at_delivery),
      'unpaid'
    FROM delivery_items
    WHERE delivery_id = NEW.id;
  END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `after_delivery_status_update` AFTER UPDATE ON `deliveries` FOR EACH ROW BEGIN
    IF OLD.status <> NEW.status THEN
        INSERT INTO delivery_logs (delivery_id, user_id, old_status, new_status)
        VALUES (
            NEW.id,
            COALESCE(NULLIF(@current_user_id, 0), NEW.user_id),
            OLD.status,
            NEW.status
        );
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `delivery_items`
--

DROP TABLE IF EXISTS `delivery_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `delivery_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `delivery_id` int NOT NULL,
  `product_id` int NOT NULL,
  `quantity` int NOT NULL,
  `type` enum('refill','new_tank') COLLATE utf8mb4_general_ci NOT NULL,
  `price_at_delivery` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `product_id` (`product_id`),
  KEY `idx_delivery_items_delivery_id` (`delivery_id`),
  KEY `idx_delivery_items_product_delivery` (`product_id`,`delivery_id`),
  CONSTRAINT `delivery_items_ibfk_1` FOREIGN KEY (`delivery_id`) REFERENCES `deliveries` (`id`),
  CONSTRAINT `delivery_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `lpg_products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `delivery_items`
--

LOCK TABLES `delivery_items` WRITE;
/*!40000 ALTER TABLE `delivery_items` DISABLE KEYS */;
INSERT INTO `delivery_items` VALUES (1,7,15,1,'refill',310.00),(2,8,14,1,'refill',930.00),(3,8,15,1,'new_tank',1310.00),(4,8,15,1,'refill',310.00),(5,8,14,1,'new_tank',2630.00),(6,9,15,1,'refill',310.00),(7,9,15,1,'new_tank',1310.00),(8,10,14,1,'new_tank',2630.00),(9,11,15,2,'refill',310.00),(10,11,15,1,'refill',310.00),(11,12,15,1,'refill',310.00),(12,12,15,1,'new_tank',1310.00),(13,12,14,1,'refill',930.00),(14,13,15,1,'refill',310.00),(15,13,15,3,'new_tank',1310.00),(16,14,14,2,'refill',930.00),(17,15,15,1,'refill',310.00),(18,16,14,2,'new_tank',2630.00),(19,16,14,1,'refill',930.00),(20,16,15,2,'new_tank',1310.00),(21,16,15,1,'refill',310.00),(22,16,14,3,'new_tank',2630.00),(23,16,15,1,'refill',310.00),(24,17,15,1,'refill',310.00),(25,17,15,1,'refill',310.00),(26,17,15,1,'refill',310.00),(27,17,14,1,'refill',930.00),(28,17,15,1,'refill',310.00),(29,17,14,1,'refill',930.00),(30,17,14,1,'refill',930.00),(31,17,15,1,'refill',310.00),(32,17,15,1,'refill',310.00),(33,18,15,1,'new_tank',1310.00),(34,18,15,1,'new_tank',1310.00),(35,18,15,1,'new_tank',1310.00),(36,18,15,1,'new_tank',1310.00),(37,18,15,1,'new_tank',1310.00),(38,18,14,1,'new_tank',2630.00),(39,19,15,1,'refill',310.00),(40,20,14,1,'new_tank',2630.00),(41,21,15,1,'refill',310.00),(42,21,14,1,'new_tank',2630.00),(45,25,14,2,'new_tank',2630.00),(46,25,15,1,'refill',310.00),(47,25,14,1,'refill',930.00),(48,26,15,1,'refill',310.00),(49,27,15,1,'refill',310.00),(50,28,14,1,'refill',930.00);
/*!40000 ALTER TABLE `delivery_items` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = cp850 */ ;
/*!50003 SET character_set_results = cp850 */ ;
/*!50003 SET collation_connection  = cp850_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `before_delivery_item_insert` BEFORE INSERT ON `delivery_items` FOR EACH ROW BEGIN
    IF NEW.delivery_id IS NULL
       OR NOT EXISTS (
           SELECT 1
           FROM deliveries
           WHERE id = NEW.delivery_id
             AND status = 'pending'
       )
    THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Delivery items can only be added to pending deliveries.';
    END IF;

    IF NEW.product_id IS NULL
       OR NOT EXISTS (
           SELECT 1
           FROM lpg_products
           WHERE id = NEW.product_id
             AND is_active = 1
       )
    THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Please select an active product.';
    END IF;

    IF NEW.quantity IS NULL OR NEW.quantity <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Quantity must be at least 1.';
    END IF;

    IF NEW.price_at_delivery IS NULL OR NEW.price_at_delivery <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Delivery item price must be greater than zero.';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = cp850 */ ;
/*!50003 SET character_set_results = cp850 */ ;
/*!50003 SET collation_connection  = cp850_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `before_delivery_item_update` BEFORE UPDATE ON `delivery_items` FOR EACH ROW BEGIN
    IF NOT (OLD.delivery_id <=> NEW.delivery_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Delivery item cannot be moved to another delivery.';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM deliveries
        WHERE id = OLD.delivery_id
          AND status = 'pending'
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Delivery items can only be edited while the delivery is pending.';
    END IF;

    IF NEW.product_id IS NULL
       OR NOT EXISTS (
           SELECT 1
           FROM lpg_products
           WHERE id = NEW.product_id
             AND is_active = 1
       )
    THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Please select an active product.';
    END IF;

    IF NEW.quantity IS NULL OR NEW.quantity <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Quantity must be at least 1.';
    END IF;

    IF NEW.price_at_delivery IS NULL OR NEW.price_at_delivery <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Delivery item price must be greater than zero.';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `before_delivery_item_delete` BEFORE DELETE ON `delivery_items` FOR EACH ROW BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM deliveries
        WHERE id = OLD.delivery_id
          AND status = 'pending'
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Delivery items can only be deleted while the delivery is pending.';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `delivery_logs`
--

DROP TABLE IF EXISTS `delivery_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `delivery_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `delivery_id` int NOT NULL,
  `user_id` int NOT NULL,
  `old_status` varchar(20) COLLATE utf8mb4_general_ci NOT NULL,
  `new_status` varchar(20) COLLATE utf8mb4_general_ci NOT NULL,
  `changed_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `idx_delivery_logs_delivery_id` (`delivery_id`),
  KEY `idx_delivery_logs_changed_at_id` (`changed_at`,`id`),
  CONSTRAINT `delivery_logs_ibfk_1` FOREIGN KEY (`delivery_id`) REFERENCES `deliveries` (`id`),
  CONSTRAINT `delivery_logs_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `delivery_logs`
--

LOCK TABLES `delivery_logs` WRITE;
/*!40000 ALTER TABLE `delivery_logs` DISABLE KEYS */;
INSERT INTO `delivery_logs` VALUES (3,11,2,'pending','in_transit','2026-04-27 15:48:58'),(4,10,2,'pending','in_transit','2026-04-27 15:49:05'),(5,8,2,'pending','in_transit','2026-04-27 15:49:10'),(6,9,2,'pending','cancelled','2026-04-27 15:49:15'),(7,7,2,'pending','in_transit','2026-04-27 15:49:21'),(8,11,2,'in_transit','delivered','2026-04-27 15:49:26'),(9,10,2,'in_transit','delivered','2026-04-27 15:49:33'),(10,8,2,'in_transit','delivered','2026-04-27 15:49:40'),(11,7,2,'in_transit','cancelled','2026-04-27 15:49:45'),(12,14,2,'pending','in_transit','2026-04-29 11:43:04'),(13,13,2,'pending','in_transit','2026-04-29 11:43:10'),(14,12,2,'pending','in_transit','2026-04-29 11:43:15'),(15,14,2,'in_transit','delivered','2026-04-29 11:43:24'),(16,13,2,'in_transit','delivered','2026-04-29 11:43:28'),(17,12,2,'in_transit','delivered','2026-04-29 11:43:32'),(18,15,2,'pending','cancelled','2026-04-29 14:10:14'),(19,18,2,'pending','in_transit','2026-04-29 15:28:09'),(20,17,2,'pending','in_transit','2026-04-29 15:28:12'),(21,16,2,'pending','in_transit','2026-04-29 15:28:16'),(22,18,2,'in_transit','delivered','2026-04-29 15:28:34'),(23,17,2,'in_transit','delivered','2026-04-29 15:28:37'),(24,16,2,'in_transit','cancelled','2026-04-29 15:33:49'),(25,21,2,'pending','in_transit','2026-04-30 01:00:39'),(26,20,2,'pending','in_transit','2026-04-30 01:00:42'),(27,19,2,'pending','in_transit','2026-04-30 01:00:45'),(28,21,2,'in_transit','delivered','2026-04-30 07:16:14'),(29,20,2,'in_transit','delivered','2026-04-30 07:16:18'),(30,19,2,'in_transit','cancelled','2026-04-30 07:16:23'),(33,27,2,'pending','in_transit','2026-05-01 04:03:21'),(34,27,2,'in_transit','delivered','2026-05-01 04:03:26'),(35,28,2,'pending','in_transit','2026-05-01 07:38:07'),(36,26,2,'pending','in_transit','2026-05-01 07:38:10'),(37,25,2,'pending','in_transit','2026-05-01 07:38:13'),(38,28,2,'in_transit','delivered','2026-05-01 07:38:51'),(39,26,2,'in_transit','delivered','2026-05-01 07:38:55'),(40,25,2,'in_transit','delivered','2026-05-01 07:38:59');
/*!40000 ALTER TABLE `delivery_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `internal_messages`
--

DROP TABLE IF EXISTS `internal_messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `internal_messages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sender_id` int NOT NULL,
  `receiver_id` int NOT NULL,
  `body` text COLLATE utf8mb4_general_ci NOT NULL,
  `read_at` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_internal_messages_receiver_read` (`receiver_id`,`read_at`),
  KEY `idx_internal_messages_pair_created` (`sender_id`,`receiver_id`,`created_at`),
  KEY `idx_internal_messages_created` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `internal_messages`
--

LOCK TABLES `internal_messages` WRITE;
/*!40000 ALTER TABLE `internal_messages` DISABLE KEYS */;
INSERT INTO `internal_messages` VALUES (1,2,1,'hello!','2026-05-01 14:54:29','2026-05-01 14:54:03','2026-05-01 14:54:29'),(2,2,1,'i miss you baby','2026-05-01 15:32:23','2026-05-01 15:31:23','2026-05-01 15:32:23'),(3,1,2,'thank you hehe','2026-05-01 15:33:12','2026-05-01 15:32:28','2026-05-01 15:33:12'),(4,2,1,'kumain ka na ba?',NULL,'2026-05-01 15:55:13','2026-05-01 15:55:13'),(5,2,1,'pautang muna ako ha',NULL,'2026-05-01 15:55:23','2026-05-01 15:55:23'),(6,2,1,'wala na makain d2 sa shop ende aq makakupit oy naka-padlock',NULL,'2026-05-01 15:55:56','2026-05-01 15:55:56'),(7,2,1,'ang pagmamahal ko sau ay parang bato, matigas hindi nababasag ahahahaha miss u mahal q\n\nkung andito ka lang sana sa tabi ko',NULL,'2026-05-01 15:56:43','2026-05-01 15:56:43');
/*!40000 ALTER TABLE `internal_messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lpg_products`
--

DROP TABLE IF EXISTS `lpg_products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lpg_products` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `cylinder_size` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `refill_price` decimal(10,2) NOT NULL,
  `new_tank_price` decimal(10,2) NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `normalized_name` varchar(100) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `normalized_cylinder_size` varchar(20) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `active_name_key` varchar(100) COLLATE utf8mb4_general_ci GENERATED ALWAYS AS ((case when (`is_active` = 1) then `normalized_name` else NULL end)) STORED,
  `active_size_key` varchar(20) COLLATE utf8mb4_general_ci GENERATED ALWAYS AS ((case when (`is_active` = 1) then `normalized_cylinder_size` else NULL end)) STORED,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_lpg_products_active_name_size` (`active_name_key`,`active_size_key`),
  CONSTRAINT `chk_lpg_products_is_active_boolean` CHECK ((`is_active` in (0,1))),
  CONSTRAINT `chk_lpg_products_new_tank_price_positive` CHECK ((`new_tank_price` > 0)),
  CONSTRAINT `chk_lpg_products_refill_price_positive` CHECK ((`refill_price` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lpg_products`
--

LOCK TABLES `lpg_products` WRITE;
/*!40000 ALTER TABLE `lpg_products` DISABLE KEYS */;
INSERT INTO `lpg_products` (`id`, `name`, `cylinder_size`, `refill_price`, `new_tank_price`, `is_active`, `created_at`, `updated_at`, `normalized_name`, `normalized_cylinder_size`) VALUES (14,'Town Gaz','11kg',930.00,2630.00,1,'2026-04-30 23:27:03','2026-04-30 23:45:58','town gaz','11kg'),(15,'Superkalan','2.7kg',310.00,1310.00,1,'2026-04-30 23:27:03','2026-05-01 04:01:57','superkalan','2.7kg');
/*!40000 ALTER TABLE `lpg_products` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = cp850 */ ;
/*!50003 SET character_set_results = cp850 */ ;
/*!50003 SET collation_connection  = cp850_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `before_product_insert` BEFORE INSERT ON `lpg_products` FOR EACH ROW BEGIN
    DECLARE v_size_value DECIMAL(10,2);

    SET NEW.name = TRIM(COALESCE(NEW.name, ''));
    SET NEW.cylinder_size = TRIM(COALESCE(NEW.cylinder_size, ''));
    SET NEW.is_active = COALESCE(NEW.is_active, 1);

    IF NEW.name = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Product name cannot be empty.';
    END IF;

    IF NEW.cylinder_size = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cylinder size cannot be empty.';
    END IF;

    IF NOT REGEXP_LIKE(NEW.cylinder_size, '^[[:space:]]*[0-9]+(\\.[0-9]+)?[[:space:]]*(kg)?[[:space:]]*$', 'i') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Enter a valid cylinder size like 2.7 or 11kg.';
    END IF;

    SET v_size_value = CAST(REGEXP_REPLACE(NEW.cylinder_size, '[^0-9.]', '') AS DECIMAL(10,2));
    IF v_size_value <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cylinder size must be greater than zero.';
    END IF;

    IF NEW.refill_price IS NULL OR NEW.refill_price <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Refill price must be greater than zero.';
    END IF;

    IF NEW.new_tank_price IS NULL OR NEW.new_tank_price <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'New tank price must be greater than zero.';
    END IF;

    IF NEW.is_active NOT IN (0, 1) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Product active status must be valid.';
    END IF;

    SET NEW.refill_price = ROUND(NEW.refill_price, 2);
    SET NEW.new_tank_price = ROUND(NEW.new_tank_price, 2);
    SET NEW.normalized_name = TRIM(
        REGEXP_REPLACE(
            REGEXP_REPLACE(LOWER(NEW.name), '[^a-z0-9 ]', ''),
            '\\s+',
            ' '
        )
    );
    SET NEW.normalized_cylinder_size = LOWER(NEW.cylinder_size);
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = cp850 */ ;
/*!50003 SET character_set_results = cp850 */ ;
/*!50003 SET collation_connection  = cp850_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `after_product_insert` AFTER INSERT ON `lpg_products` FOR EACH ROW BEGIN
    INSERT INTO audit_logs (user_id, action, table_name, record_id, old_value, new_value)
    VALUES (
        COALESCE(@current_user_id, 1),
        'INSERT',
        'lpg_products',
        NEW.id,
        NULL,
        CONCAT(
            'Name: ', NEW.name,
            ', Size: ', COALESCE(NEW.cylinder_size, ''),
            ', Refill: ', NEW.refill_price,
            ', New Tank: ', NEW.new_tank_price,
            ', Active: ', IF(NEW.is_active = 1, 'Yes', 'No')
        )
    );
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = cp850 */ ;
/*!50003 SET character_set_results = cp850 */ ;
/*!50003 SET collation_connection  = cp850_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `before_product_update` BEFORE UPDATE ON `lpg_products` FOR EACH ROW BEGIN
    DECLARE v_size_value DECIMAL(10,2);

    SET NEW.name = TRIM(COALESCE(NEW.name, ''));
    SET NEW.cylinder_size = TRIM(COALESCE(NEW.cylinder_size, ''));
    SET NEW.is_active = COALESCE(NEW.is_active, OLD.is_active, 1);

    IF NEW.name = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Product name cannot be empty.';
    END IF;

    IF NEW.cylinder_size = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cylinder size cannot be empty.';
    END IF;

    IF NOT REGEXP_LIKE(NEW.cylinder_size, '^[[:space:]]*[0-9]+(\\.[0-9]+)?[[:space:]]*(kg)?[[:space:]]*$', 'i') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Enter a valid cylinder size like 2.7 or 11kg.';
    END IF;

    SET v_size_value = CAST(REGEXP_REPLACE(NEW.cylinder_size, '[^0-9.]', '') AS DECIMAL(10,2));
    IF v_size_value <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cylinder size must be greater than zero.';
    END IF;

    IF NEW.refill_price IS NULL OR NEW.refill_price <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Refill price must be greater than zero.';
    END IF;

    IF NEW.new_tank_price IS NULL OR NEW.new_tank_price <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'New tank price must be greater than zero.';
    END IF;

    IF NEW.is_active NOT IN (0, 1) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Product active status must be valid.';
    END IF;

    SET NEW.refill_price = ROUND(NEW.refill_price, 2);
    SET NEW.new_tank_price = ROUND(NEW.new_tank_price, 2);
    SET NEW.normalized_name = TRIM(
        REGEXP_REPLACE(
            REGEXP_REPLACE(LOWER(NEW.name), '[^a-z0-9 ]', ''),
            '\\s+',
            ' '
        )
    );
    SET NEW.normalized_cylinder_size = LOWER(NEW.cylinder_size);
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = cp850 */ ;
/*!50003 SET character_set_results = cp850 */ ;
/*!50003 SET collation_connection  = cp850_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `after_product_update` AFTER UPDATE ON `lpg_products` FOR EACH ROW BEGIN
    IF NOT (OLD.name <=> NEW.name)
       OR NOT (OLD.cylinder_size <=> NEW.cylinder_size)
       OR NOT (OLD.refill_price <=> NEW.refill_price)
       OR NOT (OLD.new_tank_price <=> NEW.new_tank_price)
       OR NOT (OLD.is_active <=> NEW.is_active)
    THEN
        INSERT INTO audit_logs (user_id, action, table_name, record_id, old_value, new_value)
        VALUES (
            COALESCE(@current_user_id, 1),
            'UPDATE',
            'lpg_products',
            NEW.id,
            CONCAT(
                'Name: ', OLD.name,
                ', Size: ', COALESCE(OLD.cylinder_size, ''),
                ', Refill: ', OLD.refill_price,
                ', New Tank: ', OLD.new_tank_price,
                ', Active: ', IF(OLD.is_active = 1, 'Yes', 'No')
            ),
            CONCAT(
                'Name: ', NEW.name,
                ', Size: ', COALESCE(NEW.cylinder_size, ''),
                ', Refill: ', NEW.refill_price,
                ', New Tank: ', NEW.new_tank_price,
                ', Active: ', IF(NEW.is_active = 1, 'Yes', 'No')
            )
        );
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = cp850 */ ;
/*!50003 SET character_set_results = cp850 */ ;
/*!50003 SET collation_connection  = cp850_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `after_product_delete` AFTER DELETE ON `lpg_products` FOR EACH ROW BEGIN
    INSERT INTO audit_logs (user_id, action, table_name, record_id, old_value, new_value)
    VALUES (
        COALESCE(@current_user_id, 1),
        'DELETE',
        'lpg_products',
        OLD.id,
        CONCAT(
            'Name: ', OLD.name,
            ', Size: ', COALESCE(OLD.cylinder_size, ''),
            ', Refill: ', OLD.refill_price,
            ', New Tank: ', OLD.new_tank_price,
            ', Active: ', IF(OLD.is_active = 1, 'Yes', 'No')
        ),
        NULL
    );
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `monthly_reports`
--

DROP TABLE IF EXISTS `monthly_reports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `monthly_reports` (
  `id` int NOT NULL AUTO_INCREMENT,
  `report_month` date NOT NULL,
  `total_deliveries` int NOT NULL DEFAULT '0',
  `total_delivered` int NOT NULL DEFAULT '0',
  `total_cancelled` int NOT NULL DEFAULT '0',
  `total_pending` int NOT NULL DEFAULT '0',
  `total_in_transit` int NOT NULL DEFAULT '0',
  `total_sales` decimal(10,2) NOT NULL DEFAULT '0.00',
  `total_paid` decimal(10,2) NOT NULL DEFAULT '0.00',
  `total_unpaid` decimal(10,2) NOT NULL DEFAULT '0.00',
  `generated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `report_month` (`report_month`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `monthly_reports`
--

LOCK TABLES `monthly_reports` WRITE;
/*!40000 ALTER TABLE `monthly_reports` DISABLE KEYS */;
/*!40000 ALTER TABLE `monthly_reports` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notification_reads`
--

DROP TABLE IF EXISTS `notification_reads`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notification_reads` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `notification_key` varchar(160) COLLATE utf8mb4_general_ci NOT NULL,
  `read_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_notification_reads_user_key` (`user_id`,`notification_key`),
  KEY `idx_notification_reads_user_read_at` (`user_id`,`read_at`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notification_reads`
--

LOCK TABLES `notification_reads` WRITE;
/*!40000 ALTER TABLE `notification_reads` DISABLE KEYS */;
INSERT INTO `notification_reads` VALUES (1,1,'summary:today-open-deliveries:2:2:0','2026-05-01 14:01:27','2026-05-01 13:42:49','2026-05-01 14:01:27'),(2,2,'audit:150','2026-05-01 14:00:54','2026-05-01 13:43:44','2026-05-01 14:00:54'),(3,2,'summary:today-open-deliveries:2:2:0','2026-05-01 14:00:54','2026-05-01 14:00:54','2026-05-01 14:00:54'),(4,2,'audit:149','2026-05-01 14:00:56','2026-05-01 14:00:54','2026-05-01 14:00:56'),(5,2,'audit:148','2026-05-01 14:00:54','2026-05-01 14:00:54','2026-05-01 14:00:54'),(6,2,'audit:147','2026-05-01 14:00:54','2026-05-01 14:00:54','2026-05-01 14:00:54'),(7,2,'audit:146','2026-05-01 14:00:54','2026-05-01 14:00:54','2026-05-01 14:00:54'),(8,2,'audit:145','2026-05-01 14:00:54','2026-05-01 14:00:54','2026-05-01 14:00:54'),(11,1,'audit:150','2026-05-01 14:01:27','2026-05-01 14:01:27','2026-05-01 14:01:27'),(12,1,'audit:149','2026-05-01 14:01:27','2026-05-01 14:01:27','2026-05-01 14:01:27'),(13,1,'audit:148','2026-05-01 14:01:27','2026-05-01 14:01:27','2026-05-01 14:01:27'),(14,1,'audit:147','2026-05-01 14:01:27','2026-05-01 14:01:27','2026-05-01 14:01:27'),(15,1,'audit:146','2026-05-01 14:01:27','2026-05-01 14:01:27','2026-05-01 14:01:27'),(16,1,'audit:145','2026-05-01 14:01:27','2026-05-01 14:01:27','2026-05-01 14:01:27'),(18,2,'audit:151','2026-05-01 14:06:16','2026-05-01 14:06:16','2026-05-01 14:06:16'),(19,1,'summary:today-open-deliveries:3:3:0','2026-05-01 14:17:27','2026-05-01 14:17:27','2026-05-01 14:17:27'),(20,2,'audit:159','2026-05-01 15:39:45','2026-05-01 15:39:45','2026-05-01 15:39:45'),(21,2,'audit:158','2026-05-01 15:39:45','2026-05-01 15:39:45','2026-05-01 15:39:45'),(22,2,'audit:157','2026-05-01 15:39:45','2026-05-01 15:39:45','2026-05-01 15:39:45'),(23,2,'audit:156','2026-05-01 15:39:45','2026-05-01 15:39:45','2026-05-01 15:39:45'),(24,2,'audit:155','2026-05-01 15:39:45','2026-05-01 15:39:45','2026-05-01 15:39:45'),(25,2,'audit:154','2026-05-01 15:39:45','2026-05-01 15:39:45','2026-05-01 15:39:45');
/*!40000 ALTER TABLE `notification_reads` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transactions`
--

DROP TABLE IF EXISTS `transactions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transactions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `delivery_id` int NOT NULL,
  `total_amount` decimal(10,2) NOT NULL,
  `payment_status` enum('paid','unpaid') COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'unpaid',
  `paid_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `delivery_id` (`delivery_id`),
  KEY `idx_transactions_created_at_id` (`created_at`,`id`),
  KEY `idx_transactions_payment_delivery` (`payment_status`,`delivery_id`),
  CONSTRAINT `transactions_ibfk_1` FOREIGN KEY (`delivery_id`) REFERENCES `deliveries` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transactions`
--

LOCK TABLES `transactions` WRITE;
/*!40000 ALTER TABLE `transactions` DISABLE KEYS */;
INSERT INTO `transactions` VALUES (3,11,930.00,'paid','2026-04-28 03:56:27','2026-04-27 15:49:26'),(4,10,2630.00,'paid','2026-04-28 03:50:31','2026-04-27 15:49:33'),(5,8,5180.00,'paid','2026-04-27 16:14:43','2026-04-27 15:49:40'),(6,14,1860.00,'paid','2026-04-29 11:44:11','2026-04-29 11:43:24'),(7,13,4240.00,'paid','2026-04-29 11:44:08','2026-04-29 11:43:28'),(8,12,2550.00,'paid','2026-04-29 11:44:05','2026-04-29 11:43:32'),(9,18,9180.00,'paid','2026-04-29 15:33:39','2026-04-29 15:28:34'),(10,17,4650.00,'paid','2026-04-29 15:33:37','2026-04-29 15:28:37'),(12,21,2940.00,'paid','2026-04-30 22:51:00','2026-04-30 07:16:14'),(13,20,2630.00,'paid','2026-04-30 07:16:33','2026-04-30 07:16:18'),(15,27,310.00,'paid','2026-05-01 04:03:53','2026-05-01 04:03:26'),(16,28,930.00,'paid','2026-05-01 07:39:18','2026-05-01 07:38:51'),(17,26,310.00,'paid','2026-05-01 07:39:16','2026-05-01 07:38:55'),(18,25,6500.00,'paid','2026-05-01 07:39:14','2026-05-01 07:38:59');
/*!40000 ALTER TABLE `transactions` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `after_transaction_insert` AFTER INSERT ON `transactions` FOR EACH ROW BEGIN
    INSERT INTO audit_logs (user_id, action, table_name, record_id, old_value, new_value)
    VALUES (
        COALESCE(
            NULLIF(@current_user_id, 0),
            (SELECT d.user_id FROM deliveries d WHERE d.id = NEW.delivery_id),
            1
        ),
        'INSERT',
        'transactions',
        NEW.id,
        NULL,
        CONCAT(
            'Payment Status: ', NEW.payment_status,
            ', Customer: ', COALESCE((
                SELECT c.full_name
                FROM deliveries d
                INNER JOIN customers c ON c.id = d.customer_id
                WHERE d.id = NEW.delivery_id
            ), '-'),
            ', Total Amount: ', NEW.total_amount,
            ', Delivery ID: ', NEW.delivery_id
        )
    );
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'NO_AUTO_VALUE_ON_ZERO' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `before_transaction_update` BEFORE UPDATE ON `transactions` FOR EACH ROW BEGIN
  IF OLD.payment_status = 'paid' THEN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Cannot modify a transaction that has already been paid.';
  END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `after_transaction_update` AFTER UPDATE ON `transactions` FOR EACH ROW BEGIN
  IF OLD.payment_status != NEW.payment_status THEN
    INSERT INTO audit_logs (user_id, action, table_name, record_id, old_value, new_value)
    VALUES (
      COALESCE(@current_user_id, 1),
      'UPDATE',
      'transactions',
      NEW.id,
      CONCAT(
        'Payment Status: ', OLD.payment_status,
        ', Customer: ', (SELECT c.full_name FROM deliveries d 
                         INNER JOIN customers c ON c.id = d.customer_id 
                         WHERE d.id = NEW.delivery_id),
        ', Total Amount: ', NEW.total_amount,
        ', Delivery ID: ', NEW.delivery_id
      ),
      CONCAT(
        'Payment Status: ', NEW.payment_status,
        ', Customer: ', (SELECT c.full_name FROM deliveries d 
                         INNER JOIN customers c ON c.id = d.customer_id 
                         WHERE d.id = NEW.delivery_id),
        ', Total Amount: ', NEW.total_amount,
        ', Delivery ID: ', NEW.delivery_id
      )
    );
  END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `full_name` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `username` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `password` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `role` enum('admin','owner') COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'admin',
  `email` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `reset_code` varchar(6) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `reset_code_expires_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `uq_users_username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'G&C Owner','owner','$2b$12$1nwt8Yf/YTdHNbj1NMjfxeO/e/pyaPUXVYgvisdkbpGcTPwqH.MT6','owner','katigbakkristine11@gmail.com',NULL,NULL),(2,'G&C Admin','admin','$2b$12$muBz/U6WRPTrfZ3jQWFhW.K94ac3xRDSS.ac89D6.HAKEa8MfHUVK','admin','katigbakkristine04@gmail.com',NULL,NULL),(3,'sample admin','s_admin','$2b$12$muBz/U6WRPTrfZ3jQWFhW.K94ac3xRDSS.ac89D6.HAKEa8MfHUVK','admin',NULL,NULL,NULL);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `after_user_update` AFTER UPDATE ON `users` FOR EACH ROW BEGIN
    IF NOT (OLD.full_name <=> NEW.full_name)
       OR NOT (OLD.username <=> NEW.username)
       OR NOT (OLD.email <=> NEW.email)
       OR NOT (OLD.role <=> NEW.role)
       OR NOT (OLD.password <=> NEW.password)
    THEN
        INSERT INTO audit_logs (user_id, action, table_name, record_id, old_value, new_value)
        VALUES (
            COALESCE(NULLIF(@current_user_id, 0), NEW.id),
            'UPDATE',
            'users',
            NEW.id,
            CONCAT_WS(', ',
                IF(NOT (OLD.full_name <=> NEW.full_name), CONCAT('Full Name: ', OLD.full_name), NULL),
                IF(NOT (OLD.username <=> NEW.username), CONCAT('Username: ', OLD.username), NULL),
                IF(NOT (OLD.email <=> NEW.email), CONCAT('Email: ', COALESCE(OLD.email, '-')), NULL),
                IF(NOT (OLD.role <=> NEW.role), CONCAT('Role: ', OLD.role), NULL),
                IF(NOT (OLD.password <=> NEW.password), 'Password: Previous password', NULL)
            ),
            CONCAT_WS(', ',
                IF(NOT (OLD.full_name <=> NEW.full_name), CONCAT('Full Name: ', NEW.full_name), NULL),
                IF(NOT (OLD.username <=> NEW.username), CONCAT('Username: ', NEW.username), NULL),
                IF(NOT (OLD.email <=> NEW.email), CONCAT('Email: ', COALESCE(NEW.email, '-')), NULL),
                IF(NOT (OLD.role <=> NEW.role), CONCAT('Role: ', NEW.role), NULL),
                IF(NOT (OLD.password <=> NEW.password), 'Password: New password', NULL)
            )
        );
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Temporary view structure for view `vw_customer_sales_summary`
--

DROP TABLE IF EXISTS `vw_customer_sales_summary`;
/*!50001 DROP VIEW IF EXISTS `vw_customer_sales_summary`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vw_customer_sales_summary` AS SELECT 
 1 AS `customer_id`,
 1 AS `customer_name`,
 1 AS `address`,
 1 AS `total_deliveries`,
 1 AS `completed_deliveries`,
 1 AS `total_spent`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vw_customer_summary`
--

DROP TABLE IF EXISTS `vw_customer_summary`;
/*!50001 DROP VIEW IF EXISTS `vw_customer_summary`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vw_customer_summary` AS SELECT 
 1 AS `id`,
 1 AS `full_name`,
 1 AS `address`,
 1 AS `contact_number`,
 1 AS `notes`,
 1 AS `created_at`,
 1 AS `created_at_fmt`,
 1 AS `total_deliveries`,
 1 AS `delivered_deliveries`,
 1 AS `last_delivery_date`,
 1 AS `last_delivery`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vw_dashboard_today`
--

DROP TABLE IF EXISTS `vw_dashboard_today`;
/*!50001 DROP VIEW IF EXISTS `vw_dashboard_today`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vw_dashboard_today` AS SELECT 
 1 AS `total_today`,
 1 AS `delivered_today`,
 1 AS `pending_today`,
 1 AS `in_transit_today`,
 1 AS `cancelled_today`,
 1 AS `sales_today`,
 1 AS `paid_today`,
 1 AS `unpaid_today`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vw_delivery_details`
--

DROP TABLE IF EXISTS `vw_delivery_details`;
/*!50001 DROP VIEW IF EXISTS `vw_delivery_details`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vw_delivery_details` AS SELECT 
 1 AS `delivery_id`,
 1 AS `schedule_date`,
 1 AS `status`,
 1 AS `notes`,
 1 AS `created_at`,
 1 AS `updated_at`,
 1 AS `customer_id`,
 1 AS `customer_name`,
 1 AS `customer_address`,
 1 AS `customer_contact`,
 1 AS `encoded_by`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vw_delivery_items_details`
--

DROP TABLE IF EXISTS `vw_delivery_items_details`;
/*!50001 DROP VIEW IF EXISTS `vw_delivery_items_details`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vw_delivery_items_details` AS SELECT 
 1 AS `item_id`,
 1 AS `delivery_id`,
 1 AS `product_id`,
 1 AS `product_base_name`,
 1 AS `cylinder_size`,
 1 AS `product_name`,
 1 AS `quantity`,
 1 AS `type`,
 1 AS `price_at_delivery`,
 1 AS `subtotal`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vw_owner_dashboard_daily`
--

DROP TABLE IF EXISTS `vw_owner_dashboard_daily`;
/*!50001 DROP VIEW IF EXISTS `vw_owner_dashboard_daily`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vw_owner_dashboard_daily` AS SELECT 
 1 AS `schedule_date`,
 1 AS `total_deliveries`,
 1 AS `delivered_deliveries`,
 1 AS `pending_deliveries`,
 1 AS `in_transit_deliveries`,
 1 AS `cancelled_deliveries`,
 1 AS `recognized_sales`,
 1 AS `paid_sales`,
 1 AS `unpaid_sales`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vw_report_delivery_financials`
--

DROP TABLE IF EXISTS `vw_report_delivery_financials`;
/*!50001 DROP VIEW IF EXISTS `vw_report_delivery_financials`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vw_report_delivery_financials` AS SELECT 
 1 AS `delivery_id`,
 1 AS `customer_id`,
 1 AS `customer_name`,
 1 AS `customer_contact`,
 1 AS `customer_address`,
 1 AS `user_id`,
 1 AS `schedule_date`,
 1 AS `delivery_status`,
 1 AS `notes`,
 1 AS `created_at`,
 1 AS `updated_at`,
 1 AS `transaction_id`,
 1 AS `transaction_payment_status`,
 1 AS `report_payment_status`,
 1 AS `paid_at`,
 1 AS `total_quantity`,
 1 AS `item_total`,
 1 AS `gross_amount`,
 1 AS `delivered_count`,
 1 AS `cancelled_count`,
 1 AS `pending_count`,
 1 AS `in_transit_count`,
 1 AS `recognized_sales`,
 1 AS `paid_sales`,
 1 AS `unpaid_sales`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vw_report_delivery_lines`
--

DROP TABLE IF EXISTS `vw_report_delivery_lines`;
/*!50001 DROP VIEW IF EXISTS `vw_report_delivery_lines`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vw_report_delivery_lines` AS SELECT 
 1 AS `delivery_id`,
 1 AS `customer_id`,
 1 AS `customer_name`,
 1 AS `customer_contact`,
 1 AS `customer_address`,
 1 AS `schedule_date`,
 1 AS `delivery_status`,
 1 AS `payment_status`,
 1 AS `transaction_id`,
 1 AS `paid_at`,
 1 AS `delivery_item_id`,
 1 AS `product_id`,
 1 AS `product_name`,
 1 AS `quantity`,
 1 AS `type`,
 1 AS `price_at_delivery`,
 1 AS `line_amount`,
 1 AS `recognized_line_sales`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vw_transaction_summary`
--

DROP TABLE IF EXISTS `vw_transaction_summary`;
/*!50001 DROP VIEW IF EXISTS `vw_transaction_summary`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vw_transaction_summary` AS SELECT 
 1 AS `transaction_id`,
 1 AS `delivery_id`,
 1 AS `total_amount`,
 1 AS `payment_status`,
 1 AS `paid_at`,
 1 AS `created_at`,
 1 AS `customer_id`,
 1 AS `schedule_date`,
 1 AS `delivery_status`,
 1 AS `customer_name`,
 1 AS `customer_contact`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `weekly_reports`
--

DROP TABLE IF EXISTS `weekly_reports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `weekly_reports` (
  `id` int NOT NULL AUTO_INCREMENT,
  `week_start` date NOT NULL,
  `week_end` date NOT NULL,
  `total_deliveries` int NOT NULL DEFAULT '0',
  `total_delivered` int NOT NULL DEFAULT '0',
  `total_cancelled` int NOT NULL DEFAULT '0',
  `total_pending` int NOT NULL DEFAULT '0',
  `total_in_transit` int NOT NULL DEFAULT '0',
  `total_sales` decimal(10,2) NOT NULL DEFAULT '0.00',
  `total_paid` decimal(10,2) NOT NULL DEFAULT '0.00',
  `total_unpaid` decimal(10,2) NOT NULL DEFAULT '0.00',
  `generated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `week_start` (`week_start`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `weekly_reports`
--

LOCK TABLES `weekly_reports` WRITE;
/*!40000 ALTER TABLE `weekly_reports` DISABLE KEYS */;
INSERT INTO `weekly_reports` VALUES (1,'2026-04-20','2026-04-26',0,0,0,0,0,0.00,0.00,0.00,'2026-04-27 02:38:51');
/*!40000 ALTER TABLE `weekly_reports` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'gnclpgdb'
--
/*!50106 SET @save_time_zone= @@TIME_ZONE */ ;
/*!50106 DROP EVENT IF EXISTS `generate_daily_summary` */;
DELIMITER ;;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;;
/*!50003 SET character_set_client  = utf8mb4 */ ;;
/*!50003 SET character_set_results = utf8mb4 */ ;;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;;
/*!50003 SET @saved_time_zone      = @@time_zone */ ;;
/*!50003 SET time_zone             = 'SYSTEM' */ ;;
/*!50106 CREATE*/ /*!50117 DEFINER=`root`@`localhost`*/ /*!50106 EVENT `generate_daily_summary` ON SCHEDULE EVERY 1 DAY STARTS '2026-04-30 00:00:00' ON COMPLETION NOT PRESERVE ENABLE DO INSERT INTO daily_reports (
    report_date,
    total_deliveries,
    total_delivered,
    total_cancelled,
    total_pending,
    total_in_transit,
    total_sales,
    total_paid,
    total_unpaid
)
SELECT
    CURDATE() - INTERVAL 1 DAY,
    COUNT(*),
    COALESCE(SUM(f.delivered_count), 0),
    COALESCE(SUM(f.cancelled_count), 0),
    COALESCE(SUM(f.pending_count), 0),
    COALESCE(SUM(f.in_transit_count), 0),
    COALESCE(SUM(f.recognized_sales), 0),
    COALESCE(SUM(f.paid_sales), 0),
    COALESCE(SUM(f.unpaid_sales), 0)
FROM vw_report_delivery_financials f
WHERE f.schedule_date = CURDATE() - INTERVAL 1 DAY
ON DUPLICATE KEY UPDATE
    total_deliveries  = VALUES(total_deliveries),
    total_delivered   = VALUES(total_delivered),
    total_cancelled   = VALUES(total_cancelled),
    total_pending     = VALUES(total_pending),
    total_in_transit  = VALUES(total_in_transit),
    total_sales       = VALUES(total_sales),
    total_paid        = VALUES(total_paid),
    total_unpaid      = VALUES(total_unpaid),
    generated_at      = CURRENT_TIMESTAMP */ ;;
/*!50003 SET time_zone             = @saved_time_zone */ ;;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;;
/*!50003 SET character_set_client  = @saved_cs_client */ ;;
/*!50003 SET character_set_results = @saved_cs_results */ ;;
/*!50003 SET collation_connection  = @saved_col_connection */ ;;
/*!50106 DROP EVENT IF EXISTS `generate_monthly_summary` */;;
DELIMITER ;;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;;
/*!50003 SET character_set_client  = utf8mb4 */ ;;
/*!50003 SET character_set_results = utf8mb4 */ ;;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;;
/*!50003 SET @saved_time_zone      = @@time_zone */ ;;
/*!50003 SET time_zone             = 'SYSTEM' */ ;;
/*!50106 CREATE*/ /*!50117 DEFINER=`root`@`localhost`*/ /*!50106 EVENT `generate_monthly_summary` ON SCHEDULE EVERY 1 MONTH STARTS '2026-04-01 00:00:00' ON COMPLETION NOT PRESERVE ENABLE DO BEGIN
    INSERT INTO monthly_reports (
        report_month,
        total_deliveries,
        total_delivered,
        total_cancelled,
        total_pending,
        total_in_transit,
        total_sales,
        total_paid,
        total_unpaid
    )
    SELECT
        DATE_FORMAT(CURDATE() - INTERVAL 1 MONTH, '%Y-%m-01'),
        COUNT(*),
        COALESCE(SUM(f.delivered_count), 0),
        COALESCE(SUM(f.cancelled_count), 0),
        COALESCE(SUM(f.pending_count), 0),
        COALESCE(SUM(f.in_transit_count), 0),
        COALESCE(SUM(f.recognized_sales), 0),
        COALESCE(SUM(f.paid_sales), 0),
        COALESCE(SUM(f.unpaid_sales), 0)
    FROM vw_report_delivery_financials f
    WHERE f.schedule_date >= DATE_FORMAT(CURDATE() - INTERVAL 1 MONTH, '%Y-%m-01')
      AND f.schedule_date <  DATE_FORMAT(CURDATE(), '%Y-%m-01')
    ON DUPLICATE KEY UPDATE
        total_deliveries  = VALUES(total_deliveries),
        total_delivered   = VALUES(total_delivered),
        total_cancelled   = VALUES(total_cancelled),
        total_pending     = VALUES(total_pending),
        total_in_transit  = VALUES(total_in_transit),
        total_sales       = VALUES(total_sales),
        total_paid        = VALUES(total_paid),
        total_unpaid      = VALUES(total_unpaid),
        generated_at      = CURRENT_TIMESTAMP;
END */ ;;
/*!50003 SET time_zone             = @saved_time_zone */ ;;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;;
/*!50003 SET character_set_client  = @saved_cs_client */ ;;
/*!50003 SET character_set_results = @saved_cs_results */ ;;
/*!50003 SET collation_connection  = @saved_col_connection */ ;;
/*!50106 DROP EVENT IF EXISTS `generate_weekly_summary` */;;
DELIMITER ;;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;;
/*!50003 SET character_set_client  = utf8mb4 */ ;;
/*!50003 SET character_set_results = utf8mb4 */ ;;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;;
/*!50003 SET @saved_time_zone      = @@time_zone */ ;;
/*!50003 SET time_zone             = 'SYSTEM' */ ;;
/*!50106 CREATE*/ /*!50117 DEFINER=`root`@`localhost`*/ /*!50106 EVENT `generate_weekly_summary` ON SCHEDULE EVERY 1 WEEK STARTS '2026-03-30 00:00:00' ON COMPLETION NOT PRESERVE ENABLE DO BEGIN
    INSERT INTO weekly_reports (
        week_start,
        week_end,
        total_deliveries,
        total_delivered,
        total_cancelled,
        total_pending,
        total_in_transit,
        total_sales,
        total_paid,
        total_unpaid
    )
    SELECT
        CURDATE() - INTERVAL 7 DAY,
        CURDATE() - INTERVAL 1 DAY,
        COUNT(*),
        COALESCE(SUM(f.delivered_count), 0),
        COALESCE(SUM(f.cancelled_count), 0),
        COALESCE(SUM(f.pending_count), 0),
        COALESCE(SUM(f.in_transit_count), 0),
        COALESCE(SUM(f.recognized_sales), 0),
        COALESCE(SUM(f.paid_sales), 0),
        COALESCE(SUM(f.unpaid_sales), 0)
    FROM vw_report_delivery_financials f
    WHERE f.schedule_date BETWEEN CURDATE() - INTERVAL 7 DAY
                              AND CURDATE() - INTERVAL 1 DAY
    ON DUPLICATE KEY UPDATE
        week_end          = VALUES(week_end),
        total_deliveries  = VALUES(total_deliveries),
        total_delivered   = VALUES(total_delivered),
        total_cancelled   = VALUES(total_cancelled),
        total_pending     = VALUES(total_pending),
        total_in_transit  = VALUES(total_in_transit),
        total_sales       = VALUES(total_sales),
        total_paid        = VALUES(total_paid),
        total_unpaid      = VALUES(total_unpaid),
        generated_at      = CURRENT_TIMESTAMP;
END */ ;;
/*!50003 SET time_zone             = @saved_time_zone */ ;;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;;
/*!50003 SET character_set_client  = @saved_cs_client */ ;;
/*!50003 SET character_set_results = @saved_cs_results */ ;;
/*!50003 SET collation_connection  = @saved_col_connection */ ;;
DELIMITER ;
/*!50106 SET TIME_ZONE= @save_time_zone */ ;

--
-- Dumping routines for database 'gnclpgdb'
--
/*!50003 DROP PROCEDURE IF EXISTS `sp_add_customer` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_add_customer`(
    IN p_full_name       VARCHAR(255),
    IN p_address         TEXT,
    IN p_contact_number  VARCHAR(20),
    IN p_notes           TEXT
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;
    
    IF TRIM(COALESCE(p_full_name, '')) = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Full name cannot be empty.';
    END IF;
    
    IF TRIM(COALESCE(p_address, '')) = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Address cannot be empty.';
    END IF;
    
    IF TRIM(COALESCE(p_contact_number, '')) = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Contact number cannot be empty.';
    END IF;
    
		IF p_contact_number NOT REGEXP '^(09[0-9]{9}|63[0-9]{10}|\\+63[0-9]{10})$' THEN
				 SIGNAL SQLSTATE '45000'
				 SET MESSAGE_TEXT = 'Contact number must be a valid PH number (09XXXXXXXXX, 639XXXXXXXXX, or +639XXXXXXXXX).';
		END IF;

		IF EXISTS (
		    SELECT 1 FROM customers
		    WHERE REGEXP_REPLACE(LOWER(TRIM(full_name)), '[^a-z0-9 ]', '')
		        = REGEXP_REPLACE(LOWER(TRIM(p_full_name)), '[^a-z0-9 ]', '')
		      AND LOWER(TRIM(address)) = LOWER(TRIM(p_address))
		) THEN
		    SIGNAL SQLSTATE '45000'
		    SET MESSAGE_TEXT = 'A customer with the same name and address already exists.';
		END IF;
		
		IF EXISTS (
		    SELECT 1 FROM customers
		    WHERE REGEXP_REPLACE(LOWER(TRIM(full_name)), '[^a-z0-9 ]', '')
		        = REGEXP_REPLACE(LOWER(TRIM(p_full_name)), '[^a-z0-9 ]', '')
		      AND TRIM(contact_number) = TRIM(p_contact_number)
		) THEN
		    SIGNAL SQLSTATE '45000'
		    SET MESSAGE_TEXT = 'A customer with the same name and contact number already exists.';
		END IF;
    
    START TRANSACTION;
        INSERT INTO customers (full_name, address, contact_number, notes)
        VALUES (
            TRIM(p_full_name),
            TRIM(p_address),
            TRIM(p_contact_number),
            NULLIF(TRIM(COALESCE(p_notes, '')), '')
        );
    COMMIT;
    SELECT LAST_INSERT_ID() AS new_customer_id;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_add_product` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = cp850 */ ;
/*!50003 SET character_set_results = cp850 */ ;
/*!50003 SET collation_connection  = cp850_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_add_product`(
    IN p_name           VARCHAR(100),
    IN p_cylinder_size  VARCHAR(20),
    IN p_refill_price   DECIMAL(10,2),
    IN p_new_tank_price DECIMAL(10,2)
)
BEGIN
    DECLARE v_normalized_name VARCHAR(100);
    DECLARE v_normalized_size VARCHAR(20);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    SET v_normalized_name = TRIM(
        REGEXP_REPLACE(
            REGEXP_REPLACE(LOWER(TRIM(COALESCE(p_name, ''))), '[^a-z0-9 ]', ''),
            '\\s+',
            ' '
        )
    );
    SET v_normalized_size = LOWER(TRIM(COALESCE(p_cylinder_size, '')));

    IF EXISTS (
        SELECT 1
        FROM lpg_products
        WHERE is_active = 1
          AND normalized_name = v_normalized_name
          AND normalized_cylinder_size = v_normalized_size
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A product with this name and cylinder size already exists.';
    END IF;

    START TRANSACTION;
        INSERT INTO lpg_products (
            name,
            cylinder_size,
            refill_price,
            new_tank_price,
            is_active
        )
        VALUES (
            TRIM(p_name),
            TRIM(p_cylinder_size),
            p_refill_price,
            p_new_tank_price,
            1
        );
    COMMIT;

    SELECT LAST_INSERT_ID() AS new_product_id;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_archive_product` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = cp850 */ ;
/*!50003 SET character_set_results = cp850 */ ;
/*!50003 SET collation_connection  = cp850_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_archive_product`(IN p_product_id INT)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;
        UPDATE lpg_products
        SET is_active = 0
        WHERE id = p_product_id
          AND is_active = 1;

        IF ROW_COUNT() = 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Product not found.';
        END IF;
    COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_change_user_password` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_change_user_password`(
    IN p_user_id      INT,
    IN p_password_hash VARCHAR(255)
)
BEGIN
    -- Validate user ID
    IF p_user_id IS NULL OR p_user_id <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid user ID.';
    END IF;

    -- Validate hash not empty
    IF TRIM(COALESCE(p_password_hash, '')) = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Password hash cannot be empty.';
    END IF;

    -- Validate bcrypt hash length (always 60 chars)
    IF LENGTH(TRIM(p_password_hash)) < 60 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid password hash format.';
    END IF;

    -- Check user exists
    IF NOT EXISTS (
        SELECT 1 FROM users WHERE id = p_user_id
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'User not found.';
    END IF;

    -- Check new password is different from current
    IF EXISTS (
        SELECT 1 FROM users
        WHERE id = p_user_id
          AND password = p_password_hash
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'New password must be different from your current password.';
    END IF;

    -- Update password and clear any reset code
    UPDATE users
    SET
        password              = p_password_hash,
        reset_code            = NULL,
        reset_code_expires_at = NULL
    WHERE id = p_user_id;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_create_delivery` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'NO_AUTO_VALUE_ON_ZERO' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_create_delivery`(IN `p_customer_id` INT, IN `p_user_id` INT, IN `p_schedule_date` DATE, IN `p_notes` TEXT)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    IF p_customer_id IS NULL OR NOT EXISTS (
        SELECT 1 FROM customers WHERE id = p_customer_id
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid customer.';
    END IF;

    IF p_user_id IS NULL OR NOT EXISTS (
        SELECT 1 FROM users WHERE id = p_user_id
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid user.';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM users
        WHERE id = p_user_id
          AND role = 'admin'
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Only administrators can create deliveries.';
    END IF;

    IF p_schedule_date IS NULL OR p_schedule_date < CURDATE() THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Schedule date cannot be in the past.';
    END IF;

    INSERT INTO deliveries (customer_id, user_id, schedule_date, notes)
    VALUES (p_customer_id, p_user_id, p_schedule_date, p_notes);

    SELECT LAST_INSERT_ID() AS new_delivery_id;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_delete_customer` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_delete_customer`(
    IN p_customer_id INT
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    IF p_customer_id IS NULL OR p_customer_id <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid customer ID.';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM customers WHERE id = p_customer_id
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Customer not found.';
    END IF;

    IF EXISTS (
        SELECT 1 FROM deliveries
        WHERE customer_id = p_customer_id
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'This customer has delivery records and cannot be deleted to preserve transaction history.';
    END IF;

    START TRANSACTION;
        DELETE FROM customers WHERE id = p_customer_id;
    COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_delete_product` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = cp850 */ ;
/*!50003 SET character_set_results = cp850 */ ;
/*!50003 SET collation_connection  = cp850_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_delete_product`(IN p_product_id INT)
BEGIN
    DECLARE v_product_count INT DEFAULT 0;
    DECLARE v_linked_count INT DEFAULT 0;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    SELECT COUNT(*)
    INTO v_product_count
    FROM lpg_products
    WHERE id = p_product_id;

    IF v_product_count = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Product not found.';
    END IF;

    SELECT COUNT(*)
    INTO v_linked_count
    FROM delivery_items
    WHERE product_id = p_product_id;

    IF v_linked_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'This product has delivery history and cannot be permanently deleted. Archive it instead.';
    END IF;

    START TRANSACTION;
        DELETE FROM lpg_products
        WHERE id = p_product_id;
    COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_get_delivery_report` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_get_delivery_report`(
    IN p_date_from DATE,
    IN p_date_to DATE
)
BEGIN
    SELECT
        f.delivery_id,
        f.schedule_date,
        f.delivery_status                                     AS status,
        f.customer_name,
        f.customer_address,
        f.total_quantity,
        f.gross_amount                                        AS computed_total,
        f.report_payment_status                               AS payment_status,
        f.paid_at
    FROM vw_report_delivery_financials f
    WHERE f.schedule_date BETWEEN p_date_from AND p_date_to
    ORDER BY f.schedule_date DESC, f.delivery_id DESC;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_get_sales_summary` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_get_sales_summary`(
    IN p_period VARCHAR(10)
)
BEGIN
    DECLARE v_date_from DATE;

    SET v_date_from = CASE p_period
        WHEN 'daily'   THEN CURDATE()
        WHEN 'weekly'  THEN DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        WHEN 'monthly' THEN DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        ELSE CURDATE()
    END;

    SELECT
        f.schedule_date                                        AS delivery_date,
        COUNT(*)                                               AS total_deliveries,
        COALESCE(SUM(f.delivered_count), 0)                    AS delivered,
        COALESCE(SUM(f.cancelled_count), 0)                    AS cancelled,
        COALESCE(SUM(f.pending_count), 0)                      AS pending,
        COALESCE(SUM(f.in_transit_count), 0)                   AS in_transit,
        COALESCE(SUM(f.recognized_sales), 0)                   AS total_sales,
        COALESCE(SUM(f.paid_sales), 0)                         AS paid_sales,
        COALESCE(SUM(f.unpaid_sales), 0)                       AS unpaid_sales
    FROM vw_report_delivery_financials f
    WHERE f.schedule_date BETWEEN v_date_from AND CURDATE()
    GROUP BY f.schedule_date
    ORDER BY delivery_date DESC;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_mark_payment` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'NO_AUTO_VALUE_ON_ZERO' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_mark_payment`(IN `p_delivery_id` INT)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

        SAVEPOINT before_payment;

        UPDATE transactions
        SET
            payment_status = 'paid',
            paid_at        = NOW()
        WHERE delivery_id = p_delivery_id
          AND payment_status = 'unpaid';

        IF ROW_COUNT() = 0 THEN
            ROLLBACK TO SAVEPOINT before_payment;
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Transaction not found or already paid.';
        END IF;

    COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_restore_product` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = cp850 */ ;
/*!50003 SET character_set_results = cp850 */ ;
/*!50003 SET collation_connection  = cp850_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_restore_product`(IN p_product_id INT)
BEGIN
    DECLARE v_product_count INT DEFAULT 0;
    DECLARE v_is_active TINYINT DEFAULT 0;
    DECLARE v_normalized_name VARCHAR(100);
    DECLARE v_normalized_size VARCHAR(20);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    SELECT
        COUNT(*),
        COALESCE(MAX(is_active), 0),
        MAX(normalized_name),
        MAX(normalized_cylinder_size)
    INTO
        v_product_count,
        v_is_active,
        v_normalized_name,
        v_normalized_size
    FROM lpg_products
    WHERE id = p_product_id;

    IF v_product_count = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Product not found.';
    END IF;

    IF v_is_active = 1 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Product is already active.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM lpg_products
        WHERE is_active = 1
          AND normalized_name = v_normalized_name
          AND normalized_cylinder_size = v_normalized_size
          AND id != p_product_id
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A product with this name and cylinder size is already active.';
    END IF;

    START TRANSACTION;
        UPDATE lpg_products
        SET is_active = 1
        WHERE id = p_product_id
          AND is_active = 0;

        IF ROW_COUNT() = 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Product not found.';
        END IF;
    COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_save_reset_code` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_save_reset_code`(
    IN p_user_id INT,
    IN p_code    VARCHAR(6)
)
BEGIN
    -- Validate user ID
    IF p_user_id IS NULL OR p_user_id <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid user ID.';
    END IF;

    -- Validate code
    IF TRIM(COALESCE(p_code, '')) = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Reset code cannot be empty.';
    END IF;
    IF LENGTH(TRIM(p_code)) != 6 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Reset code must be exactly 6 digits.';
    END IF;
    IF TRIM(p_code) NOT REGEXP '^[0-9]{6}$' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Reset code must contain digits only.';
    END IF;

    -- Check user exists
    IF NOT EXISTS (
        SELECT 1 FROM users WHERE id = p_user_id
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'User not found.';
    END IF;

    -- Save code with 10 minute expiry
    UPDATE users
    SET
        reset_code            = TRIM(p_code),
        reset_code_expires_at = DATE_ADD(NOW(), INTERVAL 10 MINUTE)
    WHERE id = p_user_id;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_update_customer` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_update_customer`(
    IN p_customer_id     INT,
    IN p_full_name       VARCHAR(255),
    IN p_address         TEXT,
    IN p_contact_number  VARCHAR(20),
    IN p_notes           TEXT
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;
    
    IF NOT EXISTS (SELECT 1 FROM customers WHERE id = p_customer_id) THEN
		    SIGNAL SQLSTATE '45000'
		    SET MESSAGE_TEXT = 'Customer not found.';
		END IF;
		
    IF TRIM(COALESCE(p_full_name, '')) = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Full name cannot be empty.';
    END IF;

    IF TRIM(COALESCE(p_address, '')) = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Address cannot be empty.';
    END IF;

    IF TRIM(COALESCE(p_contact_number, '')) = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Contact number cannot be empty.';
    END IF;

		IF p_contact_number NOT REGEXP '^(09[0-9]{9}|63[0-9]{10}|\\+63[0-9]{10})$' THEN
		    SIGNAL SQLSTATE '45000'
		    SET MESSAGE_TEXT = 'Contact number must be a valid PH number (09XXXXXXXXX, 639XXXXXXXXX, or +639XXXXXXXXX).';
		END IF;

    IF EXISTS (
        SELECT 1 FROM customers
        WHERE REGEXP_REPLACE(LOWER(TRIM(full_name)), '[^a-z0-9 ]', '')
            = REGEXP_REPLACE(LOWER(TRIM(p_full_name)), '[^a-z0-9 ]', '')
          AND LOWER(TRIM(address)) = LOWER(TRIM(p_address))
          AND id != p_customer_id
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A customer with the same name and address already exists.';
    END IF;

    IF EXISTS (
        SELECT 1 FROM customers
        WHERE REGEXP_REPLACE(LOWER(TRIM(full_name)), '[^a-z0-9 ]', '')
            = REGEXP_REPLACE(LOWER(TRIM(p_full_name)), '[^a-z0-9 ]', '')
          AND TRIM(contact_number) = TRIM(p_contact_number)
          AND id != p_customer_id
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A customer with the same name and contact number already exists.';
    END IF;

    START TRANSACTION;
        UPDATE customers
        SET
            full_name      = TRIM(p_full_name),
            address        = TRIM(p_address),
            contact_number = TRIM(p_contact_number),
            notes          = NULLIF(TRIM(COALESCE(p_notes, '')), '')
        WHERE id = p_customer_id;
    COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_update_delivery_status` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_update_delivery_status`(
    IN p_delivery_id INT,
    IN p_new_status VARCHAR(20),
    IN p_user_id INT
)
BEGIN
    DECLARE v_old_status VARCHAR(20);
    DECLARE v_delivery_count INT DEFAULT 0;
    DECLARE v_paid_transaction_count INT DEFAULT 0;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    SET p_new_status = LOWER(TRIM(p_new_status));
    SET @current_user_id = NULLIF(p_user_id, 0);

    IF p_new_status NOT IN ('pending', 'in_transit', 'delivered', 'cancelled') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid delivery status.';
    END IF;

    SELECT COUNT(*), MAX(status)
    INTO v_delivery_count, v_old_status
    FROM deliveries
    WHERE id = p_delivery_id;

    IF v_delivery_count = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Delivery not found.';
    END IF;

    IF v_old_status = p_new_status THEN
        SELECT v_old_status AS old_status, p_new_status AS new_status;
    ELSEIF v_old_status = 'pending'
          AND p_new_status NOT IN ('in_transit', 'delivered', 'cancelled') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Pending deliveries can only move to in transit, delivered, or cancelled.';
    ELSEIF v_old_status = 'in_transit'
          AND p_new_status NOT IN ('delivered', 'cancelled') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'In-transit deliveries can only move to delivered or cancelled.';
    ELSEIF v_old_status = 'cancelled' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cancelled deliveries cannot be changed.';
    ELSEIF v_old_status = 'delivered'
          AND p_new_status <> 'cancelled' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Delivered deliveries can only be cancelled when unpaid.';
    ELSE
        START TRANSACTION;

            IF p_new_status <> 'delivered' THEN
                SELECT COUNT(*)
                INTO v_paid_transaction_count
                FROM transactions
                WHERE delivery_id = p_delivery_id
                  AND payment_status = 'paid';

                IF v_paid_transaction_count > 0 THEN
                    SIGNAL SQLSTATE '45000'
                    SET MESSAGE_TEXT = 'Paid deliveries cannot be cancelled.';
                END IF;

                DELETE FROM transactions
                WHERE delivery_id = p_delivery_id
                  AND payment_status = 'unpaid';
            END IF;

            UPDATE deliveries
            SET status = p_new_status
            WHERE id = p_delivery_id;

        COMMIT;

        SELECT v_old_status AS old_status, p_new_status AS new_status;
    END IF;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_update_product` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = cp850 */ ;
/*!50003 SET character_set_results = cp850 */ ;
/*!50003 SET collation_connection  = cp850_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_update_product`(
    IN p_product_id     INT,
    IN p_name           VARCHAR(100),
    IN p_cylinder_size  VARCHAR(20),
    IN p_refill_price   DECIMAL(10,2),
    IN p_new_tank_price DECIMAL(10,2)
)
BEGIN
    DECLARE v_normalized_name VARCHAR(100);
    DECLARE v_normalized_size VARCHAR(20);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    SET v_normalized_name = TRIM(
        REGEXP_REPLACE(
            REGEXP_REPLACE(LOWER(TRIM(COALESCE(p_name, ''))), '[^a-z0-9 ]', ''),
            '\\s+',
            ' '
        )
    );
    SET v_normalized_size = LOWER(TRIM(COALESCE(p_cylinder_size, '')));

    IF EXISTS (
        SELECT 1
        FROM lpg_products
        WHERE is_active = 1
          AND normalized_name = v_normalized_name
          AND normalized_cylinder_size = v_normalized_size
          AND id != p_product_id
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A product with this name and cylinder size already exists.';
    END IF;

    START TRANSACTION;
        UPDATE lpg_products
        SET
            name = TRIM(p_name),
            cylinder_size = TRIM(p_cylinder_size),
            refill_price = p_refill_price,
            new_tank_price = p_new_tank_price
        WHERE id = p_product_id
          AND is_active = 1;

        IF ROW_COUNT() = 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Product not found.';
        END IF;
    COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_update_user_profile` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_update_user_profile`(
    IN p_user_id   INT,
    IN p_full_name VARCHAR(100),
    IN p_username  VARCHAR(100),
    IN p_email     VARCHAR(100)
)
BEGIN
    -- Validate user ID
    IF p_user_id IS NULL OR p_user_id <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid user ID.';
    END IF;

    -- Validate full name
    IF TRIM(COALESCE(p_full_name, '')) = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Full name cannot be empty.';
    END IF;
    IF LENGTH(TRIM(p_full_name)) > 100 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Full name cannot exceed 100 characters.';
    END IF;

    -- Validate username
    IF TRIM(COALESCE(p_username, '')) = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Username cannot be empty.';
    END IF;
    IF LENGTH(TRIM(p_username)) > 50 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Username cannot exceed 50 characters.';
    END IF;

    -- Validate email format if provided
    IF p_email IS NOT NULL AND TRIM(p_email) != '' THEN
        IF LENGTH(TRIM(p_email)) > 100 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Email cannot exceed 100 characters.';
        END IF;
        IF TRIM(p_email) NOT REGEXP '^[a-zA-Z0-9._%+\\-]+@[a-zA-Z0-9.\\-]+\\.[a-zA-Z]{2,}$' THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Invalid email format.';
        END IF;
    END IF;

    -- Check user exists
    IF NOT EXISTS (
        SELECT 1 FROM users WHERE id = p_user_id
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'User not found.';
    END IF;

    -- Check username not taken by another user
    IF EXISTS (
        SELECT 1 FROM users
        WHERE username = TRIM(p_username)
          AND id <> p_user_id
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Username is already taken.';
    END IF;

    -- Check email not taken by another user
    IF p_email IS NOT NULL AND TRIM(p_email) != '' THEN
        IF EXISTS (
            SELECT 1 FROM users
            WHERE email = TRIM(p_email)
              AND id <> p_user_id
        ) THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Email is already in use by another account.';
        END IF;
    END IF;

    -- Update
    UPDATE users
    SET
        full_name = TRIM(p_full_name),
        username  = TRIM(p_username),
        email     = NULLIF(TRIM(COALESCE(p_email, '')), '')
    WHERE id = p_user_id;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Current Database: `gnclpgdb`
--

USE `gnclpgdb`;

--
-- Final view structure for view `vw_customer_sales_summary`
--

/*!50001 DROP VIEW IF EXISTS `vw_customer_sales_summary`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_customer_sales_summary` AS select `c`.`id` AS `customer_id`,`c`.`full_name` AS `customer_name`,`c`.`address` AS `address`,count(`d`.`id`) AS `total_deliveries`,sum((case when (`d`.`status` = 'delivered') then 1 else 0 end)) AS `completed_deliveries`,coalesce(sum(`t`.`total_amount`),0) AS `total_spent` from ((`customers` `c` left join `deliveries` `d` on((`d`.`customer_id` = `c`.`id`))) left join `transactions` `t` on((`t`.`delivery_id` = `d`.`id`))) group by `c`.`id`,`c`.`full_name`,`c`.`address` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vw_customer_summary`
--

/*!50001 DROP VIEW IF EXISTS `vw_customer_summary`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_customer_summary` AS select `c`.`id` AS `id`,trim(`c`.`full_name`) AS `full_name`,trim(`c`.`address`) AS `address`,`c`.`contact_number` AS `contact_number`,coalesce(`c`.`notes`,'') AS `notes`,`c`.`created_at` AS `created_at`,date_format(`c`.`created_at`,'%b %d, %Y') AS `created_at_fmt`,coalesce(`ds`.`total_deliveries`,0) AS `total_deliveries`,coalesce(`ds`.`delivered_deliveries`,0) AS `delivered_deliveries`,`ds`.`last_delivery_date` AS `last_delivery_date`,coalesce(date_format(`ds`.`last_delivery_date`,'%b %d, %Y'),'-') AS `last_delivery` from (`customers` `c` left join (select `d`.`customer_id` AS `customer_id`,count(0) AS `total_deliveries`,sum((case when (`d`.`status` = 'delivered') then 1 else 0 end)) AS `delivered_deliveries`,max(`d`.`schedule_date`) AS `last_delivery_date` from `deliveries` `d` group by `d`.`customer_id`) `ds` on((`ds`.`customer_id` = `c`.`id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vw_dashboard_today`
--

/*!50001 DROP VIEW IF EXISTS `vw_dashboard_today`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_dashboard_today` AS select coalesce(sum(`vw_owner_dashboard_daily`.`total_deliveries`),0) AS `total_today`,coalesce(sum(`vw_owner_dashboard_daily`.`delivered_deliveries`),0) AS `delivered_today`,coalesce(sum(`vw_owner_dashboard_daily`.`pending_deliveries`),0) AS `pending_today`,coalesce(sum(`vw_owner_dashboard_daily`.`in_transit_deliveries`),0) AS `in_transit_today`,coalesce(sum(`vw_owner_dashboard_daily`.`cancelled_deliveries`),0) AS `cancelled_today`,round(coalesce(sum(`vw_owner_dashboard_daily`.`recognized_sales`),0),2) AS `sales_today`,round(coalesce(sum(`vw_owner_dashboard_daily`.`paid_sales`),0),2) AS `paid_today`,round(coalesce(sum(`vw_owner_dashboard_daily`.`unpaid_sales`),0),2) AS `unpaid_today` from `vw_owner_dashboard_daily` where (`vw_owner_dashboard_daily`.`schedule_date` = curdate()) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vw_delivery_details`
--

/*!50001 DROP VIEW IF EXISTS `vw_delivery_details`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_delivery_details` AS select `d`.`id` AS `delivery_id`,`d`.`schedule_date` AS `schedule_date`,`d`.`status` AS `status`,`d`.`notes` AS `notes`,`d`.`created_at` AS `created_at`,`d`.`updated_at` AS `updated_at`,`c`.`id` AS `customer_id`,concat(`c`.`full_name`) AS `customer_name`,`c`.`address` AS `customer_address`,`c`.`contact_number` AS `customer_contact`,`u`.`full_name` AS `encoded_by` from ((`deliveries` `d` join `customers` `c` on((`c`.`id` = `d`.`customer_id`))) join `users` `u` on((`u`.`id` = `d`.`user_id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vw_delivery_items_details`
--

/*!50001 DROP VIEW IF EXISTS `vw_delivery_items_details`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_delivery_items_details` AS select `di`.`id` AS `item_id`,`di`.`delivery_id` AS `delivery_id`,`di`.`product_id` AS `product_id`,trim(`p`.`name`) AS `product_base_name`,coalesce(trim(`p`.`cylinder_size`),'') AS `cylinder_size`,trim(concat(trim(`p`.`name`),(case when (coalesce(trim(`p`.`cylinder_size`),'') = '') then '' else concat(' ',trim(`p`.`cylinder_size`)) end))) AS `product_name`,`di`.`quantity` AS `quantity`,`di`.`type` AS `type`,`di`.`price_at_delivery` AS `price_at_delivery`,round((`di`.`quantity` * `di`.`price_at_delivery`),2) AS `subtotal` from (`delivery_items` `di` join `lpg_products` `p` on((`p`.`id` = `di`.`product_id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vw_owner_dashboard_daily`
--

/*!50001 DROP VIEW IF EXISTS `vw_owner_dashboard_daily`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_owner_dashboard_daily` AS select `f`.`schedule_date` AS `schedule_date`,count(0) AS `total_deliveries`,coalesce(sum(`f`.`delivered_count`),0) AS `delivered_deliveries`,coalesce(sum(`f`.`pending_count`),0) AS `pending_deliveries`,coalesce(sum(`f`.`in_transit_count`),0) AS `in_transit_deliveries`,coalesce(sum(`f`.`cancelled_count`),0) AS `cancelled_deliveries`,round(coalesce(sum(`f`.`recognized_sales`),0),2) AS `recognized_sales`,round(coalesce(sum(`f`.`paid_sales`),0),2) AS `paid_sales`,round(coalesce(sum(`f`.`unpaid_sales`),0),2) AS `unpaid_sales` from `vw_report_delivery_financials` `f` group by `f`.`schedule_date` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vw_report_delivery_financials`
--

/*!50001 DROP VIEW IF EXISTS `vw_report_delivery_financials`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_report_delivery_financials` AS select `d`.`id` AS `delivery_id`,`d`.`customer_id` AS `customer_id`,trim(`c`.`full_name`) AS `customer_name`,`c`.`contact_number` AS `customer_contact`,`c`.`address` AS `customer_address`,`d`.`user_id` AS `user_id`,`d`.`schedule_date` AS `schedule_date`,`d`.`status` AS `delivery_status`,`d`.`notes` AS `notes`,`d`.`created_at` AS `created_at`,`d`.`updated_at` AS `updated_at`,`t`.`id` AS `transaction_id`,`t`.`payment_status` AS `transaction_payment_status`,(case when (`d`.`status` = 'delivered') then coalesce(`t`.`payment_status`,'unpaid') else 'not_applicable' end) AS `report_payment_status`,`t`.`paid_at` AS `paid_at`,coalesce(`it`.`total_quantity`,0) AS `total_quantity`,coalesce(`it`.`item_total`,0) AS `item_total`,coalesce(`t`.`total_amount`,`it`.`item_total`,0) AS `gross_amount`,(case when (`d`.`status` = 'delivered') then 1 else 0 end) AS `delivered_count`,(case when (`d`.`status` = 'cancelled') then 1 else 0 end) AS `cancelled_count`,(case when (`d`.`status` = 'pending') then 1 else 0 end) AS `pending_count`,(case when (`d`.`status` = 'in_transit') then 1 else 0 end) AS `in_transit_count`,(case when (`d`.`status` = 'delivered') then coalesce(`t`.`total_amount`,`it`.`item_total`,0) else 0 end) AS `recognized_sales`,(case when ((`d`.`status` = 'delivered') and (coalesce(`t`.`payment_status`,'unpaid') = 'paid')) then coalesce(`t`.`total_amount`,`it`.`item_total`,0) else 0 end) AS `paid_sales`,(case when ((`d`.`status` = 'delivered') and (coalesce(`t`.`payment_status`,'unpaid') = 'unpaid')) then coalesce(`t`.`total_amount`,`it`.`item_total`,0) else 0 end) AS `unpaid_sales` from (((`deliveries` `d` join `customers` `c` on((`c`.`id` = `d`.`customer_id`))) left join `transactions` `t` on((`t`.`delivery_id` = `d`.`id`))) left join (select `di`.`delivery_id` AS `delivery_id`,sum(`di`.`quantity`) AS `total_quantity`,sum((`di`.`quantity` * `di`.`price_at_delivery`)) AS `item_total` from `delivery_items` `di` group by `di`.`delivery_id`) `it` on((`it`.`delivery_id` = `d`.`id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vw_report_delivery_lines`
--

/*!50001 DROP VIEW IF EXISTS `vw_report_delivery_lines`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_report_delivery_lines` AS select `f`.`delivery_id` AS `delivery_id`,`f`.`customer_id` AS `customer_id`,`f`.`customer_name` AS `customer_name`,`f`.`customer_contact` AS `customer_contact`,`f`.`customer_address` AS `customer_address`,`f`.`schedule_date` AS `schedule_date`,`f`.`delivery_status` AS `delivery_status`,`f`.`report_payment_status` AS `payment_status`,`f`.`transaction_id` AS `transaction_id`,`f`.`paid_at` AS `paid_at`,`di`.`id` AS `delivery_item_id`,`di`.`product_id` AS `product_id`,concat(trim(`p`.`name`),' ',coalesce(`p`.`cylinder_size`,'')) AS `product_name`,`di`.`quantity` AS `quantity`,`di`.`type` AS `type`,`di`.`price_at_delivery` AS `price_at_delivery`,round((`di`.`quantity` * `di`.`price_at_delivery`),2) AS `line_amount`,(case when (`f`.`delivery_status` = 'delivered') then round((`di`.`quantity` * `di`.`price_at_delivery`),2) else 0 end) AS `recognized_line_sales` from ((`vw_report_delivery_financials` `f` join `delivery_items` `di` on((`di`.`delivery_id` = `f`.`delivery_id`))) join `lpg_products` `p` on((`p`.`id` = `di`.`product_id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vw_transaction_summary`
--

/*!50001 DROP VIEW IF EXISTS `vw_transaction_summary`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_transaction_summary` AS select `t`.`id` AS `transaction_id`,`t`.`delivery_id` AS `delivery_id`,`t`.`total_amount` AS `total_amount`,`t`.`payment_status` AS `payment_status`,`t`.`paid_at` AS `paid_at`,`t`.`created_at` AS `created_at`,`d`.`customer_id` AS `customer_id`,`d`.`schedule_date` AS `schedule_date`,`d`.`status` AS `delivery_status`,`c`.`full_name` AS `customer_name`,`c`.`contact_number` AS `customer_contact` from ((`transactions` `t` join `deliveries` `d` on((`d`.`id` = `t`.`delivery_id`))) join `customers` `c` on((`c`.`id` = `d`.`customer_id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-05-01 16:55:06
