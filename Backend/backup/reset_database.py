"""
Complete database reset - delete and recreate from scratch
"""
import os

# Just delete the database file directly
db_file = "resumify.db"

if os.path.exists(db_file):
    os.remove(db_file)
    print(f"✓ Deleted {db_file}")
else:
    print(f"✓ No existing database found")

print("\nDatabase deleted. Now run:")
print("  python main.py")
print("\nThis will auto-create the database with the new schema.")
print("Then run:")
print("  python setup_initial_user.py")
