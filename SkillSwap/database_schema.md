# SkillSwap Database Schema

## Database: `skillswap_db`

### Table Structure

#### 1. `users` Table
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | Unique user identifier |
| `name` | VARCHAR(100) | NOT NULL | User's full name |
| `email` | VARCHAR(120) | UNIQUE, NOT NULL | User's email address |
| `password_hash` | VARCHAR(255) | NOT NULL | Hashed password |
| `bio` | TEXT | NULL | User's biography |
| `location` | VARCHAR(100) | NULL | User's location |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Account creation date |
| `updated_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE | Last update date |

**Indexes:**
- `idx_email` (email)
- `idx_created_at` (created_at)

#### 2. `skills` Table
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | Unique skill identifier |
| `name` | VARCHAR(100) | NOT NULL | Skill name |
| `description` | TEXT | NOT NULL | Skill description |
| `category` | VARCHAR(50) | NOT NULL | Skill category |
| `level` | VARCHAR(20) | DEFAULT 'Beginner' | Skill level |
| `is_available` | BOOLEAN | DEFAULT TRUE | Availability status |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Skill creation date |
| `updated_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE | Last update date |
| `user_id` | INT | FOREIGN KEY → users(id) | Owner of the skill |

**Indexes:**
- `idx_category` (category)
- `idx_level` (level)
- `idx_is_available` (is_available)
- `idx_user_id` (user_id)
- `idx_created_at` (created_at)

#### 3. `exchanges` Table
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | Unique exchange identifier |
| `status` | VARCHAR(20) | DEFAULT 'Pending' | Exchange status |
| `message` | TEXT | NULL | Exchange message |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Exchange creation date |
| `updated_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE | Last update date |
| `completed_at` | DATETIME | NULL | Completion date |
| `offering_user_id` | INT | FOREIGN KEY → users(id) | User offering a skill |
| `requesting_user_id` | INT | FOREIGN KEY → users(id) | User requesting a skill |
| `offered_skill_id` | INT | FOREIGN KEY → skills(id) | Skill being offered |
| `requested_skill_id` | INT | FOREIGN KEY → skills(id) | Skill being requested |

**Indexes:**
- `idx_status` (status)
- `idx_offering_user_id` (offering_user_id)
- `idx_requesting_user_id` (requesting_user_id)
- `idx_created_at` (created_at)
- `idx_completed_at` (completed_at)

### Relationships

```
users (1) ←→ (many) skills
users (1) ←→ (many) exchanges (as offering_user)
users (1) ←→ (many) exchanges (as requesting_user)
skills (1) ←→ (many) exchanges (as offered_skill)
skills (1) ←→ (many) exchanges (as requested_skill)
```

### Views

#### 1. `skill_exchanges` View
Provides a comprehensive view of all exchanges with user and skill details.

**Columns:**
- `exchange_id` - Exchange ID
- `status` - Exchange status
- `message` - Exchange message
- `created_at` - Creation date
- `completed_at` - Completion date
- `offering_user_name` - Name of user offering skill
- `requesting_user_name` - Name of user requesting skill
- `offered_skill_name` - Name of skill being offered
- `requested_skill_name` - Name of skill being requested
- `offered_skill_category` - Category of offered skill
- `requested_skill_category` - Category of requested skill

#### 2. `user_skills` View
Provides skills with user information for easier querying.

**Columns:**
- `id` - Skill ID
- `name` - Skill name
- `description` - Skill description
- `category` - Skill category
- `level` - Skill level
- `is_available` - Availability status
- `created_at` - Creation date
- `user_id` - User ID
- `user_name` - User name
- `user_email` - User email
- `user_location` - User location

### Data Types and Constraints

#### Enums and Valid Values

**Skill Levels:**
- Beginner
- Intermediate
- Advanced
- Expert

**Skill Categories:**
- Technology
- Language
- Arts
- Sports
- Cooking
- Music
- Other

**Exchange Status:**
- Pending
- Accepted
- Completed
- Cancelled

### Sample Data

The database includes sample data for testing:

**Users (5):**
- John Doe (Software Developer)
- Jane Smith (Graphic Designer)
- Mike Johnson (Chef)
- Sarah Wilson (Spanish Teacher)
- David Brown (Guitar Instructor)

**Skills (10):**
- Python Programming (Technology, Advanced)
- Web Development (Technology, Expert)
- Graphic Design (Arts, Expert)
- Digital Illustration (Arts, Advanced)
- Italian Cooking (Cooking, Expert)
- Baking & Pastry (Cooking, Intermediate)
- Spanish Language (Language, Advanced)
- French Language (Language, Intermediate)
- Guitar Lessons (Music, Expert)
- Piano Basics (Music, Beginner)

**Exchanges (4):**
- Pending exchanges between users
- Completed exchanges with feedback
- Various skill combinations

### Database Configuration

**Engine:** InnoDB
**Character Set:** utf8mb4
**Collation:** utf8mb4_unicode_ci

### Security Considerations

1. **Password Hashing:** All passwords are hashed using bcrypt
2. **Foreign Key Constraints:** CASCADE on delete for data integrity
3. **Indexes:** Optimized for common queries
4. **Data Validation:** Application-level validation required

### Performance Optimizations

1. **Indexes:** Strategic indexes on frequently queried columns
2. **Views:** Pre-computed joins for complex queries
3. **Partitioning:** Consider partitioning for large datasets
4. **Caching:** Application-level caching recommended

### Backup and Maintenance

**Recommended Backup Schedule:**
- Daily incremental backups
- Weekly full backups
- Monthly archive backups

**Maintenance Tasks:**
- Regular index optimization
- Data integrity checks
- Orphaned record cleanup
- Performance monitoring 