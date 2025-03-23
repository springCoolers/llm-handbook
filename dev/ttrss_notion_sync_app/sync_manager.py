"""
Synchronization management module for handling sync operations between TTRSS and Notion.
"""
import time
from tqdm import tqdm
from config import logger
from db_manager import DatabaseManager
from notion_manager import NotionManager

class SyncManager:
    """Class to manage synchronization between TTRSS and Notion"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.notion_manager = NotionManager()
        
    def initialize(self, connect_notion=True, timeout=10):
        """
        Initialize connections and ensure sync table exists
        
        Args:
            connect_notion (bool): Whether to connect to Notion API (default: True)
            timeout (int): Connection timeout in seconds (default: 10)
        
        Returns:
            bool: True if initialization was successful
        """
        # Connect to database with timeout
        try:
            self.db_manager.connect()
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
            
        # Connect to Notion API if requested
        if connect_notion:
            try:
                self.notion_manager.connect()
                logger.info("Notion API connection established")
            except Exception as e:
                logger.error(f"Failed to connect to Notion API: {e}")
                raise
        else:
            logger.info("Skipping Notion API connection as requested")
            
        # Create sync table if it doesn't exist
        table_created = self.db_manager.create_sync_table()
        if table_created:
            logger.info("Sync table created")
        else:
            logger.info("Sync table already exists")
            
        logger.info("Initialization complete")
        return True
        
    def close(self):
        """Close connections"""
        self.db_manager.close()
        logger.info("Connections closed")
        
    def connect_notion(self):
        """
        Explicitly connect to Notion API if not already connected
        
        Returns:
            bool: True if connection was successful
        """
        try:
            if not hasattr(self.notion_manager, 'client') or self.notion_manager.client is None:
                self.notion_manager.connect()
                logger.info("Notion API connection established")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Notion API: {e}")
            raise
        
    def check_notion_database(self):
        """
        Method to check the Notion database contents
        Returns all pages from the Notion database in a structured format
        
        Automatically connects to Notion API if not already connected
        """
        # Ensure we're connected to Notion
        self.connect_notion()
        
        # Get all pages from the Notion database
        pages = self.notion_manager.get_database_pages()
        
        # Extract relevant data from each page
        extracted_pages = []
        for page in tqdm(pages, desc="Processing Notion pages"):
            page_data = self.notion_manager.extract_page_data(page)
            if page_data:
                extracted_pages.append(page_data)
                
        logger.info(f"Processed {len(extracted_pages)} pages from Notion database")
        return extracted_pages
        
    def compare_notion_with_sync(self, notion_pages=None):
        """
        Method to compare Notion database with sync table
        Returns:
        - new_in_notion: Pages that exist in Notion but not in sync table
        - missing_from_notion: Records that exist in sync table with Notion source but missing from Notion
        """
        if notion_pages is None:
            notion_pages = self.check_notion_database()
            
        # Get all entries from sync table
        sync_entries = self.db_manager.get_sync_entries()
        
        # Create sets of IDs for comparison
        notion_page_ids = {page['notion_page_id'] for page in notion_pages}
        sync_notion_ids = {entry['notion_page_id'] for entry in sync_entries 
                          if entry['notion_page_id'] is not None}
        
        # Find new pages in Notion
        new_in_notion = [page for page in notion_pages 
                         if page['notion_page_id'] not in sync_notion_ids]
        
        # Find entries in sync but missing from Notion
        missing_from_notion = [entry for entry in sync_entries 
                              if entry['source'] == 'notion' and 
                              entry['notion_page_id'] is not None and
                              entry['notion_page_id'] not in notion_page_ids]
        
        logger.info(f"Found {len(new_in_notion)} new pages in Notion")
        logger.info(f"Found {len(missing_from_notion)} sync entries missing from Notion")
        
        return new_in_notion, missing_from_notion
        
    def sync_notion_to_sync_table(self, notion_pages=None):
        """
        Method to sync between Notion database and sync table
        Uses Notion as the source of truth:
        - Adds new Notion pages to sync table
        - Removes sync records that don't exist in Notion anymore
        """
        # Get comparison results
        new_in_notion, missing_from_notion = self.compare_notion_with_sync(notion_pages)
        
        # Add new Notion pages to sync table
        for page in tqdm(new_in_notion, desc="Adding new Notion pages to sync table"):
            self.db_manager.add_notion_entry_to_sync(page)
            
        # Remove sync records missing from Notion
        for entry in tqdm(missing_from_notion, desc="Removing orphaned sync records"):
            self.db_manager.delete_sync_entry(entry['id'])
            
        logger.info(f"Added {len(new_in_notion)} new Notion pages to sync table")
        logger.info(f"Removed {len(missing_from_notion)} orphaned sync records")
        
        return len(new_in_notion), len(missing_from_notion)
        
    def check_ttrss_entries(self):
        """
        Method to check the TTRSS entries
        Returns all entries from the TTRSS entries table
        """
        return self.db_manager.get_ttrss_entries()
        
    def compare_ttrss_with_sync(self, ttrss_entries=None):
        """
        Method to compare TTRSS entries with sync table
        Returns entries that exist in TTRSS but not in sync table
        """
        if ttrss_entries is None:
            ttrss_entries = self.check_ttrss_entries()
            
        # Use the database manager's method to compare
        new_entries = self.db_manager.compare_ttrss_with_sync()
        
        logger.info(f"Found {len(new_entries)} new entries in TTRSS")
        return new_entries
        
    def sync_ttrss_to_sync_table(self, ttrss_entries=None):
        """
        Method to sync TTRSS entries to sync table
        Never deletes from sync table even if entries are deleted from TTRSS
        Only adds new entries from TTRSS to sync table
        """
        # Get new entries from TTRSS
        new_entries = self.compare_ttrss_with_sync(ttrss_entries)
        
        # Add new entries to sync table
        for entry in tqdm(new_entries, desc="Adding new TTRSS entries to sync table"):
            self.db_manager.add_ttrss_entry_to_sync(entry)
            
        logger.info(f"Added {len(new_entries)} new TTRSS entries to sync table")
        
        return len(new_entries)
        
    def sync_to_notion(self):
        """
        Method to sync entries from sync table to Notion
        Finds entries in sync table that haven't been synced to Notion yet
        Creates new pages in Notion for these entries
        """
        # Find entries to sync
        entries_to_sync = self.db_manager.find_entries_to_sync_to_notion()
        
        # Create new pages in Notion
        synced_count = 0
        for entry in tqdm(entries_to_sync, desc="Syncing to Notion"):
            # Create a new page in Notion
            notion_page_id = self.notion_manager.create_page(entry)
            
            if notion_page_id:
                # Update the sync status
                self.db_manager.update_sync_status(entry['id'], notion_page_id)
                synced_count += 1
                
                # Add a small delay to avoid rate limiting
                time.sleep(0.5)
        
        logger.info(f"Synced {synced_count} entries to Notion")
        return synced_count
        
    def perform_full_sync(self):
        """
        Perform a full synchronization between TTRSS, sync table, and Notion
        1. Sync Notion to sync table (Notion is source of truth)
        2. Sync TTRSS to sync table (only add, never delete)
        3. Sync new entries from sync table to Notion
        """
        # Step 1: Sync Notion to sync table
        logger.info("Step 1: Syncing Notion to sync table")
        notion_pages = self.check_notion_database()
        added_notion, removed_notion = self.sync_notion_to_sync_table(notion_pages)
        
        # Step 2: Sync TTRSS to sync table
        logger.info("Step 2: Syncing TTRSS to sync table")
        ttrss_entries = self.check_ttrss_entries()
        added_ttrss = self.sync_ttrss_to_sync_table(ttrss_entries)
        
        # Step 3: Sync new entries to Notion
        logger.info("Step 3: Syncing new entries to Notion")
        synced_to_notion = self.sync_to_notion()
        
        return {
            "added_from_notion": added_notion,
            "removed_from_sync": removed_notion,
            "added_from_ttrss": added_ttrss,
            "synced_to_notion": synced_to_notion
        }
