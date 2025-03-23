"""
Main module for the TTRSS-Notion synchronization application.
"""
import argparse
import sys
import os
from dotenv import load_dotenv
from config import logger
from sync_manager import SyncManager

# Ensure environment variables are loaded
load_dotenv()

def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description='TTRSS to Notion Synchronization Tool')
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Full sync command
    full_sync_parser = subparsers.add_parser('full-sync', help='Perform full synchronization')
    
    # Check Notion database command
    notion_check_parser = subparsers.add_parser('check-notion', help='Check Notion database')
    
    # Check TTRSS entries command
    ttrss_check_parser = subparsers.add_parser('check-ttrss', help='Check TTRSS entries')
    
    # Sync Notion to sync table command
    notion_sync_parser = subparsers.add_parser('sync-notion', 
                                             help='Sync Notion database to sync table')
    
    # Sync TTRSS to sync table command
    ttrss_sync_parser = subparsers.add_parser('sync-ttrss', 
                                            help='Sync TTRSS entries to sync table')
    
    # Sync to Notion command
    to_notion_parser = subparsers.add_parser('sync-to-notion', 
                                           help='Sync entries from sync table to Notion')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare databases')
    compare_parser.add_argument('--source', choices=['notion', 'ttrss'], 
                              required=True, help='Source to compare with sync table')
    
    return parser.parse_args()

def main():
    """Main function"""
    args = parse_arguments()
    
    if args.command is None:
        print("No command specified. Use --help for usage information.")
        return 1
    
    # Initialize sync manager
    sync_manager = SyncManager()
    
    try:
        sync_manager.initialize()
        
        if args.command == 'full-sync':
            results = sync_manager.perform_full_sync()
            print("\nSync Summary:")
            print(f"- Added from Notion: {results['added_from_notion']}")
            print(f"- Removed from sync table: {results['removed_from_sync']}")
            print(f"- Added from TTRSS: {results['added_from_ttrss']}")
            print(f"- Synced to Notion: {results['synced_to_notion']}")
            
        elif args.command == 'check-notion':
            pages = sync_manager.check_notion_database()
            print(f"\nFound {len(pages)} pages in Notion database.")
            if pages:
                print("\nSample pages:")
                for page in pages[:3]:  # Show first 3 pages
                    print(f"- {page['title']} (ID: {page['notion_page_id']})")
            
        elif args.command == 'check-ttrss':
            entries = sync_manager.check_ttrss_entries()
            print(f"\nFound {len(entries)} entries in TTRSS.")
            if entries:
                print("\nSample entries:")
                for entry in entries[:3]:  # Show first 3 entries
                    print(f"- {entry['title']} (ID: {entry['id']})")
            
        elif args.command == 'sync-notion':
            added, removed = sync_manager.sync_notion_to_sync_table()
            print(f"\nAdded {added} pages from Notion to sync table.")
            print(f"Removed {removed} orphaned records from sync table.")
            
        elif args.command == 'sync-ttrss':
            added = sync_manager.sync_ttrss_to_sync_table()
            print(f"\nAdded {added} entries from TTRSS to sync table.")
            
        elif args.command == 'sync-to-notion':
            synced = sync_manager.sync_to_notion()
            print(f"\nSynced {synced} entries to Notion.")
            
        elif args.command == 'compare':
            if args.source == 'notion':
                new_in_notion, missing_from_notion = sync_manager.compare_notion_with_sync()
                print(f"\nFound {len(new_in_notion)} pages in Notion that are not in sync table.")
                print(f"Found {len(missing_from_notion)} entries in sync table missing from Notion.")
                
            elif args.source == 'ttrss':
                new_in_ttrss = sync_manager.compare_ttrss_with_sync()
                print(f"\nFound {len(new_in_ttrss)} entries in TTRSS that are not in sync table.")
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1
        
    finally:
        sync_manager.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
