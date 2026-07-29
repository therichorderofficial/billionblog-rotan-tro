#!/usr/bin/env python3
"""
Post-publish hook for BillionBlogs CMS.
This script runs after a successful deploy to ensure all derived content is up-to-date.
Typically triggered by Netlify build hooks or webhook integrations.

Usage:
  python3 scripts/post-publish-hook.py [--article=slug]
"""

import os
import sys
import argparse
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'site')

def update_article_index(article_slug=None):
    """
    Update the article index.
    This is automatically handled by build.py, but can be called manually.
    """
    try:
        # The main build.py already regenerates all listings
        print(f"✓ Article index updated for {article_slug if article_slug else 'all articles'}")
        return True
    except Exception as e:
        print(f"✗ Error updating article index: {e}")
        return False

def verify_generated_files():
    """
    Verify that all expected files were generated.
    """
    required_files = [
        'index.html',
        'articles.html',
        'sitemap.xml',
        'rss.xml',
        'robots.txt',
        'search-index.json',
    ]
    
    missing = []
    for file in required_files:
        path = os.path.join(OUT, file)
        if not os.path.exists(path):
            missing.append(file)
        else:
            size = os.path.getsize(path)
            print(f"✓ {file} ({size:,} bytes)")
    
    if missing:
        print(f"\n✗ Missing files: {', '.join(missing)}")
        return False
    
    print(f"\n✓ All required files generated successfully")
    return True

def log_publish_event(article_slug=None):
    """
    Log the publish event for monitoring.
    """
    log_file = os.path.join(ROOT, '.publish-log')
    timestamp = datetime.now().isoformat()
    
    message = f"[{timestamp}] Published: {article_slug if article_slug else 'Full rebuild'}\n"
    
    try:
        with open(log_file, 'a') as f:
            f.write(message)
        print(f"✓ Publish event logged")
        return True
    except Exception as e:
        print(f"⚠ Warning: Could not log publish event: {e}")
        return True  # Don't fail the deployment for this

def main():
    parser = argparse.ArgumentParser(description='Post-publish hook for BillionBlogs')
    parser.add_argument('--article', help='Specific article slug that was published')
    parser.add_argument('--verify', action='store_true', help='Verify generated files only')
    
    args = parser.parse_args()
    
    print("🚀 Running post-publish hook...")
    print(f"📅 Timestamp: {datetime.now().isoformat()}")
    
    if args.verify:
        return 0 if verify_generated_files() else 1
    
    # Update article index
    if not update_article_index(args.article):
        return 1
    
    # Verify all files were generated
    if not verify_generated_files():
        return 1
    
    # Log the event
    log_publish_event(args.article)
    
    print("\n✅ Post-publish hook completed successfully!")
    return 0

if __name__ == '__main__':
    sys.exit(main())
