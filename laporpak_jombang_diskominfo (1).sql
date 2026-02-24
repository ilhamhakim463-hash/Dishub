-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3307
-- Generation Time: Feb 24, 2026 at 04:27 AM
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
-- Database: `laporpak_jombang_diskominfo`
--

-- --------------------------------------------------------

--
-- Table structure for table `alembic_version`
--

CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `alembic_version`
--

INSERT INTO `alembic_version` (`version_num`) VALUES
('4d6fb002e218');

-- --------------------------------------------------------

--
-- Table structure for table `categories`
--

CREATE TABLE `categories` (
  `id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `slug` varchar(50) NOT NULL,
  `icon` varchar(50) DEFAULT 'bi-chat-dots',
  `description` varchar(255) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `nama` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `categories`
--

INSERT INTO `categories` (`id`, `name`, `slug`, `icon`, `description`, `is_active`, `created_at`, `nama`) VALUES
(1, 'Lampu Lalu Lintas Mati/Rusak', 'lampu-lalin-rusak', 'bi-lightbulb-off', 'Gangguan APILL / Traffic Light', 1, '2026-02-11 07:16:08', ''),
(2, 'Rambu Lalu Lintas Rusak/Hilang', 'rambu-rusak', 'bi-signpost-split', 'Rambu roboh, pudar, atau hilang', 1, '2026-02-11 07:16:08', ''),
(3, 'Marka Jalan Pudar/Hilang', 'marka-jalan-pudar', 'bi-border-width', 'Garis marka jalan tidak terlihat jelas', 1, '2026-02-11 07:16:08', ''),
(4, 'Kemacetan Parah', 'kemacetan-parah', 'bi-car-front-fill', 'Kondisi lalu lintas macet total', 1, '2026-02-11 07:16:08', ''),
(5, 'Parkir Liar', 'parkir-liar', 'bi-p-circle-fill', 'Kendaraan parkir di area terlarang', 1, '2026-02-11 07:16:08', ''),
(6, 'Angkutan Umum Bermasalah', 'angkutan-umum', 'bi-bus-front', 'Masalah pada bus, angkot, atau terminal', 1, '2026-02-11 07:16:08', ''),
(8, 'Jalan Rawan Kecelakaan', 'jalan-berbahaya', 'bi-shield-slash', 'Area rawan kecelakaan (Blackspot)', 1, '2026-02-11 07:16:08', ''),
(9, 'Fasilitas Pejalan Kaki Rusak', 'pedestrian-rusak', 'bi-person-walking', 'Kerusakan trotoar atau zebra cross', 1, '2026-02-11 07:16:08', ''),
(10, 'Darurat Lalu Lintas', 'darurat-lalin', 'bi-megaphone-fill', 'Kejadian luar biasa butuh respon instan', 1, '2026-02-11 07:16:08', '');

-- --------------------------------------------------------

--
-- Table structure for table `emergency_alerts`
--

CREATE TABLE `emergency_alerts` (
  `id` int(11) NOT NULL,
  `tipe_bencana` varchar(50) NOT NULL,
  `pesan` text NOT NULL,
  `wilayah_terdampak` varchar(50) NOT NULL,
  `level_bahaya` enum('waspada','siaga','bahaya') DEFAULT 'bahaya',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `emergency_alerts`
--

INSERT INTO `emergency_alerts` (`id`, `tipe_bencana`, `pesan`, `wilayah_terdampak`, `level_bahaya`, `created_at`) VALUES
(1, '', '', 'Semua', 'bahaya', '2026-02-09 22:59:28'),
(2, 'hgjtjhhdhdh', 'fghrdtdfsr rgsgw', 'Jombang', 'bahaya', '2026-02-12 06:25:06'),
(3, 'banjir bandang', 'aswr wr', 'Jombang', 'siaga', '2026-02-23 07:40:43'),
(4, 'banjir bandang', 'asdfw', 'Jombang', 'siaga', '2026-02-23 08:00:19');

-- --------------------------------------------------------

--
-- Table structure for table `interactions`
--

CREATE TABLE `interactions` (
  `id` int(11) NOT NULL,
  `report_id` int(11) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `tipe` varchar(20) DEFAULT NULL,
  `konten` text DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `interactions`
--

INSERT INTO `interactions` (`id`, `report_id`, `user_id`, `tipe`, `konten`, `created_at`) VALUES
(1, 1, 2, 'comment', 'seegra diperbaiki', '2026-02-09 04:37:37'),
(2, 3, 2, 'comment', 'segera diatasi ', '2026-02-10 03:42:53'),
(4, NULL, 2, 'comment', 'seegra diperbaiki', '2026-02-12 03:01:16'),
(5, NULL, 2, 'comment', 'segera diatasi ', '2026-02-12 04:06:26'),
(6, NULL, 2, 'comment', 'segera diatasi ', '2026-02-12 04:08:04'),
(7, 13, 2, 'comment', 'seegra diperbaiki', '2026-02-12 04:34:04'),
(8, 15, 2, 'comment', 'segera diatasi ', '2026-02-12 04:40:01'),
(9, 15, 2, 'comment', 'seegra diperbaiki', '2026-02-12 05:42:38'),
(10, 16, 7, 'comment', 'segera diatasi ', '2026-02-12 06:58:54'),
(11, 16, 7, 'comment', 'ffff', '2026-02-12 14:36:27'),
(12, 19, 2, 'comment', 'ersttewesr', '2026-02-15 02:18:26'),
(13, 30, 2, 'comment', 'vasf trtvasdf3w 4', '2026-02-20 04:19:10'),
(14, 35, 2, 'comment', 'vasf trtvasdf3w 4', '2026-02-22 04:38:31'),
(15, 35, 12, 'comment', 'gysiuhf aer', '2026-02-24 03:22:31'),
(16, 38, 12, 'comment', 'asdfwDS', '2026-02-24 03:25:57');

-- --------------------------------------------------------

--
-- Table structure for table `notifications`
--

CREATE TABLE `notifications` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `report_id` int(11) DEFAULT NULL,
  `type` varchar(50) NOT NULL COMMENT 'status_update | comment | support',
  `title` varchar(200) NOT NULL,
  `message` text NOT NULL,
  `is_read` tinyint(1) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `reports`
--

CREATE TABLE `reports` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `category_id` int(11) DEFAULT NULL,
  `judul` varchar(200) NOT NULL,
  `deskripsi` text NOT NULL,
  `kategori` varchar(50) NOT NULL,
  `foto_awal` varchar(255) DEFAULT NULL,
  `foto_proses` varchar(255) DEFAULT NULL,
  `latitude` float DEFAULT NULL,
  `longitude` float DEFAULT NULL,
  `alamat_manual` varchar(255) DEFAULT NULL,
  `hashtag` varchar(255) DEFAULT NULL,
  `status_warna` varchar(20) DEFAULT 'merah',
  `urgency_level` varchar(20) DEFAULT 'normal',
  `is_approved` tinyint(1) DEFAULT 0,
  `sentiment` enum('positive','neutral','negative','marah','panik') DEFAULT 'neutral',
  `sentiment_score` float DEFAULT NULL,
  `is_incognito` tinyint(1) DEFAULT 0,
  `is_public` tinyint(1) DEFAULT 0,
  `foto_perbaikan` varchar(255) DEFAULT NULL,
  `foto_selesai` varchar(255) DEFAULT NULL,
  `catatan_admin` text DEFAULT NULL,
  `views_count` int(11) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `approved_at` timestamp NULL DEFAULT NULL,
  `resolved_at` timestamp NULL DEFAULT NULL,
  `foto_2` varchar(255) DEFAULT NULL,
  `foto_3` varchar(255) DEFAULT NULL,
  `target_selesai` datetime DEFAULT NULL,
  `petugas_id` int(11) DEFAULT NULL,
  `is_archived` tinyint(1) DEFAULT 0,
  `status_label` varchar(50) DEFAULT NULL,
  `support_count` int(11) DEFAULT 0,
  `komentar_admin` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `reports`
--

INSERT INTO `reports` (`id`, `user_id`, `category_id`, `judul`, `deskripsi`, `kategori`, `foto_awal`, `foto_proses`, `latitude`, `longitude`, `alamat_manual`, `hashtag`, `status_warna`, `urgency_level`, `is_approved`, `sentiment`, `sentiment_score`, `is_incognito`, `is_public`, `foto_perbaikan`, `foto_selesai`, `catatan_admin`, `views_count`, `created_at`, `updated_at`, `approved_at`, `resolved_at`, `foto_2`, `foto_3`, `target_selesai`, `petugas_id`, `is_archived`, `status_label`, `support_count`, `komentar_admin`) VALUES
(1, 2, NULL, 'jalan berlobang', 'tidak terlalu besar', 'infrastruktur', NULL, NULL, NULL, NULL, NULL, NULL, 'merah', '2', 1, NULL, NULL, 0, 0, NULL, NULL, NULL, 0, '2026-02-05 06:23:30', '2026-02-12 10:42:17', '2026-02-11 19:18:46', NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, NULL),
(3, 2, NULL, 'sampah menumpuk di selokan sepanjang 200m di daerah plosogeneng', 'sepanjang 200m di daerah plosogeneng dan menyebabkan bau tak enak dan bisa berdampak banjir ', 'lingkungan', 'report_2_Screenshot_2026-01-19_150411.png', NULL, -7.52377, 112.219, 'Plosogeneng, Jombang, East Java, Java, 61416, Indonesia', NULL, 'biru', '2', 1, 'neutral', NULL, 0, 1, NULL, NULL, NULL, 0, '2026-02-09 20:42:30', '2026-02-12 10:42:16', '2026-02-11 19:15:48', '2026-02-11 19:24:15', NULL, NULL, NULL, NULL, 0, NULL, 0, NULL),
(10, 2, NULL, 'kemalingan', 'fhgrthrt', 'Fasilitas Pejalan Kaki Rusak', 'foto_awal_2_20260212_104406_Cuplikan_layar_2026-01-13_101803.png', NULL, -7.52374, 112.219, 'Plosogeneng, Jombang, East Java, Java, 61416, Indonesia', NULL, 'kuning', 'normal', 1, 'neutral', NULL, 0, 0, NULL, NULL, NULL, 0, '2026-02-12 03:44:06', '2026-02-12 10:42:12', '2026-02-11 21:16:05', NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, NULL),
(11, 2, NULL, 'gggg', 'dfgsdegergf\n\n[Catatan Admin 12/02/2026 11:22] yowwwww', 'Fasilitas Pejalan Kaki Rusak', 'foto_awal_2_20260212_111722_Cuplikan_layar_2026-01-13_103903.png', NULL, -7.52375, 112.219, 'Plosogeneng, Jombang, East Java, Java, 61416, Indonesia', NULL, 'merah', 'normal', 1, 'neutral', NULL, 0, 0, NULL, 'selesai_11_20260212112221.jpg', NULL, 0, '2026-02-12 04:17:22', '2026-02-12 10:58:32', '2026-02-11 21:17:45', NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, NULL),
(12, 6, NULL, 'gggg', 'dfgsdegergf\n\n[Catatan Admin 12/02/2026 11:20] woowwwww', 'Fasilitas Pejalan Kaki Rusak', 'foto_awal_6_20260212_111854_Cuplikan_layar_2026-01-13_103903.png', NULL, -7.5465, 112.233, '', NULL, 'biru', 'normal', 1, 'neutral', NULL, 0, 0, NULL, 'selesai_12_20260212112050.jpg', NULL, 0, '2026-02-12 04:18:54', '2026-02-12 10:58:30', '2026-02-11 21:19:01', '2026-02-11 21:20:50', NULL, NULL, NULL, NULL, 0, NULL, 0, NULL),
(13, 2, NULL, 'kemalingan', 'wowwww\n\n[Catatan Admin 12/02/2026 11:24] yeahhhhh', 'Parkir Liar', 'foto_awal_2_20260212_112350_Cuplikan_layar_2026-01-14_111123.png', NULL, -7.52375, 112.219, 'Plosogeneng, Jombang, East Java, Java, 61416, Indonesia', NULL, 'biru', 'normal', 1, 'neutral', NULL, 0, 0, NULL, 'selesai_13_20260212112447.jpg', NULL, 0, '2026-02-12 04:23:50', '2026-02-12 10:58:29', '2026-02-11 21:24:13', '2026-02-11 21:24:47', NULL, NULL, NULL, NULL, 0, NULL, 0, NULL),
(15, 2, NULL, 'jalan berlobang', 'jhjhjhhjjh\n\n[Catatan Admin 12/02/2026 11:37] xcszasd\n\n[Catatan Admin 12/02/2026 11:38] asdsasaasd\n\n[Catatan Admin 12/02/2026 11:39] yeahhhhh', 'Kemacetan Parah', 'foto_awal_2_20260212_113725_Screenshot_2026-02-12_110916.png', NULL, -7.52374, 112.219, 'Plosogeneng, Jombang, East Java, Java, 61416, Indonesia', NULL, 'biru', 'normal', 1, 'neutral', NULL, 0, 0, NULL, 'selesai_15_20260212113936.jpg', NULL, 0, '2026-02-12 04:37:25', '2026-02-12 13:05:06', '2026-02-11 21:37:39', '2026-02-11 21:39:36', NULL, NULL, NULL, NULL, 0, NULL, 0, NULL),
(16, 2, NULL, 'gggg', 'r', 'Fasilitas Pejalan Kaki Rusak', 'foto_awal_2_20260212_134334_Cuplikan_layar_2026-01-13_090410.png', NULL, -7.52375, 112.219, 'Plosogeneng, Jombang, East Java, Java, 61416, Indonesia', NULL, 'kuning', 'normal', 1, 'neutral', NULL, 0, 0, NULL, NULL, NULL, 0, '2026-02-12 06:43:34', '2026-02-12 10:58:24', '2026-02-11 23:57:40', NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, NULL),
(17, 7, NULL, 'gggg', 'sdfvdsg\n\n[Catatan Admin 12/02/2026 13:58] yeahhhhh', 'Kemacetan Parah', 'foto_awal_7_20260212_135038_Cuplikan_layar_2026-01-13_104753.png', NULL, -7.52373, 112.219, 'Plosogeneng, Jombang, East Java, Java, 61416, Indonesia', NULL, 'biru', 'normal', 1, 'neutral', NULL, 0, 0, NULL, 'selesai_17_20260212135800.jpg', NULL, 0, '2026-02-12 06:50:38', '2026-02-21 02:18:00', '2026-02-11 23:57:38', '2026-02-11 23:58:00', NULL, NULL, NULL, NULL, 0, NULL, 0, NULL),
(18, 7, NULL, 'sampah menumpuk di selokan sepanjang 200m di daerah plosogeneng', 'fsdsdd\n\n[Catatan Admin 15/02/2026 09:17] afwefwe', 'Lampu Lalu Lintas Mati / Rusak', 'foto_awal_7_20260212_191119_download.png', NULL, -7.52372, 112.219, 'Plosogeneng, Jombang, East Java, Java, 61416, Indonesia', NULL, 'biru', 'normal', 1, 'neutral', NULL, 0, 0, NULL, 'selesai_18_20260215091728.jpg', NULL, 0, '2026-02-12 12:11:19', '2026-02-15 02:17:28', '2026-02-12 19:11:41', '2026-02-14 19:17:28', NULL, NULL, NULL, NULL, 0, NULL, 0, NULL),
(19, 2, NULL, 'kemalingan', 'maling\n\n[Catatan Admin 13/02/2026 09:12] fghghhghghggh\n\n[Catatan Admin 13/02/2026 09:18] youuuu', 'Angkutan Umum Bermasalah', 'foto_awal_2_202602130831_download.png', NULL, -7.52373, 112.219, 'Plosogeneng, Jombang, East Java, Java, 61416, Indonesia', NULL, 'biru', 'normal', 1, 'neutral', NULL, 0, 0, NULL, 'selesai_19_20260213091847.jpg', NULL, 0, '2026-02-12 18:31:32', '2026-02-15 02:37:33', '2026-02-12 18:35:12', '2026-02-12 19:18:47', NULL, NULL, NULL, NULL, 0, NULL, 0, NULL),
(20, 2, NULL, 'kemalingan', 'yjtfyujfty', 'Angkutan Umum Bermasalah', 'foto_awal_2_202602152112_Cuplikan_layar_2026-01-13_104753.png', NULL, -7.52371, 112.219, 'Plosogeneng, Jombang, East Java, Java, 61416, Indonesia', NULL, 'merah', 'normal', 1, 'neutral', NULL, 0, 0, NULL, NULL, NULL, 0, '2026-02-15 07:12:18', '2026-02-18 06:29:09', '2026-02-17 23:29:09', NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, NULL),
(21, 2, NULL, 'jalan berlobang', 'sadferwfsdfearfae\n\n[Catatan Admin 17/02/2026 13:07] asdferaf', 'Fasilitas Pejalan Kaki Rusak', 'foto_awal_2_202602161304_Cuplikan_layar_2026-01-13_104753.png', NULL, -7.52373, 112.219, 'Plosogeneng, Jombang, East Java, Java, 61416, Indonesia', NULL, 'kuning', 'normal', 1, 'neutral', NULL, 0, 0, NULL, 'selesai_21_20260217130717.jpg', NULL, 0, '2026-02-15 23:04:57', '2026-02-17 06:07:17', '2026-02-16 23:07:06', NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, NULL),
(22, 2, NULL, 'jalan berlobang', 'bahaya', 'Kemacetan Parah', 'foto_awal_2_202602181320_a.jpeg', NULL, -7.5465, 112.233, 'Jalan Wage Rudolf Supratman III, Tawangsari, Jombatan, Jombang, East Java, Java, 61417, Indonesia', NULL, 'kuning', 'normal', 1, 'neutral', NULL, 0, 0, NULL, NULL, NULL, 0, '2026-02-17 23:20:01', '2026-02-18 06:22:56', '2026-02-17 23:21:50', NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, NULL),
(23, 2, NULL, 'marka jalan hilang', 'di sepanjang jalan umum jombang', 'Marka Jalan Pudar / Hilang', 'foto_awal_2_202602192122_download.png', NULL, -7.5465, 112.233, NULL, NULL, 'merah', 'normal', 1, 'neutral', NULL, 0, 0, NULL, NULL, NULL, 0, '2026-02-19 07:22:43', '2026-02-19 14:31:01', '2026-02-19 07:31:01', NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, NULL),
(24, 2, NULL, 'pudarnya marka jalan', 'di senajang jalan kota jombang\n\n[Catatan Admin 19/02/2026 21:29] terimakaish atas laporan anda', 'Marka Jalan Pudar / Hilang', 'foto_awal_2_202602192127_download.png', NULL, -7.5465, 112.233, NULL, NULL, 'kuning', 'normal', 1, 'neutral', NULL, 0, 0, NULL, NULL, NULL, 0, '2026-02-19 07:27:23', '2026-02-19 14:31:09', '2026-02-19 07:29:28', NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, NULL),
(27, 2, NULL, 'kemalingan', 'zsdfgawert', 'Jalan Berbahaya / Rawan Kecelakaan', 'foto_awal_2_202602192135_cv.png', NULL, -7.52374, 112.219, NULL, NULL, 'merah', 'normal', 1, 'neutral', NULL, 0, 0, NULL, NULL, NULL, 0, '2026-02-19 07:35:40', '2026-02-19 14:36:08', '2026-02-19 07:36:08', NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, NULL),
(28, 2, NULL, 'kemalingan', 'asdqwer', 'Lampu Lalu Lintas Mati / Rusak', 'foto_awal_2_202602192145_aura.png', NULL, -7.52373, 112.219, NULL, NULL, 'merah', 'normal', 1, 'neutral', NULL, 0, 0, NULL, NULL, NULL, 0, '2026-02-19 07:45:35', '2026-02-19 14:59:10', '2026-02-19 07:59:10', NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, NULL),
(29, 2, NULL, 'dfghdr bc', 'dsfrq ctawercq34', 'Jalan Berbahaya / Rawan Kecelakaan', 'foto_awal_2_202602192151_541940081_18060084341379191_2546127724466123054_n.jpg', NULL, -7.52376, 112.219, NULL, NULL, 'merah', 'normal', 1, 'neutral', NULL, 0, 0, NULL, NULL, NULL, 0, '2026-02-19 07:51:16', '2026-02-19 14:51:55', '2026-02-19 07:51:55', NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, NULL),
(30, 2, NULL, 'sampah menumpuk di selokan sepanjang 200m di daerah plosogeneng', 'asdfwqfrsadefewar 34q\n\n[Catatan Admin 20/02/2026 11:18] xcgbse tgse twsrq', 'Jalan Berbahaya / Rawan Kecelakaan', 'foto_awal_2_202602201117_cvb.png', NULL, -7.52375, 112.219, NULL, NULL, 'biru', 'normal', 1, 'neutral', NULL, 0, 0, NULL, NULL, NULL, 0, '2026-02-19 21:17:59', '2026-02-20 04:18:30', '2026-02-19 21:18:17', '2026-02-19 21:18:30', NULL, NULL, NULL, NULL, 0, NULL, 0, NULL),
(31, 2, NULL, 'jalan berlobang', 'segera diperbaiki jalan berlobang di tengah kota\n\n[Catatan Admin 20/02/2026 11:25] sedang diperbaiki', 'Jalan Berbahaya / Rawan Kecelakaan', 'foto_awal_2_202602201123_download.png', NULL, -7.52374, 112.219, NULL, NULL, 'kuning', 'normal', 1, 'neutral', NULL, 0, 0, NULL, NULL, NULL, 0, '2026-02-19 21:23:34', '2026-02-20 04:26:29', '2026-02-19 21:25:31', NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, NULL),
(32, 2, NULL, 'sampah menumpuk di selokan sepanjang 200m di daerah plosogeneng', 'fdgertarweaew', 'Jalan Berbahaya / Rawan Kecelakaan', 'foto_awal_2_202602210922_download.png', NULL, -7.52374, 112.219, NULL, NULL, 'kuning', 'normal', 1, 'neutral', NULL, 0, 0, NULL, NULL, NULL, 0, '2026-02-20 19:22:13', '2026-02-21 03:55:40', '2026-02-20 20:55:40', NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, NULL),
(34, 2, NULL, 'gggg', 'sadwr af ', 'Angkutan Umum Bermasalah', 'foto_awal_2_202602211055_cv.png', NULL, -7.52374, 112.219, NULL, NULL, 'kuning', 'normal', 1, 'neutral', NULL, 0, 0, NULL, NULL, NULL, 0, '2026-02-20 20:55:04', '2026-02-21 03:55:38', '2026-02-20 20:55:38', NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, NULL),
(35, 2, NULL, 'gggg', 'zxcwqertqw crqwr \n\n[Catatan Admin] sdgwtewr', 'APILL Error', 'foto_awal_2_202602211343_download.png', NULL, -7.5465, 112.233, NULL, NULL, 'merah', 'normal', 1, 'neutral', NULL, 0, 0, NULL, NULL, NULL, 0, '2026-02-20 23:43:37', '2026-02-22 04:37:36', '2026-02-21 21:35:57', NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, NULL),
(36, 2, NULL, 'sampah menumpuk di selokan sepanjang 200m di daerah plosogeneng', 'ZXefrawer awr w\n\n[Catatan Admin] xzf ersfser', 'APILL Error', 'foto_awal_2_202602221135_Cuplikan_layar_2026-01-13_105929.png', NULL, -7.52373, 112.219, NULL, NULL, 'biru', 'normal', 1, 'neutral', NULL, 0, 0, NULL, NULL, NULL, 0, '2026-02-21 21:35:20', '2026-02-22 04:36:18', '2026-02-21 21:35:59', '2026-02-21 21:36:18', NULL, NULL, NULL, NULL, 0, NULL, 0, NULL),
(37, 2, NULL, 'gggg', 'setaw4\n\n[Catatan Admin] fwerQWE ', 'Jalan Berbahaya / Rawan Kecelakaan', 'foto_awal_2_202602241010_Cuplikan_layar_2026-01-13_104753.png', NULL, -7.52376, 112.219, NULL, NULL, 'biru', 'normal', 1, 'neutral', NULL, 0, 0, NULL, NULL, NULL, 0, '2026-02-23 20:10:48', '2026-02-24 03:11:25', '2026-02-23 20:11:06', '2026-02-23 20:11:25', NULL, NULL, NULL, NULL, 0, NULL, 0, NULL),
(38, 12, NULL, 'sampah menumpuk disamping jalan raya', 'asfd r\n\n[Catatan Admin] sdfawrwe', 'APILL Error', 'foto_awal_12_202602241023_Cuplikan_layar_2026-01-14_111123.png', NULL, -7.52376, 112.219, NULL, NULL, 'biru', 'normal', 1, 'neutral', NULL, 0, 0, NULL, NULL, NULL, 0, '2026-02-23 20:23:35', '2026-02-24 03:24:02', '2026-02-23 20:23:53', '2026-02-23 20:24:02', NULL, NULL, NULL, NULL, 0, NULL, 0, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `nik` varchar(16) NOT NULL COMMENT 'NIK 16 digit mulai 3517',
  `no_wa` varchar(20) DEFAULT NULL,
  `kecamatan` varchar(50) DEFAULT NULL,
  `poin_warga` int(11) DEFAULT 0,
  `nama` varchar(100) NOT NULL,
  `email` varchar(120) DEFAULT NULL,
  `password_hash` varchar(255) DEFAULT NULL,
  `role` varchar(20) DEFAULT 'user',
  `foto_profil` varchar(255) DEFAULT 'default-avatar.png',
  `is_verified` tinyint(1) DEFAULT 0,
  `telepon` varchar(15) DEFAULT NULL,
  `alamat` text DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `last_login` timestamp NULL DEFAULT NULL,
  `is_online` tinyint(1) DEFAULT 0,
  `last_seen` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `nik`, `no_wa`, `kecamatan`, `poin_warga`, `nama`, `email`, `password_hash`, `role`, `foto_profil`, `is_verified`, `telepon`, `alamat`, `is_active`, `created_at`, `updated_at`, `last_login`, `is_online`, `last_seen`) VALUES
(1, '3517010101010001', NULL, NULL, 0, 'Admin Diskominfo Jombang', 'admin@diskominfo.jombang.go.id', 'scrypt:32768:8:1$iKZ0f8XL6M2zYqcl$ac5f29c54c6e935d8e8d4e4b0b0f5e3a8e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e', 'admin', 'default-avatar.png', 0, NULL, NULL, 1, '2026-02-05 02:41:55', '2026-02-05 02:41:55', NULL, 0, NULL),
(2, '3517222222222222', '085267967492', 'Bandar Kedung Mulyo', 290, 'iwan', 'riswanwan0812@gmail.com', 'scrypt:32768:8:1$jjpcBfYGSygXFNNk$d79a73247f7b88f0f6109a6a02502e88892f7f4f6ca58db0ef4658ee770715bb30934d475fef0c733ad7c327dd9e210398eb6be19591eebf3c16c9a030a9ecc2', 'user', 'user_2_Gemini_Generated_Image_e9uczte9uczte9uc_2.png', 0, NULL, NULL, 1, '2026-02-05 03:59:45', '2026-02-24 03:11:06', NULL, 0, NULL),
(4, '3517000000000001', '08123456789', 'Jombang', 0, 'Admin Demo', 'admin@demo.com', 'scrypt:32768:8:1$VG6ax2vfchsnVvcm$e883e5d7a96d299432b2753172fee0e7d427114eaa1f81b7c643a5f76d12e6e4f23501f649c2ab3ade90f0d6f193f73c31cf7601665b7810214ea7410a9c07bc', 'admin', 'user_4_Gemini_Generated_Image_ec4tosec4tosec4t.png', 0, NULL, NULL, 1, '2026-02-06 00:37:06', '2026-02-06 14:26:00', NULL, 0, NULL),
(6, '9988776655443322', '089999999999', 'Jombang', 20, 'Administrator Utama', 'admin@gmail.com', 'scrypt:32768:8:1$qJ73KNq1qENRGNmS$f2cb4d41067b5813049f5c8ca6bb1f263293129892f84cbce9355c9dc7fa00b817efcd5df5267656045dff3c2b98d82b33d5ed9ffaf15cb6ceb0ba80fd2bc236', 'admin', 'admin_6_20260220040444.jpg', 0, NULL, NULL, 1, '2026-02-06 07:29:51', '2026-02-19 21:04:44', NULL, 0, NULL),
(7, '3517234484750980', '083842827344', 'Jombang', 20, 'Ilham ', 'ilham@gmail.com', 'scrypt:32768:8:1$SsmeVpfXyO7JbpCS$a139acf8039d97b0aeae8448e05b2590143b65267e10959f76bdae1689cd828576234603b8d5a312164b0ef0c061efd6881fcfd2639d8e371b98b0e830e57928', 'user', 'default.png', 0, NULL, NULL, 1, '2026-02-11 23:49:59', '2026-02-13 02:11:41', NULL, 0, NULL),
(8, '3517453465365645', '088851422418', 'Plandaan', 0, 'dani', 'dani@gmail.com', 'scrypt:32768:8:1$lClwlVqIJKWzgxqb$356937e6b8b6d5f1c42fc90fb25e6963fb0fac860aaa1eec61f4a97d9b53e0e1899412a92bf7433fdaa3939acb37bfb7ee8beab7b72171707caae4f279da34f0', 'user', 'default.png', 0, NULL, NULL, 1, '2026-02-12 07:41:53', '2026-02-12 14:41:53', NULL, 0, '2026-02-12 14:41:53'),
(9, '3517434235465767', '085266879678', 'Plandaan', 0, 'lana', 'lana@gmail.com', 'scrypt:32768:8:1$sNSjK34nv7k73aot$90f51c01aafb8eeca0e7cb40351e9f0879420b3e5146a137bd9b5171ce312cbdbbb17dd9420a16fbe394f171f66bb768fea9989408d707eebdf280b260bf4eef', 'user', 'user_9_aura.png', 0, NULL, NULL, 1, '2026-02-12 07:43:56', '2026-02-12 14:49:23', NULL, 0, '2026-02-12 14:43:56'),
(11, '3517786285112323', '088851482418', 'Jombang', 0, 'bayu', 'bayu@gmail.com', 'scrypt:32768:8:1$J0AdK9Vd6Yp0Uexe$2edad3cf35e0b77f9f08749fe566239591532eb80e8b8c73193e82801854359d9f749aa891ffb87ffd366e7977650a300f9ca886c80fff22ece8dcbd455b0d09', 'user', 'default.png', 0, NULL, NULL, 1, '2026-02-19 04:54:08', '2026-02-21 06:27:37', NULL, 0, '2026-02-19 11:54:08'),
(12, '3517891298621321', '0896565876865', 'Jombang', 10, 'alaina', 'alaina@gmail.com', 'scrypt:32768:8:1$NLuoNlXRBuJE7lZU$97bf60cfe57e1e8f8cc3bd3f3e805a6098626d5472a58d61f56e67e1dd5ff7991342c199027e9f7c2587e9419fd19c46946c8906f228f9e8aaa6e2641466a97d', 'user', 'default.png', 0, NULL, NULL, 1, '2026-02-23 20:17:19', '2026-02-24 03:23:53', NULL, 0, '2026-02-24 03:17:19');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `alembic_version`
--
ALTER TABLE `alembic_version`
  ADD PRIMARY KEY (`version_num`);

--
-- Indexes for table `categories`
--
ALTER TABLE `categories`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`),
  ADD UNIQUE KEY `slug` (`slug`),
  ADD KEY `idx_slug` (`slug`),
  ADD KEY `idx_is_active` (`is_active`);

--
-- Indexes for table `emergency_alerts`
--
ALTER TABLE `emergency_alerts`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `interactions`
--
ALTER TABLE `interactions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `report_id` (`report_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `report_id` (`report_id`),
  ADD KEY `idx_user_read` (`user_id`,`is_read`);

--
-- Indexes for table `reports`
--
ALTER TABLE `reports`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_user_id` (`user_id`),
  ADD KEY `idx_status` (`status_warna`),
  ADD KEY `idx_kategori` (`kategori`),
  ADD KEY `idx_created_at` (`created_at`),
  ADD KEY `idx_is_public` (`is_public`),
  ADD KEY `idx_sentiment` (`sentiment`),
  ADD KEY `idx_public_status` (`is_public`,`status_warna`),
  ADD KEY `idx_user_status` (`user_id`,`status_warna`),
  ADD KEY `fk_report_category` (`category_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nik` (`nik`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `no_wa` (`no_wa`),
  ADD KEY `idx_nik` (`nik`),
  ADD KEY `idx_email` (`email`),
  ADD KEY `idx_role` (`role`),
  ADD KEY `idx_created_at` (`created_at`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `categories`
--
ALTER TABLE `categories`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=22;

--
-- AUTO_INCREMENT for table `emergency_alerts`
--
ALTER TABLE `emergency_alerts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `interactions`
--
ALTER TABLE `interactions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `notifications`
--
ALTER TABLE `notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `reports`
--
ALTER TABLE `reports`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=39;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `interactions`
--
ALTER TABLE `interactions`
  ADD CONSTRAINT `interactions_ibfk_1` FOREIGN KEY (`report_id`) REFERENCES `reports` (`id`),
  ADD CONSTRAINT `interactions_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `notifications`
--
ALTER TABLE `notifications`
  ADD CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `notifications_ibfk_2` FOREIGN KEY (`report_id`) REFERENCES `reports` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `reports`
--
ALTER TABLE `reports`
  ADD CONSTRAINT `fk_report_category` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `reports_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
