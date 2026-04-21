from flask import Flask, jsonify, request
from db import Base, engine, SessionLocal
from models import Review
from services.aggregator import fetch_all_reviews

app = Flask(__name__)

# Create DB tables
Base.metadata.create_all(bind=engine)


@app.route("/")
def home():
    return {"message": "Movie Review API Running"}


# 🔹 Fetch & store new reviews with optional pagination
@app.route("/scrape")
def scrape():
    """
    Scrape reviews from all sources
    Query parameters:
    - pages (optional): number of pages to fetch from each source
      * 0 or omitted: scrape 1 page (default)
      * positive integer: scrape that many pages
      * 'all': scrape all available pages
    
    Examples:
    - GET /scrape  (default: 1 page)
    - GET /scrape?pages=5  (5 pages from each source)
    - GET /scrape?pages=all  (all available pages from each source)
    """
    db = SessionLocal()
    
    # Get pages parameter from query string
    pages_param = request.args.get('pages', '1')
    
    # Parse pages parameter
    if pages_param.lower() == 'all':
        pages = None  # None means scrape all pages
    else:
        try:
            pages = int(pages_param)
        except ValueError:
            pages = 1
    
    try:
        data = fetch_all_reviews(pages=pages)
        
        saved = 0
        duplicates = 0
        errors = 0
        
        for item in data:
            if not item:
                errors += 1
                continue
            
            exists = db.query(Review).filter_by(url=item["url"]).first()
            if not exists:
                review = Review(**item)
                db.add(review)
                saved += 1
            else:
                duplicates += 1
        
        db.commit()
        
        return {
            "message": f"Scraping completed",
            "saved": saved,
            "duplicates": duplicates,
            "errors": errors,
            "pages_parameter": pages_param,
            "total_processed": saved + duplicates + errors
        }
    except Exception as e:
        db.rollback()
        return {"error": str(e)}, 500
    finally:
        db.close()


# 🔹 Get all reviews
@app.route("/reviews")
def get_reviews():
    db = SessionLocal()
    reviews = db.query(Review).all()

    result = [
        {
            "title": r.title,
            "source": r.source,
            "url": r.url
        } for r in reviews
    ]

    db.close()
    return jsonify(result)


# 🔹 Filter by source
@app.route("/reviews/<source>")
def get_by_source(source):
    db = SessionLocal()
    reviews = db.query(Review).filter_by(source=source).all()

    result = [
        {
            "title": r.title,
            "url": r.url
        } for r in reviews
    ]

    db.close()
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)