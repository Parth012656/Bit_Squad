-- Add availability and exchange schedule tables
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
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
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
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (exchange_id) REFERENCES exchanges(id) ON DELETE CASCADE
);

-- Add indexes for better performance
CREATE INDEX idx_availabilities_user_id ON availabilities(user_id);
CREATE INDEX idx_availabilities_day ON availabilities(day_of_week);
CREATE INDEX idx_exchange_schedules_exchange_id ON exchange_schedules(exchange_id);
CREATE INDEX idx_exchange_schedules_date ON exchange_schedules(scheduled_date);

-- Insert some sample availability data for existing users (optional)
-- This creates default availability for weekdays 9 AM to 5 PM for existing users
INSERT IGNORE INTO availabilities (user_id, day_of_week, start_time, end_time, is_available)
SELECT 
    u.id,
    day_name,
    '09:00:00',
    '17:00:00',
    TRUE
FROM users u
CROSS JOIN (
    SELECT 'Monday' as day_name UNION ALL
    SELECT 'Tuesday' UNION ALL
    SELECT 'Wednesday' UNION ALL
    SELECT 'Thursday' UNION ALL
    SELECT 'Friday'
) days
WHERE u.id > 1; -- Skip admin user

-- Update the app to include today's date in the schedule template
-- This is handled in the Python code, not SQL

PRINT 'Availability tables created successfully!';
PRINT 'Users can now set their availability schedules.';
PRINT 'Exchange scheduling feature is now available.'; 