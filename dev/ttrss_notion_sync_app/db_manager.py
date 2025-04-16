"""
Database management module for handling TTRSS database operations.
"""
import psycopg2
from datetime import datetime, timedelta
import pytz
from bs4 import BeautifulSoup
from config import DB_CONFIG, TTRSS_ENTRIES_TABLE, SYNC_TABLE, logger

def convert_to_kst(utc_time):
    """Convert UTC datetime to KST (UTC+9)"""
    if utc_time is None:
        return None
        
    # If the datetime object doesn't have tzinfo, assume it's UTC
    if utc_time.tzinfo is None:
        utc_time = utc_time.replace(tzinfo=pytz.UTC)
    
    # Convert to KST (UTC+9)
    kst = pytz.timezone('Asia/Seoul')
    kst_time = utc_time.astimezone(kst)
    
    return kst_time

class DatabaseManager:
    """Class to manage database connections and operations"""
    
    def __init__(self):
        self.conn = None
        
    def connect(self):
        """Connect to the TTRSS database"""
        try:
            self.conn = psycopg2.connect(
                host=DB_CONFIG["host"],
                port=DB_CONFIG["port"],
                dbname=DB_CONFIG["dbname"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"]
            )
            logger.info("Connected to TTRSS database successfully")
            return self.conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
            
    def table_exists(self, table_name):
        """Check if a table exists in the database"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """, (table_name,))
            return cur.fetchone()[0]
            
    def create_sync_table(self):
        """Create a new table to sync TTRSS entries with Notion database if it doesn't exist"""
        if self.table_exists(SYNC_TABLE):
            # Check if category, tag, ai_summary, and why_it_matters columns exist, add them if not
            with self.conn.cursor() as cur:
                cur.execute(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = '{SYNC_TABLE}' AND column_name = 'category'
                    )
                """)
                category_exists = cur.fetchone()[0]
                
                if not category_exists:
                    cur.execute(f"ALTER TABLE {SYNC_TABLE} ADD COLUMN category TEXT")
                    logger.info(f"Added category column to {SYNC_TABLE}")
                
                cur.execute(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = '{SYNC_TABLE}' AND column_name = 'tag'
                    )
                """)
                tag_exists = cur.fetchone()[0]
                
                if not tag_exists:
                    cur.execute(f"ALTER TABLE {SYNC_TABLE} ADD COLUMN tag TEXT")
                    logger.info(f"Added tag column to {SYNC_TABLE}")
                    
                # Check for ai_summary column
                cur.execute(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = '{SYNC_TABLE}' AND column_name = 'ai_summary'
                    )
                """)
                ai_summary_exists = cur.fetchone()[0]
                
                if not ai_summary_exists:
                    cur.execute(f"ALTER TABLE {SYNC_TABLE} ADD COLUMN ai_summary TEXT")
                    logger.info(f"Added ai_summary column to {SYNC_TABLE}")
                    
                # Check for why_it_matters column
                cur.execute(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = '{SYNC_TABLE}' AND column_name = 'why_it_matters'
                    )
                """)
                why_it_matters_exists = cur.fetchone()[0]
                
                if not why_it_matters_exists:
                    cur.execute(f"ALTER TABLE {SYNC_TABLE} ADD COLUMN why_it_matters TEXT")
                    logger.info(f"Added why_it_matters column to {SYNC_TABLE}")
                
                self.conn.commit()
            
            logger.info(f"Table {SYNC_TABLE} already exists, skipping creation")
            return False
            
        with self.conn.cursor() as cur:
            # Create the sync table
            cur.execute(f"""
                CREATE TABLE {SYNC_TABLE} (
                    id SERIAL PRIMARY KEY,
                    ttrss_entry_id INTEGER REFERENCES {TTRSS_ENTRIES_TABLE}(id),
                    notion_page_id TEXT,
                    title TEXT,
                    content TEXT,
                    category TEXT,
                    tag TEXT,
                    ai_summary TEXT,
                    why_it_matters TEXT,
                    link TEXT,
                    published TIMESTAMP,
                    updated TIMESTAMP,
                    source TEXT,           -- Where the entry originated from: 'ttrss' or 'notion'
                    synced_to_notion BOOLEAN DEFAULT FALSE,
                    last_sync TIMESTAMP
                )
            """)
            self.conn.commit()
            logger.info(f"Created {SYNC_TABLE} table")
            return True
            
    def get_ttrss_entries_schema(self):
        """Get the schema of ttrss_entries table"""
        with self.conn.cursor() as cur:
            cur.execute(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{TTRSS_ENTRIES_TABLE}'
            """)
            schema = cur.fetchall()
            logger.info(f"Retrieved {TTRSS_ENTRIES_TABLE} schema")
            return schema
            
    def get_ttrss_entries(self):
        """Get all entries from ttrss_entries table with timestamps converted to KST"""
        with self.conn.cursor() as cur:
            cur.execute(f"""
                SELECT id, title, link, updated, content, date_entered, date_updated, author
                FROM {TTRSS_ENTRIES_TABLE}
                ORDER BY date_updated DESC
            """)
            columns = [desc[0] for desc in cur.description]
            entries = []
            
            for row in cur.fetchall():
                entry = dict(zip(columns, row))
                
                # Convert datetime fields to KST
                if 'date_entered' in entry and entry['date_entered']:
                    entry['date_entered'] = convert_to_kst(entry['date_entered'])
                if 'date_updated' in entry and entry['date_updated']:
                    entry['date_updated'] = convert_to_kst(entry['date_updated'])
                if 'updated' in entry and entry['updated']:
                    entry['updated'] = convert_to_kst(entry['updated'])
                    
                entries.append(entry)
                
            logger.info(f"Retrieved {len(entries)} entries from {TTRSS_ENTRIES_TABLE} (timestamps converted to KST)")
            return entries
            
    def get_sync_entries(self):
        """Get all entries from the sync table with timestamps converted to KST"""
        with self.conn.cursor() as cur:
            cur.execute(f"""
                SELECT id, ttrss_entry_id, notion_page_id, title, content, category, tag, ai_summary, why_it_matters, link, 
                       published, updated, source, synced_to_notion, last_sync
                FROM {SYNC_TABLE}
                ORDER BY updated DESC
            """)
            columns = [desc[0] for desc in cur.description]
            entries = []
            
            for row in cur.fetchall():
                entry = dict(zip(columns, row))
                
                # Convert datetime fields to KST
                if 'published' in entry and entry['published']:
                    entry['published'] = convert_to_kst(entry['published'])
                if 'updated' in entry and entry['updated']:
                    entry['updated'] = convert_to_kst(entry['updated'])
                if 'last_sync' in entry and entry['last_sync']:
                    entry['last_sync'] = convert_to_kst(entry['last_sync'])
                    
                entries.append(entry)
                
            logger.info(f"Retrieved {len(entries)} entries from {SYNC_TABLE} (timestamps converted to KST)")
            return entries
            
    def check_duplicate_entry(self, entry, source):
        """
        Check if an entry already exists in the sync table
        Uses title and link to identify duplicates
        
        Args:
            entry (dict): The entry to check
            source (str): The source of the entry ('ttrss' or 'notion')
            
        Returns:
            dict or None: The existing entry if found, None otherwise
        """
        with self.conn.cursor() as cur:
            # Check by exact title and link match
            query = f"""
                SELECT id, ttrss_entry_id, notion_page_id, title, link, source
                FROM {SYNC_TABLE}
                WHERE (title = %s AND link = %s)
            """
            params = [entry.get('title'), entry.get('link')]
            
            if source == 'ttrss' and 'id' in entry:
                # Also check for TTRSS entry ID if this is a TTRSS entry
                query += " OR ttrss_entry_id = %s"
                params.append(entry['id'])
            elif source == 'notion' and 'notion_page_id' in entry:
                # Also check for Notion page ID if this is a Notion entry
                query += " OR notion_page_id = %s"
                params.append(entry['notion_page_id'])
                
            cur.execute(query, params)
            result = cur.fetchone()
            
            if result:
                columns = [desc[0] for desc in cur.description]
                existing_entry = dict(zip(columns, result))
                logger.info(f"Found duplicate entry: {existing_entry['id']} (source: {existing_entry['source']})")
                return existing_entry
            
            logger.debug(f"No duplicate found for entry with title: {entry.get('title')}")
            return None
    
    def add_ttrss_entry_to_sync(self, entry):
        """Add a TTRSS entry to the sync table if it doesn't exist already"""
        # Check for duplicates first
        existing_entry = self.check_duplicate_entry(entry, 'ttrss')
        if existing_entry:
            logger.info(f"Skipping duplicate TTRSS entry: {entry['id']} (title: {entry['title']})")
            return existing_entry['id']
            
        # Convert HTML content to plain text
        plain_text_content = self.html_to_text(entry['content'])
        
        # Extract category and tag if available
        category = entry.get('category', '')
        tag = entry.get('tag', '')
            
        with self.conn.cursor() as cur:
            cur.execute(f"""
                INSERT INTO {SYNC_TABLE} 
                (ttrss_entry_id, title, content, category, tag, ai_summary, why_it_matters, link, published, updated, source)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                entry['id'], 
                entry['title'],
                plain_text_content,
                category,
                tag,
                entry.get('ai_summary', ''),
                entry.get('why_it_matters', ''),
                entry['link'],
                entry['date_entered'],
                entry['date_updated'],
                'ttrss'
            ))
            new_id = cur.fetchone()[0]
            self.conn.commit()
            logger.info(f"Added TTRSS entry {entry['id']} to sync table with ID {new_id}")
            return new_id
            
    def add_notion_entry_to_sync(self, entry):
        """Add a Notion entry to the sync table, replacing any existing entry with the same title and URL"""
        # Check for duplicates first
        existing_entry = self.check_duplicate_entry(entry, 'notion')
        
        # If duplicate exists, delete it to replace with the new entry from Notion
        if existing_entry:
            logger.info(f"Found duplicate entry: {existing_entry['id']} (title: {entry['title']}). Replacing with Notion data.")
            self.delete_sync_entry(existing_entry['id'])
            
        # Check if content is empty and try to find matching TTRSS entry for content
        if not entry.get('content') or entry.get('content') == "":
            # First check if there's a TTRSS entry with the same title in the sync table
            ttrss_entries = self.find_matching_entries_by_title(entry['title'])
            ttrss_entries = [e for e in ttrss_entries if e['source'] == 'ttrss']
            
            if ttrss_entries:
                # Get the content of the first matching TTRSS entry
                with self.conn.cursor() as cur:
                    cur.execute(f"""
                        SELECT content FROM {SYNC_TABLE}
                        WHERE id = %s
                    """, (ttrss_entries[0]['id'],))
                    result = cur.fetchone()
                    if result and result[0]:
                        entry['content'] = result[0]
                        logger.info(f"Using content from matching TTRSS entry for Notion entry: {entry['title'][:50]}...")
                        entry['source'] = 'ttrss'  # Change source to ttrss
            
            # If no matching entry in sync table, try to find in TTRSS entries table
            if (not entry.get('content') or entry.get('content') == "") and entry.get('title'):
                with self.conn.cursor() as cur:
                    cur.execute(f"""
                        SELECT content FROM {TTRSS_ENTRIES_TABLE}
                        WHERE title = %s
                        LIMIT 1
                    """, (entry['title'],))
                    result = cur.fetchone()
                    if result and result[0]:
                        # Convert HTML to text for better readability in Notion
                        entry['content'] = self.html_to_text(result[0])
                        logger.info(f"Using content from TTRSS entries table for Notion entry: {entry['title'][:50]}...")
                        entry['source'] = 'ttrss'  # Change source to ttrss
            
        with self.conn.cursor() as cur:
            cur.execute(f"""
                INSERT INTO {SYNC_TABLE} 
                (notion_page_id, title, content, category, tag, ai_summary, why_it_matters, link, published, updated, source, synced_to_notion)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                entry['notion_page_id'],
                entry['title'],
                entry['content'],
                entry.get('category', ''),
                entry.get('tag', ''),
                entry.get('ai_summary', ''),
                entry.get('why_it_matters', ''),
                entry['link'],
                entry['published'],
                entry['updated'],
                entry.get('source', 'notion'),  # Use the potentially updated source
                True  # Notion 항목은 이미 Notion에 있으므로 synced_to_notion=TRUE로 설정
            ))
            new_id = cur.fetchone()[0]
            self.conn.commit()
            logger.info(f"Added Notion page {entry['notion_page_id']} to sync table with ID {new_id} (synced_to_notion=TRUE)")
            return new_id
            
    def update_sync_status(self, sync_id, notion_page_id):
        """Update the sync status of an entry in the sync table"""
        with self.conn.cursor() as cur:
            cur.execute(f"""
                UPDATE {SYNC_TABLE}
                SET notion_page_id = %s, synced_to_notion = TRUE, last_sync = NOW()
                WHERE id = %s
            """, (notion_page_id, sync_id))
            self.conn.commit()
            logger.info(f"Updated sync status for entry {sync_id}")
            
    def compare_ttrss_with_sync(self):
        """
        Compare TTRSS entries table with sync table
        Returns entries that are in TTRSS but not in the sync table
        """
        with self.conn.cursor() as cur:
            cur.execute(f"""
                SELECT t.id, t.title, t.link, t.updated, t.content, t.date_entered, t.date_updated, t.author
                FROM {TTRSS_ENTRIES_TABLE} t
                LEFT JOIN {SYNC_TABLE} s ON t.id = s.ttrss_entry_id
                WHERE s.id IS NULL
                ORDER BY t.date_updated DESC
            """)
            columns = [desc[0] for desc in cur.description]
            entries = [dict(zip(columns, row)) for row in cur.fetchall()]
            logger.info(f"Found {len(entries)} entries in TTRSS that are not in sync table")
            return entries
            
    def find_entries_to_sync_to_notion(self):
        """Find entries in the sync table that need to be synced to Notion"""
        with self.conn.cursor() as cur:
            cur.execute(f"""
                SELECT id, ttrss_entry_id, title, content, link, published, updated
                FROM {SYNC_TABLE}
                WHERE source = 'ttrss' AND synced_to_notion = FALSE
            """)
            columns = [desc[0] for desc in cur.description]
            entries = [dict(zip(columns, row)) for row in cur.fetchall()]
            logger.info(f"Found {len(entries)} entries to sync to Notion")
            return entries
            
    def find_matching_entries_by_title(self, title):
        """Find entries in the sync table that have the same title"""
        with self.conn.cursor() as cur:
            cur.execute(f"""
                SELECT id, notion_page_id, title, source, synced_to_notion
                FROM {SYNC_TABLE}
                WHERE title = %s
            """, (title,))
            columns = [desc[0] for desc in cur.description]
            entries = [dict(zip(columns, row)) for row in cur.fetchall()]
            return entries
            
    def update_duplicate_entries_sync_status(self):
        """
        Find entries with identical titles and update their sync status.
        If a Notion entry and a TTRSS entry share the same title, mark the TTRSS entry as synced
        """
        updated_count = 0
        content_updated_count = 0
        with self.conn.cursor() as cur:
            # Find all duplicate titles in the sync table
            cur.execute(f"""
                SELECT title
                FROM {SYNC_TABLE}
                GROUP BY title
                HAVING COUNT(*) > 1
            """)
            duplicate_titles = [row[0] for row in cur.fetchall()]
            
            for title in duplicate_titles:
                # For each duplicate title, check if there's a Notion entry
                cur.execute(f"""
                    SELECT id, notion_page_id, synced_to_notion, content
                    FROM {SYNC_TABLE}
                    WHERE title = %s AND source = 'notion'
                """, (title,))
                notion_entries = cur.fetchall()
                
                # Check for TTRSS entries with the same title
                cur.execute(f"""
                    SELECT id, content
                    FROM {SYNC_TABLE}
                    WHERE title = %s AND source = 'ttrss' AND synced_to_notion = FALSE
                """, (title,))
                ttrss_entries = cur.fetchall()
                
                if notion_entries and ttrss_entries:
                    # Check if Notion entry has empty content
                    notion_entry = notion_entries[0]
                    notion_id = notion_entry[0]
                    notion_page_id = notion_entry[1]
                    notion_content = notion_entry[3]
                    
                    # If Notion content is empty, get content from TTRSS
                    if not notion_content or notion_content.strip() == "":
                        ttrss_entry = ttrss_entries[0]
                        ttrss_content = ttrss_entry[1]
                        
                        if ttrss_content and ttrss_content.strip() != "":
                            # Update Notion entry with TTRSS content and change source to 'ttrss'
                            cur.execute(f"""
                                UPDATE {SYNC_TABLE}
                                SET content = %s, source = 'ttrss'
                                WHERE id = %s
                            """, (ttrss_content, notion_id))
                            content_updated_count += 1
                            logger.info(f"Updated Notion entry {notion_id} with content from TTRSS entry for title '{title[:30]}...'")
                        else:
                            # If sync table TTRSS content is also empty, try to get content from ttrss_entries table
                            cur.execute(f"""
                                SELECT content FROM {TTRSS_ENTRIES_TABLE}
                                WHERE title = %s
                                LIMIT 1
                            """, (title,))
                            result = cur.fetchone()
                            if result and result[0]:
                                # Convert HTML to text for better readability
                                plain_text_content = self.html_to_text(result[0])
                                # Update Notion entry with TTRSS content and change source to 'ttrss'
                                cur.execute(f"""
                                    UPDATE {SYNC_TABLE}
                                    SET content = %s, source = 'ttrss'
                                    WHERE id = %s
                                """, (plain_text_content, notion_id))
                                content_updated_count += 1
                                logger.info(f"Updated Notion entry {notion_id} with content from TTRSS entries table for title '{title[:30]}...'")
                    
                    # Mark TTRSS entries as synced
                    cur.execute(f"""
                        UPDATE {SYNC_TABLE}
                        SET synced_to_notion = TRUE,
                            last_sync = NOW(),
                            notion_page_id = %s
                        WHERE title = %s 
                          AND source = 'ttrss' 
                          AND synced_to_notion = FALSE
                    """, (notion_page_id, title))
                    
                    rows_updated = cur.rowcount
                    if rows_updated > 0:
                        updated_count += rows_updated
                        logger.info(f"Updated {rows_updated} TTRSS entries with title '{title[:30]}...' to synced=TRUE based on matching Notion entry")
            
            # 추가: 마지막 단계에서 모든 Notion 항목 중 content가 비어있는 항목 확인
            cur.execute(f"""
                SELECT id, title
                FROM {SYNC_TABLE}
                WHERE source = 'notion' AND (content IS NULL OR content = '')
            """)
            empty_notion_entries = cur.fetchall()
            
            for notion_entry in empty_notion_entries:
                notion_id, title = notion_entry
                
                # ttrss_entries 테이블에서 동일한 제목의 항목 찾기
                cur.execute(f"""
                    SELECT content FROM {TTRSS_ENTRIES_TABLE}
                    WHERE title = %s
                    LIMIT 1
                """, (title,))
                result = cur.fetchone()
                
                if result and result[0]:
                    # HTML을 텍스트로 변환
                    plain_text_content = self.html_to_text(result[0])
                    
                    # Notion 항목 업데이트
                    cur.execute(f"""
                        UPDATE {SYNC_TABLE}
                        SET content = %s, source = 'ttrss'
                        WHERE id = %s
                    """, (plain_text_content, notion_id))
                    
                    content_updated_count += 1
                    logger.info(f"Final update: Notion entry {notion_id} with content from TTRSS entries for title '{title[:30]}...'")
            
            self.conn.commit()
        
        logger.info(f"Total of {updated_count} entries were marked as synced based on title matching")
        if content_updated_count > 0:
            logger.info(f"Total of {content_updated_count} Notion entries were updated with content from TTRSS entries")
        return updated_count

    def delete_sync_entry(self, sync_id):
        """Delete an entry from the sync table"""
        with self.conn.cursor() as cur:
            cur.execute(f"""
                DELETE FROM {SYNC_TABLE}
                WHERE id = %s
            """, (sync_id,))
            self.conn.commit()
            logger.info(f"Deleted entry {sync_id} from sync table")
            
    def get_sync_entries_by_notion_ids(self, notion_ids):
        """Get sync entries by Notion page IDs"""
        if not notion_ids:
            return []
            
        with self.conn.cursor() as cur:
            placeholders = ', '.join(['%s'] * len(notion_ids))
            cur.execute(f"""
                SELECT id, notion_page_id
                FROM {SYNC_TABLE}
                WHERE notion_page_id IN ({placeholders})
            """, tuple(notion_ids))
            columns = [desc[0] for desc in cur.description]
            entries = [dict(zip(columns, row)) for row in cur.fetchall()]
            return entries
            
    def update_ttrss_entries_in_sync(self):
        """
        Update all TTRSS entries in the sync table with the latest data from ttrss_entries table
        This ensures any changes in TTRSS entries are reflected in the sync table
        
        Returns:
            int: Number of entries updated
        """
        updated_count = 0
        
        # Get all entries from ttrss_entries table
        ttrss_entries = self.get_ttrss_entries()
        
        # Get all entries in sync table with ttrss source
        with self.conn.cursor() as cur:
            cur.execute(f"""
                SELECT id, ttrss_entry_id, title, link, category, tag, ai_summary, why_it_matters, updated
                FROM {SYNC_TABLE}
                WHERE source = 'ttrss'
            """)
            sync_entries = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]
        
        # Create a dictionary of TTRSS entries by ID for faster lookup
        ttrss_entries_dict = {entry['id']: entry for entry in ttrss_entries}
        
        # Update each sync entry with the latest data from TTRSS
        for sync_entry in sync_entries:
            ttrss_id = sync_entry['ttrss_entry_id']
            if ttrss_id in ttrss_entries_dict:
                ttrss_entry = ttrss_entries_dict[ttrss_id]
                
                # Check if the TTRSS entry has been updated since the last sync
                if ttrss_entry['date_updated'] > sync_entry['updated']:
                    # Convert HTML content to plain text
                    plain_text_content = self.html_to_text(ttrss_entry['content'])
                    
                    # Update the sync entry with the latest data
                    # Preserve existing category, tag, ai_summary, and why_it_matters values
                    category = sync_entry.get('category', '')
                    tag = sync_entry.get('tag', '')
                    ai_summary = sync_entry.get('ai_summary', '')
                    why_it_matters = sync_entry.get('why_it_matters', '')
                    
                    with self.conn.cursor() as cur:
                        cur.execute(f"""
                            UPDATE {SYNC_TABLE}
                            SET title = %s,
                                content = %s,
                                category = %s,
                                tag = %s,
                                ai_summary = %s,
                                why_it_matters = %s,
                                link = %s,
                                updated = %s
                            WHERE id = %s
                        """, (
                            ttrss_entry['title'],
                            plain_text_content,
                            category,
                            tag,
                            ai_summary,
                            why_it_matters,
                            ttrss_entry['link'],
                            ttrss_entry['date_updated'],
                            sync_entry['id']
                        ))
                        updated_count += 1
        
        if updated_count > 0:
            self.conn.commit()
            logger.info(f"Updated {updated_count} TTRSS entries in sync table with latest data")
        
        return updated_count
    
    def update_notion_entry_in_sync(self, notion_entry):
        """
        Update a sync table entry with the latest data from Notion
        This ensures any changes in Notion are reflected in the sync table
        
        Args:
            notion_entry (dict): Notion entry data
            
        Returns:
            bool: True if entry was updated, False otherwise
        """
        # Find the sync entry with the matching Notion page ID
        with self.conn.cursor() as cur:
            cur.execute(f"""
                SELECT id, updated
                FROM {SYNC_TABLE}
                WHERE notion_page_id = %s
            """, (notion_entry['notion_page_id'],))
            result = cur.fetchone()
            
            if not result:
                logger.debug(f"No sync entry found with Notion page ID: {notion_entry['notion_page_id']}")
                return False
            
            sync_id, sync_updated = result
            
            # Always update the sync entry with the latest data from Notion
            # as per requirement 4: "notion database에서 데이터를 수정하면, 무조건 notion database에 존재하는 데이터로 업데이트"
            cur.execute(f"""
                UPDATE {SYNC_TABLE}
                SET title = %s,
                    content = %s,
                    category = %s,
                    tag = %s,
                    ai_summary = %s,
                    why_it_matters = %s,
                    link = %s,
                    updated = %s,
                    source = 'notion'
                WHERE id = %s
            """, (
                notion_entry['title'],
                notion_entry['content'],
                notion_entry.get('category', ''),
                notion_entry.get('tag', ''),
                notion_entry.get('ai_summary', ''),
                notion_entry.get('why_it_matters', ''),
                notion_entry['link'],
                notion_entry['updated'],
                sync_id
            ))
            self.conn.commit()
            logger.info(f"Updated sync entry {sync_id} with latest data from Notion page {notion_entry['notion_page_id']}")
            return True
    
    def html_to_text(self, html_content):
        """
        Convert HTML content to plain text format
        
        Args:
            html_content (str): HTML content to convert
            
        Returns:
            str: Plain text content with HTML tags removed
        """
        if not html_content:
            return ""
            
        try:
            # Parse HTML using BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script_or_style in soup(["script", "style"]):
                script_or_style.extract()
                
            # Get text and normalize whitespace
            text = soup.get_text(separator=' ')
            
            # Normalize whitespace and clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            logger.debug(f"Converted HTML content to text (length: {len(text)} chars)")
            return text
        except Exception as e:
            logger.error(f"Error converting HTML to text: {e}")
            # Return original content if conversion fails
            return html_content
