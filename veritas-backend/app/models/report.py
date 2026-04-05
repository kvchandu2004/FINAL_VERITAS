#veritas-backend\app\models\report.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class AnalysisReport(Base):
    __tablename__ = "analysis_reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    manuscript_id = Column(
        Integer,
        ForeignKey("manuscripts.id", ondelete="CASCADE"),
        nullable=False, 
        index=True
    )

    editor_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    csad_results = Column(JSON, nullable=True)
    saiv_results = Column(JSON, nullable=True)

    overall_risk_score = Column(Float, nullable=True)

    comments = Column(Text, nullable=True)

    recommendation = Column(
        String(50),
        nullable=True
    )  # approve / revise / reject

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    manuscript = relationship(
        "Manuscript",
        back_populates="analysis_report"
    )

    editor = relationship(
        "User",
        back_populates="assigned_reports"
    )

    manuscript = relationship("Manuscript", back_populates="analysis_report")