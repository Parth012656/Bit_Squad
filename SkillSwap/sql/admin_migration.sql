-- Admin Role Migration for Skillify
-- Run this script in MySQL Workbench to add admin functionality

-- Add admin fields to users table
ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user';
ALTER TABLE users ADD COLUMN is_banned BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN ban_reason TEXT;
ALTER TABLE users ADD COLUMN banned_at DATETIME;
ALTER TABLE users ADD COLUMN banned_by INT;
ALTER TABLE users ADD FOREIGN KEY (banned_by) REFERENCES users(id);

-- Create platform_messages table
CREATE TABLE platform_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'info',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NOT NULL,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Create moderation_actions table
CREATE TABLE moderation_actions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    action_type VARCHAR(50) NOT NULL,
    target_type VARCHAR(20) NOT NULL,
    target_id INT NOT NULL,
    reason TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    moderator_id INT NOT NULL,
    FOREIGN KEY (moderator_id) REFERENCES users(id)
);

-- Create reports table
CREATE TABLE reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    report_type VARCHAR(50) NOT NULL,
    target_type VARCHAR(20) NOT NULL,
    target_id INT NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME,
    reporter_id INT NOT NULL,
    resolved_by INT,
    FOREIGN KEY (reporter_id) REFERENCES users(id),
    FOREIGN KEY (resolved_by) REFERENCES users(id)
);

-- Create indexes for better performance
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_banned ON users(is_banned);
CREATE INDEX idx_platform_messages_active ON platform_messages(is_active);
CREATE INDEX idx_reports_status ON reports(status);
CREATE INDEX idx_reports_created ON reports(created_at);

-- Insert a default admin user (password: admin123)
-- You should change this password after first login
INSERT INTO users (name, email, password_hash, role, created_at) 
VALUES ('Admin', 'admin@skillify.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uOeK', 'admin', NOW());

-- Sample platform message
INSERT INTO platform_messages (title, message, message_type, created_by) 
VALUES ('Welcome to Skillify!', 'Welcome to our community! We''re excited to have you here. Please read our community guidelines and start sharing your skills.', 'info', 1);

-- Display success message
SELECT 'Admin migration completed successfully!' as status; 