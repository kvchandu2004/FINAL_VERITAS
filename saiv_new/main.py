from fastapi import FastAPI
from pydantic import BaseModel
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from model import predict_ai_score, get_embedding, explain_ai_likelihood
from claim_verifier import verify_all_claims

app = FastAPI()

class ManuscriptText(BaseModel):
    abstract: str
    body: str
    conclusion: str

@app.post("/analyze_authorship")
def analyze_authorship(data: ManuscriptText):

    # --- THE SAFETY GATE ---
    # Prevents NaN errors if text is missing
    if not data.abstract.strip() or not data.conclusion.strip():
        return {
            "section_similarity": {
                "abstract_body": 0.0,
                "body_conclusion": 0.0,
                "abstract_conclusion": 0.0,
                "overall": 0.0,
            },
            "semantic_similarity": 0.0,
            "semantic_flagged": True,
            "claim_verification": None,
            "ai_likelihood": 0.0,
            "ai_explanation": "Incomplete extraction: Abstract or Conclusion was missing from the PDF."
        }

    try:
        # =========================
        # Layer 1: Section-level cosine similarity (topic coherence)
        # =========================
        emb_abs = get_embedding(data.abstract)
        emb_body = get_embedding(data.body)
        emb_con = get_embedding(data.conclusion)

        sim_abs_body = float(cosine_similarity(
            emb_abs.reshape(1, -1), emb_body.reshape(1, -1)
        )[0][0])

        sim_body_con = float(cosine_similarity(
            emb_body.reshape(1, -1), emb_con.reshape(1, -1)
        )[0][0])

        sim_abs_con = float(cosine_similarity(
            emb_abs.reshape(1, -1), emb_con.reshape(1, -1)
        )[0][0])

        overall_similarity = float((sim_abs_body + sim_body_con + sim_abs_con) / 3)

        # NaN safety
        for val in [sim_abs_body, sim_body_con, sim_abs_con, overall_similarity]:
            if np.isnan(val):
                val = 0.0

        similarity_flagged = overall_similarity < 0.6

        # =========================
        # Layer 2: Claim verification (abstract → conclusion)
        # =========================
        claim_result = verify_all_claims(data.abstract, data.conclusion)

        # =========================
        # AI Authorship Detection
        # =========================
        ai_score = predict_ai_score(data.body)
        ai_score = float(ai_score)

        ai_flag = True if ai_score > 0.7 else False
        print("THRESHOLD CHECK: ai_score =", ai_score)
        print("USING 0.7 THRESHOLD")

        return {
            # Layer 1: Topic coherence
            "section_similarity": {
                "abstract_body": sim_abs_body,
                "body_conclusion": sim_body_con,
                "abstract_conclusion": sim_abs_con,
                "overall": overall_similarity,
            },
            "semantic_similarity": overall_similarity,
            "semantic_flagged": similarity_flagged,

            # Layer 2: Claim verification
            "claim_verification": claim_result,

            # AI authorship
            "ai_likelihood": ai_score,
            "ai_explanation": explain_ai_likelihood(ai_score)
        }

    except Exception as e:
        # Ensures the backend never gets a 500 error from this module
        return {
            "section_similarity": {
                "abstract_body": 0.0,
                "body_conclusion": 0.0,
                "abstract_conclusion": 0.0,
                "overall": 0.0,
            },
            "semantic_similarity": 0.0,
            "semantic_flagged": False,
            "claim_verification": None,
            "ai_likelihood": 0.0,
            "ai_explanation": f"Model calculation error: {str(e)}"
        }
