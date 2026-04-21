# 🎬 Movie Reviews API

A robust Flask-based web scraping API that aggregates Telugu movie reviews from multiple sources with intelligent HTML parsing using BeautifulSoup. The application automatically fetches, parses, and stores detailed review data including ratings, cast information, technical details, and comprehensive review content.

## 🎯 Features

- **Multi-source aggregation** - Scrapes reviews from:
  - 🎭 [123telugu.com](https://www.123telugu.com/category/reviews/)
  - 📰 [GreatAndhra.com](https://www.greatandhra.com/movies/reviews/)
  
- **BeautifulSoup-based HTML parsing** - Reliable DOM-based extraction instead of regex
- **Comprehensive data extraction** - Captures:
  - Movie titles and ratings (numeric and star-based)
  - Full cast and crew details (Director, Music Director, DOP, etc.)
  - Release dates and production information
  - Detailed review content with structured sections
  - Story summaries, performance analysis, technical aspects, and verdicts
  
- **SQLite database with ORM** - SQLAlchemy-based persistent storage
- **RESTful JSON API** - Simple HTTP endpoints for scraping and data retrieval
- **Flexible pagination control** - Single page, multiple pages, or complete scraping
- **Duplicate prevention** - Unique URL constraints prevent duplicate entries
- **Comprehensive error handling** - Robust exception handling and fallbacks
- **Production-ready structure** - Modular design with services and scrapers

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- macOS, Linux, or Windows with terminal access
- Internet connection for web scraping

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone <repository-url>
cd movie_reviews_api
```

### 2. Create and activate virtual environment
```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
pip install beautifulsoup4
```

### 4. Run the application
```bash
# Using Flask CLI (recommended for development)
python -m flask run

# Or directly
python app.py
```

Server starts at **http://localhost:5000**

## 📚 API Documentation

### 1. Home Endpoint
```http
GET /
```

**Response:**
```json
{
  "message": "Movie Review API Running"
}
```

---

### 2. Scrape Reviews Endpoint
```http
GET /scrape?pages=<value>
```

Scrapes reviews from all configured sources and stores them in the SQLite database.

**Query Parameters:**

| Parameter | Value | Description |
|-----------|-------|-------------|
| `pages` | `1` (default) | Scrapes 1 page from each source |
| `pages` | Integer (e.g., `5`) | Scrapes that many pages from each source |
| `pages` | `all` | Scrapes all available pages from each source |
| `pages` | `0` | Same as `all` |

**Examples:**

```bash
# Default: Scrape 1 page from each source
curl http://localhost:5000/scrape

# Scrape 5 pages from each source
curl "http://localhost:5000/scrape?pages=5"

# Scrape all available pages
curl "http://localhost:5000/scrape?pages=all"
```

**Response:**
```json
{
  "status": "success",
  "new_reviews": 45,
  "duplicate_reviews": 5,
  "total_stored": 150
}
```

---

## 📁 Project Structure

```
movie_reviews_api/
├── app.py                      # Flask application & API routes
├── db.py                       # Database configuration & session
├── models.py                   # SQLAlchemy Review model
├── requirements.txt            # Python dependencies
├── reviews.db                  # SQLite database (auto-created)
│
├── scrapers/                   # Web scrapers for each source
│   ├── __init__.py
│   ├── telugu123.py           # 123telugu.com scraper
│   └── greatandhra.py         # GreatAndhra.com scraper
│
├── services/                   # Application services
│   └── aggregator.py          # Multi-source review aggregator
│
├── .venv/                      # Virtual environment
├── .git/                       # Git repository
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

---

## 🔧 Component Details

### Flask Application (`app.py`)

**Routes:**
- `GET /` - Health check
- `GET /scrape?pages=<value>` - Trigger scraping and storage

**Features:**
- Automatic database table creation
- Query parameter parsing for pagination
- Duplicate URL detection using `unique=True` constraint
- Transaction-based storage with error handling

---

### Database (`db.py`)

**Configuration:**
- SQLite for development/testing
- SQLAlchemy ORM
- Session factory pattern for thread-safe connections

```python
# Usage
db = SessionLocal()
reviews = db.query(Review).all()
```

---

### Data Models (`models.py`)

**Review Table Columns:**

| Field | Type | Purpose |
|-------|------|---------|
| `id` | Integer | Primary key |
| `title` | String | Movie title |
| `content` | Text | Full review text |
| `rating` | String | Review rating (e.g., "4/5", "⭐⭐⭐⭐") |
| `source` | String | Source name (123telugu/greatandhra) |
| `url` | String | Direct review URL (unique) |
| `banner` | String | Production company |
| `cast` | Text | Actor/actress names |
| `dop` | String | Director of Photography |
| `music_director` | String | Music composer |
| `editor` | String | Film editor |
| `production_designer` | String | Set designer |
| `action` | String | Action director |
| `producers` | Text | Producer names |
| `director` | String | Film director |
| `release_date` | String | Movie release date |
| `story` | Text | Story/plot summary |
| `performances` | Text | Actor performance analysis |
| `technical_aspects` | Text | Cinematography, editing, music analysis |
| `analysis` | Text | Overall verdict and analysis |

---

### Scrapers

#### 123telugu.com Scraper (`scrapers/telugu123.py`)

**Source:** https://www.123telugu.com/category/reviews/

**Key Functions:**
- `fetch(url)` - Fetches HTML with SSL and timeout handling
- `list_reviews_page(page)` - Extracts review URLs from listing pages
- `get_review_from_page(url)` - Parses individual review pages
- `list_reviews_full(pages)` - Handles pagination and aggregation

**HTML Parsing:**
```python
# Uses BeautifulSoup.find() for reliable DOM-based extraction
soup = BeautifulSoup(html, "html.parser")
main_div = soup.find("div", id="penci-post-entry-inner")

# Falls back to full page if div not found
if not main_div:
    main_div = soup
```

**Example Review Extraction:**
```python
review = get_review_from_page("https://www.123telugu.com/reviews/...")
# Returns:
{
    "title": "Movie Title",
    "rating": "3.5/5",
    "cast": "Actor 1, Actor 2",
    "director": "Director Name",
    "content": "Full review text...",
    "source": "123telugu",
    "url": "https://..."
}
```

---

#### GreatAndhra.com Scraper (`scrapers/greatandhra.py`)

**Source:** https://www.greatandhra.com/movies/reviews/

**Key Functions:**
- `fetch(url)` - Fetches HTML with SSL and timeout handling
- `list_reviews(page)` - Extracts review URLs using BeautifulSoup
- `get_review(url)` - Parses individual review pages
- `list_reviews_full(pages)` - Handles pagination and aggregation

**HTML Parsing:**
```python
# Extracts from specific div class
page_news_div = soup.find("div", class_="page_news")

# Falls back gracefully if div not found
if not page_news_div:
    page_news_div = soup
```

**Field Extraction:**
```python
# Reliable BeautifulSoup-based extraction
director = _extract_field(page_news_div, 'Directed by')
cast = _extract_field(page_news_div, 'Starring')
music = _extract_field(page_news_div, 'Music')
```

---

### Services (`services/aggregator.py`)

**Multi-source Aggregator:**
```python
def fetch_all_reviews(pages=1):
    """
    Aggregates reviews from all scrapers.
    
    Args:
        pages: None/0 for all pages, positive int for specific count
    
    Returns:
        List of review dictionaries from all sources
    """
```

**Features:**
- Orchestrates multiple scrapers
- Combines results
- Error isolation (one source failure won't crash others)
- Detailed logging

---

## 💻 Usage Examples

### Using the API with Python

```python
from services.aggregator import fetch_all_reviews
from db import SessionLocal
from models import Review

# Scrape fresh reviews
reviews = fetch_all_reviews(pages=2)
print(f"Fetched {len(reviews)} reviews")

# Query database
db = SessionLocal()
all_reviews = db.query(Review).all()

# Filter by source
telugu123_reviews = db.query(Review).filter(
    Review.source == "123telugu"
).all()

# Search by title
movie_reviews = db.query(Review).filter(
    Review.title.ilike("%movie%")
).all()

# Get review statistics
excellent_reviews = db.query(Review).filter(
    Review.rating.ilike("%5%")
).count()

print(f"Excellent reviews: {excellent_reviews}")
```

---

### Using the API with cURL

```bash
# Scrape 1 page (default)
curl http://localhost:5000/scrape

# Scrape 3 pages
curl "http://localhost:5000/scrape?pages=3"

# Scrape all available pages
curl "http://localhost:5000/scrape?pages=all"

# Pretty print JSON response
curl http://localhost:5000/scrape | python -m json.tool
```

---

### Using the API with JavaScript/Node.js

```javascript
// Fetch in Node.js
const response = await fetch('http://localhost:5000/scrape?pages=2');
const data = await response.json();
console.log(`Fetched ${data.new_reviews} new reviews`);

// Browser fetch
fetch('http://localhost:5000/scrape?pages=all')
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## 🛠️ Technologies & Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 3.0.0 | Web framework |
| SQLAlchemy | 1.4.52 | ORM for database |
| Requests | 2.31.0 | HTTP library |
| BeautifulSoup4 | Latest | HTML parsing |
| Certifi | 2023.7.22 | SSL certificate handling |

---

## 🔍 How It Works

### Scraping Flow

```
1. User calls /scrape?pages=N
   ↓
2. Aggregator starts both scrapers
   ├─→ 123telugu.list_reviews_full(N)
   │   ├─→ list_reviews_page(1..N)
   │   │   └─→ Extract URLs with BeautifulSoup
   │   └─→ get_review_from_page(url)
   │       └─→ Parse <div id="penci-post-entry-inner">
   │
   └─→ greatandhra.list_reviews_full(N)
       ├─→ list_reviews(1..N)
       │   └─→ Extract URLs with BeautifulSoup
       └─→ get_review(url)
           └─→ Parse <div class="page_news">
   ↓
3. Combined results returned
   ↓
4. Database stores with duplicate prevention
   ↓
5. Response returned to user
```

### BeautifulSoup Advantage

**Before (Regex-based):**
```python
# Fragile and error-prone
html = re.findall(r'<div[^>]*id="penci-post-entry-inner"[^>]*>(.*?)</div>', html)
# Breaks if HTML structure changes
```

**After (BeautifulSoup-based):**
```python
# Robust and maintainable
soup = BeautifulSoup(html, "html.parser")
main_div = soup.find("div", id="penci-post-entry-inner")
# Tolerates HTML variations, much more flexible
```

---

## 📊 Database Schema

```sql
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY,
    title VARCHAR,
    content TEXT,
    rating VARCHAR,
    source VARCHAR,
    url VARCHAR UNIQUE,
    banner VARCHAR,
    cast TEXT,
    dop VARCHAR,
    music_director VARCHAR,
    editor VARCHAR,
    production_designer VARCHAR,
    action VARCHAR,
    producers TEXT,
    director VARCHAR,
    release_date VARCHAR,
    story TEXT,
    performances TEXT,
    technical_aspects TEXT,
    analysis TEXT
);
```

---

## 🐛 Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'bs4'`

**Solution:**
```bash
pip install beautifulsoup4
# or
pip install -r requirements.txt
```

---

### Issue: `Import "bs4" could not be resolved`

**Solution (VS Code):**
1. Confirm virtual environment is activated
2. Run: `pip install beautifulsoup4`
3. Reload VS Code window (Cmd+R)

---

### Issue: Database is locked

**Solution:**
```bash
# Kill Flask process
pkill -f "python.*flask"

# Or manually delete and restart
rm reviews.db
python -m flask run
```

---

### Issue: No reviews are being scraped

**Debugging:**
```python
# Test scraper directly
from scrapers import telugu123
reviews = telugu123.list_reviews_full(pages=1)
print(f"Found {len(reviews)} reviews")

# Check specific URL
review = telugu123.get_review_from_page("https://...")
print(review)
```

**Common causes:**
- Website HTML structure changed
- Network connectivity issue
- Website blocked the scraper (add delay/rotate user agents)

---

### Issue: Port 5000 already in use

**Solution:**
```bash
# Use different port
flask run --port 5001

# Or kill existing process
lsof -i :5000
kill -9 <PID>
```

---

## 🚀 Production Deployment

### Before Production:

1. **Use production WSGI server**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

2. **Upgrade database**
```bash
# Switch from SQLite to PostgreSQL
pip install psycopg2-binary
# Update db.py connection string
DATABASE_URL = "postgresql://user:pass@localhost/reviews"
```

3. **Add environment configuration**
```bash
# Create .env file
DEBUG=False
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
```

4. **Implement rate limiting**
```python
from flask_limiter import Limiter
limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route("/scrape")
@limiter.limit("5 per minute")
def scrape():
    ...
```

5. **Add logging**
```python
import logging
logging.basicConfig(
    filename='scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

6. **Deploy with Docker**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

---

## 🤝 Extending the Solution

### Adding a New Scraper Source

1. **Create scraper file** (`scrapers/newsource.py`):
```python
import requests
from bs4 import BeautifulSoup

def list_reviews_full(pages=1):
    """Fetch all reviews from source with pagination."""
    reviews = []
    for page in range(1, pages + 1):
        urls = list_reviews(page)
        for url in urls:
            review = get_review(url)
            if review:
                reviews.append(review)
    return reviews

def list_reviews(page):
    """Extract review URLs from listing page."""
    # Implementation here
    pass

def get_review(url):
    """Extract review data from individual page."""
    # Return dict with review data
    pass
```

2. **Register in aggregator** (`services/aggregator.py`):
```python
from scrapers import telugu123, greatandhra, newsource

def fetch_all_reviews(pages=1):
    results = []
    
    results.extend(telugu123.list_reviews_full(pages))
    results.extend(greatandhra.list_reviews_full(pages))
    results.extend(newsource.list_reviews_full(pages))  # Add new
    
    return results
```

3. **Test thoroughly before committing**

---

## 📈 Performance Tips

- **Scraping speed:** 1-3 seconds per review (includes network latency)
- **Database:** SQLite suitable for ~10k reviews; use PostgreSQL for larger datasets
- **Full scrape:** All pages typically takes 2-5 minutes depending on internet speed
- **Caching:** Implement Redis for API responses to reduce database queries
- **Rate limiting:** Respectful scraping with delays between requests

---

## 📝 Best Practices

✅ **DO:**
- Respect website Terms of Service
- Add User-Agent headers (prevent blocking)
- Use appropriate delays between requests
- Cache results when possible
- Handle errors gracefully

❌ **DON'T:**
- Scrape aggressively (add delays)
- Ignore robots.txt
- Bypass authentication
- Store personal data without consent
- Redistribute scraped content commercially

---

## 📄 License & Attribution

This project aggregates publicly available movie reviews for educational purposes. 

**Sources:**
- 123telugu.com
- GreatAndhra.com

Please respect the intellectual property rights of these websites.

---

## 💬 Support & Issues

**For bugs or questions:**

1. Check console logs for detailed errors
2. Verify all dependencies: `pip list`
3. Test internet connectivity
4. Ensure target websites are accessible
5. Review scraper implementation for HTML changes

**Common fixes:**
```bash
# Reinstall dependencies
pip install --upgrade --force-reinstall -r requirements.txt

# Reset database
rm reviews.db

# Clear cache
rm -rf __pycache__
find . -type d -name __pycache__ -exec rm -rf {} +
```

---

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [BeautifulSoup Guide](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Requests Library](https://requests.readthedocs.io/)

---

## 🎬 Final Notes

This Movie Reviews API demonstrates:
- ✅ Web scraping best practices
- ✅ BeautifulSoup for HTML parsing
- ✅ SQLAlchemy ORM patterns
- ✅ Flask RESTful API design
- ✅ Error handling and fallbacks
- ✅ Modular, scalable architecture

**Ready to start scraping movie reviews? Happy coding! 🚀**

---

**Last Updated:** April 2026  
**Python Version:** 3.8+  
**Status:** 🟢 Production Ready
