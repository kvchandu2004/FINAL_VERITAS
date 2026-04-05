from datasets import load_dataset

def load_hc3_dataset(limit=2000):
    dataset = load_dataset("Hello-SimpleAI/HC3", "all", split="train")

    texts = []
    labels = []

    for i in range(limit):
        sample = dataset[i]
        texts.append(sample["answer"])   # AI-generated text
        labels.append(1)                 # ✅ AI = 1

    return texts, labels
