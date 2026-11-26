"""
Seeder script for Supplier Management API
Loads initial suppliers from the BRIEFING into TinyDB
"""
import sys
from database import seed_suppliers, get_db

if __name__ == "__main__":
    try:
        count = seed_suppliers()
        print(f"\n✓ Seed completed successfully")
        print(f"  Total suppliers in database: {len(get_db().all())}")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error during seeding: {e}", file=sys.stderr)
        sys.exit(1)
