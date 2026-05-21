"""
Reset demo data by clearing all predictions and labels from the database.

This script directly connects to PostgreSQL and deletes all records
from the predictions and ground_truth_labels tables.

Usage:
    python scripts/reset_demo_data.py
"""
import os
import sys
from pathlib import Path

try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    print("❌ psycopg2 not found. Install with: pip install psycopg2-binary")
    sys.exit(1)


def main():
    """Connect to database and clear demo data."""
    print("🗑️  ModelDrift Demo Data Reset\n")
    print("=" * 60)
    
    # Get database URL from environment or use default
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/modeldrift"
    )
    
    try:
        # Parse connection string
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        print("✅ Connected to PostgreSQL database\n")
        
        # Get counts before deletion
        cursor.execute("SELECT COUNT(*) FROM predictions;")
        pred_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM ground_truth_labels;")
        label_count = cursor.fetchone()[0]
        
        print(f"📊 Current data in database:")
        print(f"  Predictions:       {pred_count}")
        print(f"  Ground truth labels: {label_count}\n")
        
        if pred_count == 0 and label_count == 0:
            print("✅ Database is already empty. Nothing to reset.\n")
            cursor.close()
            conn.close()
            return
        
        # Ask for confirmation
        confirmation = input("⚠️  Are you sure you want to delete all predictions and labels? (yes/no): ")
        
        if confirmation.lower() != "yes":
            print("\n❌ Reset cancelled.\n")
            cursor.close()
            conn.close()
            return
        
        # Delete ground truth labels first (foreign key dependency, if any)
        print("\n🗑️  Deleting ground truth labels...")
        cursor.execute("DELETE FROM ground_truth_labels;")
        deleted_labels = cursor.rowcount
        
        # Delete predictions
        print("🗑️  Deleting predictions...")
        cursor.execute("DELETE FROM predictions;")
        deleted_preds = cursor.rowcount
        
        # Commit changes
        conn.commit()
        
        print("\n" + "=" * 60)
        print("✅ Reset Complete!\n")
        print(f"  Deleted {deleted_labels} ground truth labels")
        print(f"  Deleted {deleted_preds} predictions")
        print(f"  Total records removed: {deleted_labels + deleted_preds}\n")
        
        print("💡 Next steps:")
        print("  1. Generate new demo data: python scripts/generate_demo_data.py")
        print("  2. Verify empty database: curl http://localhost:8000/api/v1/predictions/recent\n")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        print("\nTroubleshooting:")
        print("  • Make sure PostgreSQL is running")
        print("  • Check DATABASE_URL environment variable or .env file")
        print(f"  • Using connection string: {database_url}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
