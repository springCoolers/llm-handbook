#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Multi-RSS Feed Collector
-----------------------
This script collects up to 100 posts from multiple RSS feeds and saves them as JSON.

Usage:
    python multi_feed_collector.py [url1] [url2] ... [urlN]
    
Example:
    python multi_feed_collector.py https://dev.to https://news.ycombinator.com
"""

import feedparser
from bs4 import BeautifulSoup
import json
import sys
import os
import time
import re
import concurrent.futures
from urllib.parse import urlparse, urljoin

def get_plain_text(html_content):
    """Extract plain text from HTML content, properly handling code blocks and formatting."""
    if not html_content:
        return ""
    
    # Parse HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()
    
    # Find and clean code blocks with language identifiers
    # First, look for language identifiers that appear before code blocks
    for code_lang in soup.find_all('code'):
        # If this is a language identifier (typically short and alone)
        if code_lang.get_text().strip() in ['bash', 'python', 'javascript', 'js', 'html', 'css', 'java', 'php', 'ruby', 'go', 'c', 'cpp', 'csharp', 'typescript', 'ts', 'sql']:
            # If it's followed by a code block, remove the language identifier
            if code_lang.find_next('div', class_='highlight'):
                code_lang.extract()
    
    # Handle code blocks in div.highlight
    for highlight in soup.find_all('div', class_='highlight'):
        # Find the code content within pre and code tags
        pre_tag = highlight.find('pre')
        if pre_tag:
            code_content = pre_tag.get_text().strip()
            # Replace the entire highlight div with formatted code
            highlight.replace_with(soup.new_string(f"\n```\n{code_content}\n```\n"))
    
    # Handle remaining pre tags (not in highlight divs)
    for pre in soup.find_all('pre'):
        code_content = pre.get_text().strip()
        pre.replace_with(soup.new_string(f"\n```\n{code_content}\n```\n"))
    
    # Handle inline code
    for code in soup.find_all('code'):
        code_content = code.get_text().strip()
        code.replace_with(soup.new_string(f"`{code_content}`"))
    
    # Process headings to make them stand out
    for i, tag in enumerate(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        for heading in soup.find_all(tag):
            text = heading.get_text().strip()
            # Add appropriate formatting based on heading level
            prefix = '#' * (i + 1) + ' '
            heading.replace_with(soup.new_string(f"\n\n{prefix}{text}\n"))
    
    # Add line breaks for paragraphs and list items
    for tag in soup.find_all(['p', 'br', 'li']):
        tag.append(soup.new_string('\n'))
    
    # Add extra line break for block elements to improve readability
    for tag in soup.find_all(['div', 'ul', 'ol', 'blockquote']):
        tag.append(soup.new_string('\n'))
    
    # Process strong/bold text
    for bold in soup.find_all(['strong', 'b']):
        text = bold.get_text().strip()
        bold.replace_with(soup.new_string(f"**{text}**"))
    
    # Process italic text
    for italic in soup.find_all(['em', 'i']):
        text = italic.get_text().strip()
        italic.replace_with(soup.new_string(f"*{text}*"))
    
    # Get text content
    text = soup.get_text()
    
    # Clean up the text
    # Remove language identifiers that might be left (like 'bash' or 'python' before code blocks)
    text = re.sub(r'\n(bash|python|javascript|js|html|css|java|php|ruby|go|c|cpp|csharp|typescript|ts|sql)\s*\n```', r'\n```', text, flags=re.IGNORECASE)
    
    # Replace multiple newlines with just two
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Replace multiple spaces with a single space
    text = re.sub(r' {2,}', ' ', text)
    
    # Trim leading/trailing whitespace
    text = text.strip()
    
    return text

def discover_feed_url(site_url):
    """
    Discover RSS feed URL from a website URL.
    
    Args:
        site_url (str): Website URL (e.g., https://dev.to)
        
    Returns:
        str: RSS feed URL if found, None otherwise
    """
    # Common feed paths to try
    common_paths = [
        '/feed',
        '/rss',
        '/atom',
        '/feed.xml',
        '/rss.xml',
        '/atom.xml',
        '/feed/atom',
        '/feed/rss',
        '/feeds/posts/default',
        '/rss/all',
        '/blog/feed',
        '/blog/atom',
        '/blog/rss',
        '/index.xml'
    ]
    
    # If the URL already ends with a common feed path, return it
    parsed_url = urlparse(site_url)
    path = parsed_url.path.lower()
    
    for feed_path in common_paths:
        if path.endswith(feed_path):
            return site_url
    
    # Try common feed paths
    for feed_path in common_paths:
        feed_url = urljoin(site_url, feed_path)
        try:
            feed = feedparser.parse(feed_url)
            if feed.entries and len(feed.entries) > 0:
                print(f"Found feed at: {feed_url}")
                return feed_url
        except Exception as e:
            continue
    
    # If no feed found, return None
    return None

def fetch_feed_entries(feed_url, max_entries=100):
    """
    Fetch entries from an RSS feed URL.
    
    Args:
        feed_url (str): RSS feed URL
        max_entries (int): Maximum number of entries to fetch
        
    Returns:
        tuple: (feed_title, entries)
    """
    print(f"Fetching feed from: {feed_url}")
    
    # Parse the feed
    feed = feedparser.parse(feed_url)
    
    if feed.bozo and hasattr(feed, 'bozo_exception'):
        print(f"Warning: Feed may be malformed. Error: {feed.bozo_exception}")
    
    # Get feed title
    feed_title = feed.feed.get('title', 'Unknown Feed')
    print(f"Feed Title: {feed_title}")
    
    entries_count = len(feed.entries)
    print(f"Found {entries_count} entries in feed")
    
    # Process entries
    entries = []
    for i, entry in enumerate(feed.entries):
        if i >= max_entries:
            break
            
        # Extract basic information
        title = entry.get('title', 'No Title')
        link = entry.get('link', '')
        published = entry.get('published', entry.get('updated', 'Unknown date'))
        author = entry.get('author', 'Unknown author')
        
        # Get tags/categories if available
        tags = []
        if 'tags' in entry:
            tags = [tag.get('term', '') for tag in entry.tags]
        elif 'categories' in entry:
            tags = entry.categories
        
        # Get description/content and extract plain text
        description = entry.get('description', '')
        
        # Some feeds use 'content' instead of 'description'
        content = ''
        if 'content' in entry:
            content = entry.get('content', [{}])[0].get('value', '')
        
        # Use the longer of description or content
        html_content = content if len(content) > len(description) else description
        plain_text = get_plain_text(html_content)
        
        # Add to entries list
        entries.append({
            'title': title,
            'link': link,
            'published': published,
            'author': author,
            'tags': tags,
            'text': plain_text,
            'html': html_content  # Keep the HTML content as well
        })
        
        # Print progress
        if (i + 1) % 10 == 0:
            print(f"Processed {i + 1} entries...")
    
    return feed_title, entries

def save_to_json(data, filename):
    """
    Save data to a JSON file.
    
    Args:
        data (dict): Data to save
        filename (str): Output filename
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Data saved to {filename}")

def get_feed_data(url, max_entries=100):
    """
    Get feed data from a URL.
    
    Args:
        url (str): Website or feed URL
        max_entries (int): Maximum number of entries to fetch
        
    Returns:
        dict: Feed data including title and entries
    """
    # Check if the URL is a valid feed URL
    feed = feedparser.parse(url)
    
    # If no entries found, try to discover the feed URL
    if not feed.entries:
        feed_url = discover_feed_url(url)
        if not feed_url:
            print(f"Could not find a valid RSS feed for {url}")
            return None
    else:
        feed_url = url
    
    # Fetch entries from the feed
    feed_title, entries = fetch_feed_entries(feed_url, max_entries)
    
    # Create feed data dictionary
    feed_data = {
        'feed_url': feed_url,
        'site_url': url,
        'title': feed_title,
        'fetch_date': time.strftime('%Y-%m-%d %H:%M:%S'),
        'entries_count': len(entries),
        'entries': entries
    }
    
    return feed_data

def process_url(url, max_entries=100):
    """Process a single URL and return the feed data and filename."""
    # Ensure URL has a scheme
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Get feed data
    feed_data = get_feed_data(url, max_entries=max_entries)
    
    if feed_data:
        # Create output filename based on the feed title
        domain = urlparse(url).netloc
        filename = f"{domain.replace('.', '_')}_feed.json"
        
        return feed_data, filename
    
    return None, None

def main():
    # Get URLs from command line
    urls = sys.argv[1:] if len(sys.argv) > 1 else ["https://dev.to"]
    
    if not urls:
        print("Please provide at least one URL")
        print(f"Usage: python {sys.argv[0]} [url1] [url2] ... [urlN]")
        return
    
    # Create output directory if it doesn't exist
    output_dir = "feeds"
    os.makedirs(output_dir, exist_ok=True)
    
    # Process URLs in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(5, len(urls))) as executor:
        # Submit tasks
        future_to_url = {executor.submit(process_url, url, 100): url for url in urls}
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                feed_data, filename = future.result()
                
                if feed_data and filename:
                    # Save to JSON
                    save_to_json(feed_data, os.path.join(output_dir, filename))
                    
                    # Print summary
                    print(f"\nSummary for {url}:")
                    print(f"Feed Title: {feed_data['title']}")
                    print(f"Total Entries: {feed_data['entries_count']}")
                    print(f"Output File: {os.path.join(output_dir, filename)}")
                else:
                    print(f"Failed to fetch feed data from {url}")
            
            except Exception as e:
                print(f"Error processing {url}: {e}")
    
    # Create a combined feed file with all entries
    if len(urls) > 1:
        all_entries = []
        feed_info = []
        
        # Read all feed files
        for filename in os.listdir(output_dir):
            if filename.endswith('_feed.json'):
                with open(os.path.join(output_dir, filename), 'r', encoding='utf-8') as f:
                    feed_data = json.load(f)
                    all_entries.extend(feed_data['entries'])
                    feed_info.append({
                        'title': feed_data['title'],
                        'url': feed_data['site_url'],
                        'entries_count': feed_data['entries_count']
                    })
        
        # Create combined feed data
        combined_data = {
            'fetch_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'feeds_count': len(feed_info),
            'feeds': feed_info,
            'total_entries': len(all_entries),
            'entries': all_entries
        }
        
        # Save combined feed data
        combined_filename = os.path.join(output_dir, 'all_feeds.json')
        save_to_json(combined_data, combined_filename)
        
        print(f"\nCombined feed data saved to {combined_filename}")
        print(f"Total feeds: {len(feed_info)}")
        print(f"Total entries: {len(all_entries)}")

if __name__ == "__main__":
    main()
