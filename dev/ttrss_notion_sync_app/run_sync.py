#!/usr/bin/env python3
"""
TTRSS-Notion Synchronization Script
TTRSS-Notion 동기화 스크립트

This script manages the synchronization process between Tiny Tiny RSS (TTRSS) and Notion.
It handles:
1. Importing TTRSS entries to the local sync table
2. Synchronizing entries from the sync table to Notion
3. Optionally running a full bidirectional sync

이 스크립트는 Tiny Tiny RSS(TTRSS)와 Notion 간의 동기화 프로세스를 관리합니다.
다음 기능을 처리합니다:
1. TTRSS 항목을 로컬 동기화 테이블로 가져오기
2. 동기화 테이블에서 Notion으로 항목 동기화
3. 선택적으로 전체 양방향 동기화 실행

Configuration:
- Database settings are loaded from environment variables
- Works with the Docker setup (ttrss-db:5432, credentials: ttrss/handbook12)
- Notion API credentials are required for Notion synchronization
"""
import sys
import argparse
import time
from tqdm import tqdm
from config import logger
from sync_manager import SyncManager
from db_manager import DatabaseManager

def parse_args():
    """Parse command line arguments / 명령줄 인수 파싱"""
    parser = argparse.ArgumentParser(description='Sync TTRSS entries with Notion / TTRSS 항목을 Notion과 동기화')
    
    # Basic options
    parser.add_argument('--no-notion', action='store_true', 
                        help='Skip Notion sync / Notion 동기화 건너뛰기')
    parser.add_argument('--import-only', action='store_true', 
                        help='Only import TTRSS entries to sync table / TTRSS 항목만 동기화 테이블로 가져오기')
    parser.add_argument('--export-only', action='store_true',
                        help='Only export from sync table to Notion / 동기화 테이블에서 Notion으로만 내보내기')
    parser.add_argument('--limit', type=int, default=50, 
                        help='Limit number of entries to process / 처리할 항목 수 제한')
    
    # Advanced options
    parser.add_argument('--full-sync', action='store_true',
                        help='Perform full bidirectional sync / 전체 양방향 동기화 수행')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be synchronized without making changes / 변경 없이 동기화될 내용 표시')
    parser.add_argument('--retry-failed', action='store_true',
                        help='Retry previously failed synchronizations / 이전에 실패한 동기화 재시도')
    parser.add_argument('--verbose', action='store_true',
                        help='Show detailed output / 상세 출력 표시')
    
    return parser.parse_args()

def import_ttrss_to_sync():
    """
    Import TTRSS entries to sync table
    TTRSS 항목을 동기화 테이블로 가져오기
    
    Returns:
        tuple: (success_flag, count_of_added_entries)
    """
    # Setup database manager and connect
    db_manager = DatabaseManager()
    
    try:
        # Connect to database
        db_manager.connect()
        logger.info("Connected to TTRSS database / TTRSS 데이터베이스에 연결됨")
        
        # Ensure sync table exists
        db_manager.create_sync_table()
        
        # Get entries from TTRSS
        logger.info("Retrieving entries from TTRSS... / TTRSS에서 항목을 가져오는 중...")
        ttrss_entries = db_manager.get_ttrss_entries()
        logger.info(f"Retrieved {len(ttrss_entries)} entries from TTRSS / TTRSS에서 {len(ttrss_entries)}개 항목을 가져옴")
        
        if not ttrss_entries:
            logger.warning("No entries found in TTRSS. Make sure feeds are subscribed and updated. / "
                          "TTRSS에서 항목을 찾을 수 없습니다. 피드가 구독되고 업데이트되었는지 확인하세요.")
            return True, 0
        
        # Find entries not yet in sync table
        new_entries = db_manager.compare_ttrss_with_sync()
        logger.info(f"Found {len(new_entries)} new entries to sync / 동기화할 {len(new_entries)}개의 새 항목을 찾음")
        
        # Add entries to sync table
        added_count = 0
        for entry in tqdm(new_entries, desc="Adding entries to sync table / 동기화 테이블에 항목 추가 중"):
            db_manager.add_ttrss_entry_to_sync(entry)
            added_count += 1
            
        logger.info(f"Added {added_count} entries to sync table / 동기화 테이블에 {added_count}개 항목을 추가함")
        return True, added_count
    except Exception as e:
        logger.error(f"Error importing TTRSS entries: {e} / TTRSS 항목 가져오기 오류: {e}")
        logger.error("Make sure your database settings are correct and the TTRSS Docker container is running / "
                    "데이터베이스 설정이 올바른지, TTRSS Docker 컨테이너가 실행 중인지 확인하세요.")
        return False, 0
    finally:
        db_manager.close()

def export_to_notion(sync_manager, limit=50, retry_failed=False, dry_run=False):
    """
    Export entries from sync table to Notion
    동기화 테이블에서 Notion으로 항목 내보내기
    
    Args:
        sync_manager: Initialized SyncManager instance
        limit: Maximum number of entries to synchronize
        retry_failed: Whether to retry previously failed synchronizations
        dry_run: If True, only show what would be done without making changes
        
    Returns:
        tuple: (success_flag, count_of_synced_entries)
    """
    try:
        # Find entries to sync
        if retry_failed:
            entries_to_sync = sync_manager.db_manager.find_failed_notion_syncs()
            logger.info(f"Found {len(entries_to_sync)} previously failed entries to retry / "
                       f"재시도할 {len(entries_to_sync)}개의 이전에 실패한 항목을 찾음")
        else:
            entries_to_sync = sync_manager.db_manager.find_entries_to_sync_to_notion()
            logger.info(f"Found {len(entries_to_sync)} entries to sync to Notion / "
                       f"Notion에 동기화할 {len(entries_to_sync)}개 항목을 찾음")
        
        if limit > 0 and len(entries_to_sync) > limit:
            logger.info(f"Limiting sync to {limit} entries (out of {len(entries_to_sync)}) / "
                       f"동기화를 {len(entries_to_sync)}개 중 {limit}개 항목으로 제한함")
            entries_to_sync = entries_to_sync[:limit]
        
        if not entries_to_sync:
            logger.info("No entries to sync to Notion / Notion에 동기화할 항목이 없음")
            return True, 0
            
        if dry_run:
            logger.info("DRY RUN: Would sync these entries to Notion: / 가상 실행: 다음 항목을 Notion에 동기화:")
            for i, entry in enumerate(entries_to_sync[:10], 1):  # Show first 10
                logger.info(f"{i}. {entry['title'][:50]}..." if len(entry['title']) > 50 else entry['title'])
            if len(entries_to_sync) > 10:
                logger.info(f"...and {len(entries_to_sync) - 10} more entries / ...및 {len(entries_to_sync) - 10}개 추가 항목")
            return True, 0
        
        # Sync entries to Notion
        synced_count = 0
        error_count = 0
        for entry in tqdm(entries_to_sync, desc="Syncing to Notion / Notion에 동기화 중"):
            try:
                notion_id = sync_manager.notion_manager.create_page(entry)
                if notion_id:
                    # Update sync status
                    sync_manager.db_manager.update_sync_status(entry['id'], notion_id)
                    synced_count += 1
                else:
                    error_count += 1
            except Exception as e:
                logger.error(f"Error syncing entry {entry['id']}: {e} / 항목 {entry['id']} 동기화 오류: {e}")
                error_count += 1
                # Short pause to avoid rate limits
                time.sleep(1)
        
        logger.info(f"Synced {synced_count} entries to Notion / Notion에 {synced_count}개 항목 동기화됨")
        if error_count:
            logger.warning(f"Failed to sync {error_count} entries / {error_count}개 항목 동기화 실패")
            logger.warning("Use --retry-failed flag to retry these entries / 이러한 항목을 재시도하려면 --retry-failed 플래그 사용")
        
        return True, synced_count
    except Exception as e:
        logger.error(f"Error during Notion export: {e} / Notion 내보내기 중 오류: {e}")
        logger.error("Check your Notion API key and database ID / Notion API 키와 데이터베이스 ID를 확인하세요")
        return False, 0

def perform_full_sync(sync_manager, limit=50, dry_run=False):
    """
    Perform a full bidirectional sync between TTRSS and Notion
    TTRSS와 Notion 간의 전체 양방향 동기화 수행
    
    Args:
        sync_manager: Initialized SyncManager instance
        limit: Maximum number of entries to synchronize in each direction
        dry_run: If True, only show what would be done without making changes
        
    Returns:
        bool: Success flag
    """
    try:
        if dry_run:
            logger.info("DRY RUN: Performing full sync analysis / 가상 실행: 전체 동기화 분석 수행 중")
            
            # Step 1: Check Notion to sync table
            notion_pages = sync_manager.notion_manager.get_database_pages()
            logger.info(f"Found {len(notion_pages)} pages in Notion database / Notion 데이터베이스에서 {len(notion_pages)}개 페이지 발견")
            
            # Step 2: Check TTRSS to sync table
            ttrss_entries = sync_manager.db_manager.get_ttrss_entries()
            logger.info(f"Found {len(ttrss_entries)} entries in TTRSS / TTRSS에서 {len(ttrss_entries)}개 항목 발견")
            
            # Step 3: Check sync table to Notion
            sync_entries = sync_manager.db_manager.find_entries_to_sync_to_notion()
            logger.info(f"Found {len(sync_entries)} entries to sync to Notion / Notion에 동기화할 {len(sync_entries)}개 항목 발견")
            
            return True
            
        logger.info("Performing full bidirectional sync / 전체 양방향 동기화 수행 중")
        result = sync_manager.full_sync(limit=limit)
        
        # Print results
        notion_to_db = result.get('notion_to_db', [])
        ttrss_to_db = result.get('ttrss_to_db', [])
        sync_to_notion = result.get('sync_to_notion', [])
        
        logger.info(f"Full sync completed / 전체 동기화 완료:")
        logger.info(f"- Synced {len(notion_to_db)} Notion pages to sync table / {len(notion_to_db)}개 Notion 페이지를 동기화 테이블에 동기화")
        logger.info(f"- Synced {len(ttrss_to_db)} TTRSS entries to sync table / {len(ttrss_to_db)}개 TTRSS 항목을 동기화 테이블에 동기화")
        logger.info(f"- Synced {len(sync_to_notion)} entries from sync table to Notion / {len(sync_to_notion)}개 항목을 동기화 테이블에서 Notion으로 동기화")
        
        return True
    except Exception as e:
        logger.error(f"Full sync failed: {e} / 전체 동기화 실패: {e}")
        return False

def print_config_info(verbose=False):
    """
    Print configuration information
    구성 정보 출력
    
    Args:
        verbose: Whether to show detailed information
    """
    from config import DB_CONFIG, NOTION_DATABASE_ID, NOTION_API_KEY
    
    logger.info("=== TTRSS-Notion Sync Configuration / TTRSS-Notion 동기화 구성 ===")
    logger.info(f"Database: {DB_CONFIG['host']}:{DB_CONFIG['port']} - {DB_CONFIG['dbname']}")
    
    # Check if using default Docker configuration
    if (DB_CONFIG['host'] in ['localhost', '127.0.0.1'] and 
        DB_CONFIG['port'] == '5432' and 
        DB_CONFIG['dbname'] == 'ttrss' and 
        DB_CONFIG['user'] == 'ttrss'):
        logger.info("Using standard Docker configuration / 표준 Docker 구성 사용 중")
    
    # Notion info (partial key for security)
    if NOTION_API_KEY:
        logger.info(f"Notion Database ID: {NOTION_DATABASE_ID}")
        logger.info(f"Notion API Key: {NOTION_API_KEY[:4]}...{NOTION_API_KEY[-4:]}")
    else:
        logger.info("Notion API key not configured / Notion API 키가 구성되지 않음")
    
    if verbose:
        logger.info("\nDocker Setup Information / Docker 설정 정보:")
        logger.info("- PostgreSQL container: ttrss-db (port 5432)")
        logger.info("- TTRSS container: ttrss-app (port 8080)")
        logger.info("- Default credentials: ttrss/handbook12")
        logger.info("- TTRSS admin login: admin/handbook12")
        logger.info("- Web interface: http://localhost:8080/")

def main():
    """
    Main function to run sync process
    동기화 프로세스를 실행하는 주요 기능
    """
    args = parse_args()
    
    # Display configuration information
    print_config_info(verbose=args.verbose)
    
    # Initialize sync manager
    sync_manager = SyncManager()
    
    try:
        # Initialize connections
        sync_manager.initialize(connect_notion=not args.no_notion)
        logger.info("Connections initialized successfully / 연결이 성공적으로 초기화됨")
        
        # Full sync if requested
        if args.full_sync:
            success = perform_full_sync(sync_manager, limit=args.limit, dry_run=args.dry_run)
            if not success:
                return 1
            return 0
            
        # Import TTRSS entries to sync table (unless export only)
        if not args.export_only:
            logger.info("Starting TTRSS import process... / TTRSS 가져오기 프로세스 시작 중...")
            success, added_count = import_ttrss_to_sync()
            if not success:
                return 1
                
            if added_count > 0:
                logger.info(f"Successfully imported {added_count} entries from TTRSS / "
                           f"TTRSS에서 {added_count}개 항목을 성공적으로 가져옴")
            else:
                logger.info("No new entries to import from TTRSS / TTRSS에서 가져올 새 항목 없음")
        
        # Sync to Notion if not skipped and not import-only
        if not args.no_notion and not args.import_only:
            logger.info("Starting Notion sync process... / Notion 동기화 프로세스 시작 중...")
            success, synced_count = export_to_notion(
                sync_manager, 
                limit=args.limit, 
                retry_failed=args.retry_failed,
                dry_run=args.dry_run
            )
            if not success:
                return 1
                
            if synced_count > 0:
                logger.info(f"Successfully synced {synced_count} entries to Notion / "
                           f"Notion에 {synced_count}개 항목을 성공적으로 동기화함")
        
        logger.info("Sync process completed successfully / 동기화 프로세스가 성공적으로 완료됨")
        return 0
    except Exception as e:
        logger.error(f"Sync process failed: {e} / 동기화 프로세스 실패: {e}")
        return 1
    finally:
        sync_manager.close()

if __name__ == "__main__":
    sys.exit(main())
