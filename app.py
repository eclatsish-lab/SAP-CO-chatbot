import streamlit as st
import sys
import chromadb
from openai import OpenAI
from dotenv import load_dotenv
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
question = st.text_input("Ask SAP CO Question")

st.stop()

