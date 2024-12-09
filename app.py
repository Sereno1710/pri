import streamlit as st
from query_streaml_lit import perform_search, display_results  
### search and re-rank


def on_send_query(solr_endpoint, collection, query_text):
   
    try:
        reranked_docs = perform_search(solr_endpoint, collection, query_text)
        return reranked_docs
    except Exception as e:
        return {"error": str(e)}

def on_clear_results():
  
    return []

### UI


st.set_page_config(page_title="Document Search App", layout="wide")

st.session_state.setdefault("results", [])
st.session_state.setdefault("query_text", "")

st.title("Document Search Tool")
st.divider()

solr_endpoint = "http://localhost:8983/solr"
collection = "covid"

query_input = st.text_input("Enter your search query:", st.session_state.query_text)

col1, col2 = st.columns([6, 1])
with col1:
    if st.button("Search"):
        if query_input.strip():
            st.session_state.query_text = query_input
            with st.spinner("Searching..."):
                results = on_send_query(solr_endpoint, collection, query_input)
                if "error" in results:
                    st.error(f"Error: {results['error']}")
                else:
                    st.session_state.results = results
        else:
            st.warning("Please enter a query.")

with col2:
    if st.button("Clear Results"):
        st.session_state.results = on_clear_results()
        st.session_state.query_text = ""

st.divider()
if st.session_state.results:
    st.subheader(f"Search Results ({len(st.session_state.results)} found):")
    for idx, doc in enumerate(st.session_state.results, start=1):
        st.write(f"### Result {idx}: {doc.get('title', 'No Title')}")
        st.write(f"**Abstract:** {doc.get('abstract', 'No Abstract')}")
        st.write(f"**Score:** {doc.get('score', 0):.2f}")
        st.write("---")
else:
    st.info("No results to display.")