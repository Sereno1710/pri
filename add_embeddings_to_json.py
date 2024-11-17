import sys
import json
from transformers import AutoTokenizer
from adapters import AutoAdapterModel

tokenizer = AutoTokenizer.from_pretrained('allenai/specter2_base')
model = AutoAdapterModel.from_pretrained('allenai/specter2_base')

model.load_adapter("allenai/specter2", source="hf", load_as="specter2_proximity", set_active=True)

def get_document_embedding(text):
    inputs = tokenizer(text, padding=True, truncation=True, return_tensors="pt", return_token_type_ids=False, max_length=512)
    outputs = model(**inputs)
    embedding = outputs.last_hidden_state[:, 0, :].squeeze().tolist()
    return embedding

if __name__ == "__main__":
    data = json.load(sys.stdin)
    for document in data:
        title = document.get("title", "")
        abstract = document.get("abstract", "")
        combined_text = title + " " + abstract
        document["vector"] = get_document_embedding(combined_text)
    json.dump(data, sys.stdout, indent=4, ensure_ascii=False)
