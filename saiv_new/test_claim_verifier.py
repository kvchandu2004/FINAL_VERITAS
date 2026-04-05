"""
Test script for Claim Verifier
Run: python test_claim_verifier.py
"""

from claim_verifier import extract_claims, verify_claim, verify_all_claims


def test_aligned_claims():
    """Abstract and conclusion agree — expect high consistency."""
    abstract = (
        "We propose a novel deep learning method for sentiment analysis. "
        "Our approach achieves 95% accuracy on the benchmark dataset. "
        "The model generalizes well across multiple domains."
    )
    conclusion = (
        "In this work, we presented a deep learning approach for sentiment analysis "
        "that achieved 94.8% accuracy on the standard benchmark, demonstrating "
        "strong generalization across different domains."
    )

    result = verify_all_claims(abstract, conclusion)

    print("=" * 60)
    print("TEST 1: Aligned Claims")
    print("=" * 60)
    print(f"Consistency Score: {result['consistency_score']:.3f}")
    print(f"Supported: {result['num_supported']}, "
          f"Contradicted: {result['num_contradicted']}, "
          f"Neutral: {result['num_neutral']}")
    print(f"Flagged: {result['flagged']}")
    for r in result["claim_results"]:
        print(f"  [{r['label']:>13}] ({r['confidence']:.2f}) {r['claim'][:80]}")
    print()


def test_contradicted_claims():
    """Abstract and conclusion disagree — expect low consistency."""
    abstract = (
        "We propose a novel method that significantly outperforms all baselines. "
        "Our approach reduces error rates by 50% compared to existing methods. "
        "The results demonstrate clear superiority of our technique."
    )
    conclusion = (
        "Our method showed mixed results compared to existing baselines. "
        "The error reduction was marginal at only 5%, falling short of expectations. "
        "Further work is needed to improve performance."
    )

    result = verify_all_claims(abstract, conclusion)

    print("=" * 60)
    print("TEST 2: Contradicted Claims")
    print("=" * 60)
    print(f"Consistency Score: {result['consistency_score']:.3f}")
    print(f"Supported: {result['num_supported']}, "
          f"Contradicted: {result['num_contradicted']}, "
          f"Neutral: {result['num_neutral']}")
    print(f"Flagged: {result['flagged']}")
    for r in result["claim_results"]:
        print(f"  [{r['label']:>13}] ({r['confidence']:.2f}) {r['claim'][:80]}")
    print()


def test_neutral_claims():
    """Abstract claims not addressed in conclusion — expect neutral labels."""
    abstract = (
        "We investigate the effect of temperature on protein folding rates. "
        "Our experiments reveal a non-linear relationship between heat and stability. "
        "The findings have implications for drug design and biotechnology."
    )
    conclusion = (
        "This paper presented a review of recent advances in machine learning "
        "for natural language processing tasks."
    )

    result = verify_all_claims(abstract, conclusion)

    print("=" * 60)
    print("TEST 3: Unrelated (Neutral) Claims")
    print("=" * 60)
    print(f"Consistency Score: {result['consistency_score']:.3f}")
    print(f"Supported: {result['num_supported']}, "
          f"Contradicted: {result['num_contradicted']}, "
          f"Neutral: {result['num_neutral']}")
    print(f"Flagged: {result['flagged']}")
    for r in result["claim_results"]:
        print(f"  [{r['label']:>13}] ({r['confidence']:.2f}) {r['claim'][:80]}")
    print()


def test_extract_claims():
    """Test claim extraction from abstract."""
    abstract = (
        "We propose X. This is a short bit. "
        "Our experiments show significant improvements over baseline methods. "
        "The model was trained on 10,000 samples from the benchmark dataset."
    )
    claims = extract_claims(abstract)

    print("=" * 60)
    print("TEST 4: Claim Extraction")
    print("=" * 60)
    for i, c in enumerate(claims, 1):
        print(f"  Claim {i}: {c}")
    print(f"  Total claims extracted: {len(claims)}")
    print()


if __name__ == "__main__":
    test_extract_claims()
    test_aligned_claims()
    test_contradicted_claims()
    test_neutral_claims()

    print("All tests completed!")
