import requests
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

def get_relevant_docs_rerank(query_text, docs):   
    doc_texts = [
        f"{doc.get('title', '')} {doc.get('abstract', '')}"
        for doc in docs
    ]
    
    results = co.rerank(
        model='rerank-v3.5',
        query=query_text,
        documents=doc_texts,
        top_n=10
    )

    reranked_docs = [
        {
            "doc_id": docs[result.index].get('doc_id'),
            "title": docs[result.index].get('title'),
            "abstract": docs[result.index].get('abstract'),
            "score": result.relevance_score
        }
        for result in results.results
    ]

    return reranked_docs


def display_results(docs):
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
    solr_endpoint = "http://localhost:8983/solr"
    collection = "covid"
    query_text = input("Enter your query: ")
    query_embedding = get_query_embedding(query_text)

    try:
        results = solr_knn_query(solr_endpoint, collection, query_embedding)
        docs = results.get("response", {}).get("docs", [])
        reranked_docs = get_relevant_docs_rerank(query_text, docs)
        display_results(reranked_docs)
    except requests.HTTPError as e:
        print(f"Error {e.response.status_code}: {e.response.text}")

if __name__ == "__main__":
    main()