import requests, re, certifi
import html as html_module
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        url,
        headers=headers,
        verify=certifi.where(),
        timeout=15
    )

    response.raise_for_status()
    return response.text


def list_reviews(page=1):
    """
    Fetch review links from greatandhra reviews page with pagination
    URL format: https://www.greatandhra.com/reviews/{page}
    Returns a list of review URLs
    """
    url = f"https://www.greatandhra.com/reviews/{page}"
    
    try:
        html = fetch(url)
    except Exception as e:
        print(f"Error fetching page {page} from greatandhra: {e}")
        return []

    data = []
    soup = BeautifulSoup(html, "html.parser")
    
    # Extract review links from the page using BeautifulSoup
    # Pattern: links inside review containers
    review_links = soup.find_all("a", href=re.compile(r'/movies/reviews/'))
    
    seen = set()
    for link in review_links:
        href = link.get("href", "")
        if href and "/movies/reviews/" in href:
            # Build full URL
            if href.startswith("http"):
                full_link = href
            else:
                full_link = "https://www.greatandhra.com" + href if href.startswith("/") else f"https://www.greatandhra.com/movies/reviews/{href}"
            
            if full_link not in seen:
                seen.add(full_link)
                # Extract title from link text or URL
                title = link.get_text().strip()
                if not title:
                    link_part = href.split("/reviews/")[-1].rstrip("/")
                    title = link_part.rsplit('-', 1)[0].replace('-', ' ').strip()
                data.append({
                    "title": title,
                    "url": full_link
                })
    
    return data


def _extract_field(soup, field_name):
    """
    Extract a specific field from review content using BeautifulSoup
    Returns the field value or None if not found
    Handles field patterns like "Field Name: Value"
    """
    try:
        if not soup:
            return None
        
        # Convert to string if it's a BeautifulSoup element
        if hasattr(soup, 'get_text'):
            text = soup.get_text()
        else:
            text = str(soup)
        
        # Pattern: Field Name: [optional HTML tags] Value
        pattern = rf'{field_name}[^:]*:\s*(?:</[^>]*>)*\s*([^\n<]+?)(?=\n|<|$)'
        match = re.search(pattern, text, re.IGNORECASE)
        if match and match.group(1):
            value = match.group(1).strip()
            # Clean HTML tags and entities
            value = re.sub('<[^>]+>', '', value)
            value = html_module.unescape(value)
            return value if value else None
    except Exception:
        pass
    return None


def _extract_section(soup, section_title):
    """
    Extract a section of content that starts with a title like 'Story:', 'Performances:', etc.
    Returns the section content until the next section or a reasonable limit
    """
    try:
        if not soup:
            return None
        
        # Convert to string if it's a BeautifulSoup element
        if hasattr(soup, 'get_text'):
            text = soup.get_text()
        else:
            text = str(soup)
        
        # Pattern: Section Title: content (until next section or end)
        pattern = rf'{section_title}\s*:?\s*\n?(.*?)(?=\n\w+\s*:|$)'
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match and match.group(1):
            content = match.group(1).strip()
            # Remove HTML tags but keep text
            content = re.sub('<[^>]+>', '', content)
            content = html_module.unescape(content)
            # Clean up excessive whitespace
            content = re.sub(r'\s{2,}', ' ', content)
            return content.strip() if content.strip() else None
    except Exception:
        pass
    return None


def get_review(url):
    """
    Fetch and extract review data from individual greatandhra review page
    Extracts content from the <div class="page_news"> tag
    Extracts: title, rating, metadata fields (if present), and content
    """
    try:
        html = fetch(url)
        if not html:
            print(f"No HTML content returned from {url}")
            return None
    except Exception as e:
        print(f"Error fetching review from {url}: {e}")
        return None

    try:
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        
        # Extract title using BeautifulSoup
        title = ""
        
        # Try to get title from h1 tag
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text().strip()
        
        # Fallback to meta og:title
        if not title:
            og_title = soup.find("meta", property="og:title")
            if og_title and og_title.get("content"):
                title = og_title.get("content").strip()
        
        # Fallback to title tag
        if not title:
            title_tag = soup.find("title")
            if title_tag:
                title = title_tag.get_text().strip().split('|')[0].strip()
        
        # Fallback: extract from URL
        if not title:
            title = url.split('/reviews/')[-1].replace('-', ' ').strip('/')

        # Extract description/summary from meta tags
        description = ""
        desc_meta = soup.find("meta", property="og:description")
        if desc_meta and desc_meta.get("content"):
            description = html_module.unescape(desc_meta.get("content").strip())

        # Try to extract rating (may not be present)
        rating = None
        rating_match = re.search(r'\n Rating: \s*:\s*(\d+\.?\d*)\s*/\s*5', html, re.IGNORECASE)
        if rating_match and rating_match.group(1):
            rating = f"{rating_match.group(1)}/5"

        # Extract main content div - this is the key part
        page_news_div = soup.find("div", class_="page_news")
        if not page_news_div:
            page_news_div = soup
        
        # Extract structured metadata fields from the main div
        banner = _extract_field(page_news_div, 'Banner')
        rating = _extract_field(page_news_div, 'Rating')
        cast = _extract_field(page_news_div, 'Cast')
        dop = _extract_field(page_news_div, 'DOP')
        music_director = _extract_field(page_news_div, 'Music Director|Music')
        editor = _extract_field(page_news_div, 'Editor')
        production_designer = _extract_field(page_news_div, 'Production Designer')
        action = _extract_field(page_news_div, 'Action')
        producers = _extract_field(page_news_div, 'Producers')
        director = _extract_field(page_news_div, 'Directed by|Directed By|Written and Directed by|Director')
        release_date = _extract_field(page_news_div, 'Release Date')

        # Extract main content sections using BeautifulSoup
        story = _extract_section(page_news_div, 'Story')
        performances = _extract_section(page_news_div, 'Performances')
        technical = _extract_section(page_news_div, 'Technical Aspects|Technical')
        analysis = _extract_section(page_news_div, 'Analysis')

        # Build main content from available sections
        content_parts = []
        if description:
            content_parts.append(description)
        if story:
            content_parts.append(story)
        if performances:
            content_parts.append(performances)
        if technical:
            content_parts.append(technical)
        if analysis:
            content_parts.append(analysis)

        # If no sections found, extract all paragraphs using BeautifulSoup from page_news div
        if not content_parts:
            paragraphs = page_news_div.find_all("p")
            for p in paragraphs:
                text = p.get_text().strip()
                if text and len(text) > 10:
                    content_parts.append(text)

        content = " ".join(content_parts)

        return {
            "title": title,
            "rating": rating,
            "banner": banner,
            "cast": cast,
            "dop": dop,
            "music_director": music_director,
            "editor": editor,
            "production_designer": production_designer,
            "action": action,
            "producers": producers,
            "director": director,
            "release_date": release_date,
            "story": story,
            "performances": performances,
            "technical_aspects": technical,
            "analysis": analysis,
            "content": content,
            "source": "greatandhra",
            "url": url
        }
    
    except Exception as e:
        print(f"Error processing review from {url}: {e}")
        return None


def list_reviews_full(pages=None):
    """
    Fetch all reviews from multiple pages with pagination.
    If pages=None, continues until no more reviews are found (scrapes all pages).
    If pages=N (integer), scrapes N pages.
    """
    all_reviews = []
    page = 1
    consecutive_empty_pages = 0
    max_empty_pages = 2  # Stop after 2 consecutive empty pages
    
    while True:
        # If pages limit is set and reached, stop
        if pages is not None and page > pages:
            break
        
        try:
            review_urls = list_reviews(page)
            
            if not review_urls:
                consecutive_empty_pages += 1
                print(f"No reviews found on greatandhra page {page}")
                
                # If pages limit is not set, stop after consecutive empty pages
                if pages is None and consecutive_empty_pages >= max_empty_pages:
                    print(f"Reached end of pages (consecutive empty pages: {consecutive_empty_pages})")
                    break
            else:
                consecutive_empty_pages = 0  # Reset counter when we find reviews
                
                for review_item in review_urls:
                    review_data = get_review(review_item["url"])
                    if review_data:
                        all_reviews.append(review_data)
                
                print(f"✓ Fetched {len(review_urls)} reviews from greatandhra (page {page})")
            
            page += 1
            
        except Exception as e:
            print(f"✗ Error fetching page {page} from greatandhra: {e}")
            consecutive_empty_pages += 1
            
            if pages is None and consecutive_empty_pages >= max_empty_pages:
                break
            
            page += 1
    
    return all_reviews


def fetch_all_reviews(pages=None):
    """
    Alias for list_reviews_full for backward compatibility
    pages: None for all pages, or integer for specific number of pages
    """
    return list_reviews_full(pages)