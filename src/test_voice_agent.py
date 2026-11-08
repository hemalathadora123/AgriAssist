"""
test_voice_agent.py

Test script to verify AgriAssist Voice Agent functionality:
- Text sanitization for natural speech
- Language configuration
- MP3 generation via gTTS
- HTML component generators
"""

import sys
import os
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from voice_agent import (
    clean_text_for_speech,
    text_to_speech_audio,
    SUPPORTED_VOICE_LANGUAGES,
    get_web_speech_recognition_html,
    get_web_speech_synthesis_html,
    GTTS_AVAILABLE,
)


def test_text_cleaning():
    print("Testing clean_text_for_speech...")
    raw = (
        "### Crop Protection Guide\n\n"
        "- Apply **Chlorpyrifos** at 2 kg/ha. [Page 4]\n"
        "- Ensure soil pH is between 6.5 and 7.5.\n"
        "- Add 50 kg of NPK fertilizer per ha. (Page: 12-14)\n"
        "Check more details at https://icar.org.in or [here](https://icar.org.in)."
    )
    cleaned = clean_text_for_speech(raw)
    print("Original:\n", raw)
    print("-" * 50)
    print("Cleaned for speech:\n", cleaned)
    print("-" * 50)

    assert "###" not in cleaned, "Markdown headers should be removed"
    assert "**" not in cleaned, "Markdown bold markers should be removed"
    assert "https://" not in cleaned, "URLs should be removed"
    assert "[Page 4]" not in cleaned, "Page citations should be removed"
    assert "hectares" in cleaned.lower(), "Abbreviation 'ha' should be expanded"
    assert "kilograms" in cleaned.lower(), "Abbreviation 'kg' should be expanded"
    print("✓ clean_text_for_speech passed successfully!\n")


def test_supported_languages():
    print("Testing SUPPORTED_VOICE_LANGUAGES...")
    assert len(SUPPORTED_VOICE_LANGUAGES) >= 10, "Should support multiple languages"
    assert "English (India)" in SUPPORTED_VOICE_LANGUAGES
    assert "Hindi (हिन्दी)" in SUPPORTED_VOICE_LANGUAGES
    assert "Telugu (తెలుగు)" in SUPPORTED_VOICE_LANGUAGES
    assert "Tamil (தமிழ்)" in SUPPORTED_VOICE_LANGUAGES
    print(f"✓ {len(SUPPORTED_VOICE_LANGUAGES)} languages configured properly!\n")


def test_audio_generation():
    print("Testing text_to_speech_audio...")
    if not GTTS_AVAILABLE:
        print("gTTS not installed, skipping audio test.")
        return

    sample = "Nitrogen is essential for plant growth and deep green foliage."
    audio_bytes = text_to_speech_audio(sample, lang_name="English (India)")
    assert audio_bytes is not None, "Audio bytes should not be None"
    assert len(audio_bytes) > 1000, f"Expected audio file > 1KB, got {len(audio_bytes)} bytes"
    print(f"✓ Generated {len(audio_bytes)} bytes of MP3 audio successfully!\n")

    # Test Hindi audio generation
    sample_hi = "नाइट्रोजन पौधों के विकास के लिए बहुत आवश्यक है।"
    audio_hi = text_to_speech_audio(sample_hi, lang_name="Hindi (हिन्दी)")
    assert audio_hi is not None
    print(f"✓ Generated {len(audio_hi)} bytes of Hindi MP3 audio successfully!\n")


def test_html_generators():
    print("Testing HTML widget generators...")
    rec_html = get_web_speech_recognition_html(lang_code="en-IN")
    assert "webkitSpeechRecognition" in rec_html
    assert "en-IN" in rec_html
    print("✓ Speech recognition HTML generator passed!")

    syn_html = get_web_speech_synthesis_html(
        text="Test message",
        lang_code="en-IN",
        speed=1.0,
        msg_id="test_1"
    )
    assert "speechSynthesis" in syn_html
    assert "test_1" in syn_html
    print("✓ Speech synthesis HTML generator passed!\n")


if __name__ == "__main__":
    print("=" * 60)
    print("🌱 AGRIASSIST VOICE AGENT TEST SUITE")
    print("=" * 60)
    test_text_cleaning()
    test_supported_languages()
    test_audio_generation()
    test_html_generators()
    print("=" * 60)
    print("🎉 ALL TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)
