import psycopg2
import json
from datetime import datetime
import os
from notion_client import Client
import logging
import time
from tqdm import tqdm

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database connection parameters
DB_HOST = "220.71.24.114"
DB_PORT = "5432"
DB_NAME = "ttrss"
DB_USER = "ttrss"
DB_PASSWORD = "handbook12"  # Using the password from memory

# Notion parameters
NOTION_DATABASE_ID = "1acf199edf7c8061a721d4b4d2dc3cb4"

def get_notion_api_key():
    """Get Notion API key from user input"""
    # api_key = input("Please enter your Notion API key: ")
    api_key = "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"
    return api_key

def connect_to_db():
    """Connect to the TTRSS database"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        logger.info("Connected to TTRSS database successfully")
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise

def get_ttrss_entries_schema(conn):
    """Get the schema of ttrss_entries table"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'ttrss_entries'
        """)
        schema = cur.fetchall()
        logger.info("Retrieved ttrss_entries schema")
        return schema

def create_sync_table(conn):
    """Create a new table to sync TTRSS entries with Notion database"""
    with conn.cursor() as cur:
        # Drop the table if it exists to recreate with the latest schema
        cur.execute("""
            DROP TABLE IF EXISTS ttrss_notion_sync CASCADE
        """)
        conn.commit()
        
        # Create the sync table
        cur.execute("""
            CREATE TABLE ttrss_notion_sync (
                id SERIAL PRIMARY KEY,
                ttrss_entry_id INTEGER REFERENCES ttrss_entries(id),
                notion_page_id TEXT,
                title TEXT,
                content TEXT,
                link TEXT,
                published TIMESTAMP,
                updated TIMESTAMP,
                source TEXT,           -- Where the entry originated from: 'ttrss' or 'notion'
                synced_to_notion BOOLEAN DEFAULT FALSE,
                last_sync TIMESTAMP
            )
        """)
        conn.commit()
        logger.info("Created ttrss_notion_sync table")

def get_all_ttrss_entries(conn):
    """Get all entries from ttrss_entries table"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, title, link, updated, content, date_entered, date_updated, author
            FROM ttrss_entries
            ORDER BY date_updated DESC
        """)
        columns = [desc[0] for desc in cur.description]
        entries = [dict(zip(columns, row)) for row in cur.fetchall()]
        logger.info(f"Retrieved {len(entries)} entries from ttrss_entries")
        return entries

def connect_to_notion(api_key):
    """Connect to the Notion API"""
    try:
        notion = Client(auth=api_key)
        # Test connection by querying the database
        db_info = notion.databases.retrieve(NOTION_DATABASE_ID)
        logger.info(f"Connected to Notion database: {db_info.get('title', [{}])[0].get('plain_text', 'Unknown')}")
        return notion
    except Exception as e:
        logger.error(f"Notion connection error: {e}")
        raise

def get_notion_database_structure(notion):
    """Get the structure of the Notion database"""
    try:
        db = notion.databases.retrieve(NOTION_DATABASE_ID)
        properties = db.get('properties', {})
        logger.info("Retrieved Notion database structure")
        return properties
    except Exception as e:
        logger.error(f"Error getting Notion database structure: {e}")
        raise

def get_notion_pages(notion):
    """Get all pages from the Notion database"""
    try:
        all_pages = []
        has_more = True
        start_cursor = None
        
        while has_more:
            if start_cursor:
                response = notion.databases.query(
                    database_id=NOTION_DATABASE_ID,
                    start_cursor=start_cursor
                )
            else:
                response = notion.databases.query(
                    database_id=NOTION_DATABASE_ID
                )
                
            all_pages.extend(response.get('results', []))
            has_more = response.get('has_more', False)
            start_cursor = response.get('next_cursor')
            
        logger.info(f"Retrieved {len(all_pages)} pages from Notion database")
        return all_pages
    except Exception as e:
        logger.error(f"Error getting Notion pages: {e}")
        raise

def extract_notion_page_data(page):
    """Extract relevant data from a Notion page"""
    try:
        properties = page.get('properties', {})
        
        # Extract title
        title = ""
        title_prop = properties.get('Name', properties.get('제목', properties.get('Title', {})))
        if title_prop:
            title_content = title_prop.get('title', [])
            title = " ".join([t.get('plain_text', '') for t in title_content])
        
        # Extract URL (link)
        url = ""
        url_prop = properties.get('URL', properties.get('링크', properties.get('Link', {})))
        if url_prop:
            if url_prop.get('type') == 'url':
                url = url_prop.get('url', '')
        
        # Extract content/description
        content = ""
        content_prop = properties.get('Content', properties.get('내용', properties.get('Description', {})))
        if content_prop and content_prop.get('type') == 'rich_text':
            content = " ".join([t.get('plain_text', '') for t in content_prop.get('rich_text', [])])
        
        # Extract last edited time
        last_edited = page.get('last_edited_time', '')
        if last_edited:
            last_edited = datetime.fromisoformat(last_edited.replace('Z', '+00:00'))
        
        # Extract creation time
        created_time = page.get('created_time', '')
        if created_time:
            created_time = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
        
        page_id = page.get('id', '')
        
        return {
            'notion_page_id': page_id,
            'title': title,
            'link': url,
            'content': content, 
            'updated': last_edited,
            'published': created_time
        }
    except Exception as e:
        logger.error(f"Error extracting Notion page data: {e}")
        logger.error(f"Page data: {json.dumps(page, default=str)[:500]}...")
        return None

def populate_sync_table(conn, ttrss_entries, notion_pages):
    """Populate the sync table with data from both TTRSS and Notion"""
    with conn.cursor() as cur:
        # Add TTRSS entries
        for entry in tqdm(ttrss_entries, desc="Adding TTRSS entries"):
            cur.execute("""
                INSERT INTO ttrss_notion_sync 
                (ttrss_entry_id, title, content, link, published, updated, source)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                entry['id'], 
                entry['title'],
                entry['content'],
                entry['link'],
                entry['date_entered'],
                entry['date_updated'],
                'ttrss'
            ))
        
        # Add Notion pages
        for page_data in tqdm(notion_pages, desc="Adding Notion pages"):
            data = extract_notion_page_data(page_data)
            if data:
                cur.execute("""
                    INSERT INTO ttrss_notion_sync 
                    (notion_page_id, title, content, link, published, updated, source)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    data['notion_page_id'],
                    data['title'],
                    data['content'],
                    data['link'],
                    data['published'],
                    data['updated'],
                    'notion'
                ))
        
        conn.commit()
        logger.info("Populated ttrss_notion_sync table with data from both sources")

def find_entries_to_sync_to_notion(conn):
    """Find entries in the sync table that need to be synced to Notion"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, ttrss_entry_id, title, content, link, published, updated
            FROM ttrss_notion_sync
            WHERE source = 'ttrss' AND synced_to_notion = FALSE
        """)
        columns = [desc[0] for desc in cur.description]
        entries = [dict(zip(columns, row)) for row in cur.fetchall()]
        logger.info(f"Found {len(entries)} entries to sync to Notion")
        return entries

def create_notion_page(notion, entry):
    """Create a new page in the Notion database"""
    try:
        # Prepare the page properties based on the actual Notion database structure
        properties = {
            "Name": {  # This is a standard property for the page title
                "title": [
                    {
                        "text": {
                            "content": entry['title']
                        }
                    }
                ]
            },
            "URL": {  # This matches the "URL" property seen in the database structure
                "url": entry['link'] if entry['link'] else ""
            },
            "Why it matters": {  # Using "Why it matters" instead of "Content"
                "rich_text": [
                    {
                        "text": {
                            "content": entry['content'][:2000] if entry['content'] else ""  # Notion has a limit on rich_text length
                        }
                    }
                ]
            },
            "Read": {  # Add the "Read" checkbox property
                "checkbox": False
            }
        }
        
        # Create the page
        response = notion.pages.create(
            parent={"database_id": NOTION_DATABASE_ID},
            properties=properties
        )
        
        logger.info(f"Created Notion page for entry: {entry['title']}")
        return response.get('id')
    except Exception as e:
        logger.error(f"Error creating Notion page: {e}")
        logger.error(f"Entry data: {json.dumps(entry, default=str)[:500]}...")
        return None

def update_sync_status(conn, sync_id, notion_page_id):
    """Update the sync status of an entry in the sync table"""
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE ttrss_notion_sync
            SET notion_page_id = %s, synced_to_notion = TRUE, last_sync = NOW()
            WHERE id = %s
        """, (notion_page_id, sync_id))
        conn.commit()
        logger.info(f"Updated sync status for entry {sync_id}")

def sync_to_notion(conn, notion, entries):
    """Sync entries to Notion"""
    for entry in tqdm(entries, desc="Syncing to Notion"):
        # Create a new page in Notion
        notion_page_id = create_notion_page(notion, entry)
        
        if notion_page_id:
            # Update the sync status
            update_sync_status(conn, entry['id'], notion_page_id)
            
            # Add a small delay to avoid rate limiting
            time.sleep(0.5)

def main():
    """Main function to run the script"""
    try:
        # Get Notion API key
        notion_api_key = get_notion_api_key()
        
        # Connect to the Notion API
        notion = connect_to_notion(notion_api_key)
        
        # Get the Notion database structure
        notion_db_structure = get_notion_database_structure(notion)
        logger.info(f"Notion database properties: {json.dumps(notion_db_structure, indent=2, default=str)[:1000]}...")
        
        # Get all pages from the Notion database
        notion_pages = get_notion_pages(notion)
        
        # Connect to the TTRSS database
        conn = connect_to_db()
        
        # Create the sync table
        create_sync_table(conn)
        
        # Get all entries from the TTRSS database
        ttrss_entries = get_all_ttrss_entries(conn)
        
        # Populate the sync table with data from both sources
        populate_sync_table(conn, ttrss_entries, notion_pages)
        
        # Find entries that need to be synced to Notion
        entries_to_sync = find_entries_to_sync_to_notion(conn)
        
        # Sync entries to Notion
        if entries_to_sync:
            sync_to_notion(conn, notion, entries_to_sync)
            logger.info(f"Successfully synced {len(entries_to_sync)} entries to Notion")
        else:
            logger.info("No entries to sync to Notion")
        
        # Close the connection
        conn.close()
        
        logger.info("Sync completed successfully")
        
    except Exception as e:
        logger.error(f"Error in main function: {e}")

if __name__ == "__main__":
    main()
