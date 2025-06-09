-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 30, 2025 at 08:46 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `dogarmedicalstore`
--

-- --------------------------------------------------------

--
-- Table structure for table `employees`
--

CREATE TABLE `employees` (
  `employee_id` varchar(10) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `cnic` varchar(20) DEFAULT NULL,
  `emergency` varchar(15) DEFAULT NULL,
  `role` varchar(50) DEFAULT NULL,
  `salary` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `orders`
--

CREATE TABLE `orders` (
  `order_id` int(11) NOT NULL,
  `customer_id` int(11) DEFAULT NULL,
  `total_amount` decimal(10,2) NOT NULL,
  `paid_amount` decimal(10,2) NOT NULL,
  `change_amount` decimal(10,2) NOT NULL,
  `order_date` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `orders`
--

INSERT INTO `orders` (`order_id`, `customer_id`, `total_amount`, `paid_amount`, `change_amount`, `order_date`) VALUES
(1, 1, 500.00, 600.00, 100.00, '2025-04-05 10:00:00'),
(2, 2, 750.00, 800.00, 50.00, '2025-04-05 11:30:00'),
(3, 3, 1200.00, 1300.00, 100.00, '2025-04-05 14:15:00'),
(4, 4, 300.00, 350.00, 50.00, '2025-04-05 15:00:00'),
(5, 5, 450.00, 500.00, 50.00, '2025-04-05 16:30:00'),
(6, 6, 600.00, 650.00, 50.00, '2025-04-05 17:45:00'),
(7, 7, 800.00, 850.00, 50.00, '2025-04-05 18:30:00'),
(8, 8, 350.00, 400.00, 50.00, '2025-04-05 19:00:00'),
(9, 9, 550.00, 600.00, 50.00, '2025-04-05 19:45:00'),
(10, 10, 900.00, 950.00, 50.00, '2025-04-05 20:15:00'),
(11, 11, 450.00, 500.00, 50.00, '2025-04-05 21:00:00'),
(12, 12, 700.00, 750.00, 50.00, '2025-04-05 22:00:00'),
(13, 13, 1200.00, 1300.00, 100.00, '2025-04-06 10:00:00'),
(14, 14, 950.00, 1000.00, 50.00, '2025-04-06 11:15:00'),
(15, 15, 850.00, 900.00, 50.00, '2025-04-06 12:30:00'),
(16, 16, 1000.00, 1050.00, 50.00, '2025-04-06 14:00:00'),
(17, 17, 750.00, 800.00, 50.00, '2025-04-06 15:30:00'),
(18, 18, 650.00, 700.00, 50.00, '2025-04-06 16:45:00'),
(19, 19, 840.00, 900.00, 60.00, '2025-01-12 11:00:00'),
(20, 20, 620.00, 700.00, 80.00, '2025-01-25 16:45:00'),
(21, 21, 910.00, 1000.00, 90.00, '2025-02-10 13:30:00'),
(22, 22, 710.00, 800.00, 90.00, '2025-02-27 15:15:00'),
(23, 23, 950.00, 1000.00, 50.00, '2025-03-05 12:00:00'),
(24, 24, 630.00, 700.00, 70.00, '2025-03-20 17:00:00'),
(25, 25, 1080.00, 1200.00, 120.00, '2025-04-01 10:30:00'),
(26, 26, 790.00, 850.00, 60.00, '2025-04-06 14:45:00'),
(27, NULL, 3480.00, 4000.00, 520.00, '2025-04-10 02:13:00'),
(28, NULL, 2030.00, 0.00, -2030.00, '2025-04-10 09:22:59'),
(29, NULL, 2030.00, 4000.00, 1970.00, '2025-04-10 09:28:33'),
(30, NULL, 830.00, 2995.00, 2165.00, '2025-04-10 22:43:22'),
(31, NULL, 2030.00, 2000.00, -30.00, '2025-04-17 14:08:58'),
(32, NULL, 830.00, 830.00, 0.00, '2025-04-17 14:14:29'),
(33, NULL, 830.00, 830.00, 0.00, '2025-04-17 17:54:17');

-- --------------------------------------------------------

--
-- Table structure for table `order_items`
--

CREATE TABLE `order_items` (
  `order_item_id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL,
  `unit_price` decimal(10,2) NOT NULL,
  `total_price` decimal(10,2) NOT NULL,
  `product_name` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `order_items`
--

INSERT INTO `order_items` (`order_item_id`, `order_id`, `product_id`, `quantity`, `unit_price`, `total_price`, `product_name`) VALUES
(1, 1, 101, 2, 100.00, 200.00, 'Panadol'),
(2, 1, 102, 3, 100.00, 300.00, 'Augmentin'),
(3, 2, 103, 1, 200.00, 200.00, 'Dove Face Wash'),
(4, 2, 104, 4, 150.00, 600.00, 'Vitamin C Tablets'),
(5, 3, 105, 5, 120.00, 600.00, 'Brufen'),
(6, 3, 106, 2, 150.00, 300.00, 'Disprin'),
(7, 4, 101, 1, 100.00, 100.00, 'Panadol'),
(8, 4, 102, 2, 100.00, 200.00, 'Augmentin'),
(9, 5, 103, 3, 150.00, 450.00, 'Dove Face Wash'),
(10, 5, 104, 2, 150.00, 300.00, 'Vitamin C Tablets'),
(11, 6, 105, 1, 200.00, 200.00, 'Brufen'),
(12, 6, 106, 3, 150.00, 450.00, 'Disprin'),
(13, 7, 101, 4, 100.00, 400.00, 'Panadol'),
(14, 7, 102, 2, 100.00, 200.00, 'Augmentin'),
(15, 8, 103, 2, 200.00, 400.00, 'Dove Face Wash'),
(16, 8, 104, 1, 150.00, 150.00, 'Vitamin C Tablets'),
(17, 9, 105, 3, 120.00, 360.00, 'Brufen'),
(18, 9, 106, 2, 150.00, 300.00, 'Disprin'),
(19, 10, 101, 5, 100.00, 500.00, 'Panadol'),
(20, 10, 102, 3, 100.00, 300.00, 'Augmentin'),
(21, 11, 103, 2, 200.00, 400.00, 'Dove Face Wash'),
(22, 11, 104, 1, 150.00, 150.00, 'Vitamin C Tablets'),
(23, 12, 105, 4, 120.00, 480.00, 'Brufen'),
(24, 12, 106, 2, 150.00, 300.00, 'Disprin'),
(25, 13, 101, 6, 100.00, 600.00, 'Panadol'),
(26, 13, 102, 3, 100.00, 300.00, 'Augmentin'),
(27, 14, 103, 3, 200.00, 600.00, 'Dove Face Wash'),
(28, 14, 104, 2, 150.00, 300.00, 'Vitamin C Tablets'),
(29, 15, 105, 2, 120.00, 240.00, 'Brufen'),
(30, 15, 106, 3, 150.00, 450.00, 'Disprin'),
(31, 16, 101, 7, 100.00, 700.00, 'Panadol'),
(32, 16, 102, 4, 100.00, 400.00, 'Augmentin'),
(33, 17, 103, 3, 200.00, 600.00, 'Dove Face Wash'),
(34, 17, 104, 2, 150.00, 300.00, 'Vitamin C Tablets'),
(35, 18, 105, 2, 120.00, 240.00, 'Brufen'),
(36, 18, 106, 4, 150.00, 600.00, 'Disprin'),
(37, 19, 105, 3, 120.00, 360.00, 'Brufen'),
(38, 19, 106, 3, 160.00, 480.00, 'Disprin'),
(39, 20, 101, 2, 100.00, 200.00, 'Panadol'),
(40, 20, 102, 2, 100.00, 200.00, 'Augmentin'),
(41, 20, 104, 1, 150.00, 150.00, 'Vitamin C Tablets'),
(42, 20, 106, 1, 70.00, 70.00, 'Disprin'),
(43, 21, 103, 2, 200.00, 400.00, 'Dove Face Wash'),
(44, 21, 105, 3, 170.00, 510.00, 'Brufen'),
(45, 22, 101, 3, 100.00, 300.00, 'Panadol'),
(46, 22, 106, 2, 150.00, 300.00, 'Disprin'),
(47, 22, 104, 1, 110.00, 110.00, 'Vitamin C Tablets'),
(48, 23, 103, 3, 200.00, 600.00, 'Dove Face Wash'),
(49, 23, 102, 2, 175.00, 350.00, 'Augmentin'),
(50, 24, 101, 2, 100.00, 200.00, 'Panadol'),
(51, 24, 106, 2, 150.00, 300.00, 'Disprin'),
(52, 24, 104, 1, 130.00, 130.00, 'Vitamin C Tablets'),
(53, 25, 105, 4, 120.00, 480.00, 'Brufen'),
(54, 25, 106, 4, 150.00, 600.00, 'Disprin'),
(55, 26, 103, 2, 200.00, 400.00, 'Dove Face Wash'),
(56, 26, 104, 2, 150.00, 300.00, 'Vitamin C Tablets'),
(57, 26, 102, 1, 90.00, 90.00, 'Augmentin'),
(58, 27, 166, 1, 380.00, 380.00, 'AcneFix'),
(59, 27, 189, 1, 450.00, 450.00, 'AcneRelief Gel'),
(60, 27, 170, 2, 1200.00, 2400.00, 'AllerFree'),
(61, 27, 121, 1, 250.00, 250.00, 'Amoxicillin'),
(62, 28, 166, 1, 380.00, 380.00, 'AcneFix'),
(63, 28, 189, 1, 450.00, 450.00, 'AcneRelief Gel'),
(64, 28, 170, 1, 1200.00, 1200.00, 'AllerFree'),
(65, 29, 166, 1, 380.00, 380.00, 'AcneFix'),
(66, 29, 189, 1, 450.00, 450.00, 'AcneRelief Gel'),
(67, 29, 170, 1, 1200.00, 1200.00, 'AllerFree'),
(68, 30, 166, 1, 380.00, 380.00, 'AcneFix'),
(69, 30, 189, 1, 450.00, 450.00, 'AcneRelief Gel'),
(70, 31, 166, 1, 380.00, 380.00, 'AcneFix'),
(71, 31, 189, 1, 450.00, 450.00, 'AcneRelief Gel'),
(72, 31, 170, 1, 1200.00, 1200.00, 'AllerFree'),
(73, 32, 166, 1, 380.00, 380.00, 'AcneFix'),
(74, 32, 189, 1, 450.00, 450.00, 'AcneRelief Gel'),
(75, 33, 166, 1, 380.00, 380.00, 'AcneFix'),
(76, 33, 189, 1, 450.00, 450.00, 'AcneRelief Gel');

-- --------------------------------------------------------

--
-- Table structure for table `pharmacy_orders`
--

CREATE TABLE `pharmacy_orders` (
  `pharmacy_order_id` int(11) NOT NULL,
  `order_date` datetime DEFAULT current_timestamp(),
  `expected_delivery_date` date DEFAULT NULL,
  `supplier_name` varchar(255) DEFAULT NULL,
  `status` varchar(50) DEFAULT 'Pending',
  `total_amount` decimal(12,2) DEFAULT 0.00
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Dumping data for table `pharmacy_orders`
--

INSERT INTO `pharmacy_orders` (`pharmacy_order_id`, `order_date`, `expected_delivery_date`, `supplier_name`, `status`, `total_amount`) VALUES
(1, '2025-04-10 01:55:12', '2021-07-04', 'kashaf', 'Pending', 2030.00),
(2, '2025-04-10 09:24:47', '2021-05-07', 'kashaff', 'Pending', 2030.00),
(3, '2025-04-10 10:19:23', '2021-04-03', 'rashid', 'Pending', 830.00),
(4, '2025-04-10 10:20:25', '2020-04-06', 'sarim', 'Pending', 830.00),
(5, '2025-04-10 11:17:18', '2025-05-09', 'kashaf', 'Pending', 830.00),
(6, '2025-04-10 22:38:05', '2025-04-10', 'Default Supplier', 'Pending', 830.00),
(7, '2025-04-27 16:14:58', '2025-04-27', 'Default Supplier', 'Pending', 830.00);

-- --------------------------------------------------------

--
-- Table structure for table `pharmacy_order_items`
--

CREATE TABLE `pharmacy_order_items` (
  `item_id` int(11) NOT NULL,
  `pharmacy_order_id` int(11) DEFAULT NULL,
  `product_name` varchar(255) DEFAULT NULL,
  `quantity` int(11) DEFAULT NULL,
  `unit_price` decimal(10,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Dumping data for table `pharmacy_order_items`
--

INSERT INTO `pharmacy_order_items` (`item_id`, `pharmacy_order_id`, `product_name`, `quantity`, `unit_price`) VALUES
(1, 1, 'AcneFix', 1, 380.00),
(2, 1, 'AcneRelief Gel', 1, 450.00),
(3, 1, 'AllerFree', 1, 1200.00),
(4, 2, 'AcneFix', 1, 380.00),
(5, 2, 'AcneRelief Gel', 1, 450.00),
(6, 2, 'AllerFree', 1, 1200.00),
(7, 3, 'AcneFix', 1, 380.00),
(8, 3, 'AcneRelief Gel', 1, 450.00),
(9, 4, 'AcneFix', 1, 380.00),
(10, 4, 'AcneRelief Gel', 1, 450.00),
(11, 5, 'AcneFix', 1, 380.00),
(12, 5, 'AcneRelief Gel', 1, 450.00),
(13, 6, 'AcneFix', 1, 380.00),
(14, 6, 'AcneRelief Gel', 1, 450.00),
(15, 7, 'AcneFix', 1, 380.00),
(16, 7, 'AcneRelief Gel', 1, 450.00);

-- --------------------------------------------------------

--
-- Table structure for table `products`
--

CREATE TABLE `products` (
  `product_id` int(11) NOT NULL,
  `category` varchar(255) DEFAULT NULL,
  `product_name` varchar(255) DEFAULT NULL,
  `brand` varchar(255) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `price` decimal(10,2) DEFAULT NULL,
  `stock_quantity` int(11) DEFAULT NULL,
  `expiry_date` date DEFAULT NULL,
  `dosage_form` varchar(255) DEFAULT NULL,
  `usage_indication` varchar(255) DEFAULT NULL,
  `date_added` date DEFAULT NULL,
  `cost_price` decimal(10,2) NOT NULL,
  `image_path` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `products`
--

INSERT INTO `products` (`product_id`, `category`, `product_name`, `brand`, `description`, `price`, `stock_quantity`, `expiry_date`, `dosage_form`, `usage_indication`, `date_added`, `cost_price`, `image_path`) VALUES
(101, 'Medicine', 'Panadol', 'GSK', 'Pain reliever and fever reducer', 50.00, 100, '2026-12-31', 'Tablet', 'Fever, headache', '2025-02-20', 0.00, NULL),
(102, 'Medicine', 'Augmentin', 'GlaxoSmithKline', 'Antibiotic for bacterial infections', 300.00, 50, '2025-06-15', 'Tablet', 'Bacterial infections', '2025-02-20', 0.00, NULL),
(103, 'Cosmetics', 'Dove Face Wash', 'Dove', 'Gentle cleanser for face', 450.00, 30, NULL, NULL, 'Skincare', '2025-02-22', 0.00, NULL),
(104, 'Supplement', 'Vitamin C Tablets', 'Nature\'s Bounty', 'Immune support supplement', 600.00, 40, '2027-03-10', 'Tablet', 'Immunity boost', '2025-02-22', 0.00, NULL),
(105, 'Medicine', 'Brufen', 'Abbott', 'Pain relief and anti-inflammatory', 100.00, 60, '2025-08-25', 'Tablet', 'Pain relief', '2025-02-22', 0.00, NULL),
(106, 'Medicine', 'Disprin', 'Bayer', 'Aspirin for pain relief and fever reduction', 20.00, 120, '2025-12-10', 'Tablet', 'Pain relief', '2025-02-22', 0.00, NULL),
(107, 'Supplement', 'Fish Oil Capsules', 'OmegaPlus', 'Omega-3 supplement for heart health', 700.00, 25, '2026-01-15', 'Capsule', 'Heart health', '2025-02-23', 0.00, NULL),
(108, 'Supplement', 'Calcium Tablets', 'BoneCare', 'Calcium supplement for bone health', 350.00, 90, '2027-04-20', 'Tablet', 'Bone health', '2025-02-23', 0.00, NULL),
(109, 'Medicine', 'Metformin', 'Sanofi', 'Used to manage blood sugar levels', 200.00, 80, '2025-03-15', 'Tablet', 'Diabetes management', '2025-02-23', 0.00, NULL),
(110, 'Medicine', 'Lipitor', 'Pfizer', 'Cholesterol-lowering medication', 550.00, 70, '2026-05-10', 'Tablet', 'High cholesterol', '2025-02-23', 0.00, NULL),
(111, 'Medicine', 'Ibuprofen', 'Advil', 'Pain reliever and anti-inflammatory', 150.00, 110, '2025-09-30', 'Tablet', 'Pain relief, inflammation', '2025-02-24', 0.00, NULL),
(112, 'Cosmetics', 'Nivea Body Lotion', 'Nivea', 'Moisturizing body lotion', 500.00, 45, NULL, NULL, 'Skincare', '2025-02-24', 0.00, NULL),
(113, 'Supplement', 'Zinc Tablets', 'HealthPlus', 'Zinc supplement for immunity', 250.00, 75, '2027-02-28', 'Tablet', 'Immunity support', '2025-02-24', 0.00, NULL),
(114, 'Medicine', 'Paracetamol', 'Tylenol', 'Pain reliever and fever reducer', 60.00, 95, '2026-08-15', 'Tablet', 'Fever, pain relief', '2025-02-24', 0.00, NULL),
(115, 'Medicine', 'Cough Syrup', 'Benylin', 'For cough and cold symptoms', 120.00, 55, '2025-11-20', 'Syrup', 'Cough relief', '2025-02-25', 0.00, NULL),
(116, 'Medicine', 'Aspirin', 'Bayer', 'Pain reliever, fever reducer, and anti-inflammatory', 80.00, 130, '2025-07-05', 'Tablet', 'Pain relief, fever', '2025-02-25', 0.00, NULL),
(117, 'Cosmetics', 'Vaseline Lip Balm', 'Vaseline', 'Moisturizing lip balm', 100.00, 40, NULL, NULL, 'Lip care', '2025-02-25', 0.00, NULL),
(118, 'Supplement', 'Magnesium Tablets', 'PureHealth', 'Magnesium supplement for muscle and nerve function', 400.00, 85, '2026-10-15', 'Tablet', 'Muscle health', '2025-02-25', 0.00, NULL),
(119, 'Medicine', 'Antacid', 'Tums', 'Relieves heartburn and indigestion', 90.00, 105, '2025-06-30', 'Tablet', 'Heartburn relief', '2025-02-26', 0.00, NULL),
(120, 'Medicine', 'Cetirizine', 'Zyrtec', 'Antihistamine for allergy relief', 180.00, 65, '2026-04-10', 'Tablet', 'Allergy relief', '2025-02-26', 0.00, NULL),
(121, 'Medicine', 'Amoxicillin', 'Amoxil', 'Antibiotic for bacterial infections', 250.00, 69, '2025-03-25', 'Capsule', 'Bacterial infections', '2025-02-26', 0.00, NULL),
(122, 'Cosmetics', 'Pond\'s Cold Cream', 'Pond\'s', 'Moisturizing cream for dry skin', 300.00, 35, NULL, NULL, 'Skincare', '2025-02-26', 0.00, NULL),
(123, 'Supplement', 'Iron Tablets', 'Ferrovit', 'Iron supplement for anemia', 320.00, 50, '2027-03-05', 'Tablet', 'Anemia', '2025-02-27', 0.00, NULL),
(124, 'Medicine', 'Loperamide', 'Imodium', 'For relief of diarrhea', 140.00, 90, '2026-02-15', 'Capsule', 'Diarrhea relief', '2025-02-27', 0.00, NULL),
(125, 'Medicine', 'Omeprazole', 'Prilosec', 'Reduces stomach acid', 280.00, 60, '2025-12-05', 'Capsule', 'Acid reflux', '2025-02-27', 0.00, NULL),
(126, 'Cosmetics', 'L\'Oreal Shampoo', 'L\'Oreal', 'Nourishing shampoo for dry hair', 600.00, 25, NULL, NULL, 'Hair care', '2025-02-27', 0.00, NULL),
(127, 'Supplement', 'Multivitamins', 'Centrum', 'Daily multivitamin supplement', 500.00, 95, '2027-06-10', 'Tablet', 'General health', '2025-02-27', 0.00, NULL),
(128, 'Medicine', 'Dextromethorphan', 'Robitussin', 'Cough suppressant for dry cough', 130.00, 80, '2025-10-20', 'Syrup', 'Cough relief', '2025-02-28', 0.00, NULL),
(129, 'Medicine', 'Clotrimazole Cream', 'Canesten', 'Antifungal cream for skin infections', 220.00, 45, '2026-07-01', 'Cream', 'Fungal infections', '2025-02-28', 0.00, NULL),
(130, 'Medicine', 'Loratadine', 'Claritin', 'Non-drowsy antihistamine for allergies', 160.00, 100, '2026-03-15', 'Tablet', 'Allergy relief', '2025-02-28', 0.00, NULL),
(131, 'Medicine', 'Cough Syrup', 'Benylin', 'Relieves cough', 150.00, 100, '2025-12-01', 'Syrup', 'Cough relief', '2025-03-03', 0.00, NULL),
(132, 'Cosmetics', 'Lip Balm', 'Nivea', 'Moisturizes lips', 90.00, NULL, NULL, NULL, 'Lip hydration', '2025-03-04', 0.00, NULL),
(133, 'Supplement', 'Iron Capsules', 'Nature’s', 'Iron supplement', 120.00, 40, '2027-03-14', 'Capsule', 'Iron supplementation', '2025-03-05', 0.00, NULL),
(134, 'Medicine', 'Paracetamol', 'Panadol', 'Reduces fever', 80.00, 150, '2025-06-10', 'Tablet', 'Pain relief', '2025-03-06', 0.00, NULL),
(135, 'Cosmetics', 'Face Wash', 'Clean & Clear', 'Cleanses and brightens skin', 200.00, 60, NULL, 'N/A', 'Face cleansing', '2025-03-07', 0.00, NULL),
(136, 'Supplement', 'Vitamin D', 'Ddrops', 'Supports bone health', 350.00, 35, '2026-08-25', 'Drops', 'Bone health', '2025-03-08', 0.00, NULL),
(137, 'Cosmetics', 'Shampoo', 'Head & Shoulders', 'Anti-dandruff shampoo', 450.00, 45, NULL, 'N/A', 'Dandruff treatment', '2025-03-09', 0.00, NULL),
(138, 'Medicine', 'Antibiotic Cream', 'Neosporin', 'Treats skin infections', 250.00, 30, '2025-04-15', 'Cream', 'Skin infection treatment', '2025-03-10', 0.00, NULL),
(139, 'Supplement', 'Probiotic', 'Culturelle', 'Promotes gut health', 800.00, 25, '2027-04-09', 'Capsule', 'Digestive support', '2025-02-20', 0.00, NULL),
(140, 'Cosmetics', 'Sunscreen', 'Neutrogena', 'Protects skin from UV rays', 500.00, 20, NULL, 'N/A', 'Sun protection', '2025-02-21', 0.00, NULL),
(141, 'Medicine', 'Digestive Enzyme', 'Enzymedica', 'Aids digestion', 900.00, 30, '2028-11-12', 'Capsule', 'Digestive aid', '2025-02-22', 0.00, NULL),
(142, 'Supplement', 'Hand Cream', 'Aveeno', 'Hydrates dry hands', 350.00, 60, NULL, 'Cream', 'Hand moisturizing', '2025-02-23', 0.00, NULL),
(143, 'Cosmetics', 'Hair Serum', 'L\'Oreal', 'Nourishes hair', 500.00, 55, NULL, 'N/A', 'Hair care', '2025-02-24', 0.00, NULL),
(144, 'Medicine', 'Pain Reliever', 'Advil', 'Fast pain relief', 450.00, 120, '2025-07-30', 'Tablet', 'Pain relief', '2025-02-25', 0.00, NULL),
(145, 'Cosmetics', 'BB Cream', 'Garnier', 'Skin-perfecting cream', 1400.00, 10, NULL, 'N/A', 'Skin tone correction', '2025-02-26', 0.00, NULL),
(146, 'Supplement', 'Multivitamin', 'Centrum', 'Daily multivitamin', 750.00, 75, '2027-02-01', 'Tablet', 'Overall health', '2025-02-27', 0.00, NULL),
(147, 'Medicine', 'Antifungal Spray', 'Lotrimin', 'Treats fungal infections', 600.00, 30, NULL, 'Spray', 'Fungal infection treatment', '2025-02-28', 0.00, NULL),
(148, 'Cosmetics', 'Face Mask', 'Sephora', 'Detox face mask', 1000.00, 40, NULL, 'N/A', 'Detox and cleansing', '0000-00-00', 0.00, NULL),
(149, 'Supplement', 'Electrolyte Powder', 'Pedialyte', 'Replenishes electrolytes', 250.00, 50, NULL, 'Powder', 'Hydration', '2025-03-01', 0.00, NULL),
(150, 'Medicine', 'Cold Medicine', 'NyQuil', 'Relieves cold symptoms', 90.00, 150, '2025-03-20', 'Tablet', 'Cold relief', '2025-03-03', 0.00, NULL),
(151, 'Cosmetics', 'Eye Shadow', 'Urban Decay', 'Long-lasting eye shadow', 3000.00, 15, NULL, 'N/A', 'Eye makeup', '2025-03-04', 0.00, NULL),
(152, 'Supplement', 'Whey Protein', 'MuscleTech', 'Muscle recovery', 4000.00, 120, '2027-06-18', 'Powder', 'Muscle recovery', '2025-03-05', 0.00, NULL),
(153, 'Medicine', 'Nasal Spray', 'Flonase', 'Relieves nasal congestion', 500.00, 120, '2026-10-30', 'Spray', 'Nasal decongestion', '2025-03-06', 0.00, NULL),
(154, 'Cosmetics', 'Makeup Remover', 'Bioderma', 'Removes makeup', 800.00, 35, NULL, 'N/A', 'Makeup removal', '2025-03-07', 0.00, NULL),
(155, 'Supplement', 'Omega-3 Capsules', 'Nordic Naturals', 'Heart health supplement', 950.00, 60, '2028-05-22', 'Capsule', 'Heart health', '2025-03-08', 0.00, NULL),
(156, 'Cosmetics', 'Deodorant', 'Axe', 'Body deodorant', 300.00, 60, NULL, 'N/A', 'Odor control', '2025-03-09', 0.00, NULL),
(157, 'Medicine', 'Antiseptic Solution', 'Dettol', 'Kills germs', 150.00, 100, '2024-11-10', 'Solution', 'Antiseptic', '2025-03-10', 0.00, NULL),
(158, 'Cosmetics', 'Foot Cream', 'Eucerin', 'Softens feet', 400.00, 55, NULL, 'Cream', 'Foot care', '2025-02-20', 0.00, NULL),
(159, 'Supplement', 'Collagen Powder', 'Vital Proteins', 'Skin elasticity support', 3500.00, 15, '2027-09-11', 'Powder', 'Collagen support', '2025-02-21', 0.00, NULL),
(160, 'Medicine', 'Fever Medicine', 'Tylenol', 'Reduces fever', 85.00, 140, '2025-04-04', 'Tablet', 'Fever reduction', '2025-02-22', 0.00, '/pictures/Acne releif gel.jpg'),
(161, 'Medicine', 'Neurogenix', 'NeuroCraft', 'Brain Health', 2100.00, 45, '2027-09-15', 'Capsule', 'Improves cognitive function', '2025-02-23', 0.00, '/pictures/Dove Face Wash.jpg'),
(162, 'Medicine', 'CoughEase', 'RespiraLife', 'Cough Syrup', 115.00, 160, '2025-03-11', 'Syrup', 'Relieves cough and throat irritation', '2025-02-24', 0.00, '/pictures/Face Maskk.jpg'),
(163, 'Medicine', 'LiverCare', 'HepatoShield', 'Liver Support', 340.00, 70, '2026-12-05', 'Tablet', 'Supports liver detoxification', '2025-02-25', 0.00, '/pictures/Facewash.jpg'),
(164, 'Medicine', 'OmegaPlus', 'VitaNutri', 'Supplements', 290.00, 100, '2027-04-21', 'Softgel', 'Promotes heart health', '2025-02-26', 0.00, '/pictures/Haircare Serum.jpg'),
(165, 'Medicine', 'PainShield', 'RelieveX', 'Pain Reliever', 180.00, 35, '2025-01-31', 'Gel', 'Relieves muscle and joint pain', '2025-02-27', 0.00, '/pictures/Loreal shampo.jpg'),
(166, 'Cosmetics', 'AcneFix', 'ClearSkin', 'Skin Care', 380.00, 37, '2025-08-15', 'Gel', 'Treats acne and prevents breakouts', '2025-02-28', 0.00, '/pictures/acne fix.jpg'),
(167, 'Cosmetics', 'HerbalFresh', 'NaturePure', 'Shampoo', 200.00, 70, '2026-10-09', 'Mouthwash', 'Provides fresh breath and gum protection', '2025-03-01', 0.00, '/pictures/aller free.jpg'),
(168, 'Medicine', 'CardioBoost', 'HeartSure', 'Heart Health', 450.00, 60, '2027-02-28', 'Capsule', 'Supports heart function', '2025-03-02', 0.00, '/pictures/amoxicilline.jpg'),
(169, 'Medicine', 'SleepRight', 'DreamWell', 'Sleep Aid', 320.00, 110, '2025-11-01', 'Tablet', 'Improves sleep quality', '2025-03-03', 0.00, '/pictures/antacid.jpg'),
(170, 'Medicine', 'AllerFree', 'AllergyShield', 'Allergy Relief', 1200.00, 196, '2025-07-15', 'Tablet', 'Relieves allergy symptoms', '2025-03-04', 0.00, '/pictures/anti aging creme.jpg'),
(171, 'Medicine', 'BoneCare', 'OsteoStrong', 'Calcium Supplement', 450.00, 60, '2026-02-12', 'Tablet', 'Strengthens bones', '2025-03-05', 0.00, '/pictures/anti fungal creme.jpg'),
(172, 'Cosmetics', 'SunShield SPF50', 'SunSafe', 'Sunblock', 800.00, 25, '2026-09-18', 'Lotion', 'Protects skin from UV damage', '2025-03-06', 0.00, '/pictures/antibiotic creme.jpg'),
(173, 'Medicine', 'FlexiJoints', 'JointCare', 'Joint Support', 350.00, 30, '2026-03-09', 'Capsule', 'Improves joint flexibility', '2025-03-07', 0.00, '/pictures/antidandruff shampo.jpg'),
(174, 'Medicine', 'RespiraBoost', 'BreatheEase', 'Respiratory Health', 250.00, 110, '2025-12-25', 'Syrup', 'Supports lung health', '2025-03-08', 0.00, '/pictures/antifungal spray.jpg'),
(175, 'Cosmetics', 'SkinBright Serum', 'GlowEssentials', 'Skin Care', 450.00, 25, '2026-04-04', 'Serum', 'Brightens skin and reduces dark spots', '2025-03-09', 0.00, '/pictures/antiseptic solution.jpg'),
(176, 'Medicine', 'IronMax', 'IronVital', 'Iron Supplement', 190.00, 70, '2026-01-17', 'Tablet', 'Combats anemia', '2025-03-10', 0.00, '/pictures/aspirin.jpg'),
(177, 'Cosmetic', 'BabyCare Lotion', 'BabySoft', 'Baby Care', 1500.00, 95, '2027-03-05', 'Lotion', 'Moisturizes and protects', '2025-02-20', 0.00, '/pictures/augmenton.jpg'),
(178, 'Medicine', 'KidneyFlush', 'RenalPure', 'Kidney Health', 350.00, 30, '2025-06-06', 'Capsule', 'Detoxifies kidneys', '2025-02-21', 0.00, '/pictures/avatar.jpg'),
(179, 'Medicine', 'MuscleMass', 'ProMuscl', 'Protein Supplement', 4500.00, 90, '2026-07-14', 'Powder', 'Supports muscle growth', '2025-02-22', 0.00, '/pictures/baby care lotion.jpg'),
(180, 'Cosmetic', 'AntiAging Cream', 'AgeDefy', 'Anti-Aging', 2400.00, 80, '2026-03-28', 'Cream', 'Reduces wrinkles and signs of aging', '2025-02-23', 0.00, NULL),
(181, 'Medicine', 'DetoxHerbs', 'PureHerb', 'Detox Supplement', 280.00, 60, '2025-10-16', 'Tea', 'Detoxifies the body', '2025-02-24', 0.00, NULL),
(182, 'Medicine', 'ColdRelief', 'ColdAway', 'Cold & Flu', 100.00, 100, '2025-12-08', 'Syrup', 'Relieves cold and flu symptoms', '2025-02-25', 0.00, NULL),
(183, 'Cosmetic', 'HairCare Serum', 'HairReviv', 'Hair Care', 750.00, 75, '2027-05-10', 'Serum', 'Promotes hair growth', '2025-02-26', 0.00, NULL),
(184, 'Medicine', 'MultiVitamins', 'VitaDaily', 'General Health', 400.00, 50, '2025-11-22', 'Tablet', 'Provides daily essential vitamins', '2025-02-27', 0.00, NULL),
(185, 'Medicine', 'Antifungal Cream', 'FungoClea', 'Skin Treatment', 600.00, 55, '2026-08-15', 'Cream', 'Treats fungal infections', '2025-02-28', 0.00, NULL),
(186, 'Cosmetic', 'FootCare Lotion', 'FootRelief', 'Foot Care', 2500.00, 30, '2027-01-29', 'Lotion', 'Soothes and moisturizes feet', '2025-03-01', 0.00, NULL),
(187, 'Medicine', 'VisionPlus', 'EyeVital', 'Eye Health', 290.00, 90, '2026-02-11', 'Capsule', 'Improves vision and eye health', '2025-03-02', 0.00, NULL),
(188, 'Medicine', 'ProbioticMax', 'GutHealth', 'Digestive Health', 400.00, 200, '2026-11-11', 'Capsule', 'Improves gut health and digestion', '2025-03-03', 0.00, NULL),
(189, 'Medicine', 'AcneRelief Gel', 'ClearSkin', 'Acne Treatment', 450.00, 42, '2026-04-26', 'Gel', 'Treats acne and prevents breakouts', '2025-03-04', 0.00, NULL),
(190, 'Medicine', 'Elderberry Syrup', 'ElderPure', 'Immunity Booster', 230.00, 110, '2025-09-19', 'Syrup', 'Boosts immunity', '2025-03-05', 0.00, NULL),
(191, 'Cosmetic', 'StretchMark Cream', 'SkinRepair', 'Body Care', 380.00, 25, '2026-03-09', 'Cream', 'Reduces stretch marks', '2025-03-06', 0.00, NULL),
(192, 'Medicine', 'BoneHealth Plus', 'OsteoCare', 'Bone Health', 320.00, 50, '2027-07-13', 'Tablet', 'Improves bone density', '2025-03-07', 0.00, NULL),
(193, 'Medicine', 'CalmMind', 'MindEase', 'Stress Relief', 310.00, 100, '2025-05-20', 'Capsule', 'Reduces stress and promotes relaxation', '2025-03-08', 0.00, NULL),
(194, 'Cosmetic', 'HairVital', 'HairNour', 'Hair Strengthening', 380.00, 60, '2027-06-01', 'Capsule', 'Strengthens hair and reduces hair fall', '2025-03-09', 0.00, NULL),
(195, 'Medicine', 'JointEase', 'FlexiCare', 'Joint Support', 340.00, 90, '2026-05-21', 'Capsule', 'Relieves joint pain', '2025-03-10', 0.00, NULL),
(196, 'Cosmetic', 'Vitamin C Serum', 'GlowEsse', 'Skin Care', 600.00, 20, '2026-07-20', 'Serum', 'Brightens skin and boosts collagen', '2025-02-20', 0.00, NULL),
(197, 'Medicine', 'Nasal Spray', 'BreatheFre', 'Allergy Relief', 250.00, 85, '2025-04-02', 'Spray', 'Relieves nasal congestion and allergies', '2025-02-21', 0.00, NULL),
(198, 'Cosmetic', 'AntiDandruff Shampoo', 'ScalpCare', 'Hair Care', 260.00, 75, '2026-07-18', 'Shampoo', 'Treats dandruff and soothes scalp', '2025-02-22', 0.00, NULL),
(199, 'Medicine', 'Electrolyte Drink', 'HydraBody', 'Hydration', 180.00, 200, '2025-08-30', 'Drink', 'Replenishes electrolytes', '2025-02-23', 0.00, NULL),
(200, 'Cosmetic', 'FaceHydration Gel', 'AquaGlow', 'Skin Hydration', 300.00, 60, '2026-11-14', 'Gel', 'Hydrates and nourishes skin', '2025-02-24', 0.00, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(100) NOT NULL,
  `first_name` varchar(100) DEFAULT NULL,
  `last_name` varchar(100) DEFAULT NULL,
  `email` varchar(150) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('owner','admin','employee') NOT NULL DEFAULT 'employee'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `first_name`, `last_name`, `email`, `password`, `role`) VALUES
(30, 'kashaf', 'kashaf', 'Shahzadi', 'kashayyyyrajput@gmail.com', '$2b$12$0IXnNONMCwMqxFGzxajMouF4VdDDXlzVURx/UueQLjqXHZlFAFmSi', 'owner'),
(31, 'sara', 'sara', 'khan', 'sara123@gmail.com', '$2b$12$MudI0oauYAnWmyLf/1SVU.VijMWJJIwia2THZdXJ7Wm4P/bj3vzcW', 'admin'),
(32, 'bella', 'bella', 'chao', 'bella23@gmail.com', '$2b$12$xsLdpyK5AfRwUsN5UvHqeeVtL4MmNmMEW1URuOnpEenAa0WN/po9.', 'employee'),
(33, 'maleeha', 'maleeha', 'khan', 'maleeha2@gmail.com', '$2b$12$axK33q0TMSeje2nbdSOIJ.IzuVNIGUEhVP2pQDqoHlXvb8lzCSsAi', 'employee'),
(36, 'Kashaf_', 'kashaf', 'rajput', 'kashafshahzadi50@gmail.com', '$2b$12$Xmwv3NT3MzD8NdWqtf6F5eh5nP.zUeQZ4slm9ypJqYLoCMOh9l14C', 'admin');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `employees`
--
ALTER TABLE `employees`
  ADD PRIMARY KEY (`employee_id`);

--
-- Indexes for table `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`order_id`);

--
-- Indexes for table `order_items`
--
ALTER TABLE `order_items`
  ADD PRIMARY KEY (`order_item_id`),
  ADD KEY `order_id` (`order_id`),
  ADD KEY `product_id` (`product_id`);

--
-- Indexes for table `pharmacy_orders`
--
ALTER TABLE `pharmacy_orders`
  ADD PRIMARY KEY (`pharmacy_order_id`);

--
-- Indexes for table `pharmacy_order_items`
--
ALTER TABLE `pharmacy_order_items`
  ADD PRIMARY KEY (`item_id`),
  ADD KEY `pharmacy_order_id` (`pharmacy_order_id`);

--
-- Indexes for table `products`
--
ALTER TABLE `products`
  ADD PRIMARY KEY (`product_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `orders`
--
ALTER TABLE `orders`
  MODIFY `order_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=34;

--
-- AUTO_INCREMENT for table `order_items`
--
ALTER TABLE `order_items`
  MODIFY `order_item_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=77;

--
-- AUTO_INCREMENT for table `pharmacy_orders`
--
ALTER TABLE `pharmacy_orders`
  MODIFY `pharmacy_order_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `pharmacy_order_items`
--
ALTER TABLE `pharmacy_order_items`
  MODIFY `item_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=37;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `order_items`
--
ALTER TABLE `order_items`
  ADD CONSTRAINT `order_items_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`),
  ADD CONSTRAINT `order_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`);

--
-- Constraints for table `pharmacy_order_items`
--
ALTER TABLE `pharmacy_order_items`
  ADD CONSTRAINT `pharmacy_order_items_ibfk_1` FOREIGN KEY (`pharmacy_order_id`) REFERENCES `pharmacy_orders` (`pharmacy_order_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
