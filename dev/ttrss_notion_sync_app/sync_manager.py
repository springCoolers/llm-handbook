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
                # Get the full page content
                page_id = page_data['notion_page_id']
                page_content = self.notion_manager.get_page_content(page_id)
                
                # Update the content field with the actual page content
                if page_content:
                    page_data['content'] = page_content
                    logger.info(f"Retrieved page content for {page_data['title']}: {len(page_content)} characters")
                else:
                    logger.warning(f"Could not retrieve page content for {page_data['title']}")
                    
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
        - Updates existing entries with latest data from Notion
        - Removes sync records that don't exist in Notion anymore
        """
        # Get all pages from Notion if not provided
        if notion_pages is None:
            notion_pages = self.check_notion_database()
            
        # Get comparison results
        new_in_notion, missing_from_notion = self.compare_notion_with_sync(notion_pages)
        
        # Add new Notion pages to sync table
        added_count = 0
        for page in tqdm(new_in_notion, desc="Adding new Notion pages to sync table"):
            self.db_manager.add_notion_entry_to_sync(page)
            added_count += 1
            
        # Update existing entries with latest data from Notion
        updated_count = 0
        existing_pages = [page for page in notion_pages if page['notion_page_id'] not in [p['notion_page_id'] for p in new_in_notion]]
        for page in tqdm(existing_pages, desc="Updating existing entries with Notion data"):
            # Get the full page content if not already retrieved
            if 'content' not in page or not page['content'] or page['content'] == page.get('why_it_matters', ''):
                page_id = page['notion_page_id']
                page_content = self.notion_manager.get_page_content(page_id)
                
                # Update the content field with the actual page content
                if page_content:
                    page['content'] = page_content
                    logger.info(f"Retrieved page content for update {page['title']}: {len(page_content)} characters")
                else:
                    logger.warning(f"Could not retrieve page content for update {page['title']}")
            
            if self.db_manager.update_notion_entry_in_sync(page):
                updated_count += 1
            
        # Remove sync records missing from Notion
        removed_count = 0
        for entry in tqdm(missing_from_notion, desc="Removing orphaned sync records"):
            self.db_manager.delete_sync_entry(entry['id'])
            removed_count += 1
            
        logger.info(f"Added {added_count} new Notion pages to sync table")
        logger.info(f"Updated {updated_count} existing entries with latest data from Notion")
        logger.info(f"Removed {removed_count} orphaned sync records")
        
        return added_count, updated_count, removed_count
        
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
        - Adds new entries from TTRSS to sync table
        - Updates existing entries with latest data from TTRSS
        - Never deletes from sync table even if entries are deleted from TTRSS
        """
        # Get new entries from TTRSS
        new_entries = self.compare_ttrss_with_sync(ttrss_entries)
        
        # Add new entries to sync table
        added_count = 0
        for entry in tqdm(new_entries, desc="Adding new TTRSS entries to sync table"):
            self.db_manager.add_ttrss_entry_to_sync(entry)
            added_count += 1
            
        # Update existing entries with latest data from TTRSS
        logger.info("Updating existing TTRSS entries in sync table with latest data")
        updated_count = self.db_manager.update_ttrss_entries_in_sync()
            
        logger.info(f"Added {added_count} new TTRSS entries to sync table")
        logger.info(f"Updated {updated_count} existing TTRSS entries in sync table")
        
        return added_count, updated_count
        
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
           - Add new Notion pages to sync table
           - Update existing entries with latest data from Notion
           - Remove sync records that don't exist in Notion anymore
        2. Sync TTRSS to sync table
           - Add new entries from TTRSS to sync table
           - Update existing entries with latest data from TTRSS
        3. Check for title matches and update sync status
        4. Sync new entries from sync table to Notion
        """
        # Step 1: Sync Notion to sync table
        logger.info("Step 1: Syncing Notion to sync table")
        notion_pages = self.check_notion_database()
        added_notion, updated_notion, removed_notion = self.sync_notion_to_sync_table(notion_pages)
        
        # Step 2: Sync TTRSS to sync table
        logger.info("Step 2: Syncing TTRSS to sync table")
        ttrss_entries = self.check_ttrss_entries()
        added_ttrss, updated_ttrss = self.sync_ttrss_to_sync_table(ttrss_entries)
        
        # Step 3: Check for title matches and update sync status
        logger.info("Step 3: Checking for title matches and updating sync status")
        updated_matches = self.db_manager.update_duplicate_entries_sync_status()
        
        # Step 4: Sync new entries to Notion
        logger.info("Step 4: Syncing new entries to Notion")
        synced_to_notion = self.sync_to_notion()
        
        return {
            "added_from_notion": added_notion,
            "updated_from_notion": updated_notion,
            "removed_from_sync": removed_notion,
            "added_from_ttrss": added_ttrss,
            "updated_from_ttrss": updated_ttrss,
            "updated_matches": updated_matches,
            "synced_to_notion": synced_to_notion
        }
