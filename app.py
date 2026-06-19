import streamlit as st
import sys
import chromadb

st.write("Chroma Version:", chromadb.__version__)
st.stop()

from openai import OpenAI
from dotenv import load_dotenv
import os

st.write("Python Version:")
st.write(sys.version)


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

st.write("Database Path Exists:", os.path.exists("sap_co_db"))
st.write("SQLite Exists:", os.path.exists("sap_co_db/chroma.sqlite3"))

try:
    collections = client_db.list_collections()
    st.write("Collections:", collections)

except Exception as e:
    st.error(f"LIST ERROR: {e}")

st.write("Chroma Version:", chromadb.__version__)

st.stop()

