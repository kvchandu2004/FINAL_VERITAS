from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import requests
import logging
import os
import re
import pandas as pd


from app.database import get_db
from app.models.manuscript import Manuscript
from app.utils.file_handler import save_uploaded_file
from app.utils.pdf_extractor import extract_text_from_pdf
from app.utils.auth import get_current_user
from app.utils.csad_engine import analyze_citations_and_style,build_graph
from app.schemas.manuscript import ManuscriptUploadResponse

router = APIRouter(prefix="/manuscripts", tags=["manuscripts"])
logger = logging.getLogger(__name__)

SAIV_URL = "http://127.0.0.1:8001/analyze_authorship"

try:
    df_retracted = pd.read_csv("retractions.csv", encoding="latin-1", on_bad_lines="skip")
    retracted_db = set(df_retracted[df_retracted["RetractionNature"] == "Retraction"]["OriginalPaperDOI"].dropna().str.lower().str.strip())
    logger.info(f"CSAD: Loaded {len(retracted_db)} retracted DOIs.")
except Exception as e:
    logger.error(f"CSAD: Failed to load retractions.csv: {e}")
    retracted_db = set()


def extract_sections(full_text: str, abstract_fallback: str = ""):
    # -------------------------------------------------
    # 1. STANDARDIZE TEXT
    # -------------------------------------------------
    text = " ".join(full_text.split())

    # -------------------------------------------------
    # 2. INTRODUCTION & REFERENCES ANCHORS
    # -------------------------------------------------
    intro_match = re.search(r"(?i)\b(?:1\.|I\.)?\s*Introduction\b", text)
    intro_start = intro_match.start() if intro_match else 500

    ref_match = re.search(r"(?i)\b(references|bibliography|works cited)\b", text)
    end_of_content = ref_match.start() if ref_match else len(text)

    # -------------------------------------------------
    # 3. ABSTRACT EXTRACTION (MERGED LOGIC)
    # -------------------------------------------------
    # Primary IEEE / Elsevier pattern (avoids Graphical Abstract)
    abs_match = re.search(
        r"(?i)(?<!GRAPHICAL\s)"
        r"A\s*B\s*S\s*T\s*R\s*A\s*C\s*T\s*[:\.\-]*\s*"
        r"(.*?)"
        r"(?=\s*(?:1\.\s*Introduction|I\.\s*Introduction|"
        r"Keywords:|Index Terms:|Highlights:|Graphical Abstract:))",
        text,
        re.DOTALL
    )

    if abs_match:
        abstract = abs_match.group(1).strip()
    else:
        # Structural fallback: text before Introduction
        pre_intro = text[:intro_start].strip()
        abstract = pre_intro[-800:] if len(pre_intro) > 800 else pre_intro

    # Final abstract fallback safety
    if not abstract or len(abstract) < 20:
        abstract = (
            abstract_fallback
            if (abstract_fallback and abstract_fallback.lower() != "string")
            else "Abstract extraction failed."
        )

    # -------------------------------------------------
    # 4. CONCLUSION EXTRACTION (ROBUST + FALLBACK)
    # -------------------------------------------------
    conc_patterns = [
        r"(?i)\b\d+\.\s*Conclusion\b",
        r"(?i)\bConclusion\b",
        r"(?i)\bSummary\b",
        r"(?i)\bConcluding Remarks\b",
        r"(?i)\bSummary and Future Work\b"
    ]

    conclusion = ""
    body_end = end_of_content

    for pattern in conc_patterns:
        matches = list(re.finditer(pattern, text[:end_of_content]))
        if matches:
            last_match = matches[-1]
            conclusion = text[last_match.end():end_of_content].strip()
            body_end = last_match.start()
            break

    # Structural fallback if no conclusion heading exists
    if not conclusion:
        conclusion = text[max(0, end_of_content - 1500):end_of_content].strip()
        body_end = max(intro_start, end_of_content - 1500)

    # -------------------------------------------------
    # 5. BODY EXTRACTION (CLEAN & BOUNDED)
    # -------------------------------------------------
    body = text[intro_start:body_end].strip()

    # -------------------------------------------------
    # 6. REFERENCE LIST EXTRACTION (CSAD-READY)
    # -------------------------------------------------
    references_list = []

    if ref_match:
        ref_section = text[ref_match.start():]
        raw_refs = re.split(r"\[\d+\]|\n\d+\.\s+|\d+\.\s+", ref_section)

        for r in raw_refs:
            clean_ref = r.strip()
            if len(clean_ref) > 15:
                doi_match = re.search(
                    r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+",
                    clean_ref
                )
                doi = (
                    doi_match.group(0)
                    .lower()
                    .strip()
                    .rstrip(".,;:")
                    if doi_match else None
                )

                author_part = re.split(
                    r"\(\d{4}\)|\b\d{4}\b",
                    clean_ref
                )[0].strip()

                references_list.append({
                    "author": author_part,
                    "doi": doi,
                    "raw": clean_ref
                })

    # -------------------------------------------------
    # 7. FINAL SAFE OUTPUT (AI-READY)
    # -------------------------------------------------
    return {
        "abstract": abstract,
        "body": body[:12000],             # Safe cap
        "conclusion": conclusion[:5000],  # Safe cap
        "references_list": references_list
    }


@router.post("/upload", response_model=ManuscriptUploadResponse)
async def upload_manuscript(
    title: str = Form(...),
    abstract_provided: str = Form(None),
    doi: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    file_path, file_size = await save_uploaded_file(file)
    
    try:
        # 1. Extraction
        extraction = extract_text_from_pdf(file_path)
        full_text = extraction["full_text"]
        metadata_author = extraction["metadata"].get("author", "Unknown")
        sections = extract_sections(full_text, abstract_fallback=abstract_provided or "")
        
        # 2. SAIV Analysis (AI Detection + Claim Verification)
        ai_results = {"ai_likelihood": 0.0,
                       "ai_explanation": "Connection failed",
                       "semantic_similarity": 0.0, 
                       "semantic_flagged": False,
                       "claim_verification": None,
                       "section_similarity": None,
                    }
        try:
            saiv_payload = {
                "abstract": sections["abstract"][:5000],
                "body": sections["body"][:12000],        
                "conclusion": sections["conclusion"][:5000]
            }
            res = requests.post(SAIV_URL, json=saiv_payload, timeout=120)
            print(f"DEBUG: Abstract Length: {len(saiv_payload['abstract'])} | Body Length: {len(saiv_payload['body'])} | Conclusion Length: {len(saiv_payload['conclusion'])}")
            if res.status_code == 200:
                ai_results = res.json()
                logger.info(f"SAIV claim verification: {ai_results.get('claim_verification', {}).get('num_claims', 0)} claims analyzed")
        except Exception as ai_err:
            logger.error(f"SAIV Error: {ai_err}")

        # 3. CSAD Analysis (Citation & Integrity)
        csad_results = analyze_citations_and_style(
            full_text=full_text,
            author_name=metadata_author,
            references=sections.get("references_list", []) 
        )


        print(csad_results)

        # 4. Save to MySQL
        manuscript = Manuscript(
            title=title,
            abstract=sections["abstract"],
            body=sections["body"],        # Ensure this is saved
            conclusion=sections["conclusion"], # Ensure this is saved
            doi=doi,
            file_path=file_path,
            original_filename=file.filename,
            file_size=file_size,
            extracted_text=full_text,
            page_count=extraction["page_count"],
            author_id=current_user.id,
            # AI Data
            ai_likelihood=ai_results.get("ai_likelihood"),
            ai_explanation=ai_results.get("ai_explanation"),

            semantic_similarity=ai_results.get("semantic_similarity"),
            semantic_flagged=ai_results.get("semantic_flagged", False),
            # CSAD Data
            csad_score=csad_results.get("csad_score"),
            retracted_refs_count=csad_results.get("retracted_refs_count"),
            integrity_verdict=csad_results.get("integrity_verdict"),
            # Stylometry Data (The missing column)
            stylometry_report=csad_results.get("stylometry_metrics"), 
            self_cite_ratio = csad_results.get("self_cite_ratio"),
            # Claim Verification Data (NLI-based)
            claim_verification=ai_results.get("claim_verification"),
            consistency_score=ai_results.get("claim_verification", {}).get("consistency_score") if ai_results.get("claim_verification") else None,
            claim_flagged=ai_results.get("claim_verification", {}).get("flagged", False) if ai_results.get("claim_verification") else False,
        )
        # Save manuscript first to get its ID
        db.add(manuscript)
        db.commit()
        db.refresh(manuscript)
        # Risk coefficients (paper-aligned)
        ALPHA = 0.4   # CSAD
        BETA = 0.4    # Semantic
        GAMMA = 0.2   # AI likelihood

        csad_score = csad_results.get("self_cite_rate", 0.0)
        semantic_score = ai_results.get("semantic_similarity", 1.0)
        ai_score = ai_results.get("ai_likelihood", 0.0)

        integrity_risk = (
            ALPHA * csad_score +
            BETA * (1 - semantic_score) +
            GAMMA * ai_score
        )

        overall_risk_score = round(integrity_risk, 4)

        # Now create the analysis report with both manuscript_id and editor_id
        from app.models.report import AnalysisReport
        analysis_report = AnalysisReport(
            manuscript_id=manuscript.id,
            editor_id=current_user.id,
            csad_results=csad_results,
            saiv_results=ai_results,
            overall_risk_score=overall_risk_score
        )
        
        

        db.add(analysis_report)
        db.commit()

        # 5. Build D3.js Graph Data
        graph_data = build_graph(
            paper={
                "paper_id": str(manuscript.id), 
                "author": metadata_author, 
                "references": sections.get("references_list", [])
            },
            analysis=csad_results
        )

        return {
            "manuscript": manuscript,
            "graph": graph_data
        }

    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))
    
    