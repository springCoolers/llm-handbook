#!/usr/bin/env python3
"""
Script to drop and recreate the ttrss_notion_sync table.
"""
import sys
from db_manager import DatabaseManager
from config import SYNC_TABLE, logger

def reset_sync_table():
    """Drop and recreate the ttrss_notion_sync table"""
    db_manager = DatabaseManager()
    
    try:
        # Connect to the database
        conn = db_manager.connect()
        
        # Drop the existing table if it exists
        with conn.cursor() as cur:
            logger.info(f"Attempting to drop table {SYNC_TABLE}...")
            cur.execute(f"DROP TABLE IF EXISTS {SYNC_TABLE}")
            conn.commit()
            logger.info(f"Table {SYNC_TABLE} dropped successfully")
        
        # Recreate the table
        created = db_manager.create_sync_table()
        if created:
            logger.info(f"Table {SYNC_TABLE} has been recreated")
        else:
            logger.warning(f"Table {SYNC_TABLE} was not recreated. Check for errors.")
            
    except Exception as e:
        logger.error(f"Error resetting sync table: {e}")
        return False
    finally:
        # Close the database connection
        db_manager.close()
    
    return True

if __name__ == "__main__":
    logger.info("Starting sync table reset process...")
    success = reset_sync_table()
    
    if success:
        logger.info("Sync table reset completed successfully")
        sys.exit(0)
    else:
        logger.error("Sync table reset failed")
        sys.exit(1)
