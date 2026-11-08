"""
voice_agent.py

Comprehensive Voice Agent module for AgriAssist.
Provides:
1. Speech-to-Text (STT):
   - Native audio transcription using Gemini Multimodal Audio
   - Browser Web Speech Recognition integration
2. Text-to-Speech (TTS):
   - Server-side speech generation via gTTS
   - Client-side Web Speech Synthesis controls
3. Intelligent text sanitization for natural speech output.
4. Multilingual support across Indian and global agricultural regions.
"""

import os
import re
import io
import html
from typing import Optional, Dict

try:
    from logger import get_logger
except ImportError:
    try:
        from src.logger import get_logger
    except ImportError:
        import logging
        def get_logger(name):
            return logging.getLogger(name)

logger = get_logger(__name__)

# Try importing gTTS
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    logger.warning("gTTS is not installed. Server-side TTS will be disabled.")
    GTTS_AVAILABLE = False


# ==========================================================
# Supported Languages Configuration
# ==========================================================
# Mapping: display_name -> { "code": BCP-47, "gtts_lang": gTTS code, "tld": domain }
SUPPORTED_VOICE_LANGUAGES: Dict[str, Dict[str, str]] = {
    "English (India)": {
        "code": "en-IN",
        "gtts_lang": "en",
        "tld": "co.in",
        "flag": "🇮🇳"
    },
    "English (US)": {
        "code": "en-US",
        "gtts_lang": "en",
        "tld": "com",
        "flag": "🇺🇸"
    },
    "Hindi (हिन्दी)": {
        "code": "hi-IN",
        "gtts_lang": "hi",
        "tld": "co.in",
        "flag": "🇮🇳"
    },
    "Telugu (తెలుగు)": {
        "code": "te-IN",
        "gtts_lang": "te",
        "tld": "co.in",
        "flag": "🇮🇳"
    },
    "Tamil (தமிழ்)": {
        "code": "ta-IN",
        "gtts_lang": "ta",
        "tld": "co.in",
        "flag": "🇮🇳"
    },
    "Marathi (मराठी)": {
        "code": "mr-IN",
        "gtts_lang": "mr",
        "tld": "co.in",
        "flag": "🇮🇳"
    },
    "Bengali (বাংলা)": {
        "code": "bn-IN",
        "gtts_lang": "bn",
        "tld": "co.in",
        "flag": "🇮🇳"
    },
    "Kannada (ಕನ್ನಡ)": {
        "code": "kn-IN",
        "gtts_lang": "kn",
        "tld": "co.in",
        "flag": "🇮🇳"
    },
    "Gujarati (ગુજરાતી)": {
        "code": "gu-IN",
        "gtts_lang": "gu",
        "tld": "co.in",
        "flag": "🇮🇳"
    },
    "Malayalam (മലയാളം)": {
        "code": "ml-IN",
        "gtts_lang": "ml",
        "tld": "co.in",
        "flag": "🇮🇳"
    },
    "Punjabi (ਪੰਜਾਬੀ)": {
        "code": "pa-IN",
        "gtts_lang": "pa",
        "tld": "co.in",
        "flag": "🇮🇳"
    },
    "Spanish (Español)": {
        "code": "es-ES",
        "gtts_lang": "es",
        "tld": "es",
        "flag": "🇪🇸"
    },
    "French (Français)": {
        "code": "fr-FR",
        "gtts_lang": "fr",
        "tld": "fr",
        "flag": "🇫🇷"
    }
}


def clean_text_for_speech(text: str) -> str:
    """
    Cleans markdown formatting, citations, URLs, tables, and special
    characters from LLM answers so text sounds completely natural
    when read aloud by TTS.
    """
    if not text:
        return ""

    # 1. Remove code blocks
    cleaned = re.sub(r"```[\s\S]*?```", "", text)
    cleaned = re.sub(r"`.*?`", "", cleaned)

    # 2. Remove markdown links, keep label: [label](url) -> label
    cleaned = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", cleaned)

    # 3. Remove URLs
    cleaned = re.sub(r"https?://\S+|www\.\S+", "", cleaned)

    # 4. Remove citation references like [1], [Page 4], (Page: 12), etc.
    cleaned = re.sub(r"\[\s*page\s*[:\d\-,\s]+\]", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\(\s*page\s*[:\d\-,\s]+\)", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\[\d+\]", "", cleaned)

    # 5. Remove markdown headers, bold, italics, strikethrough
    cleaned = re.sub(r"^[#\s]+", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"\*{1,3}(.*?)\*{1,3}", r"\1", cleaned)
    cleaned = re.sub(r"_{1,3}(.*?)_{1,3}", r"\1", cleaned)
    cleaned = re.sub(r"~~(.*?)~~", r"\1", cleaned)

    # 6. Replace bullet symbols with natural pauses
    cleaned = re.sub(r"^\s*[-*•]\s+", ". ", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"^\s*\d+\.\s+", ". ", cleaned, flags=re.MULTILINE)

    # 7. Expand common agricultural units / abbreviations for natural speech
    abbreviations = {
        r"\bha\b": "hectares",
        r"\bkg/ha\b": "kilograms per hectare",
        r"\bkg\b": "kilograms",
        r"\bgm\b": "grams",
        r"\bcm\b": "centimeters",
        r"\bmm\b": "millimeters",
        r"\bNPK\b": "N P K",
        r"\bFYM\b": "farm yard manure",
        r"\bpH\b": "p H",
        r"\bEC\b": "electrical conductivity",
        r"\bppm\b": "parts per million"
    }
    for pattern, replacement in abbreviations.items():
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)

    # 8. Clean up extra punctuation, whitespace, and empty lines
    cleaned = re.sub(r"\n+", ". ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = re.sub(r"\.\s*\.", ".", cleaned)
    cleaned = cleaned.strip()

    return cleaned


def text_to_speech_audio(
    text: str,
    lang_name: str = "English (India)"
) -> Optional[bytes]:
    """
    Generate MP3 audio bytes using gTTS.
    Returns bytes or None if generation failed.
    """
    if not GTTS_AVAILABLE:
        logger.warning("gTTS not installed, cannot generate audio.")
        return None

    cleaned = clean_text_for_speech(text)
    if not cleaned:
        return None

    lang_info = SUPPORTED_VOICE_LANGUAGES.get(
        lang_name,
        SUPPORTED_VOICE_LANGUAGES["English (India)"]
    )
    gtts_lang = lang_info.get("gtts_lang", "en")
    tld = lang_info.get("tld", "com")

    try:
        # Limit text length for TTS to prevent excessive processing
        # 1500 chars is ~2.5 minutes of natural speech
        tts_text = cleaned[:1800]
        tts = gTTS(text=tts_text, lang=gtts_lang, tld=tld, slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except Exception as e:
        logger.error(f"Error generating speech with gTTS: {e}")
        return None


def transcribe_audio_gemini(
    audio_bytes: bytes,
    mime_type: str = "audio/wav"
) -> Optional[str]:
    """
    Transcribe spoken agricultural audio to text using Gemini Multimodal Audio.
    Gemini 2.5/1.5 handles accents, multilingual speech (Hindi, Telugu, Tamil, etc.),
    and agricultural terms with high precision.
    """
    try:
        import google.generativeai as genai
        try:
            from config import LLM_MODEL
        except ImportError:
            try:
                from src.config import LLM_MODEL
            except ImportError:
                LLM_MODEL = "gemini-3.8-flash"

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY not found in environment.")
            return None

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name=LLM_MODEL)

        prompt = (
            "You are an agricultural speech-to-text assistant. "
            "Please listen to this audio recording carefully and transcribe "
            "the user's spoken words into clear text. "
            "If the audio is in Hindi, Tamil, Telugu, or another Indian language, "
            "transcribe it faithfully or provide the English translation if it helps clarity. "
            "Return ONLY the transcribed text. Do NOT add any preamble, quotes, or notes."
        )

        response = model.generate_content([
            prompt,
            {
                "mime_type": mime_type,
                "data": audio_bytes
            }
        ])

        if response and response.text:
            transcription = response.text.strip().strip('"').strip("'")
            logger.info(f"Audio transcribed successfully: {transcription[:60]}...")
            return transcription
        return None

    except Exception as e:
        logger.error(f"Error in Gemini audio transcription: {e}")
        return None


def get_web_speech_recognition_html(
    lang_code: str = "en-IN",
    height: int = 190
) -> str:
    """
    Returns an interactive HTML/JS Voice Assistant component for real-time
    microphone recording using the browser's Web Speech API.
    Zero server lag, works directly in Chrome, Edge, Safari, and Android!
    """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            * {{
                box-sizing: border-box;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            }}
            body {{
                margin: 0;
                padding: 10px;
                background: transparent;
            }}
            .voice-card {{
                background: linear-gradient(135deg, #1b382b 0%, #0d1f17 100%);
                border: 1px solid rgba(46, 125, 50, 0.4);
                border-radius: 14px;
                padding: 14px 18px;
                display: flex;
                flex-direction: column;
                gap: 10px;
                color: #e8f5e9;
                box-shadow: 0 4px 14px rgba(0,0,0,0.25);
            }}
            .header-row {{
                display: flex;
                align-items: center;
                justify-content: space-between;
            }}
            .badge {{
                display: inline-flex;
                align-items: center;
                gap: 6px;
                font-size: 13px;
                font-weight: 600;
                color: #81c784;
            }}
            .status-dot {{
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background-color: #81c784;
                display: inline-block;
            }}
            .status-dot.active {{
                background-color: #ef5350;
                box-shadow: 0 0 10px #ef5350;
                animation: pulse 1s infinite alternate;
            }}
            @keyframes pulse {{
                from {{ transform: scale(1); opacity: 1; }}
                to {{ transform: scale(1.4); opacity: 0.6; }}
            }}
            .controls-row {{
                display: flex;
                align-items: center;
                gap: 12px;
            }}
            .mic-btn {{
                background: #2e7d32;
                border: none;
                color: white;
                width: 48px;
                height: 48px;
                border-radius: 50%;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 20px;
                transition: all 0.2s ease;
                box-shadow: 0 4px 10px rgba(46, 125, 50, 0.4);
                outline: none;
                flex-shrink: 0;
            }}
            .mic-btn:hover {{
                background: #388e3c;
                transform: scale(1.05);
            }}
            .mic-btn.listening {{
                background: #d32f2f;
                box-shadow: 0 0 18px rgba(211, 47, 47, 0.8);
                animation: mic-pulse 1.2s infinite;
            }}
            @keyframes mic-pulse {{
                0% {{ box-shadow: 0 0 0 0 rgba(211, 47, 47, 0.7); }}
                70% {{ box-shadow: 0 0 0 14px rgba(211, 47, 47, 0); }}
                100% {{ box-shadow: 0 0 0 0 rgba(211, 47, 47, 0); }}
            }}
            .transcript-box {{
                flex-grow: 1;
                background: rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 8px 12px;
                min-height: 44px;
                font-size: 13.5px;
                color: #c8e6c9;
                display: flex;
                align-items: center;
                overflow: hidden;
                word-break: break-word;
            }}
            .copy-btn {{
                background: rgba(255, 255, 255, 0.12);
                border: 1px solid rgba(255, 255, 255, 0.2);
                color: #ffffff;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
                cursor: pointer;
                display: none;
                align-items: center;
                gap: 4px;
                transition: background 0.2s;
            }}
            .copy-btn:hover {{
                background: rgba(255, 255, 255, 0.25);
            }}
            .lang-tag {{
                font-size: 11px;
                background: rgba(46, 125, 50, 0.35);
                padding: 2px 8px;
                border-radius: 10px;
                color: #a5d6a7;
            }}
        </style>
    </head>
    <body>
        <div class="voice-card">
            <div class="header-row">
                <span class="badge">
                    <span id="dot" class="status-dot"></span>
                    <span id="status-text">Voice Agent Ready</span>
                </span>
                <span class="lang-tag">🎙️ {lang_code}</span>
            </div>
            <div class="controls-row">
                <button id="mic-btn" class="mic-btn" title="Click to speak" onclick="toggleListening()">
                    🎤
                </button>
                <div id="transcript" class="transcript-box">
                    Click the microphone to speak your agriculture question...
                </div>
                <button id="copy-btn" class="copy-btn" onclick="copyTranscript()">
                    📋 Copy
                </button>
            </div>
        </div>

        <script>
            let recognition = null;
            let isListening = false;
            const micBtn = document.getElementById('mic-btn');
            const statusText = document.getElementById('status-text');
            const dot = document.getElementById('dot');
            const transcriptDiv = document.getElementById('transcript');
            const copyBtn = document.getElementById('copy-btn');
            const lang = "{lang_code}";

            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

            if (!SpeechRecognition) {{
                transcriptDiv.innerHTML = "⚠️ Web Speech is not supported in this browser. Use Chrome, Edge, or the audio recorder below.";
                micBtn.disabled = true;
                micBtn.style.opacity = "0.5";
            }} else {{
                recognition = new SpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = true;
                recognition.lang = lang;

                recognition.onstart = function() {{
                    isListening = true;
                    micBtn.classList.add('listening');
                    dot.classList.add('active');
                    statusText.innerText = "Listening... Speak your crop or farming question";
                    transcriptDiv.innerText = "Listening...";
                    copyBtn.style.display = "none";
                }};

                recognition.onresult = function(event) {{
                    let current = '';
                    for (let i = event.resultIndex; i < event.results.length; i++) {{
                        current += event.results[i][0].transcript;
                    }}
                    transcriptDiv.innerText = current;
                }};

                recognition.onerror = function(event) {{
                    console.error("Speech Recognition Error:", event.error);
                    statusText.innerText = "Error: " + event.error;
                    stopListening();
                }};

                recognition.onend = function() {{
                    stopListening();
                    const text = transcriptDiv.innerText.trim();
                    if (text && text !== "Listening..." && text !== "Click the microphone to speak your agriculture question...") {{
                        statusText.innerText = "✅ Speech Captured! Click 'Copy' or paste into chat";
                        copyBtn.style.display = "inline-flex";
                        
                        // Attempt to populate parent chat input if accessible
                        try {{
                            const parentDoc = window.parent.document;
                            const chatInput = parentDoc.querySelector('textarea[data-testid="stChatInputTextArea"]');
                            if (chatInput) {{
                                chatInput.value = text;
                                chatInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            }}
                        }} catch (e) {{
                            // cross-origin safety
                        }}
                    }} else {{
                        statusText.innerText = "Voice Agent Ready";
                        transcriptDiv.innerText = "Click the microphone to speak your agriculture question...";
                    }}
                }};
            }}

            function toggleListening() {{
                if (!recognition) return;
                if (isListening) {{
                    recognition.stop();
                    stopListening();
                }} else {{
                    try {{
                        recognition.start();
                    }} catch(e) {{
                        console.error(e);
                    }}
                }}
            }}

            function stopListening() {{
                isListening = false;
                micBtn.classList.remove('listening');
                dot.classList.remove('active');
            }}

            function copyTranscript() {{
                const text = transcriptDiv.innerText;
                navigator.clipboard.writeText(text).then(() => {{
                    copyBtn.innerText = "✓ Copied!";
                    setTimeout(() => {{
                        copyBtn.innerText = "📋 Copy";
                    }}, 2000);
                }}).catch(err => {{
                    console.error('Failed to copy', err);
                }});
            }}
        </script>
    </body>
    </html>
    """


def get_web_speech_synthesis_html(
    text: str,
    lang_code: str = "en-IN",
    speed: float = 1.0,
    msg_id: str = "msg_0"
) -> str:
    """
    Returns an interactive HTML/JS button component to play the assistant response
    using the browser's native Web Speech Synthesis API.
    Provides instant, zero-latency natural voice playback in any browser.
    """
    cleaned = clean_text_for_speech(text)
    escaped_text = html.escape(cleaned).replace("\n", " ").replace("'", "\\'")

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            * {{
                box-sizing: border-box;
                font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }}
            body {{
                margin: 0 !important;
                padding: 0 !important;
                background: transparent !important;
                overflow: hidden !important;
            }}
            .speech-wrapper {{
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 2px 0;
            }}
            .speech-btn {{
                background: rgba(16, 185, 129, 0.12);
                border: 1px solid rgba(16, 185, 129, 0.4);
                color: #6ee7b7;
                padding: 4px 12px;
                border-radius: 14px;
                font-size: 12px;
                font-weight: 600;
                cursor: pointer;
                display: inline-flex;
                align-items: center;
                gap: 6px;
                transition: all 0.2s ease;
                outline: none;
            }}
            .speech-btn:hover {{
                background: rgba(16, 185, 129, 0.24);
                border-color: #10b981;
                color: #ecfdf5;
            }}
            @keyframes blink {{
                50% {{ opacity: 0.4; }}
            }}
        </style>
    </head>
    <body>
        <div class="speech-wrapper">
            <button id="btn_{msg_id}" class="speech-btn" onclick="speakText_{msg_id}()">
                <span id="icon_{msg_id}">🔊</span>
                <span id="label_{msg_id}">Listen to Answer</span>
            </button>
            <span id="wave_{msg_id}" style="display: none; color: #10b981; font-size: 12px; font-weight: 600; animation: blink 1s infinite;">
                🔊 Speaking...
            </span>
        </div>

    <script>
        (function() {{
            let isSpeaking_{msg_id} = false;
            const fullText_{msg_id} = '{escaped_text}';
            const langCode_{msg_id} = '{lang_code}';
            const rate_{msg_id} = {speed};

            window.speakText_{msg_id} = function() {{
                if (!('speechSynthesis' in window)) {{
                    alert('Text-to-speech is not supported by your browser.');
                    return;
                }}

                if (window.speechSynthesis.speaking && isSpeaking_{msg_id}) {{
                    window.speechSynthesis.cancel();
                    resetBtn_{msg_id}();
                    return;
                }}

                window.speechSynthesis.cancel(); // Stop any other playing utterance

                const utterance = new SpeechSynthesisUtterance(fullText_{msg_id});
                utterance.lang = langCode_{msg_id};
                utterance.rate = rate_{msg_id};

                // Pick best voice for language if available
                const voices = window.speechSynthesis.getVoices();
                const matchedVoice = voices.find(v => v.lang === langCode_{msg_id} || v.lang.startsWith(langCode_{msg_id}.split('-')[0]));
                if (matchedVoice) {{
                    utterance.voice = matchedVoice;
                }}

                utterance.onstart = function() {{
                    isSpeaking_{msg_id} = true;
                    document.getElementById('icon_{msg_id}').innerText = '⏹️';
                    document.getElementById('label_{msg_id}').innerText = 'Stop';
                    document.getElementById('wave_{msg_id}').style.display = 'inline';
                }};

                utterance.onend = function() {{
                    resetBtn_{msg_id}();
                }};

                utterance.onerror = function() {{
                    resetBtn_{msg_id}();
                }};

                window.speechSynthesis.speak(utterance);
            }};

            function resetBtn_{msg_id}() {{
                isSpeaking_{msg_id} = false;
                const icon = document.getElementById('icon_{msg_id}');
                const label = document.getElementById('label_{msg_id}');
                const wave = document.getElementById('wave_{msg_id}');
                if (icon) icon.innerText = '🔊';
                if (label) label.innerText = 'Listen to Answer';
                if (wave) wave.style.display = 'none';
            }}
        }})();
    </script>
    </body>
    </html>
    """


# ==========================================================
# Auto-processing Voice Agent Component
# ==========================================================

from pathlib import Path
import streamlit.components.v1 as components

VOICE_COMPONENT_DIR = Path(__file__).resolve().parent / "voice_component"

_voice_agent_component = None
if (VOICE_COMPONENT_DIR / "index.html").exists():
    try:
        _voice_agent_component = components.declare_component(
            "agri_voice_agent_component",
            path=str(VOICE_COMPONENT_DIR)
        )
    except Exception as e:
        logger.warning(f"Could not initialize custom voice component: {e}")


def render_voice_agent_auto(
    language_code: str = "en-IN",
    language_name: str = "English (India)",
    auto_submit: bool = True,
    key: str = "agri_voice_auto"
) -> Optional[Dict]:
    """
    Renders the real-time Voice Agent component with automatic speech end-detection.
    When the user stops speaking, it automatically submits the query and returns:
    {'query': str, 'timestamp': int}
    """
    if _voice_agent_component is not None:
        try:
            return _voice_agent_component(
                language_code=language_code,
                language_name=language_name,
                auto_submit=auto_submit,
                key=key
            )
        except Exception as e:
            logger.error(f"Error running voice component: {e}")
            return None
    return None

