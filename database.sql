-- ============================================================================
-- LaporPak Jombang Diskominfo - Database Schema
-- MySQL 8.0+ | Port 3307
-- Database: laporpak_jombang_diskominfo
-- ============================================================================

-- Create Database
CREATE DATABASE IF NOT EXISTS laporpak_jombang_diskominfo 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE laporpak_jombang_diskominfo;

-- ============================================================================
-- Table: users
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nik VARCHAR(16) NOT NULL UNIQUE COMMENT 'NIK 16 digit mulai 3517',
    nama VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user' COMMENT 'user | admin',
    foto_profil VARCHAR(255) DEFAULT 'default-avatar.png',
    telepon VARCHAR(15),
    alamat TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    
    INDEX idx_nik (nik),
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Table: reports
-- ============================================================================
CREATE TABLE IF NOT EXISTS reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    judul VARCHAR(200) NOT NULL,
    deskripsi TEXT NOT NULL,
    kategori VARCHAR(50) NOT NULL,
    foto VARCHAR(255),
    latitude FLOAT,
    longitude FLOAT,
    alamat_lokasi VARCHAR(255),
    hashtag VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending' COMMENT 'pending | approved | proses | selesai | rejected',
    sentiment VARCHAR(20) COMMENT 'positive | neutral | negative',
    sentiment_score FLOAT,
    is_incognito BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT FALSE,
    bukti_perbaikan VARCHAR(255),
    catatan_admin TEXT,
    views_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    approved_at TIMESTAMP NULL,
    resolved_at TIMESTAMP NULL,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_kategori (kategori),
    INDEX idx_created_at (created_at),
    INDEX idx_is_public (is_public),
    INDEX idx_sentiment (sentiment)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Table: interactions
-- ============================================================================
CREATE TABLE IF NOT EXISTS interactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    report_id INT NOT NULL,
    type VARCHAR(20) NOT NULL COMMENT 'support | comment',
    content TEXT COMMENT 'For comments',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE,
    
    INDEX idx_user_id (user_id),
    INDEX idx_report_id (report_id),
    INDEX idx_type (type),
    INDEX idx_created_at (created_at),
    INDEX idx_user_report_type (user_id, report_id, type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Table: notifications
-- ============================================================================
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    report_id INT,
    type VARCHAR(50) NOT NULL COMMENT 'status_update | comment | support',
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE SET NULL,
    
    INDEX idx_user_id (user_id),
    INDEX idx_is_read (is_read),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Table: analytics
-- ============================================================================
CREATE TABLE IF NOT EXISTS analytics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    total_reports INT DEFAULT 0,
    pending_reports INT DEFAULT 0,
    approved_reports INT DEFAULT 0,
    proses_reports INT DEFAULT 0,
    selesai_reports INT DEFAULT 0,
    rejected_reports INT DEFAULT 0,
    total_users INT DEFAULT 0,
    active_users INT DEFAULT 0,
    total_interactions INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_date (date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Table: categories
-- ============================================================================
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    slug VARCHAR(50) NOT NULL UNIQUE,
    icon VARCHAR(50) DEFAULT 'bi-chat-dots',
    description VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_slug (slug),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Insert Default Admin
-- Password: Admin@Jombang2024
-- ============================================================================
INSERT INTO users (nik, nama, email, password_hash, role, is_active) VALUES
('3517010101010001', 'Admin Diskominfo Jombang', 'admin@diskominfo.jombang.go.id', 
 'scrypt:32768:8:1$iKZ0f8XL6M2zYqcl$ac5f29c54c6e935d8e8d4e4b0b0f5e3a8e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e', 
 'admin', TRUE)
ON DUPLICATE KEY UPDATE email=email;

-- ============================================================================
-- Insert Default Categories
-- ============================================================================
INSERT INTO categories (name, slug, icon, description) VALUES
('Infrastruktur', 'infrastruktur', 'bi-buildings', 'Jalan, jembatan, gedung, dan fasilitas umum'),
('Kebersihan', 'kebersihan', 'bi-trash', 'Sampah, drainase, dan kebersihan lingkungan'),
('Keamanan', 'keamanan', 'bi-shield-check', 'Keamanan dan ketertiban masyarakat'),
('Kesehatan', 'kesehatan', 'bi-hospital', 'Fasilitas kesehatan dan pelayanan medis'),
('Pendidikan', 'pendidikan', 'bi-book', 'Sekolah dan fasilitas pendidikan'),
('Lingkungan', 'lingkungan', 'bi-tree', 'Pencemaran dan kerusakan lingkungan'),
('Transportasi', 'transportasi', 'bi-car-front', 'Transportasi umum dan lalu lintas'),
('Sosial', 'sosial', 'bi-people', 'Masalah sosial dan kemasyarakatan'),
('Lainnya', 'lainnya', 'bi-chat-dots', 'Kategori lain yang tidak terdaftar')
ON DUPLICATE KEY UPDATE name=name;

-- ============================================================================
-- Sample Data (Optional - Uncomment to use)
-- ============================================================================

-- Sample User
-- INSERT INTO users (nik, nama, email, password_hash, role) VALUES
-- ('3517020202020002', 'Budi Santoso', 'budi@example.com', 
--  'scrypt:32768:8:1$example$hash', 'user');

-- Sample Report
-- INSERT INTO reports (user_id, judul, deskripsi, kategori, alamat_lokasi, status) VALUES
-- (2, 'Jalan Rusak di Jl. Merdeka', 'Jalan berlubang besar di depan SD Negeri 1', 
--  'infrastruktur', 'Jl. Merdeka No. 10, Jombang', 'pending');

-- ============================================================================
-- Indexes for Performance
-- ============================================================================

-- Additional composite indexes for common queries
ALTER TABLE reports ADD INDEX idx_public_status (is_public, status);
ALTER TABLE reports ADD INDEX idx_user_status (user_id, status);
ALTER TABLE notifications ADD INDEX idx_user_read (user_id, is_read);

-- ============================================================================
-- End of Schema
-- ============================================================================

-- Show table status
SELECT 
    TABLE_NAME, 
    TABLE_ROWS, 
    AVG_ROW_LENGTH,
    DATA_LENGTH,
    INDEX_LENGTH,
    CREATE_TIME
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'laporpak_jombang_diskominfo'
ORDER BY TABLE_NAME;

-- Show database info
SELECT 
    'Database Created Successfully!' as Status,
    'laporpak_jombang_diskominfo' as Database_Name,
    'Port 3307' as Port,
    'utf8mb4_unicode_ci' as Collation;
