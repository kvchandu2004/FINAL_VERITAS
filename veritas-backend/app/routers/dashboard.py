from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.manuscript import Manuscript
from app.models.report import AnalysisReport
from app.utils.auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Total manuscripts uploaded by this user
    total_manuscripts = db.query(func.count(Manuscript.id)).filter(
        Manuscript.author_id == current_user.id
    ).scalar() or 0

    # Average risk score across user's manuscripts
    avg_risk = db.query(func.avg(AnalysisReport.overall_risk_score)).join(
        Manuscript, AnalysisReport.manuscript_id == Manuscript.id
    ).filter(
        Manuscript.author_id == current_user.id,
        AnalysisReport.overall_risk_score.isnot(None)
    ).scalar()

    avg_risk_score = round(avg_risk, 4) if avg_risk is not None else None

    # Integrity score (inverse of risk, 0-100)
    integrity_score = round((1 - avg_risk_score) * 100) if avg_risk_score is not None else None

    # Recent 5 manuscripts with their report status
    recent_manuscripts = db.query(Manuscript).filter(
        Manuscript.author_id == current_user.id
    ).order_by(Manuscript.created_at.desc()).limit(5).all()

    recent_activity = []
    for m in recent_manuscripts:
        report = db.query(AnalysisReport).filter(
            AnalysisReport.manuscript_id == m.id
        ).first()

        recent_activity.append({
            "id": m.id,
            "title": m.title,
            "filename": m.original_filename,
            "status": m.status or "uploaded",
            "risk_score": report.overall_risk_score if report else None,
            "created_at": m.created_at.isoformat() if m.created_at else None
        })

    return {
        "user_name": current_user.name,
        "total_manuscripts": total_manuscripts,
        "avg_risk_score": avg_risk_score,
        "integrity_score": integrity_score,
        "recent_activity": recent_activity
    }
