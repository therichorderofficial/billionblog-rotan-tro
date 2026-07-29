# BillionBlogs CMS Setup Guide

This document outlines the steps needed to fully configure your BillionBlogs CMS with Netlify Identity and Decap CMS.

## Prerequisites

- A Netlify account (netlify.com)
- A GitHub repository with this project
- A domain or Netlify subdomain

## Step 1: Deploy to Netlify

1. Go to [Netlify](https://netlify.com)
2. Click "New site from Git"
3. Select GitHub and authorize
4. Select the BillionBlogs repository
5. Configure build settings:
   - Build command: `pip install -r requirements.txt && python3 build.py && python3 scripts/generate-feeds.py`
   - Publish directory: `site`
   - Python version: 3.11
6. Click "Deploy site"

## Step 2: Enable Netlify Identity

1. In your Netlify site dashboard, go to **Authentication** → **Enable Identity**
2. Click **Enable Identity**
3. Under **Invite only** (recommended for security):
   - Keep enabled to restrict access to invited users only
4. Go to **Services** and enable **Git Gateway**
   - This allows the CMS to push changes to your GitHub repository

## Step 3: Configure GitHub Integration

1. In Identity settings, go to **External Providers**
2. Click **Enable GitHub** (if you want GitHub login option)
3. Create a GitHub OAuth app:
   - Go to GitHub → Settings → Developer Settings → OAuth Apps
   - Create a new OAuth App with:
     - Authorization callback URL: `https://YOUR-SITE.netlify.app/.netlify/identity/github/callback`

## Step 4: Invite Users

1. In **Authentication** → **Users**, click **Invite users**
2. Enter the email of people who should have admin access
3. They'll receive an invite email to set their password

## Step 5: Access the Admin Panel

- Go to `https://YOUR-SITE.netlify.app/admin/`
- Log in with your Netlify Identity credentials
- Start creating and managing content!

## Step 6: Configure Build Notifications (Optional)

To get notified when deployments are triggered by CMS content changes:

1. Go to **Notifications** → **Deployment notifications**
2. Add email or Slack notifications for successful/failed builds

## How the Publishing Workflow Works

### When You Publish an Article:

1. **Create/Edit Article**: Use the CMS to add or update an article in the editorial workflow
2. **Publish**: Click the Publish button in the CMS
3. **Automatic Build**: Netlify automatically rebuilds your site with the new content
4. **Feed Generation**: The build process automatically:
   - Regenerates `sitemap.xml` (for search engines)
   - Updates `rss.xml` (for RSS readers)
   - Updates `search-index.json` (for search functionality)
   - Generates `robots.txt` (for SEO)
5. **Live**: Your new article is live at `https://YOUR-SITE/article/[slug].html`

## Troubleshooting

### Admin Panel Shows "Authentication Required"

- Make sure Netlify Identity is enabled
- Check that you've invited your email address in the Identity users section
- Clear browser cache and try again

### Changes Don't Appear After Publishing

- Check the **Deployments** tab in Netlify to see if the build succeeded
- Review build logs for errors in the Python build script
- Ensure your GitHub branch is set to `main` (or your deployment branch)

### Git Gateway Not Working

- Make sure Git Gateway is enabled in **Authentication** → **Services**
- Verify your GitHub repository is connected to Netlify
- Check that your GitHub account has push access to the repository

### CMS Won't Save Articles

- Check browser console for JavaScript errors
- Ensure you're using a modern browser (Chrome, Firefox, Safari, Edge)
- Try clearing browser cache and cookies
- Verify your internet connection is stable

## File Structure

```
/admin/
  - config.yml          # Decap CMS configuration
  - index.html          # Admin panel entry point

/content/
  - articles/           # Article markdown files (CMS-editable)
  - categories/         # Category definitions
  - authors/            # Author profiles

/scripts/
  - generate-feeds.py   # Auto-generates sitemap, RSS, search index

/templates/             # Jinja2 templates for HTML generation
/assets/                # CSS, JS, images
/site/                  # Generated static HTML (Netlify publish directory)
```

## Environment Variables (Optional)

You can set environment variables in Netlify to customize behavior:

- `URL`: Your site URL (auto-detected by Netlify)
- `PYTHON_VERSION`: Set to `3.11`

## Performance Notes

- Builds typically complete in 30-60 seconds
- RSS feeds include the 20 most recent articles
- Sitemap includes all articles, categories, and author pages
- Search index is embedded in HTML for instant search

## Security Notes

- Only invited users can access the admin panel
- Changes go through Git, so there's a full commit history
- All content is version-controlled in your GitHub repository
- Use strong passwords for your Netlify Identity accounts

## Support

For issues with Decap CMS: https://decapcms.org/docs
For Netlify support: https://docs.netlify.com
For GitHub issues: https://github.com/decaporg/decap-cms/issues
