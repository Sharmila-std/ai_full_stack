from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from ..models import InfluencerModel
from ..schemas import InfluencerCreate
from fastapi import HTTPException, status

def normalize_url(url: str) -> str:
    if not url:
        return ""
    url_norm = url.lower().strip()
    if url_norm.startswith("https://"):
        url_norm = url_norm[8:]
    elif url_norm.startswith("http://"):
        url_norm = url_norm[7:]
    if url_norm.startswith("www."):
        url_norm = url_norm[4:]
    return "https://" + url_norm.rstrip("/")

def get_influencers(db: Session) -> List[InfluencerModel]:
    return db.query(InfluencerModel).order_by(InfluencerModel.created_at.desc()).all()

def get_influencer_by_url(db: Session, profile_url: str) -> Optional[InfluencerModel]:
    norm_url = normalize_url(profile_url)
    # Match both exact input and normalized format for backward compatibility
    return db.query(InfluencerModel).filter(
        (InfluencerModel.profile_url == profile_url) | 
        (InfluencerModel.profile_url == norm_url)
    ).first()

def get_influencer_by_id(db: Session, influencer_id: UUID) -> Optional[InfluencerModel]:
    return db.query(InfluencerModel).filter(InfluencerModel.id == influencer_id).first()

def create_influencer(db: Session, influencer: InfluencerCreate) -> InfluencerModel:
    norm_url = normalize_url(influencer.profile_url)
    existing = get_influencer_by_url(db, norm_url)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Influencer with profile URL {influencer.profile_url} already exists in CRM."
        )
    
    db_influencer = InfluencerModel(
        name=influencer.name,
        username=influencer.username,
        platform=influencer.platform,
        profile_url=norm_url,  # Save normalized URL
        bio=influencer.bio,
        followers=influencer.followers,
        match_score=influencer.match_score,
        match_reason=influencer.match_reason,
        tags=influencer.tags,
        notes=influencer.notes
    )
    db.add(db_influencer)
    db.commit()
    db.refresh(db_influencer)
    return db_influencer

def delete_influencer(db: Session, influencer_id: UUID) -> bool:
    db_influencer = get_influencer_by_id(db, influencer_id)
    if not db_influencer:
        return False
    db.delete(db_influencer)
    db.commit()
    return True
