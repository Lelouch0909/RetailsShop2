-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS shoptub;

-- Create the user and grant privileges
-- Removed IF NOT EXISTS from CREATE USER as it might not be supported on older MySQL versions
CREATE USER 'webapp'@'localhost' IDENTIFIED BY 'motdepassefort';
GRANT ALL PRIVILEGES ON shoptub.* TO 'webapp'@'localhost';
FLUSH PRIVILEGES;

-- Use the database
USE shoptub;

-- Create tables
CREATE TABLE IF NOT EXISTS `admin` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `firstName` varchar(125) NOT NULL,
  `lastName` varchar(125) NOT NULL,
  `email` varchar(100) NOT NULL,
  `mobile` varchar(25) NOT NULL,
  `address` text NOT NULL,
  `password` varchar(100) NOT NULL,
  `type` varchar(20) NOT NULL,
  `confirmCode` varchar(10) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `orders` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uid` int(11) DEFAULT NULL,
  `ofname` text NOT NULL,
  `pid` int(11) NOT NULL,
  `quantity` int(11) NOT NULL,
  `oplace` text NOT NULL,
  `mobile` varchar(15) NOT NULL,
  `dstatus` varchar(10) NOT NULL DEFAULT 'no',
  `odate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `ddate` date DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `products` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `pName` varchar(100) NOT NULL,
  `price` int(11) NOT NULL,
  `description` text NOT NULL,
  `available` int(11) NOT NULL,
  `category` varchar(100) NOT NULL,
  `item` varchar(100) NOT NULL,
  `pCode` varchar(20) NOT NULL,
  `picture` text NOT NULL,
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `product_level` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `product_id` int(11) NOT NULL,
  `v_shape` varchar(10) NOT NULL DEFAULT 'no',
  `polo` varchar(10) NOT NULL DEFAULT 'no',
  `clean_text` varchar(10) NOT NULL DEFAULT 'no',
  `design` varchar(10) NOT NULL DEFAULT 'no',
  `chain` varchar(10) NOT NULL DEFAULT 'no',
  `leather` varchar(10) NOT NULL DEFAULT 'no',
  `hook` varchar(10) NOT NULL DEFAULT 'no',
  `color` varchar(10) NOT NULL DEFAULT 'no',
  `formal` varchar(10) NOT NULL DEFAULT 'no',
  `converse` varchar(10) NOT NULL DEFAULT 'no',
  `loafer` varchar(10) NOT NULL DEFAULT 'no',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=22 DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `product_view` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=9 DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `product_likes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_product` (`user_id`, `product_id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `product_reviews` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `rating` int(11) NOT NULL,
  `review_text` text NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_product_review` (`user_id`, `product_id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `email` varchar(50) NOT NULL,
  `username` varchar(25) NOT NULL,
  `password` varchar(100) NOT NULL,
  `mobile` varchar(20) NOT NULL,
  `reg_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `online` varchar(1) NOT NULL DEFAULT '0',
  `activation` varchar(3) NOT NULL DEFAULT 'yes',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=16 DEFAULT CHARSET=latin1;

-- Insert sample data
INSERT INTO `admin` (`id`, `firstName`, `lastName`, `email`, `mobile`, `address`, `password`, `type`, `confirmCode`) VALUES
(4, 'Nur', 'Mohsin', 'mohsin@gmail.com', '01677876551', 'Dhaka', '$5$rounds=535000$WOAOMdgoK2JpZLY5$RFH9BZQCB3NEvG4R/FofxxJL/PUaeZm7T6G9P3PRg05', 'manager', '0');

INSERT INTO `products` (`id`, `pName`, `price`, `description`, `available`, `category`, `item`, `pCode`, `picture`, `date`) VALUES
(1, 'T-Shirt', 120, 'T-Shirt', 4, 'tshirt', 't-shirt', 't-007', 'MSTS14738.jpg', '2018-09-20 07:10:40'),
(2, 'Baborry wallet', 6000, 'Baborry-Double-Zipper-Coin-Bag-RFID-Blocking-Men-Wallets-New-Brand-PU-Leather-Wallet-Money-Purses', 3, 'wallet', 'wallet', 'w-004', 'IMG_1212.jpg', '2018-09-20 07:40:28'),
(3, 'Loafer Shoes', 2000, 'Loafer black shoes', 8, 'shoes', 'shoes', 's-001', '8544789_5_.jpg', '2018-09-20 08:33:57'),
(4, 'Artificial Belt', 1200, 'Black artificial belt', 9, 'belt', 'belt', 'b-001', '0283BLT.jpg', '2018-09-20 08:35:44');

INSERT INTO `product_level` (`id`, `product_id`, `v_shape`, `polo`, `clean_text`, `design`, `chain`, `leather`, `hook`, `color`, `formal`, `converse`, `loafer`) VALUES
(1, 1, 'no', 'no', 'yes', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no'),
(2, 2, 'no', 'no', 'no', 'no', 'yes', 'yes', 'no', 'no', 'no', 'no', 'no'),
(3, 3, 'no', 'no', 'no', 'no', 'no', 'yes', 'no', 'no', 'no', 'no', 'yes'),
(4, 4, 'no', 'no', 'no', 'no', 'no', 'yes', 'yes', 'no', 'no', 'no', 'no');

-- Insert sample data for product likes
INSERT INTO `product_likes` (`id`, `user_id`, `product_id`, `created_at`) VALUES
(1, 9, 1, '2023-10-15 10:30:00'),
(2, 12, 1, '2023-10-15 11:45:00'),
(3, 13, 1, '2023-10-16 09:20:00'),
(4, 9, 2, '2023-10-16 14:10:00'),
(5, 14, 2, '2023-10-17 16:30:00'),
(6, 9, 3, '2023-10-18 08:45:00'),
(7, 15, 4, '2023-10-18 19:15:00');

-- Insert sample data for product reviews
INSERT INTO `product_reviews` (`id`, `user_id`, `product_id`, `rating`, `review_text`, `created_at`) VALUES
(1, 9, 1, 5, 'Great t-shirt! The fabric is comfortable and the design is stylish.', '2023-10-15 10:35:00'),
(2, 12, 1, 4, 'Nice t-shirt, good quality for the price.', '2023-10-15 12:00:00'),
(3, 13, 2, 5, 'Excellent wallet, very durable and stylish.', '2023-10-16 10:15:00'),
(4, 9, 3, 4, 'Comfortable shoes, but they run a bit small.', '2023-10-17 14:30:00'),
(5, 14, 4, 5, 'Great belt, looks more expensive than it is!', '2023-10-18 09:45:00');
