import joblib
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.calibration import CalibratedClassifierCV

from load_hc3 import load_hc3_dataset


# =========================
# Load SciBERT
# =========================
tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")
bert_model = AutoModel.from_pretrained("allenai/scibert_scivocab_uncased")
bert_model.eval()


# =========================
# Embedding function
# =========================
def get_embedding(text):
    words = text.split()
    chunks = [" ".join(words[i:i+500]) for i in range(0, len(words), 500)]
    
    embeddings = []

    for chunk in chunks:
        inputs = tokenizer(
            chunk,
            return_tensors="pt",
            truncation=True,
            padding="max_length",
            max_length=512
        )

        with torch.no_grad():
            outputs = bert_model(**inputs)

        # BERT embedding (mean pooling)
        bert_emb = outputs.last_hidden_state.mean(dim=1).numpy()

        # Style features for this chunk
        style_emb = extract_style_features(chunk)

        # Combine embeddings
        combined_emb = np.hstack([bert_emb, style_emb])

        embeddings.append(combined_emb)

    # Average all chunk embeddings
    return np.mean(embeddings, axis=0)


def extract_style_features(text):
    words = text.split()
    sentences = text.split(".")

    avg_word_len = np.mean([len(w) for w in words]) if words else 0
    sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
    avg_sentence_len = np.mean(sentence_lengths) if sentence_lengths else 0
    lexical_diversity = len(set(words)) / len(words) if words else 0

    # 🔑 MUST be 2D
    return np.array([[avg_word_len, avg_sentence_len, lexical_diversity]])




# =========================
# Training
# =========================
def train_classifier():
    texts, labels = load_hc3_dataset(limit=300)

    print(f"Training on {len(texts)} samples")

    embeddings = []
    for i, text in enumerate(texts):
        embeddings.append(get_embedding(text))
        if (i + 1) % 100 == 0:
            print(f"Processed {i+1}/{len(texts)}")

    X = np.vstack(embeddings)
    y = np.array(labels)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    base_clf = LogisticRegression(max_iter=1000)
    clf = CalibratedClassifierCV(base_clf, method="sigmoid", cv=3)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    print(classification_report(y_test, y_pred))

    joblib.dump(clf, "ai_authorship_model.joblib")
    print("✅ Model saved")


# =========================
# Prediction
# =========================
def predict_ai_score(text: str) -> float:
    clf = joblib.load("ai_authorship_model.joblib")
    emb = get_embedding(text).reshape(1, -1)
    prob = clf.predict_proba(emb)[0][1]
    return float(np.clip(prob, 0.01, 0.99))


# =========================
# Explainability
# =========================
def explain_ai_likelihood(ai_score: float) -> str:
    if ai_score > 0.85:
        return (
            "High likelihood due to consistently formal academic tone, "
            "dense technical phrasing, and uniform sentence structure, "
            "which are patterns commonly observed in AI-generated scholarly text."
        )
    elif ai_score > 0.65:
        return (
            "Moderate AI likelihood caused by structured academic style "
            "with some natural variation in phrasing."
        )
    elif ai_score > 0.4:
        return (
            "Low AI likelihood; text shows noticeable stylistic variation "
            "typical of human authorship."
        )
    else:
        return (
            "Very low AI likelihood; informal or diverse writing patterns "
            "strongly resemble human-authored text."
        )


if __name__ == "__main__":
    train_classifier()
