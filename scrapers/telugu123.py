import requests
import certifi
import re
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


def list_reviews_page(page=1):
    """
    Fetch review links from the 123telugu reviews category page with pagination
    Returns a list of review URLs
    """
    # Build URL based on page number
    if page == 1:
        url = "https://www.123telugu.com/category/reviews/"
    else:
        url = f"https://www.123telugu.com/category/reviews/page/{page}/"
    
    try:
        html = fetch(url)
    except Exception as e:
        print(f"Error fetching page {page} from 123telugu: {e}")
        return []
    
    # Extract all review URLs from the page
    # Pattern: https://www.123telugu.com/reviews/some-review-title with optional .html
    review_urls = re.findall(r'https://www\.123telugu\.com/reviews/([^"<>/\s]+?)(?:\.html)?(?=["\s<>])', html)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_urls = []
    for url_part in review_urls:
        # Ensure URL ends with .html for consistency
        full_url = f"https://www.123telugu.com/reviews/{url_part}.html" if not url_part.endswith('.html') else f"https://www.123telugu.com/reviews/{url_part}"
        if full_url not in seen:
            seen.add(full_url)
            unique_urls.append(full_url)
    
    return unique_urls


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
        
        # Pattern: Field Name: [optional HTML tags] Value (until newline or closing tag)
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


def get_review_from_page(review_url):
    """
    Fetch and extract structured review data from individual 123telugu review page
    Extracts all fields: title, rating, banner, cast, DOP, music director, etc.
    """
    try:
        html = fetch(review_url)
        if not html:
            print(f"No HTML content returned from {review_url}")
            return None
    except Exception as e:
        print(f"Error fetching review from {review_url}: {e}")
        return None

    try:
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        
        # Extract title - try multiple patterns
        title = ""
        
        # Try meta og:title first
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = og_title.get("content").strip()
        
        # Fallback to page title tag
        if not title:
            title_tag = soup.find("title")
            if title_tag:
                title = title_tag.get_text().strip().split('|')[0].strip()
        
        # Fallback to h1
        if not title:
            h1 = soup.find("h1")
            if h1:
                title = h1.get_text().strip()
        
        # Fallback to structured data
        if not title:
            title_match = re.search(r'"Movie Name"\s*:\s*"([^"]*)"', html)
            if title_match:
                title = title_match.group(1).strip()

        # Extract description/summary from meta tags
        description = ""
        desc_meta = soup.find("meta", property="og:description")
        if desc_meta and desc_meta.get("content"):
            description = html_module.unescape(desc_meta.get("content").strip())

        # Extract rating - look for multiple patterns
        rating = None
        
        # Pattern 1: "Rating: X/5" in text
        rating_match = re.search(r'Rating\s*(?::|<[^>]*>)*\s*(\d+\.?\d*)\s*(?:/\s*5)?', html, re.IGNORECASE)
        if rating_match:
            rating = f"{rating_match.group(1)}/5"
        else:
            # Pattern 2: "★★★★" star pattern
            stars_match = re.search(r'(★+)', html)
            if stars_match:
                rating = f"{len(stars_match.group(1))}/5"
        
        # Extract main content div
        main_div = soup.find("div", id="penci-post-entry-inner")
        if not main_div:
            main_div = soup
        
        # Extract structured metadata fields from the main div
        release_date = _extract_field(main_div, 'Release Date')
        banner = _extract_field(main_div, 'Producer')
        cast = _extract_field(main_div, 'Starring')
        dop = _extract_field(main_div, 'Cinematographer')
        music_director = _extract_field(main_div, 'Music Director')
        director = _extract_field(main_div, 'Director')
        editor = _extract_field(main_div, 'Editor')
        production_designer = None
        action = None  # 123telugu does not typically have a separate action director field
        producers = _extract_field(main_div, 'Producer')
        
        # Extract main content sections using BeautifulSoup
        story = _extract_section(main_div, 'Story')
        performances = _extract_section(main_div, 'Plus Points')
        minus_points = _extract_section(main_div, 'Minus Points')
        if performances and minus_points:
            performances = performances + " " + minus_points
        elif minus_points:
            performances = minus_points
        
        technical = _extract_section(main_div, 'Technical Aspects')
        analysis = _extract_section(main_div, 'Verdict')

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

        # If no sections found, extract all paragraphs using BeautifulSoup
        if not content_parts:
            # Look for paragraphs in the main content area
            paragraphs = main_div.find_all("p")
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
            "source": "123telugu",
            "url": review_url
        }
    
    except Exception as e:
        print(f"Error processing review from {review_url}: {e}")
        return None


def list_reviews_full(pages=1):
    """
    Fetch all reviews from multiple pages with pagination support.
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
            review_urls = list_reviews_page(page)
            
            if not review_urls:
                consecutive_empty_pages += 1
                print(f"No reviews found on 123telugu page {page}")
                
                # If pages limit is not set, stop after consecutive empty pages
                if pages is None and consecutive_empty_pages >= max_empty_pages:
                    print(f"Reached end of pages (consecutive empty pages: {consecutive_empty_pages})")
                    break
            else:
                consecutive_empty_pages = 0  # Reset counter when we find reviews
                
                for review_url in review_urls:
                    review_data = get_review_from_page(review_url)
                    if review_data:
                        all_reviews.append(review_data)
                
                print(f"✓ Fetched {len(review_urls)} reviews from 123telugu (page {page})")
            
            page += 1
            
        except Exception as e:
            print(f"✗ Error fetching page {page} from 123telugu: {e}")
            consecutive_empty_pages += 1
            
            if pages is None and consecutive_empty_pages >= max_empty_pages:
                break
            
            page += 1
    
    return all_reviews


def fetch_all_reviews(pages=1):
    """
    Alias for list_reviews_full for backward compatibility.
    pages: None for all pages, or integer for specific number of pages
    """
    return list_reviews_full(pages)