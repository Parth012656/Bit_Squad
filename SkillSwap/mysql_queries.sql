-- SkillSwap MySQL Workbench Queries
-- Useful queries for testing and managing the database

USE skillswap_db;

-- =============================================
-- BASIC QUERIES
-- =============================================

-- View all users
SELECT id, name, email, location, created_at FROM users;

-- View all skills with user information
SELECT 
    s.id,
    s.name as skill_name,
    s.category,
    s.level,
    s.is_available,
    u.name as user_name,
    u.location
FROM skills s
JOIN users u ON s.user_id = u.id
ORDER BY s.created_at DESC;

-- View all exchanges with details
SELECT 
    e.id,
    e.status,
    e.created_at,
    offering_user.name as offering_user,
    requesting_user.name as requesting_user,
    offered_skill.name as offered_skill,
    requested_skill.name as requested_skill
FROM exchanges e
JOIN users offering_user ON e.offering_user_id = offering_user.id
JOIN users requesting_user ON e.requesting_user_id = requesting_user.id
JOIN skills offered_skill ON e.offered_skill_id = offered_skill.id
JOIN skills requested_skill ON e.requested_skill_id = requested_skill.id
ORDER BY e.created_at DESC;

-- =============================================
-- ANALYTICS QUERIES
-- =============================================

-- Count skills by category
SELECT 
    category,
    COUNT(*) as skill_count,
    AVG(CASE WHEN level = 'Beginner' THEN 1 WHEN level = 'Intermediate' THEN 2 WHEN level = 'Advanced' THEN 3 WHEN level = 'Expert' THEN 4 END) as avg_level
FROM skills
GROUP BY category
ORDER BY skill_count DESC;

-- Count skills by level
SELECT 
    level,
    COUNT(*) as count
FROM skills
GROUP BY level
ORDER BY 
    CASE level 
        WHEN 'Beginner' THEN 1 
        WHEN 'Intermediate' THEN 2 
        WHEN 'Advanced' THEN 3 
        WHEN 'Expert' THEN 4 
    END;

-- User activity (skills and exchanges)
SELECT 
    u.name,
    COUNT(DISTINCT s.id) as skills_offered,
    COUNT(DISTINCT e.id) as exchanges_involved
FROM users u
LEFT JOIN skills s ON u.id = s.user_id
LEFT JOIN exchanges e ON u.id IN (e.offering_user_id, e.requesting_user_id)
GROUP BY u.id, u.name
ORDER BY skills_offered DESC, exchanges_involved DESC;

-- Exchange status summary
SELECT 
    status,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM exchanges), 2) as percentage
FROM exchanges
GROUP BY status;

-- =============================================
-- SEARCH AND FILTER QUERIES
-- =============================================

-- Search skills by keyword
SELECT 
    s.name,
    s.description,
    s.category,
    s.level,
    u.name as user_name
FROM skills s
JOIN users u ON s.user_id = u.id
WHERE s.name LIKE '%python%' OR s.description LIKE '%python%'
ORDER BY s.created_at DESC;

-- Filter skills by category and level
SELECT 
    s.name,
    s.description,
    s.level,
    u.name as user_name,
    u.location
FROM skills s
JOIN users u ON s.user_id = u.id
WHERE s.category = 'Technology' AND s.level IN ('Advanced', 'Expert')
ORDER BY s.created_at DESC;

-- Find available skills (not in active exchanges)
SELECT 
    s.name,
    s.category,
    s.level,
    u.name as user_name
FROM skills s
JOIN users u ON s.user_id = u.id
WHERE s.is_available = TRUE
AND s.id NOT IN (
    SELECT DISTINCT offered_skill_id 
    FROM exchanges 
    WHERE status IN ('Pending', 'Accepted')
)
ORDER BY s.created_at DESC;

-- =============================================
-- EXCHANGE ANALYSIS QUERIES
-- =============================================

-- Recent exchanges
SELECT 
    e.id,
    e.status,
    e.created_at,
    CONCAT(offering_user.name, ' → ', requesting_user.name) as exchange_partners,
    CONCAT(offered_skill.name, ' ↔ ', requested_skill.name) as skills_exchanged
FROM exchanges e
JOIN users offering_user ON e.offering_user_id = offering_user.id
JOIN users requesting_user ON e.requesting_user_id = requesting_user.id
JOIN skills offered_skill ON e.offered_skill_id = offered_skill.id
JOIN skills requested_skill ON e.requested_skill_id = requested_skill.id
ORDER BY e.created_at DESC
LIMIT 10;

-- Successful exchanges (completed)
SELECT 
    e.id,
    e.completed_at,
    offering_user.name as offering_user,
    requesting_user.name as requesting_user,
    offered_skill.name as offered_skill,
    requested_skill.name as requested_skill,
    DATEDIFF(e.completed_at, e.created_at) as days_to_complete
FROM exchanges e
JOIN users offering_user ON e.offering_user_id = offering_user.id
JOIN users requesting_user ON e.requesting_user_id = requesting_user.id
JOIN skills offered_skill ON e.offered_skill_id = offered_skill.id
JOIN skills requested_skill ON e.requested_skill_id = requested_skill.id
WHERE e.status = 'Completed'
ORDER BY e.completed_at DESC;

-- =============================================
-- USER PROFILE QUERIES
-- =============================================

-- Get user profile with skills and exchange history
SELECT 
    u.id,
    u.name,
    u.email,
    u.bio,
    u.location,
    u.created_at,
    COUNT(DISTINCT s.id) as skills_count,
    COUNT(DISTINCT e.id) as exchanges_count
FROM users u
LEFT JOIN skills s ON u.id = s.user_id
LEFT JOIN exchanges e ON u.id IN (e.offering_user_id, e.requesting_user_id)
WHERE u.id = 1  -- Replace with user ID
GROUP BY u.id;

-- Get user's skills
SELECT 
    s.name,
    s.description,
    s.category,
    s.level,
    s.is_available,
    s.created_at
FROM skills s
WHERE s.user_id = 1  -- Replace with user ID
ORDER BY s.created_at DESC;

-- Get user's exchange history
SELECT 
    e.id,
    e.status,
    e.created_at,
    CASE 
        WHEN e.offering_user_id = 1 THEN 'Offering'
        ELSE 'Requesting'
    END as role,
    CASE 
        WHEN e.offering_user_id = 1 THEN requesting_user.name
        ELSE offering_user.name
    END as other_user,
    CASE 
        WHEN e.offering_user_id = 1 THEN offered_skill.name
        ELSE requested_skill.name
    END as my_skill,
    CASE 
        WHEN e.offering_user_id = 1 THEN requested_skill.name
        ELSE offered_skill.name
    END as their_skill
FROM exchanges e
JOIN users offering_user ON e.offering_user_id = offering_user.id
JOIN users requesting_user ON e.requesting_user_id = requesting_user.id
JOIN skills offered_skill ON e.offered_skill_id = offered_skill.id
JOIN skills requested_skill ON e.requested_skill_id = requested_skill.id
WHERE e.offering_user_id = 1 OR e.requesting_user_id = 1  -- Replace with user ID
ORDER BY e.created_at DESC;

-- =============================================
-- MAINTENANCE QUERIES
-- =============================================

-- Find orphaned skills (user deleted but skills remain)
SELECT s.* FROM skills s
LEFT JOIN users u ON s.user_id = u.id
WHERE u.id IS NULL;

-- Find orphaned exchanges (user or skill deleted)
SELECT e.* FROM exchanges e
LEFT JOIN users offering_user ON e.offering_user_id = offering_user.id
LEFT JOIN users requesting_user ON e.requesting_user_id = requesting_user.id
LEFT JOIN skills offered_skill ON e.offered_skill_id = offered_skill.id
LEFT JOIN skills requested_skill ON e.requested_skill_id = requested_skill.id
WHERE offering_user.id IS NULL OR requesting_user.id IS NULL 
   OR offered_skill.id IS NULL OR requested_skill.id IS NULL;

-- Update skills availability based on active exchanges
UPDATE skills s
SET is_available = FALSE
WHERE s.id IN (
    SELECT DISTINCT offered_skill_id 
    FROM exchanges 
    WHERE status IN ('Pending', 'Accepted')
);

-- Reset skills availability
UPDATE skills SET is_available = TRUE;

-- =============================================
-- SAMPLE DATA INSERTION
-- =============================================

-- Add more sample users
INSERT INTO users (name, email, password_hash, bio, location) VALUES
('Emma Davis', 'emma@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8JZqKqG', 'Yoga instructor and wellness coach', 'Portland, OR'),
('Alex Chen', 'alex@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8JZqKqG', 'Photography enthusiast and travel blogger', 'Seattle, WA'),
('Maria Garcia', 'maria@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8JZqKqG', 'Dance instructor specializing in salsa and bachata', 'San Diego, CA');

-- Add more sample skills
INSERT INTO skills (name, description, category, level, user_id) VALUES
('Yoga & Meditation', 'Learn yoga poses, breathing techniques, and meditation practices for wellness', 'Sports', 'Advanced', 6),
('Photography', 'Master digital photography, composition, and post-processing techniques', 'Arts', 'Intermediate', 7),
('Salsa Dancing', 'Learn salsa dance steps, rhythm, and partner work for social dancing', 'Sports', 'Expert', 8),
('JavaScript Programming', 'Learn JavaScript fundamentals, ES6+, and modern web development', 'Technology', 'Intermediate', 1),
('Data Science', 'Introduction to data analysis, machine learning, and statistical modeling', 'Technology', 'Advanced', 1);

-- Add more sample exchanges
INSERT INTO exchanges (status, message, offering_user_id, requesting_user_id, offered_skill_id, requested_skill_id) VALUES
('Pending', 'I would love to learn photography! I can teach you web development in exchange.', 1, 7, 2, 12),
('Accepted', 'Great! I can teach you salsa dancing and you can help me with JavaScript programming.', 8, 1, 13, 14),
('Completed', 'Amazing yoga sessions! The meditation workshop was very helpful.', 6, 2, 11, 3); 