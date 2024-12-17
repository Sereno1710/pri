import requests
import cohere
from transformers import AutoTokenizer
from adapters import AutoAdapterModel

tokenizer = AutoTokenizer.from_pretrained('allenai/specter2_base')
model = AutoAdapterModel.from_pretrained('allenai/specter2_base')
model.load_adapter("allenai/specter2_adhoc_query", source="hf", load_as="specter2_adhoc_query", set_active=True)

co = cohere.Client('SHbDLjJgqsRhcndpOT88wmmc68RTcSeUtGF3aTtO')

queries_and_qrels_paths = {
    "fever fatigue influenza": "./evaluation/qrels/qrels_q1.txt",
    "effect sars-cov-2 children": "./evaluation/qrels/qrels_q2.txt",
    "masks social distancing spread virus": "./evaluation/qrels/qrels_q3.txt"
}

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
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=data, headers=headers)
    response.raise_for_status()
    return response.json()

def get_relevant_docs_rerank(query_text, docs):
    doc_texts = [f"{doc.get('title', '')} {doc.get('abstract', '')}" for doc in docs]
    results = co.rerank(model='rerank-v3.5', query=query_text, documents=doc_texts, top_n=10)
    return [
        {
            "doc_id": docs[result.index].get('doc_id'),
            "title": docs[result.index].get('title'),
            "abstract": docs[result.index].get('abstract'),
            "score": result.relevance_score
        }
        for result in results.results
    ]

def load_qrels(file_path):
    with open(file_path, 'r') as f:
        return {line.strip() for line in f}  

def check_relevance(docs, qrels):
    for doc in docs:
        doc["relevant"] = doc.get("doc_id", "") in qrels
    return docs

def perform_search(solr_endpoint, collection, query_text):
    print(f"\n### Query: {query_text} ###\n")
    query_embedding = get_query_embedding(query_text)

    try:
        results = solr_knn_query(solr_endpoint, collection, query_embedding)
        docs = results.get("response", {}).get("docs", [])

        reranked_docs = get_relevant_docs_rerank(query_text, docs)

        qrels_path = queries_and_qrels_paths.get(query_text)
        if qrels_path:
            qrels = load_qrels(qrels_path)
            return check_relevance(reranked_docs, qrels)
        
        return reranked_docs
       
    except requests.HTTPError as e:
        raise RuntimeError(f"Error {e.response.status_code}: {e.response.text}")

def display_results(docs):
    for idx, doc in enumerate(docs, start=1):
        print(f"Result {idx}:")
        print(f"Document ID: {doc.get('doc_id')}")
        print(f"Title: {doc.get('title')}")
        print(f"Abstract: {doc.get('abstract')}")
        print(f"Score: {doc.get('score'):.4f}")
        print(f"Relevance: {'Relevant' if doc.get('relevant') else 'Not Relevant'}")
        print("\n" + "-" * 50 + "\n")

# 
if __name__ == "__main__":
    solr_endpoint = "http://localhost:8983/solr"
    collection = "covid"


    for query_text in queries_and_qrels_paths:
        try:
            results = perform_search(solr_endpoint, collection, query_text, queries_and_qrels_paths)
            display_results(results)
        except RuntimeError as e:
            print(str(e))
