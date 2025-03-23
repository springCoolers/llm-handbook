"""
Notion API management module for handling Notion database operations.
"""
from notion_client import Client
from datetime import datetime
import json
from config import NOTION_DATABASE_ID, NOTION_API_KEY, logger

class NotionManager:
    """Class to manage Notion API operations"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or NOTION_API_KEY
        self.client = None
        self.database_id = NOTION_DATABASE_ID
        
    def connect(self):
        """Connect to the Notion API"""
        try:
            self.client = Client(auth=self.api_key)
            # Test connection by querying the database
            db_info = self.client.databases.retrieve(self.database_id)
            db_name = db_info.get('title', [{}])[0].get('plain_text', 'Unknown')
            logger.info(f"Connected to Notion database: {db_name}")
            return self.client
        except Exception as e:
            logger.error(f"Notion connection error: {e}")
            raise
            
    def get_database_structure(self):
        """Get the structure of the Notion database"""
        try:
            db = self.client.databases.retrieve(self.database_id)
            properties = db.get('properties', {})
            logger.info("Retrieved Notion database structure")
            return properties
        except Exception as e:
            logger.error(f"Error getting Notion database structure: {e}")
            raise
            
    def get_database_pages(self):
        """Get all pages from the Notion database"""
        try:
            all_pages = []
            has_more = True
            start_cursor = None
            
            while has_more:
                if start_cursor:
                    response = self.client.databases.query(
                        database_id=self.database_id,
                        start_cursor=start_cursor
                    )
                else:
                    response = self.client.databases.query(
                        database_id=self.database_id
                    )
                    
                all_pages.extend(response.get('results', []))
                has_more = response.get('has_more', False)
                start_cursor = response.get('next_cursor')
                
            logger.info(f"Retrieved {len(all_pages)} pages from Notion database")
            return all_pages
        except Exception as e:
            logger.error(f"Error getting Notion pages: {e}")
            raise
            
    def extract_page_data(self, page):
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
            
            # Extract content/description from "Why it matters" field
            content = ""
            content_prop = properties.get('Why it matters', properties.get('내용', properties.get('Description', {})))
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
            
    def create_page(self, entry):
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
            response = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            
            logger.info(f"Created Notion page for entry: {entry['title']}")
            return response.get('id')
        except Exception as e:
            logger.error(f"Error creating Notion page: {e}")
            logger.error(f"Entry data: {json.dumps(entry, default=str)[:500]}...")
            return None
            
    def delete_page(self, page_id):
        """Archive a page in Notion (Notion doesn't allow true deletion via API)"""
        try:
            # Archive a page in Notion
            response = self.client.pages.update(
                page_id=page_id,
                archived=True
            )
            
            logger.info(f"Archived Notion page: {page_id}")
            return True
        except Exception as e:
            logger.error(f"Error archiving Notion page: {e}")
            return False
