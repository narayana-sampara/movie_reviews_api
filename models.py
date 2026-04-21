from sqlalchemy import Column, Integer, String, Text
from db import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(Text)
    rating = Column(String)
    source = Column(String)
    url = Column(String, unique=True)
    
    # Structured metadata fields (mainly from greatandhra)
    banner = Column(String, nullable=True)  # Production company
    cast = Column(Text, nullable=True)  # Cast list
    dop = Column(String, nullable=True)  # Director of Photography
    music_director = Column(String, nullable=True)
    editor = Column(String, nullable=True)
    production_designer = Column(String, nullable=True)
    action = Column(String, nullable=True)  # Action director
    producers = Column(Text, nullable=True)
    director = Column(String, nullable=True)
    release_date = Column(String, nullable=True)
    
    # Review section content (for detailed review tracking)
    story = Column(Text, nullable=True)
    performances = Column(Text, nullable=True)
    technical_aspects = Column(Text, nullable=True)
    analysis = Column(Text, nullable=True)