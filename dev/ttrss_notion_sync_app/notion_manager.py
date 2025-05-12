"""
Notion API management module for handling Notion database operations.
"""
from notion_client import Client
from datetime import datetime
import json
import pytz
from config import NOTION_DATABASE_ID, NOTION_API_KEY, logger
from db_manager import convert_to_kst

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
            
    def get_page_content(self, page_id):
        """Get the content of a Notion page by retrieving all blocks"""
        try:
            all_blocks = []
            has_more = True
            start_cursor = None
            
            # Retrieve all blocks from the page
            while has_more:
                if start_cursor:
                    response = self.client.blocks.children.list(
                        block_id=page_id,
                        start_cursor=start_cursor
                    )
                else:
                    response = self.client.blocks.children.list(
                        block_id=page_id
                    )
                    
                blocks = response.get('results', [])
                all_blocks.extend(blocks)
                has_more = response.get('has_more', False)
                start_cursor = response.get('next_cursor')
            
            # Extract text content from blocks
            content_parts = []
            for block in all_blocks:
                block_type = block.get('type')
                if block_type in ['paragraph', 'heading_1', 'heading_2', 'heading_3', 'bulleted_list_item', 'numbered_list_item']:
                    text_content = block.get(block_type, {}).get('rich_text', [])
                    if text_content:
                        text = " ".join([t.get('plain_text', '') for t in text_content])
                        content_parts.append(text)
                        
            # Join all content parts with newlines
            full_content = "\n\n".join(content_parts)
            logger.info(f"Retrieved content from Notion page {page_id}: {len(full_content)} characters")
            return full_content
        except Exception as e:
            logger.error(f"Error retrieving Notion page content: {e}")
            return ""
    
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
            
            # Extract AI summary
            ai_summary = ""
            ai_summary_prop = properties.get('AI summary', properties.get('AI 요약', {}))
            if ai_summary_prop and ai_summary_prop.get('type') == 'rich_text':
                ai_summary = " ".join([t.get('plain_text', '') for t in ai_summary_prop.get('rich_text', [])])
                
            # Extract content/description from "Why it matters" field
            why_it_matters = ""
            why_it_matters_prop = properties.get('Why it matters', properties.get('중요성', properties.get('내용', {})))
            if why_it_matters_prop and why_it_matters_prop.get('type') == 'rich_text':
                why_it_matters = " ".join([t.get('plain_text', '') for t in why_it_matters_prop.get('rich_text', [])])
                
            # For backward compatibility, initialize content with why_it_matters
            # The actual page content will be fetched separately
            content = why_it_matters
            
            # Extract Category
            category = ""
            category_prop = properties.get('Category', properties.get('카테고리', {}))
            if category_prop:
                if category_prop.get('type') == 'select' and category_prop.get('select'):
                    category = category_prop.get('select', {}).get('name', '')
                    
            # Extract Tags
            tags = []
            tags_prop = properties.get('Tags', properties.get('태그', {}))
            if tags_prop and tags_prop.get('type') == 'multi_select':
                tags = [tag.get('name', '') for tag in tags_prop.get('multi_select', [])]
            tag = ", ".join(tags) if tags else ""
            
            # Extract last edited time and convert to KST
            last_edited = page.get('last_edited_time', '')
            if last_edited:
                last_edited = datetime.fromisoformat(last_edited.replace('Z', '+00:00'))
                last_edited = convert_to_kst(last_edited)
            
            # Extract creation time and convert to KST
            created_time = page.get('created_time', '')
            if created_time:
                created_time = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                created_time = convert_to_kst(created_time)
            
            page_id = page.get('id', '')
            
            return {
                'notion_page_id': page_id,
                'title': title,
                'link': url,
                'content': content,
                'category': category,
                'tag': tag,
                'ai_summary': ai_summary,
                'why_it_matters': why_it_matters,
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
                "Why it matters": {  # Leave "Why it matters" empty as requested
                    "rich_text": [
                        {
                            "text": {
                                "content": ""  # Empty string instead of entry['content']
                            }
                        }
                    ]
                },
                "Read": {  # Add the "Read" checkbox property
                    "checkbox": False
                }
            }
            
            # Add Category if available
            if entry.get('category'):
                properties["Category"] = {
                    "select": {
                        "name": entry['category']
                    }
                }
                
            # Add Tags if available
            if entry.get('tag'):
                tags = [tag.strip() for tag in entry['tag'].split(',') if tag.strip()]
                if tags:
                    properties["Tags"] = {
                        "multi_select": [{
                            "name": tag
                        } for tag in tags]
                    }
                    
            # Add AI summary if available
            if entry.get('ai_summary'):
                properties["AI summary"] = {
                    "rich_text": [{
                        "text": {
                            "content": entry['ai_summary']
                        }
                    }]
                }
                
            # Add Why it matters if available
            if entry.get('why_it_matters'):
                properties["Why it matters"] = {
                    "rich_text": [{
                        "text": {
                            "content": entry['why_it_matters']
                        }
                    }]
                }
            
            # Split content into paragraphs for better formatting
            paragraphs = []
            if entry.get('content'):
                content_paragraphs = entry['content'].split('\n')
                
                # 1. Check if we have too many paragraphs (approaching Notion's 100 block limit)
                if len(content_paragraphs) > 80:  # If we have a lot of paragraphs
                    logger.info(f"Entry has {len(content_paragraphs)} paragraphs, combining to reduce block count")
                    
                    # Strategy 1: Combine paragraphs to reduce the number of blocks
                    combined_paragraphs = []
                    current_paragraph = ""
                    max_paragraph_length = 2000  # Notion's approximate text block size limit
                    
                    for paragraph in content_paragraphs:
                        # If adding this paragraph wouldn't exceed the length limit, combine it
                        if len(current_paragraph) + len(paragraph) + 1 < max_paragraph_length:
                            if current_paragraph:
                                current_paragraph += "\n" + paragraph.strip()
                            else:
                                current_paragraph = paragraph.strip()
                        else:
                            # This paragraph would make the block too long, save current and start new
                            if current_paragraph:
                                combined_paragraphs.append(current_paragraph)
                            current_paragraph = paragraph.strip()
                    
                    # Add the last paragraph if there's anything left
                    if current_paragraph:
                        combined_paragraphs.append(current_paragraph)
                    
                    # Use the combined paragraphs instead
                    content_paragraphs = combined_paragraphs
                    logger.info(f"Reduced to {len(content_paragraphs)} paragraphs after combining")
                
                # 2. Create paragraph blocks from our (possibly combined) paragraphs
                for paragraph in content_paragraphs:
                    if paragraph.strip():  # Skip empty paragraphs
                        paragraphs.append({
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": paragraph.strip()
                                        }
                                    }
                                ]
                            }
                        })
                
                # 3. Apply hard limit to ensure we stay under Notion's 100 block limit
                MAX_BLOCKS = 99  # Keep one block as safety margin
                if len(paragraphs) > MAX_BLOCKS:
                    logger.warning(f"Entry has {len(paragraphs)} blocks, truncating to {MAX_BLOCKS}")
                    # Keep the first blocks and add a truncation notice as the last block
                    paragraphs = paragraphs[:MAX_BLOCKS-1]
                    # Add a notice that content was truncated
                    paragraphs.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": "... (Content truncated due to length. Please refer to the original link for complete content.)"
                                    }
                                }
                            ]
                        }
                    })
            
            # Create the page with children blocks for content
            page_data = {
                "parent": {"database_id": self.database_id},
                "properties": properties
            }
            
            # Only add children if we have content
            if paragraphs:
                page_data["children"] = paragraphs
                logger.info(f"Creating Notion page with {len(paragraphs)} blocks")
            
            # Create the page
            response = self.client.pages.create(**page_data)
            
            logger.info(f"Created Notion page for entry: {entry['title'][:50]}...")
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
