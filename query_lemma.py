import requests
import json
import sys

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

    try:
        results = solr_text_query(solr_endpoint, collection, query_text)
        display_results(results)
        with open(output_file_path, "w") as file:
            json.dump({"response": {"docs": results.get("response", {}).get("docs", [])}}, file, indent=2)
    except requests.HTTPError as e:
        print(f"Error {e.response.status_code}: {e.response.text}")

if __name__ == "__main__":
    main()
