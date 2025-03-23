"""
Test file for duplicate entry checking functionality.
"""
import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import logging

# Configure logging for testing
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ttrss_notion_sync_app.db_manager import DatabaseManager
from ttrss_notion_sync_app.sync_manager import SyncManager

class TestDuplicateChecking(unittest.TestCase):
    """Test case for duplicate entry checking functionality"""

    def setUp(self):
        """Set up test fixtures"""
        # Create mock connection and cursor
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_conn.cursor.return_value.__enter__.return_value = self.mock_cursor
        
        # Create DatabaseManager with mocked connection
        self.db_manager = DatabaseManager()
        self.db_manager.conn = self.mock_conn
        
    def test_check_duplicate_entry_ttrss(self):
        """Test checking for duplicate TTRSS entry"""
        # Create a test TTRSS entry
        test_entry = {
            'id': 123,
            'title': 'Test Article',
            'link': 'https://example.com/test',
            'content': 'Test content',
            'date_entered': datetime.now(),
            'date_updated': datetime.now()
        }
        
        # Mock cursor fetchone to return None first (no duplicate)
        self.mock_cursor.fetchone.return_value = None
        
        # Test no duplicate found
        result = self.db_manager.check_duplicate_entry(test_entry, 'ttrss')
        self.assertIsNone(result)
        
        # Mock cursor fetchone to return a result (duplicate found)
        mock_result = (1, 123, None, 'Test Article', 'https://example.com/test', 'ttrss')
        self.mock_cursor.description = [
            ('id', None, None, None, None, None, None),
            ('ttrss_entry_id', None, None, None, None, None, None),
            ('notion_page_id', None, None, None, None, None, None),
            ('title', None, None, None, None, None, None),
            ('link', None, None, None, None, None, None),
            ('source', None, None, None, None, None, None)
        ]
        self.mock_cursor.fetchone.return_value = mock_result
        
        # Test duplicate found
        result = self.db_manager.check_duplicate_entry(test_entry, 'ttrss')
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], 1)
        self.assertEqual(result['ttrss_entry_id'], 123)
        
    def test_check_duplicate_entry_notion(self):
        """Test checking for duplicate Notion entry"""
        # Create a test Notion entry
        test_entry = {
            'notion_page_id': 'abc123',
            'title': 'Test Notion Page',
            'link': 'https://notion.so/page/abc123',
            'content': 'Test content',
            'published': datetime.now(),
            'updated': datetime.now()
        }
        
        # Mock cursor fetchone to return None first (no duplicate)
        self.mock_cursor.fetchone.return_value = None
        
        # Test no duplicate found
        result = self.db_manager.check_duplicate_entry(test_entry, 'notion')
        self.assertIsNone(result)
        
        # Mock cursor fetchone to return a result (duplicate found)
        mock_result = (2, None, 'abc123', 'Test Notion Page', 'https://notion.so/page/abc123', 'notion')
        self.mock_cursor.description = [
            ('id', None, None, None, None, None, None),
            ('ttrss_entry_id', None, None, None, None, None, None),
            ('notion_page_id', None, None, None, None, None, None),
            ('title', None, None, None, None, None, None),
            ('link', None, None, None, None, None, None),
            ('source', None, None, None, None, None, None)
        ]
        self.mock_cursor.fetchone.return_value = mock_result
        
        # Test duplicate found
        result = self.db_manager.check_duplicate_entry(test_entry, 'notion')
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], 2)
        self.assertEqual(result['notion_page_id'], 'abc123')
        
    def test_add_ttrss_entry_with_duplicate(self):
        """Test adding a TTRSS entry that is a duplicate"""
        # Create a test TTRSS entry
        test_entry = {
            'id': 123,
            'title': 'Test Article',
            'link': 'https://example.com/test',
            'content': 'Test content',
            'date_entered': datetime.now(),
            'date_updated': datetime.now()
        }
        
        # Mock check_duplicate_entry to return an existing entry
        existing_entry = {
            'id': 1,
            'ttrss_entry_id': 123,
            'notion_page_id': None,
            'title': 'Test Article',
            'link': 'https://example.com/test',
            'source': 'ttrss'
        }
        
        with patch.object(self.db_manager, 'check_duplicate_entry', return_value=existing_entry):
            # Call add_ttrss_entry_to_sync with the test entry
            result_id = self.db_manager.add_ttrss_entry_to_sync(test_entry)
            
            # Verify we got the existing ID back without inserting
            self.assertEqual(result_id, 1)
            self.mock_cursor.execute.assert_not_called()
            
    def test_add_notion_entry_with_duplicate(self):
        """Test adding a Notion entry that is a duplicate"""
        # Create a test Notion entry
        test_entry = {
            'notion_page_id': 'abc123',
            'title': 'Test Notion Page',
            'link': 'https://notion.so/page/abc123',
            'content': 'Test content',
            'published': datetime.now(),
            'updated': datetime.now()
        }
        
        # Mock check_duplicate_entry to return an existing entry
        existing_entry = {
            'id': 2,
            'ttrss_entry_id': None,
            'notion_page_id': 'abc123',
            'title': 'Test Notion Page',
            'link': 'https://notion.so/page/abc123',
            'source': 'notion'
        }
        
        with patch.object(self.db_manager, 'check_duplicate_entry', return_value=existing_entry):
            # Call add_notion_entry_to_sync with the test entry
            result_id = self.db_manager.add_notion_entry_to_sync(test_entry)
            
            # Verify we got the existing ID back without inserting
            self.assertEqual(result_id, 2)
            self.mock_cursor.execute.assert_not_called()

if __name__ == '__main__':
    unittest.main()
