"""
Claim Verification Module
=========================
Replaces surface-level cosine similarity with NLI-based claim entailment.
Extracts claims from the abstract and checks whether each is
supported (entailment), contradicted, or unaddressed (neutral)
by the conclusion.
"""

import re
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# =========================
# Load NLI Model (once)
# =========================
NLI_MODEL_NAME = "cross-encoder/nli-deberta-v3-base"

_nli_tokenizer = None
_nli_model = None


def _load_nli_model():
    """Lazy-load the NLI model on first use."""
    global _nli_tokenizer, _nli_model
    if _nli_tokenizer is None:
        print(f"Loading NLI model: {NLI_MODEL_NAME} ...")
        _nli_tokenizer = AutoTokenizer.from_pretrained(NLI_MODEL_NAME)
        _nli_model = AutoModelForSequenceClassification.from_pretrained(NLI_MODEL_NAME)
        _nli_model.eval()
        print("NLI model loaded.")
    return _nli_tokenizer, _nli_model


# Label mapping for cross-encoder/nli-deberta-v3-base
# id2label: {0: "contradiction", 1: "entailment", 2: "neutral"}
LABEL_MAP = {0: "contradiction", 1: "entailment", 2: "neutral"}


# =========================
# Claim Extraction
# =========================
def extract_claims(abstract: str) -> list[str]:
    """
    Split abstract into individual claim sentences.
    Filters out very short fragments that aren't real claims.
    """
    # Split on sentence-ending punctuation
    raw_sentences = re.split(r'(?<=[.!?])\s+', abstract.strip())

    claims = []
    for sent in raw_sentences:
        sent = sent.strip()
        # Skip very short fragments (less than 5 words)
        if len(sent.split()) < 5:
            continue
        claims.append(sent)

    return claims


# =========================
# Single Claim Verification
# =========================
def verify_claim(claim: str, conclusion: str) -> dict:
    """
    Run a single claim (premise) against the conclusion (hypothesis)
    through the NLI model.

    Returns:
        {
            "claim": str,
            "label": "entailment" | "contradiction" | "neutral",
            "confidence": float,
            "scores": {"entailment": float, "contradiction": float, "neutral": float}
        }
    """
    tokenizer, model = _load_nli_model()

    # NLI input: [claim] [SEP] [conclusion]
    inputs = tokenizer(
        claim,
        conclusion,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding=True
    )

    with torch.no_grad():
        logits = model(**inputs).logits

    probs = torch.softmax(logits, dim=1).numpy()[0]

    pred_idx = int(np.argmax(probs))
    pred_label = LABEL_MAP[pred_idx]

    return {
        "claim": claim,
        "label": pred_label,
        "confidence": float(probs[pred_idx]),
        "scores": {
            "contradiction": float(probs[0]),
            "entailment": float(probs[1]),
            "neutral": float(probs[2]),
        }
    }


# =========================
# Full Verification Pipeline
# =========================
def verify_all_claims(abstract: str, conclusion: str) -> dict:
    """
    Main entry point. Extracts claims from abstract, verifies each
    against the conclusion, and computes an aggregate consistency score.

    Returns:
        {
            "claim_results": [per-claim dicts],
            "consistency_score": float (0-1),
            "num_claims": int,
            "num_supported": int,
            "num_contradicted": int,
            "num_neutral": int,
            "flagged": bool
        }
    """
    claims = extract_claims(abstract)

    if not claims:
        # No extractable claims — return neutral result
        return {
            "claim_results": [],
            "consistency_score": 1.0,
            "num_claims": 0,
            "num_supported": 0,
            "num_contradicted": 0,
            "num_neutral": 0,
            "flagged": False,
        }

    # Verify each claim
    claim_results = []
    for claim in claims:
        result = verify_claim(claim, conclusion)
        claim_results.append(result)

    # Count labels
    num_supported = sum(1 for r in claim_results if r["label"] == "entailment")
    num_contradicted = sum(1 for r in claim_results if r["label"] == "contradiction")
    num_neutral = sum(1 for r in claim_results if r["label"] == "neutral")

    # Compute consistency score
    # entailment = 1.0, neutral = 0.5, contradiction = 0.0
    # Weighted by confidence
    score_sum = 0.0
    weight_sum = 0.0
    for r in claim_results:
        conf = r["confidence"]
        if r["label"] == "entailment":
            score_sum += 1.0 * conf
        elif r["label"] == "neutral":
            score_sum += 0.5 * conf
        else:  # contradiction
            score_sum += 0.0 * conf
        weight_sum += conf

    consistency_score = score_sum / weight_sum if weight_sum > 0 else 0.5

    return {
        "claim_results": claim_results,
        "consistency_score": float(np.clip(consistency_score, 0.0, 1.0)),
        "num_claims": len(claims),
        "num_supported": num_supported,
        "num_contradicted": num_contradicted,
        "num_neutral": num_neutral,
        "flagged": consistency_score < 0.5,
    }
