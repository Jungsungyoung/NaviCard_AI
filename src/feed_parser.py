
import feedparser
import time
from datetime import datetime, timedelta
from dateutil import parser as date_parser
import requests
from bs4 import BeautifulSoup
import re
import os

# Configuration
FEED_URLS = [
    "https://www.navalnews.com/feed/",
    "https://news.usni.org/feed",
    "https://www.defensenews.com/arc/outboundfeeds/rss/category/naval/?outputType=xml",
    "https://www.janes.com/feed",
]

# Keywords for High-Valued Technical Content (Ship Control & Platforms)
TARGET_KEYWORDS = [
    r"USV", r"Unmanned Surface", r"Autonomous Navigation", 
    r"Ship Control", r"ECS", r"IPMS", r"Integrated Platform Management",
    r"Propulsion", r"Smart Ship", r"Digital Twin", 
    r"Bridge System", r"C2", r"Command and Control",
    r"Frigate", r"Destroyer", r"Submarine", r"Corvette"
]

# Keywords to Exclude (Pure Weapons)
EXCLUDE_KEYWORDS = [
    r"Torpedo", r"Missile", r"Ammo", r"Ammunition", r"Gun", r"Rifle", 
    r"Bullet", r"Warhead", r"Strike Fighter", r"Aircraft"
]

def is_recent(published_parsed, hours=24):
    """Check if the article was published within the last N hours."""
    if not published_parsed:
        return False
    
    published_dt = datetime.fromtimestamp(time.mktime(published_parsed))
    limit_dt = datetime.now() - timedelta(hours=hours)
    return published_dt > limit_dt

def contains_keywords(text, keywords):
    """Check if text contains any of the target keywords (case-insensitive)."""
    if not text:
        return False
    
    text_lower = text.lower()
    for kw in keywords:
        if re.search(kw.lower(), text_lower):
            return True
    return False

def contains_exclude_keywords(text, exclude_keywords):
    """Check if text contains exclude keywords BUT NOT target keywords."""
    # If the article talks about "Missile integration with IPMS", we want it.
    # If it talks about "New Missile Test", we might not want it.
    # For now, strict exclusion if ANY exclude keyword is present?
    # Better logic: Exclude if (Exclude in text) AND (Target NOT in text).
    # But collect_news calls contains_keywords checks Target already.
    # So here we just check Exclude.
    
    text_lower = text.lower()
    for kw in exclude_keywords:
        if re.search(kw.lower(), text_lower):
            return True
    return False

def clean_html(html_content):
    """Remove HTML tags to get raw text for analysis."""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text().strip()

def collect_news():
    print(f"[*] Starting news collection from {len(FEED_URLS)} feeds...")
    collected_articles = []
    seen_links = set()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for url in FEED_URLS:
        try:
            print(f"Processing: {url}")
            # Use requests to fetch first
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"Failed to fetch {url}: Status {response.status_code}")
                continue
                
            feed = feedparser.parse(response.content)
            
            if not feed.entries:
                print(f"  -> No entries found in {url}")
                continue
            
            print(f"  -> Found {len(feed.entries)} entries. Filtering...")

            for entry in feed.entries:
                # 1. Check Recency
                if not is_recent(entry.get('published_parsed')):
                    # print(f"    Skip (Old): {entry.get('title')}")
                    continue
                
                # 2. Deduplication
                link = entry.get('link')
                if link in seen_links:
                    continue
                seen_links.add(link)

                # 3. Content Extraction
                title = entry.get('title', '')
                summary = clean_html(entry.get('summary', '') or entry.get('description', ''))
                content = ""
                if 'content' in entry:
                    content = clean_html(entry['content'][0].value)
                
                full_text = f"{title} {summary} {content}"

                # 4. Keyword Filtering
                is_target = contains_keywords(full_text, TARGET_KEYWORDS)
                is_excluded = contains_exclude_keywords(full_text, EXCLUDE_KEYWORDS)
                
                # Logic: Must have Target Keyword.
                # If it has Exclude Keyword, it is discarded UNLESS it is specifically about control/platform?
                # User request: "Exclude weapons scope, focus on ship/USV/Control".
                # Simplest approach: If it has Exclude keyword, drop it, unless we really trust Target keywords.
                # Let's try: If it contains Exclude Keyword, we drop it regardless (strict filter for now given 'Scope Change' note).
                
                if not is_target:
                    # print(f"    Skip (No Target KW): {title}")
                    continue

                if is_excluded:
                     # Check if it ALSO strongly matches Platform Control to save it?
                     # For now, strict exclusion to satisfy "Exclude weapons".
                     # print(f"    Skip (Excluded Topic): {title}")
                     continue

                print(f"  [+] Match: {title}")
                article_data = {
                    'title': title,
                    'link': link,
                    'published': time.strftime('%Y-%m-%d %H:%M:%S', entry.published_parsed) if entry.get('published_parsed') else datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'source': feed.feed.get('title', 'Unknown Source'),
                    'summary': summary
                }
                collected_articles.append(article_data)
                
        except Exception as e:
            print(f"Error parsing {url}: {e}")

    print(f"[*] Collection complete. Found {len(collected_articles)} relevant articles.")
    return collected_articles

if __name__ == "__main__":
    news = collect_news()
    for i, n in enumerate(news):
        print(f"[{i+1}] {n['title']} ({n['published']})")
