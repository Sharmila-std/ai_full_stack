import csv
import io
from fastapi import FastAPI, Depends, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from .database import engine, Base, get_db
from .models import SearchHistoryModel
from .schemas import (
    SearchRequest, 
    SearchResponse, 
    InfluencerResponse, 
    InfluencerCreate, 
    SearchHistoryResponse
)
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
async def search_influencers(request: SearchRequest, db: Session = Depends(get_db)):
    """
    Orchestrates the entire discovery pipeline:
    1. Logs the query text and platforms to search history (limits history to latest 10).
    2. Python templates generate query terms.
    3. Google (Serper) and YouTube search concurrently.
    4. Python removes invalid profile URLs and filters duplicates.
    5. Groq LLM filters candidates and generates match score & reason.
    """
    if not request.prompt.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prompt cannot be empty."
        )

    # 1. Log query to search history
    try:
        new_history = SearchHistoryModel(
            prompt=request.prompt.strip(),
            platforms=",".join(request.platforms)
        )
        db.add(new_history)
        db.commit()
        
        # Limit history to latest 10
        history_items = db.query(SearchHistoryModel).order_by(SearchHistoryModel.created_at.desc()).all()
        if len(history_items) > 10:
            for item in history_items[10:]:
                db.delete(item)
            db.commit()
    except Exception as e:
        print(f"[ERROR] Failed to save search history: {e}")

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
    
    # Sort by match score descending and limit to top 10
    final_matches.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    
    return {"results": final_matches[:10]}

@app.get("/api/search/history", response_model=List[SearchHistoryResponse])
def get_search_history(db: Session = Depends(get_db)):
    """
    Retrieves the latest 10 search queries from history.
    """
    items = db.query(SearchHistoryModel).order_by(SearchHistoryModel.created_at.desc()).limit(10).all()
    response_items = []
    for item in items:
        response_items.append({
            "id": item.id,
            "prompt": item.prompt,
            "platforms": item.platforms.split(",") if item.platforms else [],
            "created_at": item.created_at
        })
    return response_items

@app.delete("/api/search/history")
def clear_search_history(db: Session = Depends(get_db)):
    """
    Clears all search history.
    """
    db.query(SearchHistoryModel).delete()
    db.commit()
    return {"status": "success", "message": "Search history cleared."}

@app.get("/api/crm", response_model=List[InfluencerResponse])
def get_crm_influencers(db: Session = Depends(get_db)):
    """
    Retrieves all saved influencers from the CRM database.
    """
    return crm_service.get_influencers(db)

@app.post("/api/crm", response_model=InfluencerResponse, status_code=status.HTTP_201_CREATED)
def save_influencer_to_crm(influencer: InfluencerCreate, db: Session = Depends(get_db)):
    """
    Saves an influencer profile. Prevents duplicate profile_url inserts.
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

@app.get("/api/crm/export")
def export_crm_to_csv(db: Session = Depends(get_db)):
    """
    Exports all saved influencers from the CRM to a CSV file.
    """
    influencers = crm_service.get_influencers(db)
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header row matching exact assignment requests
    writer.writerow([
        "Name",
        "Username",
        "Platform",
        "Profile URL",
        "Followers",
        "Match Score",
        "Match Reason",
        "Tags",
        "Notes",
        "Created At"
    ])
    
    for inf in influencers:
        writer.writerow([
            inf.name,
            inf.username,
            inf.platform,
            inf.profile_url,
            inf.followers,
            inf.match_score,
            inf.match_reason,
            inf.tags or "",
            inf.notes or "",
            inf.created_at.strftime("%Y-%m-%d %H:%M:%S") if inf.created_at else ""
        ])
        
    csv_data = output.getvalue()
    output.close()
    
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=influencers.csv"
        }
    )
