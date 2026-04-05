import re
import pandas as pd
import networkx as nx
from collections import Counter

# --- 1. DATA LOAD & UNIFIED NORMALIZATION ---

def normalize_doi(doi):
    """Robust DOI normalizer with Length Gatekeeper."""
    if not doi or not isinstance(doi, str) or doi.lower() == "unavailable": 
        return ""
    
    # Strip URL prefixes and whitespace
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi.lower().strip())
    # Strip trailing punctuation
    doi = re.sub(r"[).,:;]+$", "", doi)
    
    # FIX: A valid DOI must be longer than 7 characters (e.g., 10.1000/123)
    # This prevents matching on publisher prefixes like "10.1007/s"
    return doi if len(doi) > 7 else ""

try:
    df_retracted = pd.read_csv("retractions.csv", encoding="latin-1", on_bad_lines="skip")
    # FIX: Only load DOIs that are long enough to be unique
    RETRACTED_SET = set(
        df_retracted[df_retracted["RetractionNature"] == "Retraction"]["OriginalPaperDOI"]
        .dropna()
        .apply(normalize_doi)
        .pipe(lambda x: x[x != ""]) # Remove empty/short fragments
    )
except Exception:
    RETRACTED_SET = set()

# --- 2. ROBUST AUTHOR & REFERENCE HELPERS ---
def clean_author_name(name):
    """Normalize author name to 'lastname firstinitial' for matching."""
    if not name or name.lower() == "unknown": return ""
    name = name.strip()
    # Rearrange "Last, First" format before initials extraction
    if "," in name:
        parts_comma = [p.strip() for p in name.split(",", 1)]
        if len(parts_comma) == 2:
            name = f"{parts_comma[1]} {parts_comma[0]}"
    name = re.sub(r"\(.*?\)|[^A-Za-z\s\.-]", " ", name)
    parts = name.strip().lower().split()
    return f"{parts[-1]} {parts[0][0]}" if len(parts) >= 2 else parts[0] if parts else ""

def parse_reference_authors(author_field):
    """Robustly splits author strings using heuristic grouping."""
    if not author_field or author_field.lower() == "unknown": return []
    s = re.sub(r"\band\b|&|;", ",", author_field, flags=re.I)
    parts = [p.strip() for p in s.split(",") if p.strip()]
    
    authors = []
    i = 0
    while i < len(parts):
        part = parts[i]
        if len(part.split()) >= 2:
            authors.append(part)
            i += 1
        elif i + 1 < len(parts):
            authors.append(f"{part} {parts[i+1]}")
            i += 2
        else:
            authors.append(part)
            i += 1
    return [a.strip() for a in authors if a.strip()]

# --- 3. ANALYSIS & SCORING ENGINE ---
def analyze_citations_and_style(full_text, author_name, references, abstract_text=""):
    """
    Final VERITAS Engine: Fixed naming conventions and graduated stylometry weights.
    """
    total_refs = len(references)
    words = re.findall(r"\b\w+\b", full_text.lower())
    total_words = len(words)
    sentences = [s.strip() for s in re.split(r'[.!?]+', full_text) if len(s) > 5]
    
    if total_refs == 0:
        return {"csad_score": 0.0, "integrity_verdict": "Low Risk", "explanations": ["No references detected."]}

    # A. Citation Integrity Metrics
    # Metadata parsing: Using surgical split to avoid Last, First fragmentation
    main_authors = [clean_author_name(a) for a in re.split(r",(?!\s*[a-z])|;|\band\b", author_name, flags=re.I)]
    per_author_self_cites = Counter()
    cited_author_freq = Counter()
    retracted_count = 0

    for ref in references:
        if normalize_doi(ref.get("doi")) in RETRACTED_SET:
            retracted_count += 1
        
        ref_authors_clean = [clean_author_name(a) for a in parse_reference_authors(ref.get("author", ""))]
        overlap = set(main_authors).intersection(set(ref_authors_clean))
        for auth in overlap:
            if auth: per_author_self_cites[auth] += 1
        for ra in ref_authors_clean:
            if ra: cited_author_freq[ra] += 1

    total_self_cites = sum(per_author_self_cites.values())
    self_cite_ratio = total_self_cites / total_refs
    retracted_ratio = retracted_count / total_refs
    cartel_authors = [a for a, count in cited_author_freq.items() if count >= 3]

    # B. Citation Density (Graduated Penalty)
    density = (total_refs / max(1, total_words)) * 1000
    density_penalty = 1.0 if density > 8 else ((density - 5) / 3 if density > 5 else 0.0)

    # C. Stylometry & Anomaly Classification
    avg_len = total_words / max(1, len(sentences))
    vocab_richness = len(set(words)) / max(1, total_words)
    passive_ratio = len(re.findall(r"\b(is|was|were|been|being)\b\s+\w+ed\b", full_text.lower())) / max(1, len(sentences))
    
    anomalies = []
    if avg_len > 35: anomalies.append("Unusually long sentences")
    if vocab_richness < 0.35: anomalies.append("Low vocabulary richness")
    if passive_ratio > 0.45: anomalies.append("High passive voice usage")
    
    style_shift = 0
    if abstract_text:
        abs_words = re.findall(r"\b\w+\b", abstract_text.lower())
        abs_avg = len(abs_words) / max(1, len(re.split(r'[.!?]+', abstract_text)))
        style_shift = abs(abs_avg - avg_len)
        if style_shift > 8: anomalies.append("Style shift (Abstract vs Body)")

    # D. Correct Stepped Penalty Logic
    stylometry_base_penalty = {0: 0.0, 1: 0.3, 2: 0.6}.get(len(anomalies), 1.0)
    csad_score = min(1.0, 
        (retracted_ratio * 0.50) + (self_cite_ratio * 0.10) + 
        (density_penalty * 0.10) + (stylometry_base_penalty * 0.30)
    )

    # E. Integrated Explainable Verdict
    # Fixed: Renamed key to 'integrity_verdict' to match the router
    verdict = "High Risk" if csad_score > 0.45 else ("Moderate Risk" if csad_score > 0.20 else "Low Risk")
    explanations = []
    if retracted_count > 0: explanations.append(f"Contains {retracted_count} retracted references.")
    if self_cite_ratio > 0.3: explanations.append("High self-citation ratio.")
    if density > 8: explanations.append("Excessive citation density detected.") # Restored
    for a in anomalies: explanations.append(f"Stylometric Anomaly: {a}.")

    return {
        "csad_score": round(csad_score, 3),
        "retracted_refs_count": retracted_count,
        "integrity_verdict": verdict, # Key synced with manuscripts.py
        "explanations": explanations or ["Standard academic integrity profile."],
        "self_cite_ratio": round(self_cite_ratio, 3),
        "citation_density": round(density, 2),
        "stylometry_metrics": {
            "avg_sentence_length": round(avg_len, 2),
            "vocab_richness": round(vocab_richness, 3),
            "passive_voice_ratio": round(passive_ratio, 3),
            "anomalies": anomalies
        },
        "per_author_self_cites": dict(per_author_self_cites),
        "cartel_authors": cartel_authors
    }

# --- 4. GRAPH BUILDER & REFERENCE ANALYSIS ---
def build_graph(paper, analysis):
    """Constructs the D3.js graph with self-cite and cartel flags."""
    G = nx.DiGraph()
    paper_id = paper["paper_id"]
    G.add_node(paper_id, type="paper", label="Current Paper")

    for ref in paper.get("references", []):
        ref_author = ref.get("author", "Unknown")
        clean_ref = clean_author_name(ref_author)
        if clean_ref:
            G.add_node(clean_ref, 
                       label=ref_author, 
                       type="author", 
                       retracted=normalize_doi(ref.get("doi")) in RETRACTED_SET,
                       is_self=clean_ref in analysis.get("per_author_self_cites", {}),
                       is_cartel=clean_ref in analysis.get("cartel_authors", []))
            G.add_edge(paper_id, clean_ref, doi=ref.get("doi", ""))

    return {
        "nodes": [{"id": str(n), **G.nodes[n]} for n in G.nodes()],
        "links": [{"source": str(u), "target": str(v), "doi": G.edges[u,v].get("doi")} for u, v in G.edges()]
    }

def lightweight_reference_analysis(references):
    """Full bibliometric breakdown for frontend."""
    years, venues, authors = [], [], Counter()
    for r in references:
        raw = r.get("raw", "")
        year_match = re.search(r"\b(19|20)\d{2}\b", raw)
        if year_match: years.append(year_match.group())
        
        venue_match = re.search(r"\.\s*([^\.]+)\.\s*\d{4}", raw)
        if venue_match: venues.append(venue_match.group(1).strip())
        
        for a in parse_reference_authors(r.get("author", "")):
            authors[clean_author_name(a)] += 1

    return {
        "year_distribution": dict(Counter(years)),
        "top_venues": dict(Counter(venues).most_common(5)),
        "most_frequent_cited_authors": dict(authors.most_common(5)),
        "total_citations": len(references)
    }