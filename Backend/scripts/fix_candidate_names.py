"""
Script to fix candidate names in the database by re-extracting them from raw CV text
"""
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.candidate import Candidate
from app.services.cv_parser import CVParser
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fix_candidate_names():
    """
    Re-extract candidate names from raw CV text for all existing candidates
    """
    db: Session = SessionLocal()
    cv_parser = CVParser()

    try:
        # Get all candidates
        candidates = db.query(Candidate).all()

        logger.info(f"Found {len(candidates)} candidates to process")

        fixed_count = 0
        skipped_count = 0

        for candidate in candidates:
            old_name = candidate.name

            # Skip if no raw text available
            if not candidate.raw_text:
                logger.warning(f"Candidate {candidate.id} has no raw text, skipping")
                skipped_count += 1
                continue

            # Re-extract the name using the improved parser
            new_name = cv_parser.extract_candidate_name(candidate.raw_text)

            # Only update if the name has changed and is not "Unknown"
            if new_name != old_name and new_name != "Unknown":
                logger.info(f"Candidate {candidate.id}: '{old_name}' -> '{new_name}'")
                candidate.name = new_name
                fixed_count += 1
            elif new_name == "Unknown":
                logger.warning(f"Candidate {candidate.id}: Could not extract valid name, keeping '{old_name}'")
                skipped_count += 1
            else:
                logger.info(f"Candidate {candidate.id}: Name unchanged ('{old_name}')")
                skipped_count += 1

        # Commit all changes
        db.commit()

        logger.info(f"\n{'='*60}")
        logger.info(f"SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Total candidates: {len(candidates)}")
        logger.info(f"Names fixed: {fixed_count}")
        logger.info(f"Skipped/Unchanged: {skipped_count}")
        logger.info(f"{'='*60}\n")

        return fixed_count

    except Exception as e:
        logger.error(f"Error fixing candidate names: {str(e)}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("CANDIDATE NAME FIX UTILITY")
    print("="*60)
    print("This script will re-extract candidate names from CV text")
    print("using the improved name extraction algorithm.")
    print("="*60 + "\n")

    response = input("Do you want to proceed? (yes/no): ").strip().lower()

    if response in ['yes', 'y']:
        try:
            fixed = fix_candidate_names()
            print(f"\n✓ Successfully fixed {fixed} candidate names!")
        except Exception as e:
            print(f"\n✗ Error: {str(e)}")
            sys.exit(1)
    else:
        print("\nOperation cancelled.")
