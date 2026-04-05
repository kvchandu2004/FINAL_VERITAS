from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey,Float,Boolean,JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Manuscript(Base):
    __tablename__ = "manuscripts"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    abstract = Column(Text)
    body = Column(Text)
    conclusion = Column(Text)
    doi = Column(String(255))
    file_path = Column(String(500), nullable=False)
    original_filename = Column(String(255))
    file_size = Column(Integer)
    extracted_text = Column(Text)  # Full extracted text from PDF
    page_count = Column(Integer)
    author_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String(50), default="uploaded")  # uploaded, analyzing, completed
    created_at = Column(DateTime, server_default=func.now())
    ai_likelihood = Column(Float, nullable=True)
    semantic_similarity = Column(Float, nullable=True)
    semantic_flagged = Column(Boolean, default=False)
    ai_explanation = Column(Text)
    csad_score = Column(Float)
    retracted_refs_count = Column(Integer, default=0)
    self_cite_ratio = Column(Float, default=0.0)
    citation_density = Column(Float)
    stylometry_report = Column(JSON) # Stores average sentence length, etc.
    integrity_verdict = Column(String(50)) # Low/Moderate/High Risk
    # Claim Verification (from SAIV NLI module)
    claim_verification = Column(JSON, nullable=True)  # Full claim-by-claim results
    consistency_score = Column(Float, nullable=True)   # 0-1 aggregate score
    claim_flagged = Column(Boolean, default=False)     # True if consistency < 0.5
    # Relationship
    author = relationship("User", back_populates="manuscripts")
    analysis_report = relationship("AnalysisReport", back_populates="manuscript", uselist=False)

