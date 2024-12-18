import requests
import json
import sys
import cohere
from transformers import AutoTokenizer
from adapters import AutoAdapterModel

tokenizer = AutoTokenizer.from_pretrained('allenai/specter2_base')
model = AutoAdapterModel.from_pretrained('allenai/specter2_base')
model.load_adapter("allenai/specter2_adhoc_query", source="hf", load_as="specter2_adhoc_query", set_active=True)

co = cohere.Client('-----')

def get_query_embedding(query_text):
    inputs = tokenizer(query_text, padding=True, truncation=True, return_tensors="pt", return_token_type_ids=False, max_length=512)
    outputs = model(**inputs)
    embedding = outputs.last_hidden_state[:, 0, :].squeeze().tolist()
    return embedding

def solr_knn_query(endpoint, collection, embedding):
    url = f"{endpoint}/{collection}/select"
    data = {
        "q": f"{{!knn f=vector topK=30}}{embedding}",
        "fl": "doc_id,title,abstract,score",
        "rows": 30,
        "wt": "json"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(url, data=data, headers=headers)
    response.raise_for_status()
    return response.json()

def get_relevant_docs(query_text, results, batch_size=5):
    docs = results.get("response", {}).get("docs", [])
    if not docs:
        print("No results found.")
        return []

    relevant_doc_ids = []
    for i in range(0, len(docs), batch_size):
        batch_docs = docs[i:i+batch_size]
        prompt = f"""
        Query: '{query_text}'
        List the document IDs of relevant documents below. Only one document ID per line. Do not add any other text.
        """
        for doc in batch_docs:
            prompt += f"Document ID: {doc.get('doc_id')}\nTitle: {doc.get('title')}\nAbstract: {doc.get('abstract')}\n\n"

        response = co.chat(
            message=prompt,
            model="command",
            temperature=0.3
        )
        batch_relevant_doc_ids = response.text.split('\n')
        relevant_doc_ids.extend([doc_id.strip() for doc_id in batch_relevant_doc_ids if doc_id.strip()])
    
    return relevant_doc_ids

def rerank_docs(relevant_doc_ids, docs):
    relevant_docs = [doc for doc in docs if doc.get('doc_id') in relevant_doc_ids]
    non_relevant_docs = [doc for doc in docs if doc.get('doc_id') not in relevant_doc_ids]
    return relevant_docs + non_relevant_docs

def display_results(docs):
    if not docs:
        print("No results found.")
        return
    for idx, doc in enumerate(docs, start=1):
        print(f"Result {idx}:")
        print(f"Document ID: {doc.get('doc_id')}")
        print(f"Title: {doc.get('title')}")
        print(f"Abstract: {doc.get('abstract')}")
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
        relevant_doc_ids = get_relevant_docs(query_text, results)
        print(relevant_doc_ids)
        docs = results.get("response", {}).get("docs", [])
        reranked_docs = rerank_docs(relevant_doc_ids, docs)
        display_results(reranked_docs)
        with open(output_file_path, "w") as file:
            json.dump({"response": {"docs": reranked_docs}}, file, indent=2)
    except requests.HTTPError as e:
        print(f"Error {e.response.status_code}: {e.response.text}")

if __name__ == "__main__":
    main()