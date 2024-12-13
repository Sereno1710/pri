import requests
import json
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

def solr_text_query(endpoint, collection, query_text):
    url = f"{endpoint}/{collection}/select"
    data = {
        "q": query_text,
        "q.op": "AND",
        "fl": "doc_id,title,abstract,score",
        "defType": "edismax",
        "qf": "title^3 abstract^2",
        "rows": 30,
        "wt": "json"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.get(url, params=data, headers=headers)
    response.raise_for_status()
    return response.json()

def hybrid_search(solr_endpoint, collection, query_text):
    query_embedding = get_query_embedding(query_text)
    results = solr_text_query(solr_endpoint, collection, query_text)
    lexical_docs = results.get("response", {}).get("docs", [])
    try:
        results = solr_knn_query(solr_endpoint, collection, query_embedding)
        print('after knn')
        semantic_docs = results.get("response", {}).get("docs", [])
        return semantic_docs,lexical_docs
    except requests.HTTPError as e:
        raise RuntimeError(f"Error1 {e.response.status_code}: {e.response.text}")
    

def standardize_scores(docs):
    scores = [doc['score'] for doc in docs]
    max_score = max(scores)
    min_score = min(scores)
    for doc in docs:
        doc["score"] = (doc["score"] - min_score) / (max_score - min_score)

def add_docs(semantic_docs,lexical_docs):
    merged_docs = []
    ids = set()
    for doc in semantic_docs:
        for d in lexical_docs:
            if doc['doc_id'] == d['doc_id'] and doc['doc_id'] not in ids:
                doc['score'] = sum_scores(doc['score'],d['score'])
                ids.add(doc['doc_id'])
                merged_docs.append(doc)
                break
    for doc in semantic_docs:
        if doc not in merged_docs and doc['doc_id'] not in ids:
            doc['score'] = sum_scores(0, doc['score'])
            merged_docs.append(doc)

    for doc in lexical_docs:
        if doc not in merged_docs and doc['doc_id'] not in ids:
            doc['score'] = sum_scores(doc['score'],0)
            merged_docs.append(doc)
    return merged_docs
    
def sum_scores(lexical_score,semantic_score,alpha=0.25):
    return alpha*lexical_score + (1-alpha)*semantic_score

def main():
    solr_endpoint = "http://localhost:8983/solr"
    collection = "covid"
    while True:
        query_text = input("Enter your query: ")
        if query_text:
            break
    try:
        semantic_docs,lexical_docs = hybrid_search(solr_endpoint, collection, query_text)
    except RuntimeError as e:
        print(str(e))

    standardize_scores(semantic_docs)
    standardize_scores(lexical_docs)

    merged_docs = add_docs(semantic_docs,lexical_docs)

    merged_docs = sorted(merged_docs, key=lambda x: x.get("score", 0), reverse=True)
    merged_docs = merged_docs[:30]
    
    # for idx, doc in enumerate(merged_docs, start=1):
    #    print(f"Result {idx}:")
    #    print(f"Document ID: {doc.get('doc_id')}")
    #    print(f"Title: {doc.get('title')}")
    #    print(f"Abstract: {doc.get('abstract')}")
    #    print(f"Score: {doc.get('score')}")
    #    print("\n" + "-" * 50 + "\n")
    
    json_file_path = f"{query_text}.json"

    with open(json_file_path, "w") as file:
        json.dump({"response": {"docs": merged_docs}}, file, indent=2)
    

if __name__ == "__main__":
    main()
