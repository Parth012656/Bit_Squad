"""
SkillSwap Database Setup Script
This script helps set up the database connection and create tables.
"""
import os
import sys
from dotenv import load_dotenv
load_dotenv()
def check_database_connection():
    """Check if the database connection is properly configured"""
    print("🔍 Checking database configuration...")
    
    required_vars = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("📝 Please create a .env file with the following variables:")
        print("""
DB_HOST=localhost
DB_PORT=3306
DB_NAME=skillswap_db
DB_USER=skillswap_user
DB_PASSWORD=your_password
        """)
        return False
    
    print("✅ Environment variables configured")
    return True
def test_database_connection():
    """Test the database connection"""
    try:
        from config.database import config
        from extensions import db
        from flask import Flask
        
        app = Flask(__name__)
        app.config.from_object(config['development'])
        
        db.init_app(app)
        
        with app.app_context():
            db.engine.execute('SELECT 1')
            print("✅ Database connection successful!")
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure MySQL server is running")
        print("2. Verify database credentials in .env file")
        print("3. Ensure the database 'skillswap_db' exists")
        print("4. Check if the user has proper permissions")
        return False
def create_tables():
    """Create database tables"""
    try:
        from config.database import config
        from extensions import db
        from flask import Flask
        from models.user import User
        from models.skill import Skill
        from models.exchange import Exchange
        
        app = Flask(__name__)
        app.config.from_object(config['development'])
        
        db.init_app(app)
        
        with app.app_context():
            db.create_all()
            print("✅ Database tables created successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False
def main():
    """Main setup function"""
    print("🚀 SkillSwap Database Setup")
    print("=" * 40)
    
    if not check_database_connection():
        sys.exit(1)
    
    if not test_database_connection():
        sys.exit(1)
    
    if not create_tables():
        sys.exit(1)
    
    print("\n🎉 Database setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Run the MySQL setup script: database_setup.sql")
    print("2. Start the Flask application: python app.py")
    print("3. Access the application at: http://localhost:5000")
if __name__ == '__main__':
    main() 