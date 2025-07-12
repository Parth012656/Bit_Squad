-- Add profile_photo and is_public to users
ALTER TABLE users ADD COLUMN profile_photo VARCHAR(255) NULL AFTER updated_at;
ALTER TABLE users ADD COLUMN is_public BOOLEAN NOT NULL DEFAULT TRUE AFTER profile_photo;

-- Add rating and feedback to exchanges
ALTER TABLE exchanges ADD COLUMN rating INT NULL AFTER completed_at;
ALTER TABLE exchanges ADD COLUMN feedback TEXT NULL AFTER rating; 