"""
styles.py — Injected CSS for the MIC Translator Streamlit dashboard
"""

CSS = """
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Orbitron:wght@700;900&display=swap');

/* ── Root Tokens ── */
:root {
  --bg-primary:    #0a0e1a;
  --bg-secondary:  #0f1628;
  --bg-card:       #131c35;
  --bg-card-hover: #1a2540;
  --accent:        #00d4ff;
  --accent2:       #7b5cf0;
  --accent3:       #00ff9f;
  --danger:        #ff4d6d;
  --warn:          #ffba08;
  --success:       #06d6a0;
  --text-primary:  #e8eaf6;
  --text-muted:    #7986a8;
  --border:        rgba(0,212,255,0.15);
  --glow:          0 0 20px rgba(0,212,255,0.2);
  --glow-strong:   0 0 40px rgba(0,212,255,0.4);
  --radius:        14px;
  --radius-sm:     8px;
}

/* ── Global Reset ── */
html, body, [class*="css"] {
  font-family: 'Inter', sans-serif !important;
  background-color: var(--bg-primary) !important;
  color: var(--text-primary) !important;
}

.main .block-container {
  padding: 1.5rem 2rem 3rem !important;
  max-width: 1400px !important;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, .stDeployButton { display:none !important; }
header[data-testid="stHeader"] { background: transparent !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: var(--bg-secondary) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

/* ── Hero Header ── */
.hero-header {
  background: linear-gradient(135deg, #0a0e1a 0%, #131c35 40%, #1a0a2e 100%);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 2rem 2.5rem;
  margin-bottom: 1.5rem;
  position: relative;
  overflow: hidden;
  box-shadow: var(--glow);
}
.hero-header::before {
  content: '';
  position: absolute; inset: 0;
  background: radial-gradient(ellipse at 20% 50%, rgba(0,212,255,0.08) 0%, transparent 60%),
              radial-gradient(ellipse at 80% 50%, rgba(123,92,240,0.08) 0%, transparent 60%);
}
.hero-title {
  font-family: 'Orbitron', monospace !important;
  font-size: 2.6rem !important;
  font-weight: 900 !important;
  background: linear-gradient(90deg, #00d4ff, #7b5cf0, #00ff9f);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 !important;
  line-height: 1.1;
}
.hero-subtitle {
  font-size: 1rem;
  color: var(--text-muted);
  margin-top: 0.4rem;
  letter-spacing: 0.05em;
}
.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: rgba(0,212,255,0.1);
  border: 1px solid rgba(0,212,255,0.3);
  border-radius: 50px;
  padding: 0.3rem 0.9rem;
  font-size: 0.75rem;
  color: var(--accent);
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-top: 1rem;
}
.hero-version {
  position: absolute; top: 1.2rem; right: 1.5rem;
  font-size: 0.72rem;
  color: var(--text-muted);
  font-weight: 600;
  letter-spacing: 0.1em;
}

/* ── Cards ── */
.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.2rem 1.4rem;
  margin-bottom: 1rem;
  transition: box-shadow 0.3s, border-color 0.3s;
}
.card:hover {
  border-color: rgba(0,212,255,0.35);
  box-shadow: var(--glow);
}
.card-title {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--accent);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  margin-bottom: 0.6rem;
}

/* ── Status Pills ── */
.pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  border-radius: 50px;
  padding: 0.25rem 0.75rem;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.05em;
}
.pill-green  { background: rgba(6,214,160,0.12);  color: var(--success); border: 1px solid rgba(6,214,160,0.3); }
.pill-red    { background: rgba(255,77,109,0.12);  color: var(--danger);  border: 1px solid rgba(255,77,109,0.3); }
.pill-yellow { background: rgba(255,186,8,0.12);   color: var(--warn);    border: 1px solid rgba(255,186,8,0.3); }
.pill-blue   { background: rgba(0,212,255,0.12);   color: var(--accent);  border: 1px solid rgba(0,212,255,0.3); }

/* ── Pulse dot ── */
.dot-pulse {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--success);
  display: inline-block;
  animation: pulse-anim 1.4s ease-in-out infinite;
}
.dot-inactive {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--text-muted);
  display: inline-block;
}
@keyframes pulse-anim {
  0%, 100% { opacity: 1; transform: scale(1); box-shadow: 0 0 0 0 rgba(6,214,160,0.5); }
  50%       { opacity: 0.7; transform: scale(1.2); box-shadow: 0 0 0 6px rgba(6,214,160,0); }
}

/* ── Translation entry ── */
.trans-entry {
  background: linear-gradient(135deg, rgba(19,28,53,0.9), rgba(26,37,64,0.9));
  border: 1px solid var(--border);
  border-left: 3px solid var(--accent);
  border-radius: var(--radius-sm);
  padding: 0.9rem 1rem;
  margin-bottom: 0.7rem;
  animation: slideIn 0.4s ease;
}
.trans-entry:first-child { border-left-color: var(--accent3); }
@keyframes slideIn {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
.trans-ts {
  font-size: 0.65rem;
  color: var(--text-muted);
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.trans-original {
  font-size: 0.95rem;
  color: var(--text-primary);
  margin: 0.3rem 0 0.1rem;
}
.trans-arrow { color: var(--accent); font-size: 0.85rem; }
.trans-result {
  font-size: 1rem;
  color: var(--accent3);
  font-weight: 500;
  margin-top: 0.15rem;
}
.trans-badge {
  display: inline-block;
  background: rgba(123,92,240,0.15);
  border: 1px solid rgba(123,92,240,0.3);
  border-radius: 4px;
  padding: 0.1rem 0.4rem;
  font-size: 0.63rem;
  color: #a78bfa;
  font-weight: 600;
  letter-spacing: 0.08em;
  margin-left: 0.4rem;
  vertical-align: middle;
}

/* ── Wave animation (listening) ── */
.wave-bar-container {
  display: flex; align-items: flex-end; gap: 3px; height: 28px;
}
.wave-bar {
  width: 4px; border-radius: 2px;
  background: linear-gradient(180deg, var(--accent), var(--accent2));
  animation: wave 0.9s ease-in-out infinite;
}
.wave-bar:nth-child(1) { animation-delay: 0.0s; }
.wave-bar:nth-child(2) { animation-delay: 0.1s; }
.wave-bar:nth-child(3) { animation-delay: 0.2s; }
.wave-bar:nth-child(4) { animation-delay: 0.3s; }
.wave-bar:nth-child(5) { animation-delay: 0.15s; }
.wave-bar:nth-child(6) { animation-delay: 0.05s; }
@keyframes wave {
  0%,100% { height: 4px; }
  50%      { height: 24px; }
}

/* ── Buttons ── */
div[data-testid="stButton"] > button {
  border-radius: 10px !important;
  font-weight: 600 !important;
  letter-spacing: 0.04em !important;
  transition: all 0.25s ease !important;
  border: none !important;
}
div[data-testid="stButton"] > button:first-child {
  background: linear-gradient(135deg, #00b4d8, #7b5cf0) !important;
  color: #fff !important;
}
div[data-testid="stButton"] > button:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 6px 20px rgba(0,212,255,0.35) !important;
}

/* ── Selectbox / Slider ── */
div[data-testid="stSelectbox"] > div,
div[data-testid="stSlider"] > div {
  background: var(--bg-card) !important;
  border-color: var(--border) !important;
  border-radius: var(--radius-sm) !important;
}

/* ── Metric cards ── */
div[data-testid="stMetric"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  padding: 0.8rem 1rem !important;
}
div[data-testid="stMetricValue"] { color: var(--accent) !important; }
div[data-testid="stMetricLabel"] { color: var(--text-muted) !important; font-size: 0.75rem !important; }

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 1rem 0 !important; }

/* ── Info/Warning boxes ── */
div[data-testid="stInfo"]    { background: rgba(0,212,255,0.07) !important; border-color: rgba(0,212,255,0.3) !important; }
div[data-testid="stWarning"] { background: rgba(255,186,8,0.07) !important; border-color: rgba(255,186,8,0.3) !important; }
div[data-testid="stError"]   { background: rgba(255,77,109,0.07) !important; border-color: rgba(255,77,109,0.3) !important; }
div[data-testid="stSuccess"] { background: rgba(6,214,160,0.07) !important; border-color: rgba(6,214,160,0.3) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }
</style>
"""
