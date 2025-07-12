-- Add availability and exchange schedule tables (simplified version)
-- Run this script to add the missing availability feature

-- Create availabilities table
CREATE TABLE IF NOT EXISTS availabilities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    day_of_week VARCHAR(10) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user_day (user_id, day_of_week)
);

-- Create exchange_schedules table
CREATE TABLE IF NOT EXISTS exchange_schedules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    exchange_id INT NOT NULL,
    scheduled_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    location VARCHAR(200),
    meeting_type VARCHAR(20) DEFAULT 'in_person',
    meeting_link VARCHAR(500),
    notes TEXT,
    status VARCHAR(20) DEFAULT 'scheduled',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Add indexes for better performance
CREATE INDEX idx_availabilities_user_id ON availabilities(user_id);
CREATE INDEX idx_availabilities_day ON availabilities(day_of_week);
CREATE INDEX idx_exchange_schedules_exchange_id ON exchange_schedules(exchange_id);
CREATE INDEX idx_exchange_schedules_date ON exchange_schedules(scheduled_date);

SELECT 'Availability tables created successfully!' as message;
SELECT 'Users can now set their availability schedules.' as info;
SELECT 'Exchange scheduling feature is now available.' as info; 