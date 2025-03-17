#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TTRSS Data Exporter

This script connects to the PostgreSQL database of a Tiny Tiny RSS (TTRSS) 
Docker container and exports all feed data to a structured JSON file.
Each feed's articles are grouped together for easy processing.
"""

import psycopg2
import json
import sys
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import re
import html

# Database connection parameters
DB_HOST = "localhost"  # Use 'db' if running inside the Docker network
DB_PORT = 5432
DB_NAME = "ttrss"
DB_USER = "ttrss"
DB_PASS = "handbook12"

def connect_to_database():
    """
    Connect to the TTRSS PostgreSQL database.
    
    Returns:
        connection: PostgreSQL database connection
    """
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        print(f"Successfully connected to {DB_NAME} database")
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

def get_feed_categories(connection):
    """
    Get all feed categories from the database.
    
    Args:
        connection: PostgreSQL database connection
        
    Returns:
        dict: Dictionary mapping category IDs to category names
    """
    cursor = connection.cursor()
    cursor.execute("SELECT id, title FROM ttrss_feed_categories")
    categories = {row[0]: row[1] for row in cursor.fetchall()}
    categories[0] = "Uncategorized"  # Default category
    cursor.close()
    return categories

def get_feeds(connection):
    """
    Get all feed subscriptions from the database.
    
    Args:
        connection: PostgreSQL database connection
        
    Returns:
        list: List of feed subscription details
    """
    cursor = connection.cursor()
    query = """
    SELECT 
        f.id, 
        f.title, 
        f.feed_url, 
        f.site_url, 
        f.last_updated, 
        f.last_error, 
        f.cat_id
    FROM 
        ttrss_feeds f
    ORDER BY 
        f.cat_id, f.title
    """
    cursor.execute(query)
    feeds = cursor.fetchall()
    cursor.close()
    return feeds

def get_feed_entries(connection, feed_id):
    """
    Get all entries for a specific feed.
    
    Args:
        connection: PostgreSQL database connection
        feed_id: ID of the feed to get entries for
        
    Returns:
        list: List of entries for the feed
    """
    cursor = connection.cursor()
    query = """
    SELECT 
        e.id,
        e.title,
        e.link,
        e.content,
        e.author,
        e.updated,
        e.date_entered,
        ue.marked,
        ue.published,
        ue.unread,
        ue.score,
        ue.tag_cache
    FROM 
        ttrss_entries e
    JOIN 
        ttrss_user_entries ue ON e.id = ue.ref_id
    WHERE 
        ue.feed_id = %s
    ORDER BY 
        e.date_entered DESC
    """
    cursor.execute(query, (feed_id,))
    entries = cursor.fetchall()
    cursor.close()
    return entries

def clean_html_content(content):
    """
    Clean HTML content by removing unnecessary tags and formatting.
    
    Args:
        content: HTML content to clean
        
    Returns:
        str: Cleaned content
    """
    if not content:
        return ""
    
    # Unescape HTML entities
    content = html.unescape(content)
    
    # Remove script and style elements
    content = re.sub(r'<script.*?</script>', '', content, flags=re.DOTALL)
    content = re.sub(r'<style.*?</style>', '', content, flags=re.DOTALL)
    
    # Remove HTML comments
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    
    # Preserve code blocks with proper formatting
    code_blocks = []
    
    def save_code_block(match):
        code = match.group(1)
        code_blocks.append(code)
        return f"[CODE_BLOCK_{len(code_blocks)-1}]"
    
    # Save code blocks
    content = re.sub(r'<pre.*?><code.*?>(.*?)</code></pre>', save_code_block, content, flags=re.DOTALL)
    content = re.sub(r'<pre.*?>(.*?)</pre>', save_code_block, content, flags=re.DOTALL)
    
    # Handle headings
    for i in range(6, 0, -1):
        content = re.sub(f'<h{i}.*?>(.*?)</h{i}>', r'\n\n\1\n\n', content, flags=re.DOTALL)
    
    # Handle paragraphs and breaks
    content = re.sub(r'<p.*?>(.*?)</p>', r'\n\n\1\n\n', content, flags=re.DOTALL)
    content = re.sub(r'<br\s*/?>', '\n', content)
    
    # Handle lists
    content = re.sub(r'<li.*?>(.*?)</li>', r'\n- \1', content, flags=re.DOTALL)
    
    # Handle bold and italic
    content = re.sub(r'<strong.*?>(.*?)</strong>', r'**\1**', content, flags=re.DOTALL)
    content = re.sub(r'<b.*?>(.*?)</b>', r'**\1**', content, flags=re.DOTALL)
    content = re.sub(r'<em.*?>(.*?)</em>', r'*\1*', content, flags=re.DOTALL)
    content = re.sub(r'<i.*?>(.*?)</i>', r'*\1*', content, flags=re.DOTALL)
    
    # Remove all remaining HTML tags
    content = re.sub(r'<.*?>', '', content, flags=re.DOTALL)
    
    # Restore code blocks
    for i, code in enumerate(code_blocks):
        # Remove language identifiers
        code = re.sub(r'^.*?language-.*?\n', '', code)
        content = content.replace(f"[CODE_BLOCK_{i}]", f"\n```\n{code}\n```\n")
    
    # Fix multiple newlines
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    return content.strip()

def process_feed(connection, feed, categories):
    """
    Process a feed and get all its entries.
    
    Args:
        connection: PostgreSQL database connection
        feed: Feed tuple from the database
        categories: Dictionary of category IDs to names
        
    Returns:
        dict: Feed data with all entries
    """
    feed_id, title, feed_url, site_url, last_updated, last_error, cat_id = feed
    category_name = categories.get(cat_id, "Unknown")
    
    # Get entries for this feed
    entries = get_feed_entries(connection, feed_id)
    
    # Process entries
    processed_entries = []
    for entry in entries:
        entry_id, entry_title, link, content, author, updated, date_entered, marked, published, unread, score, tag_cache = entry
        
        # Clean content
        cleaned_content = clean_html_content(content)
        
        # Process tags
        tags = tag_cache.split(',') if tag_cache else []
        
        processed_entries.append({
            "id": entry_id,
            "title": entry_title,
            "link": link,
            "content": cleaned_content,
            "author": author,
            "updated": updated.isoformat() if updated else None,
            "date_entered": date_entered.isoformat() if date_entered else None,
            "marked": marked,
            "published": published,
            "unread": unread,
            "score": score,
            "tags": tags
        })
    
    # Create feed data
    feed_data = {
        "id": feed_id,
        "title": title,
        "feed_url": feed_url,
        "site_url": site_url,
        "last_updated": last_updated.isoformat() if last_updated else None,
        "category": {
            "id": cat_id,
            "name": category_name
        },
        "entries_count": len(processed_entries),
        "entries": processed_entries
    }
    
    return feed_data

def main():
    """Main function to export TTRSS data to JSON"""
    # Connect to the database
    connection = connect_to_database()
    
    # Get categories and feeds
    categories = get_feed_categories(connection)
    feeds = get_feeds(connection)
    
    if not feeds:
        print("No feed subscriptions found in the TTRSS database.")
        connection.close()
        return
    
    print(f"Found {len(feeds)} feed subscriptions in {len(set(f[6] for f in feeds))} categories")
    
    # Process all feeds in parallel
    all_feeds_data = []
    
    # Create a new connection for each thread to avoid concurrency issues
    with ThreadPoolExecutor(max_workers=min(10, len(feeds))) as executor:
        # Submit all tasks
        future_to_feed = {
            executor.submit(
                process_feed, 
                psycopg2.connect(
                    host=DB_HOST,
                    port=DB_PORT,
                    database=DB_NAME,
                    user=DB_USER,
                    password=DB_PASS
                ), 
                feed, 
                categories
            ): feed for feed in feeds
        }
        
        # Process results as they complete
        for future in tqdm(as_completed(future_to_feed), total=len(feeds), desc="Processing feeds"):
            feed = future_to_feed[future]
            try:
                feed_data = future.result()
                all_feeds_data.append(feed_data)
            except Exception as e:
                print(f"Error processing feed {feed[1]}: {e}")
    
    # Organize data by categories
    categories_data = {}
    for feed_data in all_feeds_data:
        cat_name = feed_data["category"]["name"]
        if cat_name not in categories_data:
            categories_data[cat_name] = []
        categories_data[cat_name].append(feed_data)
    
    # Create final data structure
    final_data = {
        "export_date": datetime.now().isoformat(),
        "total_feeds": len(all_feeds_data),
        "total_entries": sum(f["entries_count"] for f in all_feeds_data),
        "categories": categories_data
    }
    
    # Save to JSON file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_filename = f"ttrss_data_export_{timestamp}.json"
    
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nExported {final_data['total_feeds']} feeds with {final_data['total_entries']} entries to {json_filename}")
    print(f"Total JSON file size: {os.path.getsize(json_filename) / (1024*1024):.2f} MB")
    
    # Close the database connection
    connection.close()

if __name__ == "__main__":
    main()