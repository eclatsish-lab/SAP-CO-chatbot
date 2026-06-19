import streamlit as st
import sys
import chromadb
import time
from openai import OpenAI
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder
import tempfile
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("OPENAI_API_KEY not found")
    st.stop()

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

audio = mic_recorder(
    start_prompt="🎤 Start Recording",
    stop_prompt="⏹ Stop Recording",
    key="recorder"
)

if audio:
    st.success("Voice recorded successfully")

question = st.chat_input("Ask SAP CO Question")

if question:

    results = collection.query(
        query_texts=[question],
        n_results=1
    )

    context = "\n".join(results["documents"][0])

    prompt = f"""
    You are a senior SAP CO Consultant.

Module:
{module}

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
    start = time.time()

    response = client_openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role":"user","content":prompt}
    
        ]
    )
    
    response_time = round(time.time() - start, 2)

    st.session_state.messages.append(
        {"role":"user","content":question}
    )

    st.session_state.messages.append(
        {"role":"assistant","content":response.choices[0].message.content}
    )
    st.caption(f"⚡ Response Time: {response_time} sec")

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.write(msg["content"])


