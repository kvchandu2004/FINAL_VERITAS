#veritas-backend\app\schemas\report.py

from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


# --- Claim Verification Schemas ---
class ClaimResult(BaseModel):
    claim: str
    label: str  # entailment | contradiction | neutral
    confidence: float
    scores: Dict[str, float]


class ClaimVerificationSummary(BaseModel):
    claim_results: List[ClaimResult] = []
    consistency_score: float = 1.0
    num_claims: int = 0
    num_supported: int = 0
    num_contradicted: int = 0
    num_neutral: int = 0
    flagged: bool = False


class ReportResponse(BaseModel):
    id: int
    manuscript_id: int

    overall_risk_score: Optional[float]

    csad_results: Optional[Dict[str, Any]]
    saiv_results: Optional[Dict[str, Any]]

    comments: Optional[str]
    recommendation: Optional[str]

    created_at: datetime

    class Config:
        orm_mode = True


class CSADResult(BaseModel):
    manuscript_id: int

    self_cite_rate: float
    citation_anomalies: List[Dict[str, Any]]

    graph_data: Dict[str, Any]


class SAIVResult(BaseModel):
    manuscript_id: int

    ai_likelihood: float
    semantic_similarity: float
    claim_verification: Optional[ClaimVerificationSummary] = None

    flagged: bool
