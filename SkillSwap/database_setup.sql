-- SkillSwap Database Setup Script
-- Run this script in MySQL Workbench to create the database and tables

-- Create the database
CREATE DATABASE IF NOT EXISTS skillswap_db;
USE skillswap_db;

-- Create users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    bio TEXT,
    location VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create skills table
CREATE TABLE skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    level VARCHAR(20) DEFAULT 'Beginner',
    is_available BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_category (category),
    INDEX idx_level (level),
    INDEX idx_is_available (is_available),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create exchanges table
CREATE TABLE exchanges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    status VARCHAR(20) DEFAULT 'Pending',
    message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    completed_at DATETIME NULL,
    offering_user_id INT NOT NULL,
    requesting_user_id INT NOT NULL,
    offered_skill_id INT NOT NULL,
    requested_skill_id INT NOT NULL,
    FOREIGN KEY (offering_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (requesting_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (offered_skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    FOREIGN KEY (requested_skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    INDEX idx_status (status),
    INDEX idx_offering_user_id (offering_user_id),
    INDEX idx_requesting_user_id (requesting_user_id),
    INDEX idx_created_at (created_at),
    INDEX idx_completed_at (completed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert sample data for testing
INSERT INTO users (name, email, password_hash, bio, location) VALUES
('John Doe', 'john@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8JZqKqG', 'Software developer with 5 years of experience', 'New York, NY'),
('Jane Smith', 'jane@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8JZqKqG', 'Graphic designer and illustrator', 'Los Angeles, CA'),
('Mike Johnson', 'mike@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8JZqKqG', 'Chef with passion for international cuisine', 'Chicago, IL'),
('Sarah Wilson', 'sarah@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8JZqKqG', 'Spanish teacher and language enthusiast', 'Miami, FL'),
('David Brown', 'david@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8JZqKqG', 'Guitar instructor and music producer', 'Austin, TX');

-- Insert sample skills
INSERT INTO skills (name, description, category, level, user_id) VALUES
('Python Programming', 'Learn Python from basics to advanced concepts including web development with Flask and Django', 'Technology', 'Advanced', 1),
('Web Development', 'Full-stack web development using HTML, CSS, JavaScript, and modern frameworks', 'Technology', 'Expert', 1),
('Graphic Design', 'Create stunning visuals using Adobe Creative Suite and digital design principles', 'Arts', 'Expert', 2),
('Digital Illustration', 'Learn digital art and illustration techniques using Procreate and Photoshop', 'Arts', 'Advanced', 2),
('Italian Cooking', 'Master authentic Italian cuisine including pasta, pizza, and traditional dishes', 'Cooking', 'Expert', 3),
('Baking & Pastry', 'Learn the art of baking bread, pastries, and desserts from scratch', 'Cooking', 'Intermediate', 3),
('Spanish Language', 'Learn Spanish conversation, grammar, and cultural context', 'Language', 'Advanced', 4),
('French Language', 'Beginner to intermediate French with focus on conversation', 'Language', 'Intermediate', 4),
('Guitar Lessons', 'Learn guitar from basic chords to advanced techniques and music theory', 'Music', 'Expert', 5),
('Piano Basics', 'Introduction to piano playing and music reading', 'Music', 'Beginner', 5);

-- Insert sample exchanges
INSERT INTO exchanges (status, message, offering_user_id, requesting_user_id, offered_skill_id, requested_skill_id) VALUES
('Pending', 'I would love to learn graphic design! I can teach you Python programming in exchange.', 1, 2, 1, 3),
('Accepted', 'Great exchange! I can teach you Spanish and you can help me with web development.', 4, 1, 7, 2),
('Completed', 'Excellent cooking lessons! The Italian cuisine workshop was amazing.', 3, 1, 5, 1),
('Pending', 'I would like to learn guitar. I can offer Spanish language lessons in return.', 4, 5, 7, 9);

-- Create views for easier querying
CREATE VIEW skill_exchanges AS
SELECT 
    e.id as exchange_id,
    e.status,
    e.message,
    e.created_at,
    e.completed_at,
    offering_user.name as offering_user_name,
    requesting_user.name as requesting_user_name,
    offered_skill.name as offered_skill_name,
    requested_skill.name as requested_skill_name,
    offered_skill.category as offered_skill_category,
    requested_skill.category as requested_skill_category
FROM exchanges e
JOIN users offering_user ON e.offering_user_id = offering_user.id
JOIN users requesting_user ON e.requesting_user_id = requesting_user.id
JOIN skills offered_skill ON e.offered_skill_id = offered_skill.id
JOIN skills requested_skill ON e.requested_skill_id = requested_skill.id;

-- Create view for user skills with user info
CREATE VIEW user_skills AS
SELECT 
    s.id,
    s.name,
    s.description,
    s.category,
    s.level,
    s.is_available,
    s.created_at,
    u.id as user_id,
    u.name as user_name,
    u.email as user_email,
    u.location as user_location
FROM skills s
JOIN users u ON s.user_id = u.id;

-- Show table structure
DESCRIBE users;
DESCRIBE skills;
DESCRIBE exchanges;

-- Show sample data
SELECT 'Users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'Skills' as table_name, COUNT(*) as count FROM skills
UNION ALL
SELECT 'Exchanges' as table_name, COUNT(*) as count FROM exchanges; 