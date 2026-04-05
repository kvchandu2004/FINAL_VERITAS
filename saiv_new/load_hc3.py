import json
import os

def load_hc3_dataset(limit=300):
    base_dir = os.path.dirname(__file__)
    path = os.path.join(base_dir, "data", "hc3.jsonl")

    texts = []
    labels = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if len(texts) >= limit * 2:
                break

            item = json.loads(line)
            question = item.get("question", "")

            # HUMAN answers
            for ans in item.get("human_answers", []):
                texts.append(question + " " + ans)
                labels.append(0)  # HUMAN
                if len(texts) >= limit * 2:
                    break

            # AI answers
            for ans in item.get("chatgpt_answers", []):
                texts.append(question + " " + ans)
                labels.append(1)  # AI
                if len(texts) >= limit * 2:
                    break

    return texts, labels
