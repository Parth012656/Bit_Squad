"""
Test script to verify SkillSwap app is ready to use
"""
import os
import sys
from dotenv import load_dotenv
load_dotenv()
def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        from flask_login import LoginManager
        from werkzeug.security import generate_password_hash
        print("✅ Flask and extensions imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
def test_configuration():
    """Test if configuration is properly set up"""
    print("🔍 Testing configuration...")
    
    try:
        from config.database import config
        dev_config = config['development']
        
        db_uri = dev_config.SQLALCHEMY_DATABASE_URI
        if 'mysql://' in db_uri:
            print("✅ Database configuration looks good")
            return True
        else:
            print("❌ Database URI format is incorrect")
            return False
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False
def test_database_connection():
    """Test database connection"""
    print("🔍 Testing database connection...")
    
    try:
        from app import create_app
        from flask_sqlalchemy import SQLAlchemy
        
        app = create_app('development')
        
        with app.app_context():
            from app import db
            with db.engine.connect() as conn:
                conn.execute(db.text('SELECT 1'))
            print("✅ Database connection successful!")
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n💡 Make sure to:")
        print("1. Create the MySQL database: skillswap_db")
        print("2. Create the user: skillswap_user")
        print("3. Run the database setup script")
        return False
def test_models():
    """Test if models can be imported"""
    print("🔍 Testing models...")
    
    try:
        from app import create_app
        app = create_app('development')
        
        with app.app_context():
            from models.user import User
            from models.skill import Skill
            from models.exchange import Exchange
            print("✅ All models imported successfully")
            return True
    except Exception as e:
        print(f"❌ Model import error: {e}")
        return False
def test_templates():
    """Test if templates exist"""
    print("🔍 Testing templates...")
    
    required_templates = [
        'templates/base.html',
        'templates/index.html',
        'templates/login.html',
        'templates/register.html',
        'templates/dashboard.html',
        'templates/skills.html',
        'templates/exchange.html'
    ]
    
    missing_templates = []
    for template in required_templates:
        if not os.path.exists(template):
            missing_templates.append(template)
    
    if missing_templates:
        print(f"❌ Missing templates: {missing_templates}")
        return False
    else:
        print("✅ All templates exist")
        return True
def test_static_files():
    """Test if static files exist"""
    print("🔍 Testing static files...")
    
    required_static = [
        'static/css/style.css',
        'static/js/main.js'
    ]
    
    missing_static = []
    for static_file in required_static:
        if not os.path.exists(static_file):
            missing_static.append(static_file)
    
    if missing_static:
        print(f"❌ Missing static files: {missing_static}")
        return False
    else:
        print("✅ All static files exist")
        return True
def main():
    """Main test function"""
    print("🚀 SkillSwap App Readiness Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_configuration,
        test_models,
        test_templates,
        test_static_files,
        test_database_connection
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Your app is ready to use!")
        print("\n📋 Next steps:")
        print("1. Set up your MySQL database")
        print("2. Create a .env file with your database credentials")
        print("3. Run: python app.py")
        print("4. Visit: http://localhost:5000")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)
if __name__ == '__main__':
    main() 