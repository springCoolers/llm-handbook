#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TTRSS Feed Subscription Lister

This script connects to the PostgreSQL database of a Tiny Tiny RSS (TTRSS) 
Docker container and retrieves all feed subscriptions.
"""

import psycopg2
import pandas as pd
from tabulate import tabulate
import sys
import os
from datetime import datetime

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

def get_feed_subscriptions(connection):
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
        f.cat_id,
        COUNT(DISTINCT ue.ref_id) as entry_count
    FROM 
        ttrss_feeds f
    LEFT JOIN 
        ttrss_user_entries ue ON f.id = ue.feed_id
    GROUP BY 
        f.id, f.title, f.feed_url, f.site_url, f.last_updated, f.last_error, f.cat_id
    ORDER BY 
        f.cat_id, f.title
    """
    cursor.execute(query)
    feeds = cursor.fetchall()
    cursor.close()
    return feeds

def format_datetime(dt):
    """Format datetime object to readable string or return empty string if None"""
    if dt:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return "Never"

def main():
    """Main function to retrieve and display TTRSS feed subscriptions"""
    # Connect to the database
    connection = connect_to_database()
    
    # Get categories and feeds
    categories = get_feed_categories(connection)
    feeds = get_feed_subscriptions(connection)
    
    if not feeds:
        print("No feed subscriptions found in the TTRSS database.")
        connection.close()
        return
    
    # Prepare data for display
    feed_data = []
    for feed in feeds:
        feed_id, title, feed_url, site_url, last_updated, last_error, cat_id, entry_count = feed
        category_name = categories.get(cat_id, "Unknown")
        
        feed_data.append({
            "ID": feed_id,
            "Title": title,
            "Category": category_name,
            "Feed URL": feed_url,
            "Site URL": site_url,
            "Last Updated": format_datetime(last_updated),
            "Entries": entry_count,
            "Last Error": last_error if last_error else "None"
        })
    
    # Convert to DataFrame for better display
    df = pd.DataFrame(feed_data)
    
    # Print summary
    print(f"\nFound {len(feeds)} feed subscriptions in {len(set(f[6] for f in feeds))} categories\n")
    
    # Print feeds by category
    for cat_id, cat_name in categories.items():
        cat_feeds = [f for f in feed_data if f["Category"] == cat_name]
        if cat_feeds:
            print(f"\n=== Category: {cat_name} ({len(cat_feeds)} feeds) ===")
            cat_df = pd.DataFrame(cat_feeds)[["ID", "Title", "Feed URL", "Last Updated", "Entries"]]
            print(tabulate(cat_df, headers="keys", tablefmt="pretty", showindex=False))
    
    # Close the database connection
    connection.close()
    
    # Save to CSV file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"ttrss_feeds_{timestamp}.csv"
    df.to_csv(csv_filename, index=False)
    print(f"\nFeed list exported to {csv_filename}")

if __name__ == "__main__":
    main()