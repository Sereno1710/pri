import sys
import json
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text):
    return model.encode(text, convert_to_tensor=False).tolist()

if __name__ == "__main__":
    data = json.load(sys.stdin)
    for document in data:
        title = document.get("title", "")
        abstract = document.get("abstract", "")
        combined_text = title + " " + abstract
        document["vector"] = get_embedding(combined_text)
    json.dump(data, sys.stdout, indent=4, ensure_ascii=False)
