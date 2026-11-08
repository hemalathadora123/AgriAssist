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
import streamlit.components.v1 as components

from history import ChatHistoryManager
from config import (
    APP_TITLE,
    LLM_MODEL,
    EMBEDDING_MODEL,
)
from voice_agent import (
    SUPPORTED_VOICE_LANGUAGES,
    text_to_speech_audio,
    transcribe_audio_gemini,
    get_web_speech_recognition_html,
    get_web_speech_synthesis_html,
    render_voice_agent_auto,
    GTTS_AVAILABLE,
)

# ---------------------------------------------
# Page Config
# ---------------------------------------------

st.set_page_config(
    page_title=f"{APP_TITLE} 🌱 Smart Agriculture Assistant",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------
# Premium Agricultural Theme CSS
# ---------------------------------------------

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    }

    /* ── Ambient Radial Glow Background ──────────────────────── */
    .stApp {
        background: radial-gradient(circle at 12% 10%, rgba(16, 185, 129, 0.09) 0%, transparent 40%),
                    radial-gradient(circle at 88% 90%, rgba(5, 150, 105, 0.07) 0%, transparent 40%),
                    #0b1612 !important;
        color: #ecfdf5;
    }

    /* ── Main Workspace Container: Perfectly Centered ────────── */
    .main .block-container,
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 7.5rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 960px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }

    /* ── Clean Header (Keep Sidebar Toggle Usable) ─────────────── */
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 2.75rem !important;
    }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    [data-testid="stDecoration"] { display: none !important; }
    [data-testid="stStatusWidget"] { visibility: hidden; }

    /* ── Sidebar ─────────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #07120e 0%, #0c1a14 100%) !important;
        border-right: 1px solid rgba(16, 185, 129, 0.18) !important;
        width: 290px !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding: 1rem 1rem 2rem 1rem !important;
    }
    [data-testid="stSidebar"] h4 {
        font-size: 12px !important;
        font-weight: 700 !important;
        letter-spacing: 0.8px !important;
        text-transform: uppercase !important;
        color: #6ee7b7 !important;
        margin: 0 0 6px 0 !important;
    }

    /* ── Sidebar Info Card ───────────────────────────────────── */
    .sidebar-card {
        background: rgba(18, 37, 30, 0.55);
        border: 1px solid rgba(16, 185, 129, 0.22);
        border-radius: 12px;
        padding: 10px 12px;
        margin-bottom: 12px;
        backdrop-filter: blur(10px);
    }
    .stat-pill {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 5px 9px;
        background: rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 7px;
        margin-bottom: 5px;
        font-size: 11.5px;
        color: #d1fae5;
    }
    .stat-pill strong {
        color: #10b981;
        font-size: 11px;
        text-align: right;
        max-width: 58%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    /* ── Hero Banner ─────────────────────────────────────────── */
    .hero-banner {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.14) 0%, rgba(6, 78, 59, 0.24) 100%);
        border: 1px solid rgba(16, 185, 129, 0.32);
        border-radius: 16px;
        padding: 18px 24px;
        margin-bottom: 16px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35);
        backdrop-filter: blur(12px);
    }
    .hero-title {
        font-size: 25px;
        font-weight: 800;
        letter-spacing: -0.4px;
        margin: 0 0 3px 0;
        line-height: 1.2;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .gradient-text {
        background: linear-gradient(135deg, #a7f3d0 0%, #34d399 50%, #10b981 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 13.5px;
        font-weight: 500;
        margin: 0 0 10px 0;
        line-height: 1.4;
    }
    .badge-row {
        display: flex;
        gap: 7px;
        flex-wrap: wrap;
    }
    .badge-chip {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.32);
        padding: 3px 9px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        color: #6ee7b7;
        white-space: nowrap;
    }

    /* ── Quick Starter Suggestion Buttons (Main Area) ────────── */
    .stButton > button {
        background: rgba(18, 37, 30, 0.65) !important;
        color: #d1fae5 !important;
        font-weight: 500 !important;
        font-size: 13px !important;
        border: 1px solid rgba(16, 185, 129, 0.25) !important;
        border-radius: 11px !important;
        padding: 9px 13px !important;
        text-align: left !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.22) !important;
        backdrop-filter: blur(8px) !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        background: rgba(16, 185, 129, 0.18) !important;
        border-color: rgba(52, 211, 153, 0.6) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 16px rgba(16, 185, 129, 0.35) !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button:active {
        transform: translateY(0px) !important;
    }

    /* ── Sidebar Conversation History Buttons ────────────────── */
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(16, 185, 129, 0.08) !important;
        color: #d1fae5 !important;
        border: 1px solid rgba(16, 185, 129, 0.16) !important;
        border-radius: 8px !important;
        font-size: 12px !important;
        padding: 6px 10px !important;
        box-shadow: none !important;
        transform: none !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(16, 185, 129, 0.2) !important;
        border-color: rgba(16, 185, 129, 0.35) !important;
        transform: none !important;
    }

    /* ── Primary "New Chat" Highlight in Sidebar ─────────────── */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] div:first-child .stButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border: 1px solid rgba(110, 231, 183, 0.4) !important;
        box-shadow: 0 2px 8px rgba(5, 150, 105, 0.3) !important;
    }
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] div:first-child .stButton > button:hover {
        background: linear-gradient(135deg, #34d399 0%, #10b981 100%) !important;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.5) !important;
    }

    /* ── Chat Messages ───────────────────────────────────────── */
    [data-testid="stChatMessage"] {
        background: rgba(18, 37, 30, 0.48) !important;
        border: 1px solid rgba(16, 185, 129, 0.16) !important;
        border-radius: 14px !important;
        padding: 13px 17px !important;
        margin-bottom: 10px !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.22) !important;
        backdrop-filter: blur(8px) !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        border-left: 3px solid #10b981 !important;
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.07) 0%, rgba(18, 37, 30, 0.55) 100%) !important;
    }

    /* ── Chat Input (Matches Main Width & Centered) ──────────── */
    [data-testid="stChatInput"] {
        border-radius: 13px !important;
        border: 1.5px solid rgba(16, 185, 129, 0.3) !important;
        background: rgba(14, 28, 22, 0.92) !important;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.38) !important;
        backdrop-filter: blur(14px) !important;
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: #10b981 !important;
        box-shadow: 0 0 16px rgba(16, 185, 129, 0.45) !important;
    }

    /* ── Bottom Sticky Bar ───────────────────────────────────── */
    [data-testid="stBottom"] {
        background: rgba(11, 22, 18, 0.94) !important;
        backdrop-filter: blur(18px) !important;
        border-top: 1px solid rgba(16, 185, 129, 0.14) !important;
        padding: 8px 0 6px 0 !important;
    }
    .main [data-testid="stBottom"] > div:first-child,
    [data-testid="stBottom"] > div {
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 960px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }

    /* ── Selectbox ───────────────────────────────────────────── */
    [data-testid="stSelectbox"] > div > div {
        background: rgba(14, 28, 22, 0.85) !important;
        border: 1px solid rgba(16, 185, 129, 0.28) !important;
        border-radius: 9px !important;
        color: #ecfdf5 !important;
        font-size: 13px !important;
    }

    /* ── Toggle ──────────────────────────────────────────────── */
    [data-testid="stToggle"] > label {
        color: #d1fae5 !important;
        font-size: 13px !important;
    }

    /* ── Slider ──────────────────────────────────────────────── */
    [data-testid="stSlider"] > div > div > div > div {
        background: #10b981 !important;
    }
    [data-testid="stSlider"] label {
        color: #a7f3d0 !important;
        font-size: 12.5px !important;
    }

    /* ── Checkbox ────────────────────────────────────────────── */
    [data-testid="stCheckbox"] > label {
        color: #d1fae5 !important;
        font-size: 13px !important;
    }

    /* ── Expander ────────────────────────────────────────────── */
    [data-testid="stExpander"] {
        background: rgba(18, 37, 30, 0.38) !important;
        border: 1px solid rgba(16, 185, 129, 0.18) !important;
        border-radius: 11px !important;
    }
    [data-testid="stExpander"] summary {
        color: #a7f3d0 !important;
        font-size: 13px !important;
        font-weight: 600 !important;
    }

    /* ── Source Cards ────────────────────────────────────────── */
    .source-card {
        background: rgba(0, 0, 0, 0.28);
        border-left: 3px solid #10b981;
        border-radius: 8px;
        padding: 9px 13px;
        margin-top: 7px;
    }

    /* ── Quick Starter Header ────────────────────────────────── */
    .starter-header {
        font-size: 13.5px;
        font-weight: 700;
        color: #a7f3d0;
        margin: 4px 0 8px 0;
        display: flex;
        align-items: center;
        gap: 7px;
    }

    /* ── Voice Agent Section Label ───────────────────────────── */
    .voice-section-label {
        font-size: 13px;
        font-weight: 700;
        color: #6ee7b7;
        letter-spacing: 0.3px;
        padding: 8px 0 5px 0;
        border-top: 1px solid rgba(16, 185, 129, 0.12);
        margin-top: 6px;
        display: flex;
        align-items: center;
        gap: 7px;
    }

    /* ── Divider ─────────────────────────────────────────────── */
    hr {
        border: none !important;
        border-top: 1px solid rgba(16, 185, 129, 0.13) !important;
        margin: 10px 0 !important;
    }

    /* ── Audio Player ────────────────────────────────────────── */
    audio {
        width: 100% !important;
        border-radius: 8px !important;
        margin-top: 4px !important;
    }

    /* ── Custom Scrollbar ────────────────────────────────────── */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: #0b1612; }
    ::-webkit-scrollbar-thumb { background: #10b981; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #34d399; }

    /* ── Responsive Mobile & Tablet Fixes ────────────────────── */
    @media (max-width: 768px) {
        .main .block-container,
        .block-container {
            padding-left: 0.85rem !important;
            padding-right: 0.85rem !important;
            padding-top: 0.8rem !important;
        }
        .hero-banner {
            padding: 14px 16px !important;
            border-radius: 14px !important;
        }
        .hero-title {
            font-size: 20px !important;
        }
        .hero-subtitle {
            font-size: 12px !important;
        }
        .main [data-testid="stBottom"] > div:first-child,
        [data-testid="stBottom"] > div {
            padding-left: 0.85rem !important;
            padding-right: 0.85rem !important;
        }
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------
# Load Pipeline
# ---------------------------------------------

@st.cache_resource
def get_pipeline():
    from download_vectordb import download_database
    from rag_pipeline import RAGPipeline

    print("Downloading vector database (if needed)...")
    download_database()

    print("Loading RAG Pipeline...")
    return RAGPipeline()


history_db = ChatHistoryManager()

# -----------------------------
# Session State Initialization
# -----------------------------

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = history_db.create_conversation(
        "New Conversation"
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

if "voice_enabled" not in st.session_state:
    st.session_state.voice_enabled = True

if "voice_lang" not in st.session_state:
    st.session_state.voice_lang = "English (India)"

if "auto_speak" not in st.session_state:
    st.session_state.auto_speak = False

if "speech_rate" not in st.session_state:
    st.session_state.speech_rate = 1.0

if "audio_cache" not in st.session_state:
    st.session_state.audio_cache = {}

if "pending_voice_query" not in st.session_state:
    st.session_state.pending_voice_query = None

if "last_processed_audio_id" not in st.session_state:
    st.session_state.last_processed_audio_id = None

if "last_processed_voice_ts" not in st.session_state:
    st.session_state.last_processed_voice_ts = 0


# ---------------------------------------------
# Helper: Render Assistant Message with Voice
# ---------------------------------------------

def render_assistant_response(
    content: str,
    sources: list = None,
    elapsed: float = None,
    msg_id: str = "0",
    autoplay: bool = False
):
    """Renders assistant message along with voice agent audio players and sources."""
    st.markdown(content)

    if elapsed is not None:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 8px; margin: 8px 0;">
                <span class="badge-chip">⏱️ {elapsed}s</span>
                <span class="badge-chip">🌿 Verified Agricultural Knowledge</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    if st.session_state.voice_enabled:
        lang_info = SUPPORTED_VOICE_LANGUAGES.get(
            st.session_state.voice_lang,
            SUPPORTED_VOICE_LANGUAGES["English (India)"]
        )
        lang_code = lang_info.get("code", "en-IN")

        # Instant Browser Web Speech Button
        components.html(
            get_web_speech_synthesis_html(
                text=content,
                lang_code=lang_code,
                speed=st.session_state.speech_rate,
                msg_id=msg_id
            ),
            height=36
        )

        # High-Quality Server Audio (gTTS MP3)
        if GTTS_AVAILABLE:
            cache_key = f"{msg_id}_{hash(content)}"
            if cache_key not in st.session_state.audio_cache:
                if autoplay:
                    with st.spinner("🔊 Generating voice audio..."):
                        audio_data = text_to_speech_audio(
                            content,
                            lang_name=st.session_state.voice_lang
                        )
                        if audio_data:
                            st.session_state.audio_cache[cache_key] = audio_data

            if cache_key in st.session_state.audio_cache:
                st.audio(
                    st.session_state.audio_cache[cache_key],
                    format="audio/mp3",
                    autoplay=autoplay
                )
            else:
                if st.button("🎧 Generate MP3 Audio", key=f"gen_audio_{msg_id}"):
                    with st.spinner("Generating MP3 audio..."):
                        audio_data = text_to_speech_audio(
                            content,
                            lang_name=st.session_state.voice_lang
                        )
                        if audio_data:
                            st.session_state.audio_cache[cache_key] = audio_data
                            st.rerun()

    if sources:
        with st.expander(f"📄 Sources Used ({len(sources)} Verified References)", expanded=False):
            for s_idx, source in enumerate(sources):
                snippet = source.get('content', '')
                if len(snippet) > 280:
                    snippet = snippet[:280] + "..."
                st.markdown(
                    f"""
                    <div class="source-card">
                        <strong style="color: #6ee7b7;">📖 {source['filename']}</strong>
                        <div style="font-size: 12px; color: #94a3b8; margin: 2px 0 6px 0;">Page {source['page']}</div>
                        <div style="font-size: 12.5px; color: #d1fae5; line-height: 1.4;">{snippet}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


# ---------------------------------------------
# Sidebar
# ---------------------------------------------

with st.sidebar:

    st.markdown(
        """
        <div style="text-align: center; padding: 10px 0 16px 0;">
            <div style="font-size: 40px; line-height: 1;">🌱</div>
            <h2 style="margin: 6px 0 2px 0; font-weight: 800; background: linear-gradient(135deg, #a7f3d0 0%, #10b981 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">AgriAssist</h2>
            <div style="font-size: 12px; color: #6ee7b7; font-weight: 600; letter-spacing: 0.5px;">SMART FARMING COPILOT</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    # ==========================================================
    # 🎙️ Voice Agent Settings Card
    # ==========================================================
    st.markdown("#### 🎙️ Voice Agent")

    with st.container():
        voice_on = st.toggle(
            "Enable Voice Assistant",
            value=st.session_state.voice_enabled,
            help="Turn on speech recognition and voice responses"
        )
        st.session_state.voice_enabled = voice_on

        if st.session_state.voice_enabled:
            available_langs = list(SUPPORTED_VOICE_LANGUAGES.keys())
            current_idx = (
                available_langs.index(st.session_state.voice_lang)
                if st.session_state.voice_lang in available_langs
                else 0
            )

            selected_lang = st.selectbox(
                "Speaking & Listening Language",
                options=available_langs,
                index=current_idx,
                help="Select the language for voice input and speech synthesis"
            )
            st.session_state.voice_lang = selected_lang

            st.session_state.auto_speak = st.checkbox(
                "🔊 Auto-read answers aloud",
                value=st.session_state.auto_speak,
                help="Automatically play voice audio when bot responds"
            )

            st.session_state.speech_rate = st.slider(
                "Voice Speed",
                min_value=0.7,
                max_value=1.3,
                value=float(st.session_state.speech_rate),
                step=0.1,
                help="Speed of speech readout"
            )

    st.markdown("---")

    # ==========================================================
    # Knowledge Engine Card
    # ==========================================================
    st.markdown("#### 📊 Knowledge Engine")
    st.markdown(
        f"""
        <div class="sidebar-card">
            <div class="stat-pill"><span>🤖 LLM</span><strong>{LLM_MODEL}</strong></div>
            <div class="stat-pill"><span>🧠 Embeddings</span><strong>{EMBEDDING_MODEL.split('/')[-1]}</strong></div>
            <div class="stat-pill"><span>📄 Reference PDFs</span><strong>5 Documents</strong></div>
            <div class="stat-pill"><span>🧩 Knowledge Chunks</span><strong>13,150</strong></div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    # ==========================================================
    # Conversation History
    # ==========================================================
    st.markdown("#### 💬 Conversations")

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
    # New Chat & Clear Chat
    # ==========================================================
    col_n1, col_n2 = st.columns(2)
    with col_n1:
        if st.button("➕ New Chat", use_container_width=True):
            cid = history_db.create_conversation("New Conversation")
            st.session_state.conversation_id = cid
            st.session_state.messages = []
            st.session_state.pending_voice_query = None
            st.rerun()

    with col_n2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.messages = []
            st.session_state.pending_voice_query = None
            st.rerun()


# ---------------------------------------------
# Main Header Banner
# ---------------------------------------------

st.markdown(
    """
    <div class="hero-banner">
        <h1 class="hero-title"><span>🌱</span> <span class="gradient-text">AgriAssist AI</span></h1>
        <p class="hero-subtitle">Intelligent Agricultural Knowledge Assistant &amp; Multilingual Voice Companion</p>
        <div class="badge-row">
            <span class="badge-chip">🟢 AI Online</span>
            <span class="badge-chip">🎙️ Voice Enabled</span>
            <span class="badge-chip">📚 RAG Verified</span>
            <span class="badge-chip">🌍 13 Languages</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------
# Interactive Suggested Questions (Click-to-Ask)
# ---------------------------------------------

suggested_query = None

if len(st.session_state.messages) == 0:
    st.markdown('<div class="starter-header">💡 Quick Starters — Click any question to ask instantly:</div>', unsafe_allow_html=True)
    q_col1, q_col2 = st.columns(2)

    with q_col1:
        if st.button("🌿 How to control weeds effectively?", use_container_width=True):
            suggested_query = "How to control weeds effectively?"
        if st.button("🧪 What is NPK nitrogen fertilizer?", use_container_width=True):
            suggested_query = "What is nitrogen fertilizer and its benefits for crops?"

    with q_col2:
        if st.button("💧 Best modern irrigation methods", use_container_width=True):
            suggested_query = "What are the best modern irrigation methods for water saving?"
        if st.button("🔄 Explain crop rotation benefits", use_container_width=True):
            suggested_query = "Explain crop rotation and why it is important for soil health."


# ---------------------------------------------
# Previous Chat Messages
# ---------------------------------------------

for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(message["content"])
        else:
            sources = message.get("sources", None)
            render_assistant_response(
                content=message["content"],
                sources=sources,
                msg_id=f"hist_{idx}"
            )


# ---------------------------------------------
# Voice Agent Input Panel (When Voice Enabled)
# ---------------------------------------------

voice_query = None

if st.session_state.voice_enabled:
    lang_info = SUPPORTED_VOICE_LANGUAGES.get(
        st.session_state.voice_lang,
        SUPPORTED_VOICE_LANGUAGES["English (India)"]
    )
    lang_code = lang_info.get("code", "en-IN")

    st.markdown('<div class="voice-section-label">🎙️ Hands-Free Voice Agent</div>', unsafe_allow_html=True)
    # Real-Time Auto-Processing Voice Agent (Listens -> Detects silence -> Auto submits)
    voice_data = render_voice_agent_auto(
        language_code=lang_code,
        language_name=st.session_state.voice_lang,
        auto_submit=True,
        key="agri_voice_auto_agent"
    )

    if voice_data and isinstance(voice_data, dict):
        spoken = voice_data.get("query", "").strip()
        ts = voice_data.get("timestamp", 0)
        if spoken and ts != st.session_state.get("last_processed_voice_ts"):
            st.session_state.last_processed_voice_ts = ts
            voice_query = spoken
            st.toast(f"🎙️ Voice captured: \"{spoken[:60]}{'...' if len(spoken) > 60 else ''}\"", icon="✅")

    # Audio Clip Recorder (Fallback & External Mic)
    with st.expander("📁 Audio File Recorder / Direct Mic Clip", expanded=False):
        st.caption("Alternative recorder: record your audio clip and let Gemini AI transcribe & answer:")
        recorded_audio = st.audio_input(
            "Record audio clip",
            key="voice_audio_input"
        )

        if recorded_audio is not None:
            audio_id = f"{recorded_audio.name}_{recorded_audio.size}"
            if st.session_state.get("last_processed_audio_id") != audio_id:
                st.session_state.last_processed_audio_id = audio_id
                with st.spinner("🎧 Transcribing audio with Gemini AI..."):
                    audio_bytes = recorded_audio.read()
                    mime = recorded_audio.type or "audio/wav"
                    transcribed = transcribe_audio_gemini(
                        audio_bytes,
                        mime_type=mime
                    )
                    if transcribed:
                        voice_query = transcribed
                    else:
                        st.warning("⚠️ Could not transcribe audio. Please speak clearly or type.")


# ---------------------------------------------
# Chat Input (Voice, Clicked Starter, or Text)
# ---------------------------------------------

text_query = st.chat_input("Ask your agriculture question or speak above...")

question = voice_query or suggested_query or text_query

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

    try:
        with st.spinner("Initializing AgriAssist (first question can take 1–2 min)..."):
            rag = get_pipeline()

        with st.spinner("Searching agricultural knowledge..."):
            result = rag.ask(question)

    except Exception as e:
        st.error(
            "AgriAssist failed to answer this question. "
            "Check Render logs for details."
        )
        st.exception(e)
        st.stop()

    elapsed = round(time.time() - start, 2)
    answer = result["answer"]
    sources = result["sources"]

    # Append to session state and history
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources
        }
    )
    history_db.add_message(
        st.session_state.conversation_id,
        "assistant",
        answer
    )

    # Render Assistant Response
    with st.chat_message("assistant"):
        render_assistant_response(
            content=answer,
            sources=sources,
            elapsed=elapsed,
            msg_id=f"current_{len(st.session_state.messages)}",
            autoplay=st.session_state.auto_speak
        )