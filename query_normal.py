import requests

def solr_text_query(endpoint, collection, query_text):
    url = f"{endpoint}/{collection}/select"
    data = {
        "q": query_text,  # Use the query text directly
        "fl": "id,title,score",
        "rows": 10,
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
    for doc in docs:
        print(f"* {doc.get('id')} {doc.get('title')} [score: {doc.get('score'):.2f}]")

def main():
    solr_endpoint = "http://localhost:8983/solr"
    collection = "covid"
    query_text = input("Enter your query: ")

    try:
        results = solr_text_query(solr_endpoint, collection, query_text)
        display_results(results)
    except requests.HTTPError as e:
        print(f"Error {e.response.status_code}: {e.response.text}")

if __name__ == "__main__":
    main()
