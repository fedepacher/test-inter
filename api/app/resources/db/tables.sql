DROP DATABASE IF EXISTS db_ti_dev;
CREATE DATABASE db_ti_dev;
USE db_ti_dev;

-- ===========================================================
-- PROFESSIONAL ROLES
-- ===========================================================
CREATE TABLE professional_roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(30) NOT NULL UNIQUE,
    spanish_name TEXT,
    english_name TEXT,
    portuguese_name TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by INT NULL,
    deleted_by INT NULL
);

-- ===========================================================
-- COUNTRIES
-- ===========================================================
CREATE TABLE countries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    spanish_name TEXT,
    english_name TEXT,
    portuguese_name TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ===========================================================
-- GENDERS
-- ===========================================================
CREATE TABLE genders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(15) NOT NULL UNIQUE,
    spanish_name TEXT,
    english_name TEXT,
    portuguese_name TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ===========================================================
-- USERS (partial, no circular FKs yet)
-- ===========================================================
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(200),
    email VARCHAR(50) NOT NULL UNIQUE,
    prof_role_id INT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at DATETIME NULL,
    active BOOLEAN DEFAULT TRUE,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    profile_id INT NULL
);

-- ===========================================================
-- PROFILES
-- ===========================================================
CREATE TABLE profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(50),
    name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    document_number VARCHAR(50),
    contact_number VARCHAR(15),
    birthdate DATE,
    gender_id INT NULL,
    country_id INT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at DATETIME NULL,
    created_by INT NULL,
    updated_by INT NULL,
    deleted_by INT NULL,
    CONSTRAINT fk_profiles_gender FOREIGN KEY (gender_id) REFERENCES genders(id),
    CONSTRAINT fk_profiles_country FOREIGN KEY (country_id) REFERENCES countries(id)
);

-- ===========================================================
-- INSTITUTIONS
-- ===========================================================
CREATE TABLE institutions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) DEFAULT 'ND',
    active BOOLEAN NOT NULL DEFAULT TRUE,
    status VARCHAR(20),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at DATETIME NULL,
    created_by INT NULL
);

-- ===========================================================
-- ATHLETES
-- ===========================================================
CREATE TABLE athletes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    institution_id INT NOT NULL,
    profile_id INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at DATETIME NULL,
    updated_by_id INT NULL,
    created_by_id INT NULL,
    deleted_by_id INT NULL,
    active BOOLEAN DEFAULT TRUE,
    status VARCHAR(20),
    CONSTRAINT fk_athletes_institution FOREIGN KEY (institution_id) REFERENCES institutions(id),
    CONSTRAINT fk_athletes_profile FOREIGN KEY (profile_id) REFERENCES profiles(id)
);

-- ===========================================================
-- ADD FOREIGN KEYS AFTER ALL TABLES EXIST
-- ===========================================================

ALTER TABLE professional_roles
  ADD CONSTRAINT fk_prof_roles_updated_by FOREIGN KEY (updated_by) REFERENCES users(id),
  ADD CONSTRAINT fk_prof_roles_deleted_by FOREIGN KEY (deleted_by) REFERENCES users(id);

ALTER TABLE profiles
  ADD CONSTRAINT fk_profiles_created_by FOREIGN KEY (created_by) REFERENCES users(id),
  ADD CONSTRAINT fk_profiles_updated_by FOREIGN KEY (updated_by) REFERENCES users(id),
  ADD CONSTRAINT fk_profiles_deleted_by FOREIGN KEY (deleted_by) REFERENCES users(id);

ALTER TABLE institutions
  ADD CONSTRAINT fk_institutions_created_by FOREIGN KEY (created_by) REFERENCES users(id);

ALTER TABLE athletes
  ADD CONSTRAINT fk_athletes_created_by FOREIGN KEY (created_by_id) REFERENCES users(id),
  ADD CONSTRAINT fk_athletes_updated_by FOREIGN KEY (updated_by_id) REFERENCES users(id),
  ADD CONSTRAINT fk_athletes_deleted_by FOREIGN KEY (deleted_by_id) REFERENCES users(id);

ALTER TABLE users
  ADD CONSTRAINT fk_users_prof_role FOREIGN KEY (prof_role_id) REFERENCES professional_roles(id),
  ADD CONSTRAINT fk_users_profile FOREIGN KEY (profile_id) REFERENCES profiles(id);
