#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Dev.to RSS Feed Text Extractor
-----------------------------
This script fetches articles from dev.to RSS feed and extracts plain text from HTML content.
"""

import feedparser
from bs4 import BeautifulSoup
import sys

def get_plain_text(html_content):
    """Extract plain text from HTML content, removing all HTML tags."""
    if not html_content:
        return ""
    
    # Parse HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Get text content (removes all HTML tags)
    text = soup.get_text(separator=' ', strip=True)
    
    return text

def fetch_devto_articles(limit=None, category=None):
    """
    Fetch articles from dev.to RSS feed.
    
    Args:
        limit (int, optional): Maximum number of articles to fetch. None for all.
        category (str, optional): Category to filter by (e.g., 'python', 'javascript').
                                 None for all categories.
    
    Returns:
        list: List of article dictionaries with title, link, date, and text content.
    """
    # Base URL for dev.to feed
    feed_url = "https://dev.to/feed"
    
    # Add category if specified
    if category:
        feed_url = f"https://dev.to/t/{category}/feed"
    
    print(f"Fetching articles from {feed_url}")
    
    # Parse the feed
    feed = feedparser.parse(feed_url)
    
    # Check if feed is valid
    if not feed.entries:
        print("No entries found or feed could not be parsed.")
        return []
    
    articles = []
    
    # Process each entry
    for i, entry in enumerate(feed.entries):
        if limit and i >= limit:
            break
        
        # Extract basic information
        title = entry.get('title', 'No Title')
        link = entry.get('link', '')
        published = entry.get('published', 'Unknown date')
        
        # Get description/content and extract plain text
        description = entry.get('description', '')
        
        # Some feeds use 'content' instead of 'description'
        content = ''
        if 'content' in entry:
            content = entry.get('content', [{}])[0].get('value', '')
        
        # Use the longer of description or content
        html_content = content if len(content) > len(description) else description
        plain_text = get_plain_text(html_content)
        
        # Add to articles list
        articles.append({
            'title': title,
            'link': link,
            'published': published,
            'text': plain_text
        })
    
    return articles

def main():
    # Parse command line arguments
    limit = 10  # Default limit
    category = None
    
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            # If not a number, treat as category
            category = sys.argv[1]
            
    if len(sys.argv) > 2:
        try:
            # If first arg was category, second might be limit
            if category:
                limit = int(sys.argv[2])
            else:
                # If first arg was limit, second is category
                category = sys.argv[2]
        except ValueError:
            print(f"Invalid limit: {sys.argv[2]}. Using default: {limit}")
    
    # Fetch articles
    articles = fetch_devto_articles(limit=limit, category=category)
    
    # Display articles
    print(f"\nFetched {len(articles)} articles from Dev.to")
    print("=" * 50)
    
    for i, article in enumerate(articles, 1):
        print(f"\n--- Article {i} ---")
        print(f"Title: {article['title']}")
        print(f"Published: {article['published']}")
        print(f"Link: {article['link']}")
        
        # Print a preview of the text (first 200 characters)
        text_preview = article['text'][:200] + "..." if len(article['text']) > 200 else article['text']
        print(f"\nPreview: {text_preview}")
        print("-" * 50)
    
    # Interactive mode to view full text
    print("\nTo view full text of an article, enter its number (or 'q' to quit):")
    while True:
        choice = input("> ")
        if choice.lower() == 'q':
            break
            
        try:
            article_num = int(choice)
            if 1 <= article_num <= len(articles):
                print(f"\n=== Full Text of Article {article_num} ===")
                print(articles[article_num-1]['text'])
                print("\nTo view another article, enter its number (or 'q' to quit):")
            else:
                print(f"Invalid article number. Please enter a number between 1 and {len(articles)}")
        except ValueError:
            print("Invalid input. Enter a number or 'q' to quit.")

if __name__ == "__main__":
    main()
