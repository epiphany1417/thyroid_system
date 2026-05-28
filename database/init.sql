CREATE DATABASE IF NOT EXISTS thyroid_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE thyroid_system;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('doctor', 'patient', 'admin') NOT NULL DEFAULT 'patient',
    real_name VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active TINYINT(1) DEFAULT 1
);

-- 患者信息表
CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    gender ENUM('male', 'female') DEFAULT NULL,
    age INT DEFAULT NULL,
    medical_history TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 诊断记录表
CREATE TABLE IF NOT EXISTS diagnoses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT DEFAULT NULL,
    image_path VARCHAR(500) NOT NULL,
    result_image_path VARCHAR(500),
    ai_result ENUM('benign', 'malignant') DEFAULT NULL,
    ai_confidence FLOAT DEFAULT NULL,
    bbox_x INT DEFAULT NULL,
    bbox_y INT DEFAULT NULL,
    bbox_w INT DEFAULT NULL,
    bbox_h INT DEFAULT NULL,
    doctor_opinion TEXT,
    risk_level ENUM('low', 'medium', 'high') DEFAULT NULL,
    original_ai_result ENUM('benign', 'malignant') DEFAULT NULL,
    original_risk_level ENUM('low', 'medium', 'high') DEFAULT NULL,
    ai_opinion TEXT DEFAULT NULL,
    status ENUM('pending', 'completed', 'reviewed') DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 操作日志表
CREATE TABLE IF NOT EXISTS operation_logs (

-- 验证码表（忘记密码）
CREATE TABLE IF NOT EXISTS verification_codes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    contact VARCHAR(100) NOT NULL,
    code VARCHAR(6) NOT NULL,
    expires_at DATETIME NOT NULL,
    used TINYINT(1) DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 操作日志表
CREATE TABLE IF NOT EXISTS operation_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(100) NOT NULL,
    detail TEXT,
    ip_address VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 插入默认管理员账户 (密码: admin123)
INSERT INTO users (username, password_hash, role, real_name) VALUES
('admin', 'pbkdf2:sha256:600000$default$admin123hash', 'admin', '系统管理员');
