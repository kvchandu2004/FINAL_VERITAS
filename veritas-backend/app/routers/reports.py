#veritas-backend\app\routers\reports.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.report import AnalysisReport
from app.models.manuscript import Manuscript
from app.schemas.report import ReportResponse, CSADResult, SAIVResult

router = APIRouter(prefix="/reports", tags=["reports"])

# Risk coefficients (paper-aligned)
ALPHA = 0.4   # CSAD
BETA = 0.4    # Semantic
GAMMA = 0.2   # AI likelihood


@router.get("/{manuscript_id}", response_model=ReportResponse)
async def get_analysis_report(manuscript_id: int, db: Session = Depends(get_db)):
    report = db.query(AnalysisReport).filter(
        AnalysisReport.manuscript_id == manuscript_id
    ).first()

    if not report:
        manuscript = db.query(Manuscript).filter(
            Manuscript.id == manuscript_id
        ).first()
        if not manuscript:
            raise HTTPException(status_code=404, detail="Manuscript not found")

        return {
            "id": 0,
            "manuscript_id": manuscript_id,
            "overall_risk_score": None,
            "csad_results": None,
            "saiv_results": None,
            "comments": "Analysis pending",
            "recommendation": "pending",
            "created_at": manuscript.created_at
        }

    return report


@router.post("/generate")
async def trigger_analysis(manuscript_id: int, db: Session = Depends(get_db)):
    manuscript = db.query(Manuscript).filter(
        Manuscript.id == manuscript_id
    ).first()

    if not manuscript:
        raise HTTPException(status_code=404, detail="Manuscript not found")

    manuscript.status = "analyzing"
    db.commit()

    return {"message": f"Analysis started for manuscript {manuscript_id}"}


# ---------- INTERNAL ENDPOINTS ---------- #

@router.post("/internal/csad-results")
async def receive_csad_results(
    csad_data: CSADResult,
    db: Session = Depends(get_db)
):
    manuscript = db.query(Manuscript).filter(
        Manuscript.id == csad_data.manuscript_id
    ).first()

    if not manuscript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manuscript not found"
        )

    report = db.query(AnalysisReport).filter(
        AnalysisReport.manuscript_id == csad_data.manuscript_id
    ).first()

    if not report:
        report = AnalysisReport(manuscript_id=csad_data.manuscript_id)
        db.add(report)

    report.csad_results = csad_data.model_dump()
    db.commit()
    db.refresh(report)

    return {"message": "CSAD results received", "report_id": report.id}


@router.post("/internal/saiv-results")
async def receive_saiv_results(
    saiv_data: SAIVResult,
    db: Session = Depends(get_db)
):
    manuscript = db.query(Manuscript).filter(
        Manuscript.id == saiv_data.manuscript_id
    ).first()

    if not manuscript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manuscript not found"
        )

    report = db.query(AnalysisReport).filter(
        AnalysisReport.manuscript_id == saiv_data.manuscript_id
    ).first()

    if not report:
        report = AnalysisReport(manuscript_id=saiv_data.manuscript_id)
        db.add(report)

    report.saiv_results = saiv_data.model_dump()

    # ---- FINAL INTEGRITY RISK SCORE (PAPER EQUATION) ----
    if report.csad_results and report.saiv_results:
        csad_score = report.csad_results.get("self_cite_rate", 0.0)
        semantic_score = report.saiv_results.get("semantic_similarity", 1.0)
        ai_score = report.saiv_results.get("ai_likelihood", 0.0)

        integrity_risk = (
            ALPHA * csad_score +
            BETA * (1 - semantic_score) +
            GAMMA * ai_score
        )

        report.overall_risk_score = round(integrity_risk, 4)

        manuscript.status = "completed"

        # Optional recommendation logic
        if integrity_risk < 0.3:
            report.recommendation = "approve"
        elif integrity_risk < 0.6:
            report.recommendation = "revise"
        else:
            report.recommendation = "reject"

    db.commit()
    db.refresh(report)

    return {"message": "SAIV results received", "report_id": report.id}