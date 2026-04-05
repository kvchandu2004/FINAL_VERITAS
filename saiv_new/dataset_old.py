import pandas as pd
import os

def load_hc3_dataset():
    # Path to your dataset
    dataset_path = os.path.join("data", "AI_Human.csv", "AI_Human.csv")

    # Load CSV
    df = pd.read_csv(dataset_path)

    # Check available columns
    print("Columns in dataset:", df.columns.tolist())

    texts, labels = [], []
    for _, row in df.iterrows():
        if pd.notna(row["text"]):
            texts.append(str(row["text"]))
            labels.append(int(row["generated"]))  # 0 = Human, 1 = AI

    print(f"✅ Loaded {len(texts)} samples")
    print("🔹 First sample text:", texts[0][:200])
    print("🔹 First label:", labels[0])

    return texts, labels

# Run a quick test when executing this file directly
if __name__ == "__main__":
    load_hc3_dataset()
