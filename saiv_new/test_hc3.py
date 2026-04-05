from dataset import load_hc3_dataset

texts, labels = load_hc3_dataset(limit=3)

print(texts[0][:200])
print(labels)
