import requests
from bs4 import BeautifulSoup
import json
import time
import re
import os
from datetime import datetime

BASE_URL = "https://paulgraham.com"
ARTICLES_URL = f"{BASE_URL}/articles.html"
OUTPUT_DIR = "/home/claude/pg_essays"
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; research-scraper/1.0)"
}

def get_article_links():
    """Scrape all essay links from the articles index page."""
    print("Fetching article index...")
    resp = requests.get(ARTICLES_URL, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # PG essays are .html files linked from the articles page
        if href.endswith(".html") and "/" not in href:
            links.append({
                "title": a.get_text(strip=True),
                "url": f"{BASE_URL}/{href}",
                "slug": href.replace(".html", "")
            })

    # deduplicate by slug
    seen = set()
    unique = []
    for l in links:
        if l["slug"] not in seen and l["title"]:
            seen.add(l["slug"])
            unique.append(l)

    print(f"Found {len(unique)} essays.")
    return unique


def clean_text(soup):
    """Extract clean plain text from essay page."""
    # PG's site uses simple table layouts — get all paragraph text
    # Remove script/style tags first
    for tag in soup(["script", "style"]):
        tag.decompose()

    # Try to get the main content area (usually inside <table> or <font> tags)
    text = soup.get_text(separator="\n")

    # Clean up whitespace
    lines = [line.strip() for line in text.splitlines()]
    lines = [l for l in lines if l]  # remove empty lines
    text = "\n".join(lines)

    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def scrape_essay(link):
    """Scrape a single essay and return structured data."""
    try:
        resp = requests.get(link["url"], headers=HEADERS, timeout=10)
        resp.raise_for_status()

        # PG's site uses windows-1252 encoding sometimes
        resp.encoding = resp.apparent_encoding
        soup = BeautifulSoup(resp.text, "html.parser")

        text = clean_text(soup)

        # Try to extract date — PG usually puts month/year at the top or bottom
        date_match = re.search(
            r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b",
            text
        )
        date_str = f"{date_match.group(1)} {date_match.group(2)}" if date_match else None

        essay = {
            "title": link["title"],
            "slug": link["slug"],
            "url": link["url"],
            "date": date_str,
            "word_count": len(text.split()),
            "text": text,
            "scraped_at": datetime.utcnow().isoformat()
        }

        return essay

    except Exception as e:
        print(f"  ERROR scraping {link['url']}: {e}")
        return None


def main():
    links = get_article_links()
    essays = []
    failed = []

    for i, link in enumerate(links, 1):
        print(f"[{i}/{len(links)}] Scraping: {link['title'][:60]}")
        essay = scrape_essay(link)

        if essay:
            essays.append(essay)
            # save individual file too (useful for chunking later)
            slug_path = os.path.join(OUTPUT_DIR, f"{link['slug']}.txt")
            with open(slug_path, "w", encoding="utf-8") as f:
                f.write(f"TITLE: {essay['title']}\n")
                f.write(f"URL: {essay['url']}\n")
                f.write(f"DATE: {essay['date'] or 'Unknown'}\n")
                f.write(f"WORD COUNT: {essay['word_count']}\n")
                f.write("=" * 60 + "\n\n")
                f.write(essay["text"])
        else:
            failed.append(link)

        # polite delay — don't hammer paulgraham.com
        time.sleep(1.2)

    # save master JSON
    master_path = os.path.join(OUTPUT_DIR, "_all_essays.json")
    with open(master_path, "w", encoding="utf-8") as f:
        json.dump(essays, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Scraped {len(essays)} essays → {OUTPUT_DIR}/")
    print(f"✓ Master JSON → {master_path}")
    if failed:
        print(f"✗ Failed ({len(failed)}): {[l['slug'] for l in failed]}")

    # quick stats
    total_words = sum(e["word_count"] for e in essays)
    print(f"\nCorpus stats:")
    print(f"  Total essays : {len(essays)}")
    print(f"  Total words  : {total_words:,}")
    print(f"  Avg length   : {total_words // len(essays):,} words/essay")


if __name__ == "__main__":
    main()