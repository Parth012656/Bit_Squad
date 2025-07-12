-- Add new columns to users table
ALTER TABLE users ADD COLUMN gender VARCHAR(20) DEFAULT NULL;
ALTER TABLE users ADD COLUMN achievements TEXT DEFAULT NULL;
ALTER TABLE users ADD COLUMN daily_tasks_completed INT DEFAULT 0;
ALTER TABLE users ADD COLUMN weekly_tasks_completed INT DEFAULT 0;
ALTER TABLE users ADD COLUMN total_rating FLOAT DEFAULT 0.0;
ALTER TABLE users ADD COLUMN total_ratings_count INT DEFAULT 0;
ALTER TABLE users ADD COLUMN badge VARCHAR(20) DEFAULT 'bronze';

-- Create notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    related_id INT DEFAULT NULL,
    related_type VARCHAR(50) DEFAULT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Add some sample achievements for existing users
UPDATE users SET 
    daily_tasks_completed = FLOOR(RAND() * 20) + 5,
    weekly_tasks_completed = FLOOR(RAND() * 10) + 2,
    total_rating = ROUND(RAND() * 2 + 3, 1),
    total_ratings_count = FLOOR(RAND() * 15) + 1
WHERE id > 1;

-- Update badges based on ratings and tasks
UPDATE users SET badge = 'gold' WHERE total_rating >= 4.5 AND daily_tasks_completed >= 50;
UPDATE users SET badge = 'silver' WHERE total_rating >= 4.0 AND daily_tasks_completed >= 25 AND badge != 'gold';
UPDATE users SET badge = 'bronze' WHERE badge IS NULL OR badge = '';

-- Add sample notifications for admin user
INSERT INTO notifications (user_id, title, message, notification_type, created_at) VALUES
(1, 'Welcome to Skillify!', 'Welcome to our community! We''re excited to have you here.', 'info', NOW()),
(1, 'Admin Panel Available', 'You have access to the admin panel to manage the platform.', 'info', NOW());

-- Add sample achievements for admin
UPDATE users SET achievements = '[
    {"title": "First Admin", "description": "Became the first administrator of Skillify", "date": "2024-01-01T00:00:00", "type": "admin"},
    {"title": "Platform Launcher", "description": "Successfully launched the Skillify platform", "date": "2024-01-01T00:00:00", "type": "achievement"}
]' WHERE id = 1; 