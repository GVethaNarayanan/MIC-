"""
app.py — MIC Translator Dashboard  (Streamlit entry point)

Run with:
    streamlit run app.py
"""

import time
import io
import threading
import streamlit as st

from config import (
    APP_TITLE, APP_SUBTITLE, APP_VERSION,
    LANGUAGES, DEFAULT_TARGET_LANG,
    DEFAULT_ENERGY_THRESHOLD, DEFAULT_PAUSE_THRESHOLD,
    DEFAULT_TTS_SPEED, DEFAULT_AUTOPLAY,
)
from styles import CSS
from translator_engine import MICTranslatorEngine


# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=f"{APP_TITLE} | AI Real-Time Translator",
    page_icon="🎙",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(CSS, unsafe_allow_html=True)


# ── Session State Init ────────────────────────────────────────────────────────
def _init_state():
    if "engine" not in st.session_state:
        st.session_state.engine = MICTranslatorEngine()
    if "target_lang" not in st.session_state:
        st.session_state.target_lang = DEFAULT_TARGET_LANG
    if "autoplay" not in st.session_state:
        st.session_state.autoplay = DEFAULT_AUTOPLAY
    if "tts_slow" not in st.session_state:
        st.session_state.tts_slow = DEFAULT_TTS_SPEED
    if "energy_threshold" not in st.session_state:
        st.session_state.energy_threshold = DEFAULT_ENERGY_THRESHOLD
    if "pause_threshold" not in st.session_state:
        st.session_state.pause_threshold = DEFAULT_PAUSE_THRESHOLD
    if "last_entry_count" not in st.session_state:
        st.session_state.last_entry_count = 0

_init_state()
engine: MICTranslatorEngine = st.session_state.engine


# ═══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR — Settings & Language
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1rem 0 0.5rem;'>
      <span style='font-family:Orbitron,monospace;font-size:1.3rem;
                   font-weight:900;background:linear-gradient(90deg,#00d4ff,#7b5cf0);
                   -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                   background-clip:text;'>🎙 MIC Translator</span>
      <br><span style='font-size:0.72rem;color:#7986a8;'>AI Voice Translation Engine</span>
    </div>
    <hr>
    """, unsafe_allow_html=True)

    # ── Language Selection ───────────────────────────────────────────────────
    st.markdown("<div class='card-title'>🌐 Target Language</div>", unsafe_allow_html=True)
    lang_names = list(LANGUAGES.keys())
    selected_lang = st.selectbox(
        "Select language",
        options=lang_names,
        index=lang_names.index(st.session_state.target_lang),
        label_visibility="collapsed",
        key="lang_select",
    )
    lang_code = LANGUAGES[selected_lang]
    st.markdown(
        f"<div class='pill pill-blue' style='margin-bottom:0.8rem;'>"
        f"🏷 Code: <strong>{lang_code}</strong></div>",
        unsafe_allow_html=True,
    )

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Settings ─────────────────────────────────────────────────────────────
    st.markdown("<div class='card-title'>⚙️ Settings</div>", unsafe_allow_html=True)

    energy_threshold = st.slider(
        "🎚 Mic Sensitivity (Energy Threshold)",
        min_value=50, max_value=3000,
        value=st.session_state.energy_threshold,
        step=50,
        help="Higher = less sensitive. Lower = picks up faint speech.",
    )
    pause_threshold = st.slider(
        "⏸ Pause Threshold (sec)",
        min_value=0.3, max_value=3.0,
        value=st.session_state.pause_threshold,
        step=0.1,
        help="Seconds of silence before treating utterance as complete.",
    )
    tts_slow = st.toggle("🐢 Slow TTS Speech", value=st.session_state.tts_slow)
    autoplay = st.toggle("▶ Auto-Play Translated Audio", value=st.session_state.autoplay)

    # Apply settings to engine
    engine.update_settings(
        target_lang_code=lang_code,
        target_lang_name=selected_lang,
        energy_threshold=energy_threshold,
        pause_threshold=pause_threshold,
        tts_slow=tts_slow,
        autoplay=autoplay,
    )
    # Persist in session
    st.session_state.target_lang     = selected_lang
    st.session_state.autoplay        = autoplay
    st.session_state.tts_slow        = tts_slow
    st.session_state.energy_threshold = energy_threshold
    st.session_state.pause_threshold  = pause_threshold

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── System Status ────────────────────────────────────────────────────────
    st.markdown("<div class='card-title'>📡 System Status</div>", unsafe_allow_html=True)
    status = engine.status

    def _pill(ok, label_ok, label_no, css_ok="pill-green", css_no="pill-red"):
        cls  = css_ok  if ok else css_no
        lbl  = label_ok if ok else label_no
        dot  = "🟢" if ok else "🔴"
        return f"<span class='pill {cls}'>{dot} {lbl}</span>"

    st.markdown(
        _pill(status.mic_connected,       "Mic Connected",      "Mic Not Found")    + "<br>" +
        _pill(status.recognizer_ready,    "Recogniser Ready",   "Recogniser Error") + "<br>" +
        _pill(status.translator_ready,    "Translator Ready",   "Translator Down")  + "<br>" +
        _pill(status.audio_engine_ready,  "Audio Engine OK",    "Audio Unavailable", "pill-green", "pill-yellow") + "<br>" +
        _pill(status.internet_ok,         "Internet OK",        "Offline / API Down"),
        unsafe_allow_html=True,
    )

    if status.last_error:
        st.markdown("<br>", unsafe_allow_html=True)
        st.error(f"⚠️ {status.last_error[:200]}", icon="🚨")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:0.65rem;color:#4a5568;text-align:center;'>"
        f"MIC Translator {APP_VERSION} · Powered by Whisper AI + gTTS</div>",
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  HERO HEADER
# ═══════════════════════════════════════════════════════════════════════════════
listening = engine.status.is_listening

st.markdown(f"""
<div class='hero-header'>
  <span class='hero-version'>{APP_VERSION}</span>
  <h1 class='hero-title'>🎙 MIC Translator</h1>
  <p class='hero-subtitle'>{APP_SUBTITLE}</p>
  <div style='display:flex;align-items:center;gap:0.8rem;margin-top:0.8rem;'>
    <span class='hero-badge'>
      {"<span class='dot-pulse'></span> LIVE TRANSLATING" if listening else "<span class='dot-inactive'></span> STANDBY"}
    </span>
    <span class='hero-badge' style='border-color:rgba(123,92,240,0.4);color:#a78bfa;background:rgba(123,92,240,0.1);'>
      🌐 {selected_lang} ({lang_code})
    </span>
    <span class='hero-badge' style='border-color:rgba(0,255,159,0.4);color:#00ff9f;background:rgba(0,255,159,0.08);'>
      🤖 Whisper AI + gTTS
    </span>
  </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  CONTROL ROW
# ═══════════════════════════════════════════════════════════════════════════════
col_start, col_stop, col_status = st.columns([1, 1, 3])

with col_start:
    if st.button("🎙 Start Listening", use_container_width=True, key="btn_start",
                 disabled=engine.is_running()):
        engine.start()
        st.rerun()

with col_stop:
    if st.button("⏹ Stop Translator", use_container_width=True, key="btn_stop",
                 disabled=not engine.is_running()):
        engine.stop()
        st.rerun()

with col_status:
    if listening:
        wave_bars = "".join(
            [f"<div class='wave-bar' style='height:{h}px'></div>"
             for h in [8, 18, 12, 22, 16, 10]]
        )
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:0.8rem;padding:0.6rem 0;'>"
            f"  <div class='wave-bar-container'>{wave_bars}</div>"
            f"  <span style='color:#00d4ff;font-weight:600;font-size:0.9rem;'>"
            f"    {status.last_activity or '🎙 Listening for speech…'}"
            f"  </span>"
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div style='padding:0.6rem 0;color:#7986a8;font-size:0.9rem;'>"
            "⏹ Translator is stopped. Press <strong>Start Listening</strong> to begin.</div>",
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN CONTENT COLUMNS
# ═══════════════════════════════════════════════════════════════════════════════
left_col, right_col = st.columns([3, 2], gap="large")

history = engine.get_history()

# ── LEFT: Translation Feed ────────────────────────────────────────────────────
with left_col:
    st.markdown("""
    <div class='card'>
      <div class='card-title'>📡 Live Translation Feed</div>
    </div>
    """, unsafe_allow_html=True)

    if not history:
        st.markdown("""
        <div style='text-align:center;padding:3rem 1rem;color:#4a5568;'>
          <div style='font-size:3rem;margin-bottom:0.8rem;'>🎙</div>
          <div style='font-size:1rem;font-weight:500;color:#7986a8;'>
            No translations yet.
          </div>
          <div style='font-size:0.82rem;color:#4a5568;margin-top:0.3rem;'>
            Press <strong>Start Listening</strong> and speak to see results here.
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Most recent at top
        for entry in reversed(history[-20:]):
            st.markdown(f"""
            <div class='trans-entry'>
              <div class='trans-ts'>⏱ {entry.timestamp} &nbsp;·&nbsp; → {entry.target_lang} <span class='trans-badge'>{LANGUAGES[entry.target_lang]}</span></div>
              <div class='trans-original'>🗣 {entry.original}</div>
              <div class='trans-arrow'>↓</div>
              <div class='trans-result'>🌐 {entry.translated}</div>
            </div>
            """, unsafe_allow_html=True)

    # Separator + Manual TTS
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>✍️ Manual Text Translation & Playback</div>", unsafe_allow_html=True)

    manual_text = st.text_area(
        "Type text to translate and play",
        placeholder=f"Enter text in any language — will be translated to {selected_lang}…",
        height=100,
        label_visibility="collapsed",
        key="manual_input",
    )

    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        if st.button("🌐 Translate", use_container_width=True, key="btn_translate_manual"):
            if manual_text.strip():
                translated = engine._translate(manual_text.strip())
                st.session_state["manual_translation"] = translated
            else:
                st.warning("Please type something first.")

    with m_col2:
        if st.button("▶ Speak", use_container_width=True, key="btn_speak_manual"):
            text = st.session_state.get("manual_translation") or manual_text
            if text:
                engine.play_text(text, lang_code)
                st.success("🔊 Playing…")

    with m_col3:
        dl_text = st.session_state.get("manual_translation") or manual_text
        if dl_text:
            audio_bytes = engine.get_audio_bytes(dl_text, lang_code)
            if audio_bytes:
                st.download_button(
                    "⬇ Download MP3",
                    data=audio_bytes,
                    file_name="translation.mp3",
                    mime="audio/mpeg",
                    use_container_width=True,
                    key="btn_dl_manual",
                )

    if "manual_translation" in st.session_state and st.session_state["manual_translation"]:
        st.markdown(f"""
        <div class='trans-entry' style='margin-top:0.6rem;'>
          <div class='trans-ts'>MANUAL TRANSLATION → {selected_lang}</div>
          <div class='trans-original'>🗣 {manual_text}</div>
          <div class='trans-arrow'>↓</div>
          <div class='trans-result'>🌐 {st.session_state['manual_translation']}</div>
        </div>
        """, unsafe_allow_html=True)


# ── RIGHT: Metrics + Recent + Audio ──────────────────────────────────────────
with right_col:

    # ── Metrics ───────────────────────────────────────────────────────────────
    st.markdown("<div class='card-title'>📊 Session Metrics</div>", unsafe_allow_html=True)
    m1, m2 = st.columns(2)
    m1.metric("Translations", len(history))
    m2.metric("Target Language", selected_lang)

    m3, m4 = st.columns(2)
    m3.metric("Recognizer", "Whisper AI" if engine._whisper_model else "Google SR")
    m4.metric("Status", "🟢 Running" if listening else "⏹ Stopped")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Latest Translation Card ───────────────────────────────────────────────
    st.markdown("<div class='card-title'>🔴 Latest Translation</div>", unsafe_allow_html=True)
    if history:
        latest = history[-1]
        st.markdown(f"""
        <div class='card' style='border-left:3px solid #00ff9f;'>
          <div class='trans-ts'>{latest.timestamp} · {latest.target_lang}</div>
          <div style='font-size:1.05rem;color:#e8eaf6;margin:0.4rem 0 0.2rem;'>
            <strong>Original:</strong><br>{latest.original}
          </div>
          <div style='color:#00ff9f;font-size:1.1rem;font-weight:600;'>
            <strong>Translated:</strong><br>{latest.translated}
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Audio playback for latest
        audio_bytes_latest = engine.get_audio_bytes(latest.translated, lang_code)
        if audio_bytes_latest:
            st.markdown("<div class='card-title'>🔊 Audio Playback</div>", unsafe_allow_html=True)
            st.audio(audio_bytes_latest, format="audio/mp3")
            st.download_button(
                "⬇ Download Latest Audio",
                data=audio_bytes_latest,
                file_name="latest_translation.mp3",
                mime="audio/mpeg",
                use_container_width=True,
                key="btn_dl_latest",
            )
    else:
        st.markdown("""
        <div class='card' style='text-align:center;color:#4a5568;padding:2rem;'>
          🎙 Waiting for first speech input…
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Recognizer Activity Log ───────────────────────────────────────────────
    st.markdown("<div class='card-title'>📋 Activity Log</div>", unsafe_allow_html=True)
    log_entries = [
        f"[{e.timestamp}] {e.original[:40]}… → {e.translated[:40]}…"
        for e in reversed(history[-8:])
    ] if history else ["No activity yet."]

    st.markdown(
        "<div class='card' style='font-size:0.78rem;font-family:monospace;"
        "color:#7986a8;line-height:1.8;max-height:200px;overflow-y:auto;'>"
        + "<br>".join(log_entries)
        + "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Error Panel ───────────────────────────────────────────────────────────
    if status.last_error:
        st.markdown("<div class='card-title'>🚨 Error Log</div>", unsafe_allow_html=True)
        st.error(status.last_error[:400])
        if st.button("Clear Error", key="btn_clear_err"):
            engine.status.last_error = ""
            st.rerun()

    # ── Clear History ─────────────────────────────────────────────────────────
    if history:
        if st.button("🗑 Clear Translation History", use_container_width=True, key="btn_clear"):
            with engine.history_lock:
                engine.history.clear()
            st.session_state["manual_translation"] = ""
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  AUTO-REFRESH while listening
# ═══════════════════════════════════════════════════════════════════════════════
if listening:
    current_count = len(history)
    time.sleep(1.5)
    st.rerun()
