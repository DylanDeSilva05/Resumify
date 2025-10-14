"""
Script to clean up candidate names that have 'email' or other keywords appended
"""
import sys
import os
import re

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.candidate import Candidate
from app.core.config import settings


def clean_candidate_name(name: str) -> str:
    """
    Clean candidate name by removing trailing keywords like 'email', 'phone', etc.

    Args:
        name: Original candidate name

    Returns:
        Cleaned candidate name
    """
    if not name or not name.strip():
        return name

    # Keywords to remove from the end of names
    trailing_keywords = [
        'email', 'phone', 'address', 'contact', 'tel', 'mobile', 'name',
        'telephone', 'fax', 'cell', 'gmail', 'yahoo', 'hotmail', 'outlook'
    ]

    cleaned_name = name.strip()

    # Remove trailing keywords (case-insensitive) using regex to handle any whitespace
    changed = True
    while changed:
        changed = False
        for keyword in trailing_keywords:
            # Use regex to match keyword at end with any whitespace (newlines, spaces, tabs) before it
            pattern = rf'\s+{re.escape(keyword)}$'
            new_name = re.sub(pattern, '', cleaned_name, flags=re.IGNORECASE).strip()
            if new_name != cleaned_name:
                cleaned_name = new_name
                changed = True
                break

    # Also remove if the entire last word is a keyword (after splitting by whitespace)
    words = cleaned_name.split()
    if len(words) > 1:
        last_word_lower = words[-1].lower()
        if last_word_lower in trailing_keywords:
            cleaned_name = ' '.join(words[:-1])

    # Final cleanup: remove any remaining newlines or extra whitespace
    cleaned_name = ' '.join(cleaned_name.split())

    return cleaned_name.strip()


def main():
    """Main function to clean up candidate names in database"""
    print("Starting candidate name cleanup...")

    # Create database connection
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Get all candidates
        candidates = db.query(Candidate).all()
        print(f"Found {len(candidates)} candidates in database")

        updated_count = 0

        # Process each candidate
        for candidate in candidates:
            original_name = candidate.name
            cleaned_name = clean_candidate_name(original_name)

            # Update if name changed
            if cleaned_name != original_name:
                print(f"Updating: '{original_name}' -> '{cleaned_name}'")
                candidate.name = cleaned_name
                updated_count += 1

        # Commit changes
        if updated_count > 0:
            db.commit()
            print(f"\nSuccessfully updated {updated_count} candidate names!")
        else:
            print("\nNo candidate names needed updating.")

        print(f"Summary: {updated_count}/{len(candidates)} names cleaned")

    except Exception as e:
        print(f"Error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
