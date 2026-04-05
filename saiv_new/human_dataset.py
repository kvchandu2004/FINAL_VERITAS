from datasets import load_dataset

def load_human_academic_samples(limit=300):
    dataset = load_dataset(
        "scientific_papers",
        "arxiv",
        split="train",
        streaming=True
    )

    texts = []
    labels = []

    for i, paper in enumerate(dataset):
        if i >= limit:
            break

        text = paper["abstract"] + " " + " ".join(paper["section_text"])
        texts.append(text)
        labels.append(0)  # HUMAN

    return texts, labels
