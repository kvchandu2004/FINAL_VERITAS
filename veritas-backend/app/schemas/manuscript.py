from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- NEW: Graph Schema for D3.js ---
class GraphData(BaseModel):
    nodes: List[Dict[str, Any]]
    links: List[Dict[str, Any]]

class ManuscriptBase(BaseModel):
    id: int
    title: str
    abstract: Optional[str]
    body: Optional[str] = None 
    conclusion: Optional[str] = None
    doi: Optional[str]
    original_filename: str
    status: str
    created_at: datetime
    
    # SAIV (AI Module) Fields
    ai_likelihood: Optional[float]
    ai_explanation: Optional[str]
    semantic_similarity: Optional[float]
    semantic_flagged: bool

    # CSAD (Citation Module) Fields
    csad_score: Optional[float]
    retracted_refs_count: Optional[int]
    integrity_verdict: Optional[str]
    stylometry_report: Optional[Dict[str, Any]] # For JSON metrics
    self_cite_ratio: Optional[float] = 0.0

    # Claim Verification Fields (from SAIV NLI)
    claim_verification: Optional[Dict[str, Any]] = None
    consistency_score: Optional[float] = None
    claim_flagged: Optional[bool] = False

    class Config:
        from_attributes = True

# --- FINAL RESPONSE SCHEMA ---
class ManuscriptUploadResponse(BaseModel):
    manuscript: ManuscriptBase
    graph: GraphData