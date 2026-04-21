from scrapers import telugu123, greatandhra

def fetch_all_reviews(pages=1):
    """
    Fetch reviews from all sources with pagination support.
    
    Parameters:
    pages: 
        - None or 0: Scrape all available pages from each source
        - positive integer: Scrape that many pages from each source
        - default: 1
    """
    results = []
    
    # Convert pages parameter for scraper functions
    scrape_pages = pages if pages is not None and pages > 0 else None

    # Fetch from 123telugu with pagination
    try:
        telugu_reviews = telugu123.list_reviews_full(pages=scrape_pages)
        results.extend(telugu_reviews)
        if scrape_pages is None:
            print(f"✓ Fetched {len(telugu_reviews)} total reviews from 123telugu (all pages)")
        else:
            print(f"✓ Fetched {len(telugu_reviews)} total reviews from 123telugu ({scrape_pages} page(s))")
    except Exception as e:
        print(f"✗ Error fetching from 123telugu: {e}")
        
    # Fetch from greatandhra with pagination
    try:
        greatandhra_reviews = greatandhra.list_reviews_full(pages=scrape_pages)
        results.extend(greatandhra_reviews)
        if scrape_pages is None:
            print(f"✓ Fetched {len(greatandhra_reviews)} total reviews from greatandhra (all pages)")
        else:
            print(f"✓ Fetched {len(greatandhra_reviews)} total reviews from greatandhra ({scrape_pages} page(s))")
    except Exception as e:
        print(f"✗ Error fetching from greatandhra: {e}")

    return results