"""
Database setup script
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys

def create_database():
    """Create the resumify database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server (not to a specific database)
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="admin",
            port=5432
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='resumify_db'")
        exists = cursor.fetchone()

        if not exists:
            # Create the database
            cursor.execute("CREATE DATABASE resumify_db")
            print("✅ Database 'resumify_db' created successfully!")
        else:
            print("✅ Database 'resumify_db' already exists.")

        # Also create test database
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='resumify_test_db'")
        exists = cursor.fetchone()

        if not exists:
            cursor.execute("CREATE DATABASE resumify_test_db")
            print("✅ Test database 'resumify_test_db' created successfully!")
        else:
            print("✅ Test database 'resumify_test_db' already exists.")

        cursor.close()
        conn.close()

    except psycopg2.OperationalError as e:
        if "password authentication failed" in str(e):
            print("❌ Database connection failed: Invalid username or password")
            print("Please check your PostgreSQL credentials in the .env file")
            print("Current credentials: postgres:admin@localhost:5432")
        elif "could not connect to server" in str(e):
            print("❌ Database connection failed: PostgreSQL server not running")
            print("Please start PostgreSQL server and try again")
        else:
            print(f"❌ Database connection failed: {e}")
        return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

    return True

if __name__ == "__main__":
    print("🔄 Setting up Resumify database...")
    success = create_database()
    if success:
        print("🎉 Database setup completed successfully!")
        print("You can now run: python main.py")
    else:
        print("💡 Please check your PostgreSQL setup and try again.")
        sys.exit(1)