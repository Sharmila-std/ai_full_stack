from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from .database import engine, Base, get_db
from .schemas import SearchRequest, SearchResponse, InfluencerResponse, InfluencerCreate
from .services import crm_service, google_service, youtube_service, groq_service

# Initialize database tables
# This creates the tables if they don't already exist in the database.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Influencer Discovery Agent API",
    description="Backend service for searching and saving social media influencers to a CRM.",
    version="1.0.0"
)

# Enable CORS for Next.js development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local testing, allow all or specify frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "running", "message": "AI Influencer Discovery Agent API is active."}

@app.post("/api/search", response_model=SearchResponse)
async def search_influencers(request: SearchRequest):
    """
    Orchestrates the entire discovery pipeline:
    1. Python templates generate query terms.
    2. Google (Serper) and YouTube search concurrently.
    3. Python removes invalid profile URLs and filters duplicates.
    4. Groq LLM filters candidates and generates match score & reason.
    """
    if not request.prompt.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prompt cannot be empty."
        )

    all_candidates = []
    
    # Trigger Serper for selected platforms
    has_serper_platform = any(p.lower() in ["instagram", "tiktok", "twitter", "x"] for p in request.platforms)
    if has_serper_platform:
        google_candidates = await google_service.search_google_serper(request.prompt, request.platforms)
        all_candidates.extend(google_candidates)

    # Trigger YouTube API if selected
    if any(p.lower() == "youtube" for p in request.platforms):
        youtube_candidates = await youtube_service.search_youtube_channels(request.prompt)
        all_candidates.extend(youtube_candidates)

    if not all_candidates:
        return {"results": []}

    # Deduplicate profile URLs in Python first
    seen_urls = set()
    deduped_candidates = []
    for candidate in all_candidates:
        url = candidate["profile_url"]
        if url not in seen_urls:
            seen_urls.add(url)
            deduped_candidates.append(candidate)

    # Send filtered candidates to Groq for matching evaluation
    final_matches = await groq_service.evaluate_candidates(request.prompt, deduped_candidates)
    
    return {"results": final_matches}

@app.get("/api/crm", response_model=List[InfluencerResponse])
def get_crm_influencers(db: Session = Depends(get_db)):
    """
    Retrieves all saved influencers from the CRM database.
    """
    return crm_service.get_influencers(db)

@app.post("/api/crm", response_model=InfluencerResponse, status_code=status.HTTP_201_CREATED)
def save_influencer_to_crm(influencer: InfluencerCreate, db: Session = Depends(get_db)):
    """
    Saves an influencer profile to PostgreSQL. Prevents duplicate profile_url inserts.
    """
    return crm_service.create_influencer(db, influencer)

@app.delete("/api/crm/{id}")
def delete_influencer_from_crm(id: UUID, db: Session = Depends(get_db)):
    """
    Deletes a saved influencer profile from the CRM.
    """
    success = crm_service.delete_influencer(db, id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Influencer with ID {id} not found in CRM."
        )
    return {"status": "success", "message": "Influencer deleted from CRM."}
