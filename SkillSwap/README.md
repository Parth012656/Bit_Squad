# SkillSwap

A web application for skill exchange between users. Connect with others, share your skills, and learn something new through mutual skill exchanges.

## Features

- **User Authentication**: Secure login and registration system
- **Skill Management**: Add, edit, and manage your skills
- **Skill Browsing**: Browse available skills with filtering and search
- **Skill Exchange**: Propose and manage skill exchanges
- **User Dashboard**: Personal dashboard to manage your profile and skills
- **Responsive Design**: Modern, mobile-friendly interface

## Technology Stack

### Backend
- **Python Flask**: Web framework
- **Flask-SQLAlchemy**: Database ORM
- **Flask-Login**: User authentication
- **MySQL**: Database
- **Werkzeug**: Security utilities

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with Bootstrap 5
- **JavaScript**: Interactive functionality
- **Bootstrap 5**: Responsive UI framework
- **Font Awesome**: Icons

## Project Structure

```
SkillSwap/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── static/               # Static files
│   ├── css/
│   │   └── style.css     # Custom styles
│   ├── js/
│   │   └── main.js       # JavaScript functionality
│   └── images/           # Image assets
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── dashboard.html    # User dashboard
│   └── skills.html       # Skills browsing page
├── models/               # Database models
│   ├── user.py           # User model
│   ├── skill.py          # Skill model
│   └── exchange.py       # Exchange model
├── controllers/          # Business logic (future)
├── config/              # Configuration files (future)
└── migrations/          # Database migrations (future)
```

## Installation

### Prerequisites
- Python 3.8 or higher
- MySQL 8.0 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SkillSwap
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up MySQL database**
   ```sql
   CREATE DATABASE skillswap_db;
   CREATE USER 'skillswap_user'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON skillswap_db.* TO 'skillswap_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

5. **Configure environment variables**
   ```bash
   # Copy the environment template
   cp env_template.txt .env
   
   # Edit .env file with your database credentials
   nano .env  # or use your preferred editor
   ```

6. **Set up the database**
   ```bash
   # Run the database setup script
   python setup_database.py
   
   # Or manually run the MySQL script
   mysql -u skillswap_user -p skillswap_db < database_setup.sql
   ```

7. **Run the application**
   ```bash
   python app.py
   ```

8. **Access the application**
   - Open your browser and go to `http://localhost:5000`

## Configuration

### Database Configuration
Update the database URI in `app.py`:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/skillswap_db'
```

### Environment Variables
Create a `.env` file for sensitive configuration:
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=mysql://username:password@localhost/skillswap_db
FLASK_ENV=development
```

## Usage

### For Users
1. **Register**: Create a new account with your email and password
2. **Add Skills**: Add skills you can teach to others
3. **Browse Skills**: Find skills you want to learn
4. **Propose Exchanges**: Request skill exchanges with other users
5. **Manage Exchanges**: Accept, reject, or complete exchanges

### For Developers
- The application uses Flask's development server by default
- For production, use a WSGI server like Gunicorn
- Database migrations should be handled with Flask-Migrate (to be added)

## API Endpoints

### Authentication
- `POST /login` - User login
- `POST /register` - User registration
- `GET /logout` - User logout

### Skills
- `GET /skills` - Browse all skills
- `GET /api/skills` - Get skills (JSON)
- `POST /api/skills` - Create new skill (JSON)

### User Dashboard
- `GET /dashboard` - User dashboard
- `GET /exchange/<skill_id>` - Skill exchange page

## Development

### Adding New Features
1. Create new models in the `models/` directory
2. Add routes to `app.py`
3. Create templates in `templates/`
4. Add JavaScript functionality in `static/js/`
5. Style with CSS in `static/css/`

### Database Changes
1. Modify models in the `models/` directory
2. Run database migrations (when Flask-Migrate is added)
3. Test the changes

### Styling
- Use Bootstrap 5 classes for layout and components
- Add custom styles in `static/css/style.css`
- Follow the existing design patterns

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the repository or contact the development team.

## Future Enhancements

- [ ] Real-time messaging between users
- [ ] Skill rating and review system
- [ ] Video call integration for remote exchanges
- [ ] Mobile app development
- [ ] Advanced search and filtering
- [ ] Skill verification system
- [ ] Payment integration for premium features 