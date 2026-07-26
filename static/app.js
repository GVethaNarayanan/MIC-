/* ═══════════════════════════════════════════════════════════════════
   MIC Translator v3.0 — Frontend Logic
   ═══════════════════════════════════════════════════════════════════ */

// ── State ────────────────────────────────────────────────────────────
let allLanguages = {};
let sourceLang = "auto";
let targetLang = "fr";
let favorites = [];
let recentLangs = [];
let pickerMode = "target";  // "source" or "target"
let isRecording = false;
let mediaRecorder = null;
let audioChunks = [];
let statusInterval = null;

// ── Init ─────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
    loadLanguages();
    loadFavorites();
    loadHistory();
    startStatusPolling();
    setupInputCounter();
    setupKeyboardShortcuts();
});

// ═══════════════════ LANGUAGES ═══════════════════════════════════════

async function loadLanguages() {
    try {
        const res = await fetch("/api/languages");
        allLanguages = await res.json();
        const count = Object.keys(allLanguages).length;
        document.getElementById("lang-count").textContent = count;
        updateLangButtons();
    } catch (e) {
        console.error("Failed to load languages:", e);
        showToast("Failed to load languages", "error");
    }
}

async function loadFavorites() {
    try {
        const res = await fetch("/api/languages/favorites");
        const data = await res.json();
        favorites = data.favorites || [];
        recentLangs = data.recent || [];
    } catch (e) {
        console.error("Failed to load favorites:", e);
    }
}

function updateLangButtons() {
    const srcName = sourceLang === "auto" ? "Auto Detect" :
        (allLanguages[sourceLang]?.name || sourceLang);
    const tgtName = allLanguages[targetLang]?.name || targetLang;
    document.getElementById("source-lang-name").textContent = srcName;
    document.getElementById("target-lang-name").textContent = tgtName;
}

// ── Language Picker ──────────────────────────────────────────────────

function openLangPicker(mode) {
    pickerMode = mode;
    const modal = document.getElementById("lang-modal");
    const title = document.getElementById("modal-title");
    const search = document.getElementById("lang-search");

    title.textContent = mode === "source" ? "Select Source Language" : "Select Target Language";
    modal.style.display = "flex";
    search.value = "";
    search.focus();

    renderLanguageGrid("");
}

function closeLangPicker(event) {
    if (event && event.target !== event.currentTarget) return;
    document.getElementById("lang-modal").style.display = "none";
}

function filterLanguages(query) {
    renderLanguageGrid(query);
}

function renderLanguageGrid(query) {
    const grid = document.getElementById("all-langs-grid");
    const favGrid = document.getElementById("favorites-grid");
    const recGrid = document.getElementById("recent-grid");
    const favSection = document.getElementById("favorites-section");
    const recSection = document.getElementById("recent-section");

    const q = query.toLowerCase().trim();
    const currentVal = pickerMode === "source" ? sourceLang : targetLang;

    // Favorites
    if (favorites.length > 0 && !q) {
        favSection.style.display = "block";
        favGrid.innerHTML = "";
        if (pickerMode === "source") {
            favGrid.innerHTML += createLangOption("auto", "Auto Detect", false, currentVal === "auto");
        }
        favorites.forEach(code => {
            const lang = allLanguages[code];
            if (lang) {
                favGrid.innerHTML += createLangOption(code, lang.name, lang.has_voice, currentVal === code);
            }
        });
    } else {
        favSection.style.display = "none";
    }

    // Recent
    if (recentLangs.length > 0 && !q) {
        recSection.style.display = "block";
        recGrid.innerHTML = "";
        recentLangs.slice(0, 6).forEach(code => {
            const lang = allLanguages[code];
            if (lang && !favorites.includes(code)) {
                recGrid.innerHTML += createLangOption(code, lang.name, lang.has_voice, currentVal === code);
            }
        });
    } else {
        recSection.style.display = "none";
    }

    // All languages
    grid.innerHTML = "";

    // Add "Auto Detect" for source picker
    if (pickerMode === "source" && (!q || "auto detect".includes(q))) {
        grid.innerHTML += createLangOption("auto", "Auto Detect", false, currentVal === "auto");
    }

    // Sort and filter
    const entries = Object.entries(allLanguages)
        .filter(([code, lang]) => {
            if (!q) return true;
            return lang.name.toLowerCase().includes(q) || code.includes(q);
        })
        .sort((a, b) => a[1].name.localeCompare(b[1].name));

    entries.forEach(([code, lang]) => {
        grid.innerHTML += createLangOption(code, lang.name, lang.has_voice, currentVal === code);
    });

    if (entries.length === 0 && !grid.innerHTML) {
        grid.innerHTML = '<div class="empty-state">No languages match your search</div>';
    }
}

function createLangOption(code, name, hasVoice, isSelected) {
    const isFav = favorites.includes(code);
    const selectedClass = isSelected ? " selected" : "";
    const voiceDot = hasVoice ? '<span class="voice-dot" title="Voice available"></span>' : "";
    const favStar = code !== "auto" ?
        `<span class="fav-star ${isFav ? 'active' : ''}" onclick="event.stopPropagation(); toggleFavorite('${code}')" title="Toggle favorite">★</span>` : "";

    return `<div class="lang-option${selectedClass}" onclick="selectLanguage('${code}')" data-code="${code}">
        ${voiceDot}
        <span>${name}</span>
        ${favStar}
    </div>`;
}

function selectLanguage(code) {
    if (pickerMode === "source") {
        sourceLang = code;
    } else {
        targetLang = code;
    }
    updateLangButtons();
    closeLangPicker();
}

function swapLanguages() {
    if (sourceLang === "auto") {
        showToast("Cannot swap when source is Auto Detect", "info");
        return;
    }
    [sourceLang, targetLang] = [targetLang, sourceLang];
    updateLangButtons();

    // Also swap text content
    const inputEl = document.getElementById("input-text");
    const outputEl = document.getElementById("output-text");
    const outputText = outputEl.textContent;

    if (outputText && outputText !== "Translation will appear here...") {
        inputEl.value = outputText;
        outputEl.innerHTML = '<span class="placeholder-text">Translation will appear here...</span>';
        updateCharCount();
    }
}

async function toggleFavorite(code) {
    const isFav = favorites.includes(code);
    const action = isFav ? "remove" : "add";

    try {
        const res = await fetch("/api/languages/favorites", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ action, lang_code: code })
        });
        const data = await res.json();
        favorites = data.favorites;
        renderLanguageGrid(document.getElementById("lang-search").value);
        showToast(isFav ? "Removed from favorites" : "Added to favorites", "success");
    } catch (e) {
        console.error("Toggle favorite error:", e);
    }
}

// ═══════════════════ TRANSLATION ═════════════════════════════════════

async function translateText() {
    const text = document.getElementById("input-text").value.trim();
    if (!text) {
        showToast("Please enter text to translate", "info");
        return;
    }

    showLoading("Translating...");
    const btn = document.getElementById("translate-btn");
    btn.disabled = true;

    try {
        const res = await fetch("/api/translate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                text,
                source_lang: sourceLang,
                target_lang: targetLang
            })
        });

        const data = await res.json();

        if (data.error && !data.translated) {
            showToast(`Translation error: ${data.error}`, "error");
            return;
        }

        // Display translation
        displayTranslation(data);

        // Auto speak translation if enabled
        const autoSpeak = document.getElementById("autoplay-voice")?.checked;
        if (autoSpeak) {
            speakOutput();
        }

        // Update source language if auto-detected
        if (sourceLang === "auto" && data.source_lang) {
            const detectedName = data.source_lang_name || data.source_lang;
            document.getElementById("source-lang-name").textContent =
                `Auto (${detectedName})`;
        }

        // Update recent languages
        if (!recentLangs.includes(targetLang)) {
            recentLangs.unshift(targetLang);
            recentLangs = recentLangs.slice(0, 10);
        }

        // Refresh history
        loadHistory();

    } catch (e) {
        console.error("Translation error:", e);
        showToast("Translation failed. Check backend.", "error");
    } finally {
        hideLoading();
        btn.disabled = false;
    }
}

function displayTranslation(data) {
    const outputEl = document.getElementById("output-text");
    const metaEl = document.getElementById("translation-meta");
    const pipelineEl = document.getElementById("pipeline-info");

    // Output text
    outputEl.innerHTML = `<span style="font-size:1.05rem;">${escapeHtml(data.translated)}</span>`;

    // Meta tags
    let metaHtml = "";
    metaHtml += `<span class="meta-tag info">⏱ ${data.time_ms}ms</span>`;
    metaHtml += `<span class="meta-tag">${data.source_lang_name} → ${data.target_lang_name}</span>`;

    if (data.detection && data.detection.confidence) {
        const conf = Math.round(data.detection.confidence * 100);
        const cls = conf > 70 ? "success" : conf > 40 ? "warning" : "";
        metaHtml += `<span class="meta-tag ${cls}">🎯 ${conf}% confidence</span>`;
    }

    if (data.pre_corrections && data.pre_corrections.length > 0) {
        metaHtml += `<span class="meta-tag warning">✏️ ${data.pre_corrections.length} corrections</span>`;
    }

    if (data.validation && data.validation.has_reference) {
        const score = Math.round(data.validation.quality_score * 100);
        metaHtml += `<span class="meta-tag ${data.validation.match ? 'success' : 'warning'}">📊 ${score}% match</span>`;
    }

    metaEl.innerHTML = metaHtml;

    // Pipeline details
    pipelineEl.style.display = "block";

    // Detection step
    document.getElementById("step-detection").innerHTML =
        `<span class="step-label">Detection:</span> ${data.source_lang_name} (${data.detection?.method || 'manual'}, ${Math.round((data.detection?.confidence || 0) * 100)}%)`;

    // Correction step
    const corrCount = data.pre_corrections?.length || 0;
    let corrHtml = `<span class="step-label">Corrections:</span> ${corrCount} applied`;
    if (corrCount > 0) {
        corrHtml += " — " + data.pre_corrections.map(c => `<em>${c.from} → ${c.to}</em>`).join(", ");
    }
    document.getElementById("step-correction").innerHTML = corrHtml;

    // Translation step
    document.getElementById("step-translation").innerHTML =
        `<span class="step-label">NLLB-200:</span> ${data.translation_time_ms || data.time_ms}ms`;

    // Post-correction
    const postCount = data.post_corrections?.length || 0;
    document.getElementById("step-post").innerHTML =
        `<span class="step-label">Post-fix:</span> ${postCount} corrections`;

    // Validation
    if (data.validation?.has_reference) {
        document.getElementById("step-validation").innerHTML =
            `<span class="step-label">Validation:</span> Reference found, ${Math.round(data.validation.quality_score * 100)}% word overlap`;
    } else {
        document.getElementById("step-validation").innerHTML =
            `<span class="step-label">Validation:</span> No reference dataset available`;
    }
}

// ═══════════════════ SPEECH RECORDING ════════════════════════════════

async function toggleRecording() {
    if (isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (e) => {
            if (e.data.size > 0) audioChunks.push(e.data);
        };

        mediaRecorder.onstop = async () => {
            stream.getTracks().forEach(t => t.stop());
            const blob = new Blob(audioChunks, { type: "audio/wav" });
            await transcribeAudio(blob);
        };

        mediaRecorder.start();
        isRecording = true;

        const btn = document.getElementById("mic-btn");
        btn.classList.add("recording");
        document.getElementById("mic-label").textContent = "Stop";

        showToast("🎙 Recording... Speak now!", "info");

    } catch (e) {
        console.error("Microphone error:", e);
        showToast("Microphone access denied. Check browser permissions.", "error");
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
    }
    isRecording = false;

    const btn = document.getElementById("mic-btn");
    btn.classList.remove("recording");
    document.getElementById("mic-label").textContent = "Record";
}

async function transcribeAudio(blob) {
    showLoading("Transcribing speech...");

    try {
        const formData = new FormData();
        formData.append("audio", blob, "recording.wav");
        formData.append("source_lang", sourceLang);

        const res = await fetch("/api/transcribe", {
            method: "POST",
            body: formData
        });

        const data = await res.json();

        if (data.error) {
            showToast(`Transcription error: ${data.error}`, "error");
            return;
        }

        // Use corrected text if available
        const text = data.corrected_text || data.text || "";
        document.getElementById("input-text").value = text;
        updateCharCount();

        if (data.language && sourceLang === "auto") {
            const langName = allLanguages[data.language]?.name || data.language;
            document.getElementById("source-lang-name").textContent = `Auto (${langName})`;
        }

        if (data.correction_count > 0) {
            showToast(`✏️ ${data.correction_count} speech corrections applied`, "info");
        }

        showToast("✅ Speech transcribed successfully!", "success");

        // Auto-translate after transcription
        if (text) {
            setTimeout(() => translateText(), 300);
        }

    } catch (e) {
        console.error("Transcription error:", e);
        showToast("Transcription failed", "error");
    } finally {
        hideLoading();
    }
}

// ═══════════════════ TTS ═════════════════════════════════════════════

async function speakOutput() {
    const outputEl = document.getElementById("output-text");
    const text = outputEl.textContent.trim();

    if (!text || text === "Translation will appear here...") {
        showToast("No translation to speak", "info");
        return;
    }

    try {
        const res = await fetch("/api/tts", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text, lang_code: targetLang })
        });

        const data = await res.json();

        if (data.success && data.audio_url) {
            const audio = new Audio(data.audio_url);
            audio.play();
            showToast("🔊 Playing audio...", "success");
        } else {
            showToast(data.error || "TTS not available for this language", "info");
        }
    } catch (e) {
        console.error("TTS error:", e);
        showToast("Text-to-speech failed", "error");
    }
}

// ═══════════════════ HISTORY ═════════════════════════════════════════

async function loadHistory() {
    try {
        const res = await fetch("/api/history?limit=30");
        const entries = await res.json();
        renderHistory(entries);
    } catch (e) {
        console.error("History load error:", e);
    }
}

function renderHistory(entries) {
    const list = document.getElementById("history-list");

    if (!entries || entries.length === 0) {
        list.innerHTML = '<div class="empty-state">No translations yet</div>';
        return;
    }

    list.innerHTML = entries.map(entry => `
        <div class="history-item" onclick="replayHistory('${escapeAttr(entry.original || '')}', '${escapeAttr(entry.translated || '')}', '${entry.source_lang || ''}', '${entry.target_lang || ''}')">
            <div class="history-original">${escapeHtml(entry.original || '')}</div>
            <div class="history-translated">${escapeHtml(entry.translated || '')}</div>
            <div class="history-meta">
                <span>${entry.timestamp || ''}</span>
                <span>${entry.time_ms || 0}ms</span>
            </div>
        </div>
    `).join("");
}

function replayHistory(original, translated, srcLang, tgtLang) {
    document.getElementById("input-text").value = original;
    document.getElementById("output-text").innerHTML =
        `<span style="font-size:1.05rem;">${escapeHtml(translated)}</span>`;

    if (srcLang && srcLang !== "auto") {
        sourceLang = srcLang;
    }
    if (tgtLang) {
        targetLang = tgtLang;
    }
    updateLangButtons();
    updateCharCount();
}

async function clearHistory() {
    if (!confirm("Clear all translation history?")) return;
    try {
        await fetch("/api/clear", { method: "POST" });
        loadHistory();
        showToast("History cleared", "success");
    } catch (e) {
        showToast("Failed to clear history", "error");
    }
}

function exportHistory(format) {
    window.open(`/api/history/export?format=${format}`, "_blank");
    showToast(`Exporting as ${format.toUpperCase()}...`, "info");
}

// ═══════════════════ STATUS ══════════════════════════════════════════

function startStatusPolling() {
    fetchStatus();
    statusInterval = setInterval(fetchStatus, 5000);
}

async function fetchStatus() {
    try {
        const res = await fetch("/api/status");
        const status = await res.json();
        updateStatusUI(status);
    } catch (e) {
        updateStatusOffline();
    }
}

function updateStatusUI(status) {
    // Header status
    const dot = document.getElementById("status-dot");
    const text = document.getElementById("status-text");

    if (status.whisper_ready && status.translator_ready) {
        dot.className = "status-dot online";
        text.textContent = "Offline Engine";
    } else {
        dot.className = "status-dot";
        text.textContent = "Loading...";
    }

    // Language count
    if (status.language_count) {
        document.getElementById("lang-count").textContent = status.language_count;
    }

    // Status indicators
    setIndicator("si-whisper", status.whisper_ready);
    setIndicator("si-translator", status.translator_ready);
    setIndicator("si-tts", status.tts_ready);
    setIndicator("si-corrections", status.corrections_loaded);
}

function setIndicator(id, active) {
    const el = document.getElementById(id);
    if (el) {
        el.className = "status-indicator " + (active ? "active" : "inactive");
    }
}

function updateStatusOffline() {
    const dot = document.getElementById("status-dot");
    const text = document.getElementById("status-text");
    dot.className = "status-dot error";
    text.textContent = "Offline";
}

// ═══════════════════ UI HELPERS ══════════════════════════════════════

function clearInput() {
    document.getElementById("input-text").value = "";
    document.getElementById("output-text").innerHTML =
        '<span class="placeholder-text">Translation will appear here...</span>';
    document.getElementById("translation-meta").innerHTML = "";
    document.getElementById("pipeline-info").style.display = "none";
    updateCharCount();
}

function copyOutput() {
    const text = document.getElementById("output-text").textContent.trim();
    if (!text || text === "Translation will appear here...") {
        showToast("Nothing to copy", "info");
        return;
    }
    navigator.clipboard.writeText(text).then(() => {
        showToast("📋 Copied to clipboard!", "success");
    }).catch(() => {
        showToast("Copy failed", "error");
    });
}

function setupInputCounter() {
    const input = document.getElementById("input-text");
    input.addEventListener("input", updateCharCount);
}

function updateCharCount() {
    const len = document.getElementById("input-text").value.length;
    document.getElementById("char-count").textContent = `${len} character${len !== 1 ? 's' : ''}`;
}

function setupKeyboardShortcuts() {
    document.addEventListener("keydown", (e) => {
        // Ctrl+Enter to translate
        if (e.ctrlKey && e.key === "Enter") {
            e.preventDefault();
            translateText();
        }
        // Escape to close modal
        if (e.key === "Escape") {
            document.getElementById("lang-modal").style.display = "none";
        }
    });
}

function togglePipeline() {
    const details = document.getElementById("pipeline-details");
    details.style.display = details.style.display === "none" ? "block" : "none";
}

// ── Loading ──────────────────────────────────────────────────────────

function showLoading(text) {
    document.getElementById("loading-text").textContent = text || "Processing...";
    document.getElementById("loading-overlay").style.display = "flex";
}

function hideLoading() {
    document.getElementById("loading-overlay").style.display = "none";
}

// ── Toast ────────────────────────────────────────────────────────────

function showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
        if (toast.parentNode) toast.parentNode.removeChild(toast);
    }, 3000);
}

// ── Escape helpers ───────────────────────────────────────────────────

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

function escapeAttr(text) {
    return text.replace(/'/g, "\\'").replace(/"/g, '\\"').replace(/\n/g, ' ');
}
