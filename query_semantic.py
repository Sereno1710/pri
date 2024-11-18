import requests
import json
import sys
from transformers import AutoTokenizer
from adapters import AutoAdapterModel

tokenizer = AutoTokenizer.from_pretrained('allenai/specter2_base')
model = AutoAdapterModel.from_pretrained('allenai/specter2_base')

model.load_adapter("allenai/specter2_adhoc_query", source="hf", load_as="specter2_adhoc_query", set_active=True)

def get_query_embedding(query_text):
    inputs = tokenizer(query_text, padding=True, truncation=True, return_tensors="pt", return_token_type_ids=False, max_length=512)
    outputs = model(**inputs)
    embedding = outputs.last_hidden_state[:, 0, :].squeeze().tolist()
    return embedding

def solr_knn_query(endpoint, collection, embedding):
    url = f"{endpoint}/{collection}/select"
    data = {
        "q": f"{{!knn f=vector topK=10}}{embedding}",
        "fl": "doc_id,title,abstract,score",
        "rows": 10,
        "wt": "json"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(url, data=data, headers=headers)
    response.raise_for_status()
    return response.json()

def display_results(results):
    docs = results.get("response", {}).get("docs", [])
    if not docs:
        print("No results found.")
        return
    for idx, doc in enumerate(docs, start=1):
        print(f"Result {idx}:")
        print(f"Document ID: {doc.get('doc_id')}")
        print(f"Title: {doc.get('title')}")
        print(f"Abstract: {doc.get('abstract')}")
        print(f"Score: {doc.get('score')}")
        print("\n" + "-" * 50 + "\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 query_normal.py <output_file_path>")
        sys.exit(1)

    output_file_path = sys.argv[1]
    solr_endpoint = "http://localhost:8983/solr"
    collection = "covid"
    query_text = input("Enter your query: ")
    query_embedding = get_query_embedding(query_text)

    try:
        results = solr_knn_query(solr_endpoint, collection, query_embedding)
        display_results(results)
        with open(output_file_path, "w") as file:
            json.dump({"response": {"docs": results.get("response", {}).get("docs", [])}}, file, indent=2)
    except requests.HTTPError as e:
        print(f"Error {e.response.status_code}: {e.response.text}")

if __name__ == "__main__":
    main()
