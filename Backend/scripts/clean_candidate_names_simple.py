"""
Simple script to clean candidate names by removing CV section words
"""
import sys
import os
import re

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.candidate import Candidate
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_name(name):
    """
    Clean a candidate name by removing CV section words and extra whitespace
    """
    if not name:
        return name

    # Split into lines and take only the first meaningful line
    lines = [line.strip() for line in name.split('\n') if line.strip()]

    if not lines:
        return name

    # Words/phrases to remove from names
    cv_section_words = [
        'personal information', 'personal', 'information', 'address', 'email',
        'phone', 'name', 'details', 'profile', 'contact', 'objective',
        'summary', 'education', 'experience', 'skills'
    ]

    # Process each line
    clean_lines = []
    for line in lines:
        line_lower = line.lower().strip()

        # Skip lines that are just CV section headers
        if line_lower in cv_section_words:
            continue

        # Skip lines containing only section words
        words = line.split()
        filtered_words = []

        for word in words:
            word_lower = word.lower().strip()
            # Keep the word if it's not a CV section word
            if word_lower not in cv_section_words:
                filtered_words.append(word)

        if filtered_words:
            clean_line = ' '.join(filtered_words)
            # Only add if it looks like a name (has letters and is reasonable length)
            if re.match(r'^[A-Za-z\s\-\.]+$', clean_line) and 2 <= len(clean_line) <= 50:
                clean_lines.append(clean_line)

    # Return the first clean line if found, otherwise return cleaned original
    if clean_lines:
        return clean_lines[0]

    # Fallback: just remove newlines and extra spaces
    return ' '.join(name.split())


def fix_candidate_names():
    """
    Clean all candidate names in the database
    """
    db: Session = SessionLocal()

    try:
        # Get all candidates
        candidates = db.query(Candidate).all()

        logger.info(f"Found {len(candidates)} candidates to process")

        fixed_count = 0
        skipped_count = 0

        for candidate in candidates:
            old_name = candidate.name

            # Clean the name
            new_name = clean_name(old_name)

            # Only update if the name has changed
            if new_name != old_name:
                logger.info(f"Candidate {candidate.id}: '{old_name}' -> '{new_name}'")
                candidate.name = new_name
                fixed_count += 1
            else:
                skipped_count += 1

        # Commit all changes
        db.commit()

        logger.info(f"\n{'='*60}")
        logger.info(f"SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Total candidates: {len(candidates)}")
        logger.info(f"Names cleaned: {fixed_count}")
        logger.info(f"Skipped/Unchanged: {skipped_count}")
        logger.info(f"{'='*60}\n")

        return fixed_count

    except Exception as e:
        logger.error(f"Error cleaning candidate names: {str(e)}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("CANDIDATE NAME CLEANER")
    print("="*60)
    print("Cleaning candidate names...")
    print("="*60 + "\n")

    try:
        fixed = fix_candidate_names()
        print(f"\nSuccessfully cleaned {fixed} candidate names!")
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)
