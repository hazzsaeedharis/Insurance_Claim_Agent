#!/usr/bin/env python
"""
Authentication Setup Script

Helps set up the authentication system for Insurance Claim Agent.
"""

import os
import secrets
import sys
from pathlib import Path


def print_banner():
    print("""
    ================================================================
    Insurance Claim Agent - Authentication Setup
    ================================================================
    """)


def generate_secret_key():
    """Generate a secure secret key for JWT."""
    return secrets.token_hex(32)


def check_postgresql():
    """Check if PostgreSQL is accessible."""
    try:
        import psycopg2
        
        # Try to connect
        conn_string = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/postgres')
        conn = psycopg2.connect(conn_string)
        conn.close()
        print("✓ PostgreSQL connection successful")
        return True
    except ImportError:
        print("✗ psycopg2-binary not installed. Run: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"✗ PostgreSQL connection failed: {e}")
        print("\nPlease ensure PostgreSQL is running and credentials are correct.")
        return False


def create_database():
    """Create the insurance_claims database if it doesn't exist."""
    try:
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
        
        # Connect to default postgres database
        conn = psycopg2.connect(
            dbname='postgres',
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'postgres'),
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432')
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='insurance_claims'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute('CREATE DATABASE insurance_claims')
            print("✓ Created database 'insurance_claims'")
        else:
            print("✓ Database 'insurance_claims' already exists")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Failed to create database: {e}")
        return False


def setup_env_file():
    """Set up .env file with authentication variables."""
    env_path = Path('.env')
    env_example_path = Path('env.example')
    
    if env_path.exists():
        print("\n.env file already exists.")
        response = input("Do you want to update it with authentication settings? (y/n): ")
        if response.lower() != 'y':
            print("Skipping .env update")
            return
    
    # Generate secret key
    secret_key = generate_secret_key()
    
    print("\n" + "="*60)
    print("AUTHENTICATION CONFIGURATION")
    print("="*60)
    
    # Get database settings
    print("\nDatabase Configuration:")
    db_user = input("PostgreSQL username [postgres]: ") or "postgres"
    db_password = input("PostgreSQL password [postgres]: ") or "postgres"
    db_host = input("PostgreSQL host [localhost]: ") or "localhost"
    db_port = input("PostgreSQL port [5432]: ") or "5432"
    db_name = input("Database name [insurance_claims]: ") or "insurance_claims"
    
    database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    # Get Google OAuth settings (optional)
    print("\nGoogle OAuth2 Configuration (optional - press Enter to skip):")
    google_client_id = input("Google Client ID: ") or ""
    google_client_secret = input("Google Client Secret: ") or ""
    
    # Prepare auth settings
    auth_settings = f"""
# ============================================================================
# AUTHENTICATION & SECURITY (Added by setup_auth.py)
# ============================================================================

# Database
DATABASE_URL={database_url}

# JWT Configuration
SECRET_KEY={secret_key}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Google OAuth2 (optional)
GOOGLE_CLIENT_ID={google_client_id}
GOOGLE_CLIENT_SECRET={google_client_secret}
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# Frontend URL
FRONTEND_URL=http://localhost:3000
"""
    
    # Read existing .env or create new
    if env_path.exists():
        with open(env_path, 'r') as f:
            existing_content = f.read()
        
        # Check if auth settings already exist
        if 'AUTHENTICATION & SECURITY' in existing_content:
            # Replace existing auth section
            lines = existing_content.split('\n')
            new_lines = []
            skip = False
            for line in lines:
                if 'AUTHENTICATION & SECURITY' in line:
                    skip = True
                elif skip and line.startswith('# ==='):
                    skip = False
                elif not skip:
                    new_lines.append(line)
            
            content = '\n'.join(new_lines) + auth_settings
        else:
            # Append auth settings
            content = existing_content + auth_settings
    else:
        # Use env.example as base if it exists
        if env_example_path.exists():
            with open(env_example_path, 'r') as f:
                content = f.read()
            # Replace placeholders
            content = content.replace('your_secret_key_here_change_in_production', secret_key)
            content = content.replace('postgresql://postgres:postgres@localhost:5432/insurance_claims', database_url)
            if google_client_id:
                content = content.replace('your_google_client_id_here', google_client_id)
            if google_client_secret:
                content = content.replace('your_google_client_secret_here', google_client_secret)
        else:
            content = auth_settings
    
    # Write .env file
    with open(env_path, 'w') as f:
        f.write(content)
    
    print(f"\n✓ .env file {'updated' if env_path.exists() else 'created'}")
    print(f"✓ Generated secure JWT secret key")
    print(f"✓ Database URL: {database_url}")
    
    if google_client_id:
        print(f"✓ Google OAuth2 configured")
    else:
        print("⚠ Google OAuth2 not configured (optional)")


def initialize_database():
    """Initialize database tables."""
    print("\nInitializing database tables...")
    
    try:
        # Add backend to path
        sys.path.insert(0, str(Path(__file__).parent / "backend"))
        
        from database import init_db, check_db_connection
        
        if not check_db_connection():
            print("✗ Cannot connect to database")
            return False
        
        init_db()
        print("✓ Database tables created successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize database: {e}")
        print("\nYou can manually initialize the database by running the application:")
        print("  python run.py")
        return False


def main():
    """Main setup function."""
    print_banner()
    
    print("This script will help you set up authentication for Insurance Claim Agent.\n")
    
    # Check dependencies
    print("Checking dependencies...")
    try:
        import psycopg2
        import sqlalchemy
        import jose
        from pwdlib import PasswordHash
        print("✓ All authentication dependencies installed\n")
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("\nPlease install all dependencies:")
        print("  pip install -r requirements.txt\n")
        sys.exit(1)
    
    # Check PostgreSQL
    print("Checking PostgreSQL...")
    if not check_postgresql():
        print("\nPlease install and start PostgreSQL:")
        print("  Windows: https://www.postgresql.org/download/windows/")
        print("  Mac: brew install postgresql && brew services start postgresql")
        print("  Linux: sudo apt-get install postgresql && sudo systemctl start postgresql")
        sys.exit(1)
    
    print()
    
    # Create database
    print("Setting up database...")
    if not create_database():
        print("\nPlease create the database manually:")
        print("  psql -U postgres")
        print("  CREATE DATABASE insurance_claims;")
        print("  \\q")
        sys.exit(1)
    
    print()
    
    # Setup .env file
    setup_env_file()
    
    print()
    
    # Initialize database tables
    response = input("\nDo you want to initialize database tables now? (y/n): ")
    if response.lower() == 'y':
        initialize_database()
    else:
        print("\nYou can initialize tables later by running:")
        print("  python run.py")
    
    print("\n" + "="*60)
    print("SETUP COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Review your .env file")
    print("2. Start the application: python run.py")
    print("3. Open frontend/auth.html in your browser")
    print("4. Register a new account")
    print("\nFor Google OAuth2 setup, see AUTHENTICATION.md")
    print("\n" + "="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)

