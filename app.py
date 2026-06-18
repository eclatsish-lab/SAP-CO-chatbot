import streamlit as st
import chromadb
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client_openai = OpenAI(
    api_key=api_key
)
# ChromaDB
client_db = chromadb.PersistentClient(path="sap_co_db")
collection = client_db.get_collection("sap_co")

if "messages" not in st.session_state:
    st.session_state.messages = []

st.sidebar.title("SAP CO Modules")

module = st.sidebar.selectbox(
    "Select Module",
    [
        "Cost Center Accounting",
        "Internal Orders",
        "Profit Center Accounting",
        "Activity Based Costing",
        "Product Costing"
    ]
)
st.title("🤖 SAP CO AI Assistant")
st.subheader("AI-Powered SAP Controlling Knowledge Assistant")
st.markdown("---")
question = st.text_input("Ask SAP CO Question")

if question:

    # Search
    results = collection.query(
        query_texts=[question],
        n_results=3
    )

    context = "\n".join(results["documents"][0])

    prompt = f"""
You are a senior SAP CO Consultant.

Context:
{context}

Question:
{question}

Provide:
1. Explanation
2. Configuration Steps
3. T-Codes
4. Tables
5. Important Notes
6. Source Chapter/Page
"""

    response = client_openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role":"user","content":prompt}
        ]
    )

    st.session_state.messages.append(
        {"role":"user","content":question}
    )

    st.session_state.messages.append(
        {"role":"assistant","content":response.choices[0].message.content}
    )

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.write("🧑 User:", msg["content"])
        else:
            st.write("🤖 SAP CO AI:", msg["content"])
