# TTRSS-Notion Synchronization Application Test Guide

This document provides an updated guide to the `test_sync_app.ipynb` Jupyter notebook. The notebook tests the synchronization functionality between Tiny Tiny RSS (TTRSS) and Notion databases.

## Original vs Updated Content

The original notebook is in Korean and contains several test cells for different components. This guide provides:
1. English translations with bilingual headers
2. Updated configuration for Docker-based TTRSS setup
3. Extended documentation for each test section
4. Troubleshooting tips for common issues

## How to Use This Guide

1. Open the original `test_sync_app.ipynb` notebook in Jupyter
2. Use this guide to update the content cell by cell
3. Keep the original Korean comments if desired, adding English translations

## Updated Notebook Content

### 1. Environment Setup and Imports (환경 설정 및 임포트)

```python
# Cell 1: Introduction
"""
# TTRSS-Notion Synchronization Application Test
# TTRSS-Notion 동기화 애플리케이션 테스트

This notebook tests the synchronization functionality between TTRSS and Notion databases.
It tests key features of each module and verifies the results.

이 노트북은 TTRSS와 Notion 데이터베이스 간 동기화 기능을 테스트합니다. 
모듈별로 주요 기능을 테스트하고 결과를 확인합니다.
"""

# Cell 2: Set up working directory
import sys
import os
from datetime import datetime
import json

# Check current working directory
print(f"Current working directory: {os.getcwd()}")

# Add path for module imports if necessary
current_dir = os.getcwd()
if not current_dir.endswith('ttrss_notion_sync_app'):
    if 'ttrss_notion_sync_app' in os.listdir():
        os.chdir('ttrss_notion_sync_app')
    elif os.path.exists('../ttrss_notion_sync_app'):
        os.chdir('../ttrss_notion_sync_app')
    print(f"Changed directory to: {os.getcwd()}")

# Cell 3: Load configuration
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

# Get configuration
from config import DB_CONFIG, NOTION_DATABASE_ID, NOTION_API_KEY, logger

# Check configuration information (only show partial API key for security)
print(f"Database Config: {DB_CONFIG['host']}:{DB_CONFIG['port']} - DB: {DB_CONFIG['dbname']}")
print(f"Notion Database ID: {NOTION_DATABASE_ID}")
if NOTION_API_KEY:
    print(f"Notion API Key: {NOTION_API_KEY[:5]}...{NOTION_API_KEY[-5:]}")
else:
    print("Notion API Key not set - please configure your .env file")
```

### 2. Database Manager Test (데이터베이스 관리자 테스트)

```python
# Cell 4: Test database connection
from db_manager import DatabaseManager

# Create database manager object
db_manager = DatabaseManager()

# Test database connection
try:
    conn = db_manager.connect()
    print("✅ Database connection successful (데이터베이스 연결 성공)")
except Exception as e:
    print(f"❌ Database connection failed (데이터베이스 연결 실패): {e}")
    print("\nTROUBLESHOOTING:")
    print("1. Check if your TTRSS Docker container is running")
    print("2. Verify your database credentials in the .env file")
    print("3. If using Docker, make sure port 5432 is properly mapped")
    print("   - Current Docker setup: PostgreSQL at port 5432")
    print("   - Username: ttrss, Database: ttrss")

# Cell 5: Check TTRSS entries table schema
try:
    schema = db_manager.get_ttrss_entries_schema()
    print("✅ TTRSS entries table schema retrieval successful (TTRSS 항목 테이블 스키마 조회 성공)")
    print(f"Schema column count (스키마 컬럼 수): {len(schema)}")
    for column, data_type in schema[:10]:  # Show first 10 columns only
        print(f"  - {column}: {data_type}")
except Exception as e:
    print(f"❌ TTRSS entries table schema retrieval failed (TTRSS 항목 테이블 스키마 조회 실패): {e}")

# Cell 6: Retrieve TTRSS entries
try:
    entries = db_manager.get_ttrss_entries()
    print(f"✅ TTRSS entries retrieval successful (TTRSS 항목 조회 성공): {len(entries)} entries found")
    
    # Preview first 5 entries
    if entries:
        print("\nFirst 5 entries (처음 5개 항목):")
        for entry in entries[:5]:
            print(f"  - ID: {entry['id']}, Title (제목): {entry['title'][:50]}...")
    else:
        print("No TTRSS entries found. You may need to subscribe to feeds and update them.")
        print("(TTRSS 항목이 없습니다. 피드를 구독하고 업데이트해야 할 수 있습니다.)")
except Exception as e:
    print(f"❌ TTRSS entries retrieval failed (TTRSS 항목 조회 실패): {e}")

# Cell 7: Test sync table creation
try:
    was_created = db_manager.create_sync_table()
    if was_created:
        print("✅ Sync table created (동기화 테이블이 생성되었습니다)")
    else:
        print("ℹ️ Sync table already exists, keeping it (동기화 테이블이 이미 존재합니다. 테이블을 유지합니다)")
except Exception as e:
    print(f"❌ Sync table operation failed (동기화 테이블 작업 실패): {e}")

# Cell 8: Check sync table entries
try:
    sync_entries = db_manager.get_sync_entries()
    print(f"✅ Sync table entries retrieval successful (동기화 테이블 항목 조회 성공): {len(sync_entries)} entries found")
    
    # If entries exist, preview first 5
    if sync_entries:
        print("\nFirst 5 entries (처음 5개 항목):")
        for entry in sync_entries[:5]:
            print(f"  - ID: {entry['id']}, Title (제목): {entry['title'][:50] if entry['title'] else 'No Title'}...")
    else:
        print("No entries in sync table. Synchronization may not have happened yet.")
        print("(동기화 테이블에 항목이 없습니다. 아직 동기화가 진행되지 않았을 수 있습니다.)")
except Exception as e:
    print(f"❌ Sync table entries retrieval failed (동기화 테이블 항목 조회 실패): {e}")
```

### 3. Notion Manager Test (Notion 관리자 테스트)

```python
# Cell 9: Test Notion API connection
from notion_manager import NotionManager

# Create Notion manager object
notion_manager = NotionManager()

# Test Notion API connection
try:
    client = notion_manager.connect()
    print("✅ Notion API connection successful (Notion API 연결 성공)")
except Exception as e:
    print(f"❌ Notion API connection failed (Notion API 연결 실패): {e}")
    print("\nTROUBLESHOOTING:")
    print("1. Check if your Notion API key is valid")
    print("2. Verify the Notion database ID is correct")
    print("3. Make sure your integration has access to the database")

# Cell 10: Retrieve Notion database structure
try:
    properties = notion_manager.get_database_structure()
    print("✅ Notion database structure retrieval successful (Notion 데이터베이스 구조 조회 성공)")
    print(f"Number of properties (속성 수): {len(properties)}")
    print("Database properties (데이터베이스 속성):")
    for prop_name, prop_data in properties.items():
        print(f"  - {prop_name} ({prop_data.get('type', 'unknown')})")
except Exception as e:
    print(f"❌ Notion database structure retrieval failed (Notion 데이터베이스 구조 조회 실패): {e}")

# Cell 11: Retrieve Notion database pages
try:
    pages = notion_manager.get_database_pages()
    print(f"✅ Notion database pages retrieval successful (Notion 데이터베이스 페이지 조회 성공): {len(pages)} pages found")
    
    # Preview first 3 page IDs
    if pages:
        print("\nFirst 3 page IDs (처음 3개 페이지 ID):")
        for i, page in enumerate(pages[:3]):
            page_id = page.get('id', 'Unknown ID')
            print(f"  - Page {i+1}: {page_id}")
            
        # Test data extraction from the first page
        if pages:
            page_data = notion_manager.extract_page_data(pages[0])
            print(f"\nFirst page data extraction (첫 번째 페이지 데이터 추출):")
            for key, value in page_data.items():
                if key == 'content' and value:
                    print(f"  - {key}: {value[:100]}...")
                else:
                    print(f"  - {key}: {value}")
    else:
        print("No pages in the Notion database (Notion 데이터베이스에 페이지가 없습니다)")
except Exception as e:
    print(f"❌ Notion database pages retrieval failed (Notion 데이터베이스 페이지 조회 실패): {e}")
```

### 4. Synchronization Manager Test (동기화 관리자 테스트)

```python
# Cell 12: Initialize sync manager without Notion connection
from sync_manager import SyncManager

# Create sync manager object
sync_manager = SyncManager()

# Initialize (without Notion connection for testing)
try:
    sync_manager.initialize(connect_notion=False)
    print("✅ Sync manager initialization successful without Notion (동기화 관리자 초기화 성공 - Notion 연결 없음)")
except Exception as e:
    print(f"❌ Sync manager initialization failed (동기화 관리자 초기화 실패): {e}")

# Cell 13: Initialize sync manager with Notion connection
try:
    sync_manager.initialize(connect_notion=True)
    print("✅ Sync manager initialization successful with Notion (동기화 관리자 초기화 성공 - Notion 연결 있음)")
except Exception as e:
    print(f"❌ Sync manager initialization failed (동기화 관리자 초기화 실패): {e}")

# Check Notion database (now automatically connected)
try:
    notion_pages = sync_manager.check_notion_database()
    print(f"✅ Notion database check successful (Notion 데이터베이스 확인 성공): {len(notion_pages)} pages found")
    
    # Preview first 3 pages
    if notion_pages:
        print("\nFirst 3 pages (처음 3개 페이지):")
        for i, page in enumerate(notion_pages[:3]):
            print(f"  - Page {i+1}: {page['title'][:50]}... (ID: {page['notion_page_id'][:10]}...)")
    else:
        print("No pages in Notion database (Notion 데이터베이스에 페이지가 없습니다)")
except Exception as e:
    print(f"❌ Notion database check failed (Notion 데이터베이스 확인 실패): {e}")

# Cell 14: Check TTRSS entries
try:
    ttrss_entries = sync_manager.check_ttrss_entries()
    print(f"✅ TTRSS entries check successful (TTRSS 항목 확인 성공): {len(ttrss_entries)} entries found")
    
    # Preview first 3 entries
    if ttrss_entries:
        print("\nFirst 3 entries (처음 3개 항목):")
        for i, entry in enumerate(ttrss_entries[:3]):
            print(f"  - Entry {i+1}: {entry['title'][:50]}... (ID: {entry['id']})")
    else:
        print("No entries in TTRSS. You may need to subscribe to feeds and update them.")
        print("(TTRSS에 항목이 없습니다. 피드를 구독하고 업데이트해야 할 수 있습니다)")
except Exception as e:
    print(f"❌ TTRSS entries check failed (TTRSS 항목 확인 실패): {e}")

# Cell 15: Compare TTRSS with sync table
try:
    new_entries = sync_manager.compare_ttrss_with_sync()
    print(f"✅ TTRSS and sync table comparison successful (TTRSS와 동기화 테이블 비교 성공): {len(new_entries)} new entries found")
    
    # Preview first 3 new entries
    if new_entries:
        print("\nFirst 3 new entries (처음 3개 새 항목):")
        for i, entry in enumerate(new_entries[:3]):
            print(f"  - New Entry {i+1}: {entry['title'][:50]}... (ID: {entry['id']})")
    else:
        print("All TTRSS entries are already in the sync table")
        print("(모든 TTRSS 항목이 이미 동기화 테이블에 있습니다)")
except Exception as e:
    print(f"❌ TTRSS and sync table comparison failed (TTRSS와 동기화 테이블 비교 실패): {e}")

# Cell 16: Compare Notion with sync table
try:
    new_notion_entries = sync_manager.compare_notion_with_sync()
    print(f"✅ Notion and sync table comparison successful (Notion과 동기화 테이블 비교 성공): {len(new_notion_entries)} new entries found")
    
    # Preview first 3 new entries
    if new_notion_entries:
        print("\nFirst 3 new entries (처음 3개 새 항목):")
        for i, entry in enumerate(new_notion_entries[:3]):
            print(f"  - New Entry {i+1}: {entry['title'][:50]}... (ID: {entry['notion_page_id'][:10]}...)")
    else:
        print("All Notion pages are already in the sync table")
        print("(모든 Notion 페이지가 이미 동기화 테이블에 있습니다)")
except Exception as e:
    print(f"❌ Notion and sync table comparison failed (Notion과 동기화 테이블 비교 실패): {e}")

# Cell 17: Get entries to sync to Notion
try:
    entries_to_sync = sync_manager.get_entries_to_sync_to_notion()
    print(f"✅ Retrieved {len(entries_to_sync)} entries to sync to Notion")
    
    # Preview first 3 entries
    if entries_to_sync:
        print("\nFirst 3 entries to sync (처음 3개 동기화할 항목):")
        for i, entry in enumerate(entries_to_sync[:3]):
            print(f"  - Entry {i+1}: {entry['title'][:50]}... (ID: {entry['id']})")
    else:
        print("No entries to sync to Notion")
        print("(Notion에 동기화할 항목이 없습니다)")
except Exception as e:
    print(f"❌ Failed to get entries to sync to Notion: {e}")

# Cell 18: Sync TTRSS to sync table
# Uncomment to run
"""
try:
    new_entries = sync_manager.sync_ttrss_to_db()
    print(f"✅ Synced {len(new_entries)} new TTRSS entries to sync table")
    
    # Preview synced entries
    if new_entries:
        print("\nNew synced entries (새로 동기화된 항목):")
        for i, entry in enumerate(new_entries[:5]):  # Show up to 5
            print(f"  - Entry {i+1}: {entry['title'][:50]}... (ID: {entry['id']})")
    else:
        print("No new entries synced (새로 동기화된 항목이 없습니다)")
except Exception as e:
    print(f"❌ TTRSS to sync table synchronization failed: {e}")
"""

# Cell 19: Sync from Notion to sync table
# Uncomment to run
"""
try:
    new_entries = sync_manager.sync_notion_to_db()
    print(f"✅ Synced {len(new_entries)} new Notion pages to sync table")
    
    # Preview synced entries
    if new_entries:
        print("\nNew synced entries (새로 동기화된 항목):")
        for i, entry in enumerate(new_entries[:5]):  # Show up to 5
            print(f"  - Entry {i+1}: {entry['title'][:50]}... (Notion ID: {entry['notion_page_id'][:10]}...)")
    else:
        print("No new entries synced (새로 동기화된 항목이 없습니다)")
except Exception as e:
    print(f"❌ Notion to sync table synchronization failed: {e}")
"""

# Cell 20: Sync entries from sync table to Notion
# Uncomment to run
"""
try:
    synced_entries = sync_manager.sync_to_notion()
    print(f"✅ Synced {len(synced_entries)} entries from sync table to Notion")
    
    # Preview synced entries
    if synced_entries:
        print("\nSynced entries (동기화된 항목):")
        for i, entry in enumerate(synced_entries[:5]):  # Show up to 5
            print(f"  - Entry {i+1}: {entry['title'][:50]}... (ID: {entry['id']})")
    else:
        print("No entries synced to Notion (Notion에 동기화된 항목이 없습니다)")
except Exception as e:
    print(f"❌ Sync table to Notion synchronization failed: {e}")
"""

# Cell 21: Run full synchronization
# Uncomment to run
"""
try:
    result = sync_manager.full_sync()
    
    # Extract results
    notion_to_db = result.get('notion_to_db', [])
    ttrss_to_db = result.get('ttrss_to_db', [])
    sync_to_notion = result.get('sync_to_notion', [])
    
    print(f"✅ Full synchronization completed")
    print(f"  - Synced {len(notion_to_db)} Notion pages to sync table")
    print(f"  - Synced {len(ttrss_to_db)} TTRSS entries to sync table")
    print(f"  - Synced {len(sync_to_notion)} entries from sync table to Notion")
    
    # Show summary of changes
    if any([notion_to_db, ttrss_to_db, sync_to_notion]):
        print("\nSynchronization Summary (동기화 요약):")
        
        if notion_to_db:
            print(f"\nNotion → Sync Table ({len(notion_to_db)} entries):")
            for i, entry in enumerate(notion_to_db[:3]):  # Show up to 3
                print(f"  - Entry {i+1}: {entry['title'][:50]}...")
                
        if ttrss_to_db:
            print(f"\nTTRSS → Sync Table ({len(ttrss_to_db)} entries):")
            for i, entry in enumerate(ttrss_to_db[:3]):  # Show up to 3
                print(f"  - Entry {i+1}: {entry['title'][:50]}...")
                
        if sync_to_notion:
            print(f"\nSync Table → Notion ({len(sync_to_notion)} entries):")
            for i, entry in enumerate(sync_to_notion[:3]):  # Show up to 3
                print(f"  - Entry {i+1}: {entry['title'][:50]}...")
    else:
        print("\nNo changes needed - all systems in sync")
        print("(변경 사항 없음 - 모든 시스템이 동기화되어 있습니다)")
except Exception as e:
    print(f"❌ Full synchronization failed: {e}")
"""

### 5. Enhanced Synchronization Logic Testing (향상된 동기화 로직 테스트)

```python
# Cell 22: Test full synchronization
from sync_manager import SyncManager

# Create sync manager object (connects to TTRSS, sync table, and Notion)
sync_manager = SyncManager()

# Test full sync process
try:
    print("\nPerforming full synchronization test (전체 동기화 테스트 수행):")
    print("Step 1: Syncing Notion to sync table")
    print("Step 2: Syncing TTRSS to sync table")
    print("Step 3: Checking for title matches and updating sync status")
    print("Step 4: Syncing new entries to Notion")
    
    # Perform full sync
    sync_summary = sync_manager.perform_full_sync()
    
    # Print summary
    print("\n✅ Full sync completed successfully (전체 동기화 성공적으로 완료)")
    print(f"Sync Summary (동기화 요약):")
    print(f"- Added from Notion (Notion에서 추가됨): {sync_summary['added_notion']}")
    print(f"- Removed from sync table (동기화 테이블에서 제거됨): {sync_summary['removed_sync']}")
    print(f"- Added from TTRSS (TTRSS에서 추가됨): {sync_summary['added_ttrss']}")
    print(f"- Updated matches by title (제목 일치로 업데이트됨): {sync_summary['updated_matches']}")
    print(f"- Synced to Notion (Notion에 동기화됨): {sync_summary['synced_notion']}")
    
except Exception as e:
    print(f"❌ Full sync failed (전체 동기화 실패): {e}")
    import traceback
    traceback.print_exc()

# Close connections
sync_manager.close_connections()
print("Connections closed (연결 종료)")
```

### 6. Enhanced Synchronization Logic Testing (향상된 동기화 로직 테스트)

```python
# Cell 23: Test duplicate title detection and sync status update
try:
    # Create managers
    db_manager = DatabaseManager()
    db_manager.connect()
    
    # Step 1: Get sample entries from both Notion and TTRSS
    print("Testing title matching functionality (제목 일치 기능 테스트):")
    notion_entries = db_manager.get_sync_entries(source='notion')
    ttrss_entries = db_manager.get_sync_entries(source='ttrss', synced=False)
    
    if notion_entries and ttrss_entries:
        # Select a sample entry from each
        notion_sample = notion_entries[0]
        ttrss_sample = ttrss_entries[0]
        
        print(f"Notion sample title: {notion_sample['title'][:50]}...")
        print(f"TTRSS sample title: {ttrss_sample['title'][:50]}...")
        
        # Step 2: Test find_matching_entries_by_title function
        print("\nTesting find_matching_entries_by_title function:")
        matches = db_manager.find_matching_entries_by_title(notion_sample['title'])
        print(f"Found {len(matches)} matches for the Notion sample title")
        
        # Step 3: Test update_duplicate_entries_sync_status function
        print("\nTesting update_duplicate_entries_sync_status function:")
        updated_count = db_manager.update_duplicate_entries_sync_status()
        print(f"Updated {updated_count} entries based on title matching")
        
        # Verify the updates
        ttrss_entries_after = db_manager.get_sync_entries(source='ttrss', synced=False)
        print(f"TTRSS unsynced entries before: {len(ttrss_entries)}")
        print(f"TTRSS unsynced entries after: {len(ttrss_entries_after)}")
        print(f"Difference (should match updated_count): {len(ttrss_entries) - len(ttrss_entries_after)}")
    else:
        print("Not enough entries to test title matching (either Notion or TTRSS entries missing)")
    
    # Close connection
    db_manager.close()
    
except Exception as e:
    print(f"❌ Title matching test failed: {e}")
    import traceback
    traceback.print_exc()
```

### 7. Docker Setup Guide (Docker 설정 가이드)

```python
# Cell 24: Docker Environment Information
"""
# Docker Environment Setup (Docker 환경 설정)

This application has been configured to work with a Docker-based TTRSS setup.
Current Docker configuration:

1. PostgreSQL Database:
   - Container name: ttrss-db
   - Port: 5432 (mapped to host 5432)
   - Database: ttrss
   - Username: ttrss
   - Password: handbook12

2. TTRSS Application:
   - Container name: ttrss-app
   - Port: 8080 (mapped to host 8080)
   - Admin login: admin/handbook12
   - Web interface: http://localhost:8080/

To check if your Docker containers are running:
```
docker ps | grep ttrss
```

To restart the containers if needed:
```
docker restart ttrss-db ttrss-app
```

If you need to modify your .env file to match the Docker setup:
```
DB_HOST=localhost  # or the Docker container IP if not using host networking
DB_PORT=5432
DB_NAME=ttrss
DB_USER=ttrss
DB_PASSWORD=handbook12
NOTION_DATABASE_ID=your_notion_database_id
NOTION_API_KEY=your_notion_api_key
```
"""
```

## 8. Troubleshooting Guide (문제 해결 가이드)

```python
# Cell 25: Troubleshooting Guide
"""
# Troubleshooting Guide (문제 해결 가이드)

## 1. Database Connection Issues:

### Problem: Cannot connect to PostgreSQL database
- Check if the Docker container is running: `docker ps | grep ttrss-db`
- Verify PostgreSQL port is accessible: `nc -zv localhost 5432`
- Check your .env file for correct credentials
- Try connecting manually: `psql -h localhost -p 5432 -U ttrss -d ttrss`

### Problem: "password authentication failed"
- Ensure DB_PASSWORD in .env matches the PostgreSQL user password
- For Docker setup, default is: ttrss/handbook12

## 2. Notion API Issues:

### Problem: Notion API authentication failed
- Verify your API key is correct and not expired
- Check if the integration has access to the database
- Make sure the database ID is correct

### Problem: "body failed validation" errors
- This often happens with long content fields
- Typical solution: Truncate content to 2000 characters before sending to Notion

## 3. Synchronization Issues:

### Problem: No entries in TTRSS
- Login to TTRSS web interface (http://localhost:8080/)
- Subscribe to RSS feeds and refresh them
- Check if articles are visible in the TTRSS interface

### Problem: Entries not syncing to Notion
- Check if entries are in the sync table: `sync_entries = db_manager.get_sync_entries()`
- Verify sync_status values, only entries with sync_status=0 will be synced
- Ensure your Notion database has all required properties

### Problem: Character encoding issues
- TTRSS content may contain special characters or HTML
- Try enabling content cleaning: update `notion_manager.py` to sanitize text
"""
```

## How to Apply These Changes

1. Create new cells in your Jupyter notebook following the structure above
2. Copy the Python code from each section
3. Run each cell to test functionality
4. Adjust the code as needed for your specific setup

## Docker TTRSS Configuration

Your TTRSS installation is configured with Docker using:

- PostgreSQL database container (ttrss-db) with port forwarding to 5432
- TTRSS application container with port forwarding to 8080
- Database credentials: ttrss/handbook12
- Admin login credentials: admin/handbook12

For any issues with the Docker setup, check the troubleshooting section above.
