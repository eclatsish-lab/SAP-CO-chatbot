import streamlit as st
import sys
import chromadb
import time
from openai import OpenAI
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder
import tempfile
import sqlite3
import os

load_dotenv()

conn = sqlite3.connect("chat_history.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT,
    answer TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()

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
        "Cost Center Accounting",client_openai = OpenAI(
        "Internal Orders",
        "Profit Center Accounting",
        "Activity Based Costing",
        "Product Costing"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("📂 Recent Chats")

recent_chats = cursor.execute("""
SELECT id, question
FROM chat_history
ORDER BY id DESC
LIMIT 10
""").fetchall()

for chat in recent_chats:

    if st.sidebar.button(
        chat[1][:30],
        key=f"chat_{chat[0]}"
    ):

        result = cursor.execute(
            "SELECT question, answer FROM chat_history WHERE id=?",
            (chat[0],)
        ).fetchone()

        st.session_state.selected_chat = result


st.title("🤖 SAP CO AI Assistant")

st.subheader("AI-Powered SAP Controlling Knowledge Assistant")

st.markdown("---")

# Show Selected Previous Chat
if "selected_chat" in st.session_state:

    st.info("📂 Previous Conversation")

    st.chat_message("user").write(
        st.session_state.selected_chat[0]
    )

    st.chat_message("assistant").write(
        st.session_state.selected_chat[1]
    )

question = None

audio = mic_recorder(
    start_prompt="🎤 Start Recording",
    stop_prompt="⏹ Stop Recording",
    key="recorder"
)

if audio:

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio["bytes"])
        audio_file = tmp.name

    with open(audio_file, "rb") as f:
        transcript = client_openai.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            language="en"
        )

    question = transcript.text

    st.caption(f"🎤 voice input: {question}")


typed_question = st.chat_input("Ask SAP CO Question")

if typed_question:
    question = typed_question

if question:

    results = collection.query(
        query_texts=[question],
        n_results=8
    )

    context = "\n".join(results["documents"][0])
    

    # Chat History
    chat_history = ""

    for msg in st.session_state.messages[-4:]:
        chat_history += f"{msg['role']}: {msg['content']}\n"

    # Decide answer type based on question

    if "table" in question.lower():
       answer_type = "Provide only the relevant SAP tables."

    elif "t-code" in question.lower() or "tcode" in question.lower():
        answer_type = "Provide only the relevant SAP T-Codes."

    elif "configuration" in question.lower():
        answer_type = "Provide only configuration steps."

    else:
        answer_type = "Provide Explanation, Configuration Steps, T-Codes, Tables and Important Notes."
        
    
    prompt = f"""
    You are a senior SAP CO Consultant.

    Always answer in English.

Answer primarily using the provided context.

If the answer exists in the context, use that information.

If the answer is not fully available in the context, use your SAP CO expertise but clearly indicate when you are supplementing the answer.

Previous Conversation:
{chat_history}

Module:
{module}

Context:
{context}

Question:
{question}

Instructions:
{answer_type}

Use the context first.
Answer only what the user asks.
"""

    start = time.time()

    response = client_openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
            "role": "system",
            "content": "You are an SAP CO expert. Use previous conversation and context to answer."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
)
    
    answer = response.choices[0].message.content

    cursor.execute(
        "INSERT INTO chat_history(question, answer) VALUES (?, ?)",
        (question, answer)
)

    conn.commit()
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


