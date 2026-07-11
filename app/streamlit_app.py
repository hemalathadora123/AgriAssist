print("========== STREAMLIT APP STARTED ==========")
import sys
import time
from pathlib import Path

# ---------------------------------------------
# Add src folder FIRST
# ---------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_DIR))

import streamlit as st

from history import ChatHistoryManager
from rag_pipeline import RAGPipeline
from config import (
    APP_TITLE,
    LLM_MODEL,
    EMBEDDING_MODEL,
)

# ---------------------------------------------
# Page Config
# ---------------------------------------------

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🌱",
    layout="wide"
)

# ---------------------------------------------
# Load Pipeline
# ---------------------------------------------

@st.cache_resource
def load_pipeline():
    return RAGPipeline()

from download_vectordb import download_database
print("========== BEFORE DOWNLOAD ==========")
download_database()
print("========== AFTER DOWNLOAD ==========")
rag = load_pipeline()
history_db = ChatHistoryManager()

# -----------------------------
# Session State
# -----------------------------

if "conversation_id" not in st.session_state:

    st.session_state.conversation_id = history_db.create_conversation(
        "New Conversation"
    )

if "messages" not in st.session_state:

    st.session_state.messages = []

# ---------------------------------------------
# Sidebar
# ---------------------------------------------

with st.sidebar:

    st.title("🌱 AgriAssist")

    st.markdown("---")

    st.subheader("Project")

    st.write("📚 Agriculture RAG Assistant")

    st.markdown("---")

    st.subheader("Models")

    st.write(f"🤖 LLM : `{LLM_MODEL}`")
    st.write(f"🧠 Embedding : `{EMBEDDING_MODEL.split('/')[-1]}`")

    st.markdown("---")

    st.subheader("Knowledge Base")

    st.write("📄 PDFs : 5")
    st.write("🧩 Chunks : 13,150")

    # ==========================================================
    # Conversation History
    # ==========================================================

    st.markdown("---")

    st.subheader("💬 Conversations")

    conversations = history_db.get_conversations()

    for cid, title in conversations:

        if st.button(
            f"📄 {title}",
            key=f"conv_{cid}",
            use_container_width=True
        ):

            st.session_state.conversation_id = cid

            rows = history_db.get_messages(cid)

            st.session_state.messages = []

            for role, content in rows:

                st.session_state.messages.append(
                    {
                        "role": role,
                        "content": content
                    }
                )

            st.rerun()

    st.markdown("---")

    # ==========================================================
    # New Chat
    # ==========================================================

    if st.button(
        "➕ New Chat",
        use_container_width=True
    ):

        cid = history_db.create_conversation(
            "New Conversation"
        )

        st.session_state.conversation_id = cid

        st.session_state.messages = []

        st.rerun()

    # ==========================================================
    # Clear Current Chat
    # ==========================================================

    if st.button(
        "🗑 Clear Current Chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()

# ---------------------------------------------
# Header
# ---------------------------------------------

st.title("🌱 AgriAssist")

st.caption("AI Powered Agriculture Assistant")

st.divider()

# ---------------------------------------------
# Suggested Questions
# ---------------------------------------------

if len(st.session_state.messages) == 0:

    st.info("💡 Try asking:")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("- How to control weeds?")

        st.markdown("- What is nitrogen fertilizer?")

    with col2:

        st.markdown("- Best irrigation methods")

        st.markdown("- Explain crop rotation")

# ---------------------------------------------
# Previous Chat
# ---------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

# ---------------------------------------------
# Chat Input
# ---------------------------------------------

question = st.chat_input("Ask your agriculture question...")

if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )
    history_db.add_message(
        st.session_state.conversation_id,
        "user",
        question
    )
    # Rename conversation only for the first user question

    if len(st.session_state.messages) == 1:

        title = question.strip()

        if len(title) > 40:
            title = title[:40] + "..."

        history_db.update_conversation_title(
            st.session_state.conversation_id,
            title
        )

    with st.chat_message("user"):

        st.markdown(question)

    start = time.time()

    with st.spinner("Searching agricultural knowledge..."):

        result = rag.ask(question)

    elapsed = round(time.time() - start, 2)

    answer = result["answer"]

    sources = result["sources"]

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )
    history_db.add_message(
        st.session_state.conversation_id,
        "assistant",
        answer
    )

    with st.chat_message("assistant"):

        st.markdown(answer)

        st.caption(f"⏱ Response generated in {elapsed} sec")

        with st.expander("📄 Sources Used"):

            for source in sources:

                st.markdown(
                    f"""
**{source['filename']}**

📄 Page : {source['page']}
"""
                )