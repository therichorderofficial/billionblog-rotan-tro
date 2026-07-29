#!/usr/bin/env python3
"""
Verification script to ensure all CMS fixes are properly installed.
Run this locally before deploying to Netlify to catch any issues early.
"""

import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

def check_file_exists(path, description):
    """Check if a file exists and report"""
    full_path = os.path.join(ROOT, path)
    exists = os.path.exists(full_path)
    status = "✓" if exists else "✗"
    print(f"  {status} {description}")
    return exists

def check_file_contains(path, search_text, description):
    """Check if a file contains specific text"""
    full_path = os.path.join(ROOT, path)
    if not os.path.exists(full_path):
        print(f"  ✗ {description} (FILE NOT FOUND)")
        return False
    
    try:
        with open(full_path, 'r') as f:
            content = f.read()
            if search_text in content:
                print(f"  ✓ {description}")
                return True
            else:
                print(f"  ✗ {description} (TEXT NOT FOUND)")
                return False
    except Exception as e:
        print(f"  ✗ {description} (ERROR: {e})")
        return False

def main():
    print("🔍 Verifying BillionBlogs CMS Fixes\n")
    
    all_passed = True
    
    # Admin Panel Fixes
    print("📱 Admin Panel & Authentication:")
    all_passed &= check_file_contains(
        'admin/index.html',
        'netlifyIdentity',
        'Netlify Identity widget configured'
    )
    all_passed &= check_file_contains(
        'admin/index.html',
        'decap-cms',
        'Decap CMS loaded'
    )
    all_passed &= check_file_contains(
        'admin/index.html',
        'admin-loading',
        'Loading state display'
    )
    all_passed &= check_file_exists(
        'admin/styles.css',
        'Mobile-responsive CMS styles'
    )
    
    # CMS Configuration
    print("\n⚙️  Decap CMS Configuration:")
    all_passed &= check_file_contains(
        'admin/config.yml',
        'git-gateway',
        'Git Gateway backend configured'
    )
    all_passed &= check_file_contains(
        'admin/config.yml',
        'editorial_workflow',
        'Editorial workflow enabled'
    )
    all_passed &= check_file_contains(
        'admin/config.yml',
        'preview_path',
        'Article preview paths configured'
    )
    
    # Netlify Configuration
    print("\n🚀 Netlify Build & Deployment:")
    all_passed &= check_file_contains(
        'netlify.toml',
        'generate-feeds.py',
        'Automatic feed generation in build'
    )
    all_passed &= check_file_contains(
        'netlify.toml',
        'Cache-Control',
        'Cache control headers configured'
    )
    all_passed &= check_file_contains(
        'netlify.toml',
        'admin',
        'Admin panel routing configured'
    )
    
    # Feed Generation Scripts
    print("\n📡 Automatic Feed Generation:")
    all_passed &= check_file_exists(
        'scripts/generate-feeds.py',
        'Feed generation script'
    )
    all_passed &= check_file_contains(
        'scripts/generate-feeds.py',
        'sitemap',
        'Sitemap generation'
    )
    all_passed &= check_file_contains(
        'scripts/generate-feeds.py',
        'rss',
        'RSS feed generation'
    )
    all_passed &= check_file_contains(
        'scripts/generate-feeds.py',
        'search-index',
        'Search index generation'
    )
    all_passed &= check_file_contains(
        'scripts/generate-feeds.py',
        'robots',
        'Robots.txt generation'
    )
    
    # SEO Meta Tags
    print("\n🔍 SEO & Meta Tags:")
    all_passed &= check_file_contains(
        'templates/base.html',
        'og:title',
        'Open Graph meta tags'
    )
    all_passed &= check_file_contains(
        'templates/base.html',
        'twitter:card',
        'Twitter Card meta tags'
    )
    all_passed &= check_file_contains(
        'templates/base.html',
        'rss.xml',
        'RSS feed link'
    )
    all_passed &= check_file_contains(
        'templates/article.html',
        'article:author',
        'Article-specific SEO metadata'
    )
    
    # Build Script Enhancements
    print("\n🔨 Build Script Updates:")
    all_passed &= check_file_contains(
        'build.py',
        'search-index.json',
        'Search index JSON generation'
    )
    all_passed &= check_file_contains(
        'build.py',
        'og_image',
        'OG image metadata'
    )
    
    # Documentation
    print("\n📚 Documentation:")
    all_passed &= check_file_exists(
        'NETLIFY_SETUP.md',
        'Setup guide'
    )
    all_passed &= check_file_exists(
        'CMS_FIXES_REPORT.md',
        'Fixes documentation'
    )
    all_passed &= check_file_exists(
        'scripts/post-publish-hook.py',
        'Post-publish verification script'
    )
    
    # Python Dependencies
    print("\n📦 Dependencies:")
    all_passed &= check_file_contains(
        'requirements.txt',
        'Jinja2',
        'Jinja2 template engine'
    )
    all_passed &= check_file_contains(
        'requirements.txt',
        'PyYAML',
        'PyYAML for parsing'
    )
    
    # Summary
    print("\n" + "="*50)
    if all_passed:
        print("✅ All CMS fixes verified successfully!")
        print("\nYou're ready to deploy to Netlify:")
        print("  1. Push to GitHub")
        print("  2. Connect to Netlify")
        print("  3. Enable Identity & Git Gateway")
        print("  4. Invite users")
        print("  5. Start publishing!")
        return 0
    else:
        print("⚠️  Some fixes are missing or incomplete.")
        print("\nPlease review the output above and verify all files")
        print("have been properly updated.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
