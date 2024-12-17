import streamlit as st
from query_streaml_lit import perform_search

def on_send_query(solr_endpoint, collection, query_text):
    try:
        reranked_docs = perform_search(solr_endpoint, collection, query_text)
        return reranked_docs
    except Exception as e:
        return {"error": str(e)}


st.set_page_config(page_title="Document Search Tool", layout="wide")

if "results" not in st.session_state:
    st.session_state.results = []

if "query_text" not in st.session_state:
    st.session_state.query_text = ""

st.markdown(
    """
    <style>
    .stTextInput input {
        background-color: #2b2b2b;
        color: white;
        border: 1px solid #4d90fe;
        border-radius: 5px;
    }
    .stButton>button {
        background-color: #4d90fe;
        color: white;
        border-radius: 5px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #357ae8;
    }
    .stMarkdown h1 {
        color: #4d90fe;
        text-align: center;
        font-size: 2.5em;
    }

    div[data-testid="stTextInput"] label {
        display: none;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("# Document Search Tool")

col1, col2, col3 = st.columns([5, 1, 1])  

with col1:
    query_input = st.text_input(
        label="",  
        value=st.session_state.query_text,
        placeholder="Type your query here..."
    )

with col2:
    search_clicked = st.button("Search")

with col3:
    clear_clicked = st.button("Clear Results")



if search_clicked:
    if query_input.strip():
        st.session_state.query_text = query_input
        with st.spinner("Searching..."):
            results = on_send_query("http://localhost:8983/solr", "covid", query_input)
            if "error" in results:
                st.error(f"Error: {results['error']}")
            else:
                st.session_state.results = results
    else:
        st.warning("Please enter a query.")

if clear_clicked:
    st.session_state.results = []

st.divider()

if st.session_state.results:
    st.subheader(f"Top {len(st.session_state.results)} Results Found:")
    for idx, doc in enumerate(st.session_state.results, start=1):
        title = doc.get("title", "No Title")
        abstract = doc.get("abstract", "No Abstract")
        relevant = doc.get("relevant", False)  

        badge = "🟢" if relevant else "🔴"

        full_title = f"🔎 {title} {badge}"

        with st.expander(full_title):
            st.write(abstract)
else:
    st.info("No results to display.")
