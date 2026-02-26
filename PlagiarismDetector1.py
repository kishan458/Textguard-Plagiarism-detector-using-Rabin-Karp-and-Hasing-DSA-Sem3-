import streamlit as st
import re
import heapq
import numpy as np
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- 1. CORE DSA ENGINE (With Explicit Min-Heap Ranking) ---

class TextGuardEngine:
    def __init__(self, n=4, w=4):
        self.n = n  
        self.w = w  
        self.mod1 = 1000000007
        self.base = 131
        self.bloom_size = 1000000
        self.bloom_filter = np.zeros(self.bloom_size, dtype=int)
        self.hash_to_phrase = {} 

    def preprocess(self, text):
        # Cleaning and tokenizing
        return re.sub(r'[^\w\s]', '', text.lower()).split()

    def get_double_hash(self, phrase):
        h1 = 0
        for char in phrase:
            h1 = (h1 * self.base + ord(char)) % self.mod1
        self.hash_to_phrase[h1] = phrase
        return h1

    def winnow(self, hashes):
        # Fingerprinting for space efficiency
        fingerprints = set()
        if len(hashes) < self.w:
            return set(hashes)
        for i in range(len(hashes) - self.w + 1):
            window = hashes[i : i + self.w]
            fingerprints.add(min(window))
        return fingerprints

    def get_top_k_matches(self, match_freq_map, k=5):
        """
        DSA Logic: Uses a Min-Heap to maintain the Top-K highest frequencies.
        Time Complexity: O(N log K)
        """
        # We store tuples of (frequency, hash) in the min-heap
        heap = []
        for h, freq in match_freq_map.items():
            if len(heap) < k:
                heapq.heappush(heap, (freq, h))
            elif freq > heap[0][0]:
                heapq.heapreplace(heap, (freq, h))
        
        # Sort heap descending for display
        return sorted(heap, key=lambda x: x[0], reverse=True)

    def execute_scan(self, doc_a, doc_b):
        words_a = self.preprocess(doc_a)
        words_b = self.preprocess(doc_b)

        if len(words_a) < self.n or len(words_b) < self.n:
            return None

        # 1. Process Document A (Fingerprinting)
        all_hashes_a = [self.get_double_hash(" ".join(words_a[i:i+self.n])) 
                        for i in range(len(words_a) - self.n + 1)]
        fingerprints_a = self.winnow(all_hashes_a)
        
        # 2. Populate Bloom Filter
        for f in fingerprints_a:
            idx = f % self.bloom_size
            self.bloom_filter[idx] = 1

        # 3. Process Document B (Scanning & Frequency Tracking)
        all_hashes_b = [self.get_double_hash(" ".join(words_b[i:i+self.n])) 
                        for i in range(len(words_b) - self.n + 1)]
        
        matches = 0
        bloom_skips = 0
        match_freq_map = {}

        for h in all_hashes_b:
            idx = h % self.bloom_size
            if self.bloom_filter[idx] == 1:
                if h in fingerprints_a:
                    matches += 1
                    match_freq_map[h] = match_freq_map.get(h, 0) + 1
            else:
                bloom_skips += 1

        # 4. Extract Top-K via Min-Heap logic
        top_k_raw = self.get_top_k_matches(match_freq_map, k=5)
        top_k_formatted = [
            {"phrase": self.hash_to_phrase.get(h, "Unknown"), "count": freq} 
            for freq, h in top_k_raw
        ]

        score = (matches / len(fingerprints_a)) * 100 if len(fingerprints_a) > 0 else 0
        return {
            "score": score,
            "matches": matches,
            "skips": bloom_skips,
            "fps": len(fingerprints_a),
            "top_k": top_k_formatted
        }

# --- 2. STYLOMETRY UTILS ---

def analyze_style(text):
    sentences = re.split(r'[.!?]+', text)
    sentences = [s for s in sentences if len(s.strip()) > 0]
    words = text.split()
    avg_sentence_len = len(words) / len(sentences) if sentences else 0
    vocab_richness = len(set(words)) / len(words) if words else 0
    return avg_sentence_len, vocab_richness

# --- 3. UI CONFIG & STYLING ---

st.set_page_config(page_title="TextGuard Ultra v5.0", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

    * { margin: 0; padding: 0; box-sizing: border-box; }
    
    .stApp { 
        background: linear-gradient(135deg, #0f172a 0%, #1a2847 50%, #0d1b2a 100%);
        color: #e2e8f0; 
        font-family: 'Inter', sans-serif;
    }

    .main-container {
        padding: 40px 20px;
        max-width: 1400px;
        margin: 0 auto;
    }

    .header-section {
        text-align: center;
        margin-bottom: 50px;
        padding-bottom: 40px;
        border-bottom: 2px solid rgba(34, 211, 238, 0.2);
    }

    .neon-text {
        background: linear-gradient(135deg, #00d9ff 0%, #0099ff 50%, #6366f1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 900;
        font-size: 3.5rem;
        letter-spacing: -1px;
        margin-bottom: 10px;
        animation: glow 2s ease-in-out infinite;
    }

    @keyframes glow {
        0%, 100% { text-shadow: 0 0 30px rgba(0, 217, 255, 0.3); }
        50% { text-shadow: 0 0 60px rgba(0, 153, 255, 0.5); }
    }

    .subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        letter-spacing: 2px;
        margin-top: -15px;
    }

    .glass-card {
        background: rgba(15, 23, 42, 0.6);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(34, 211, 238, 0.15);
        border-radius: 20px;
        padding: 28px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
    }

    .glass-card:hover {
        border-color: rgba(34, 211, 238, 0.4);
        background: rgba(15, 23, 42, 0.9);
        box-shadow: 0 16px 64px rgba(34, 211, 238, 0.2);
        transform: translateY(-12px) scale(1.02);
    }

    .card-header {
        color: #22d3ee;
        font-weight: 700;
        font-size: 13px;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 18px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .card-header.suspect {
        color: #f59e0b;
    }

    .input-section {
        display: flex;
        flex-direction: column;
        gap: 16px;
    }

    .stTextArea textarea {
        background-color: #0f172a !important;
        border: 1.5px solid #1e293b !important;
        border-radius: 12px !important;
        color: #e2e8f0 !important;
        font-size: 14px !important;
        font-family: 'JetBrains Mono', monospace !important;
        transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        padding: 16px !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2) !important;
    }

    .stTextArea textarea:hover {
        border-color: rgba(34, 211, 238, 0.4) !important;
        background-color: #1a2847 !important;
        box-shadow: 0 8px 32px rgba(34, 211, 238, 0.15) !important;
        transform: translateY(-4px) !important;
    }

    .stTextArea textarea:focus {
        border-color: #22d3ee !important;
        background-color: #1a2847 !important;
        box-shadow: 0 12px 48px rgba(34, 211, 238, 0.25) !important;
        transform: translateY(-6px) !important;
    }

    .button-container {
        display: flex;
        justify-content: center;
        gap: 16px;
        margin-top: 40px;
    }

    .stButton > button {
        background: linear-gradient(135deg, #00d9ff 0%, #0099ff 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 48px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        letter-spacing: 0.5px !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 8px 24px rgba(0, 217, 255, 0.2) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 36px rgba(0, 217, 255, 0.4) !important;
    }

    .results-section {
        margin-top: 50px;
    }

    .results-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: #e2e8f0;
        margin-bottom: 30px;
        padding-bottom: 16px;
        border-bottom: 2px solid rgba(34, 211, 238, 0.2);
    }

    [data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.6) !important;
        border: 1.5px solid rgba(34, 211, 238, 0.2) !important;
        border-radius: 16px !important;
        padding: 24px !important;
        backdrop-filter: blur(10px) !important;
        transition: all 0.3s ease !important;
    }

    [data-testid="stMetric"]:hover {
        background: rgba(30, 41, 59, 0.9) !important;
        border-color: rgba(34, 211, 238, 0.4) !important;
        transform: translateY(-4px) !important;
    }

    .metric-label {
        color: #94a3b8 !important;
        font-size: 12px !important;
        letter-spacing: 1px !important;
    }

    .metric-value {
        color: #22d3ee !important;
        font-size: 28px !important;
        font-weight: 700 !important;
    }

    [data-testid="stFileUploader"] {
        border: 1.5px solid rgba(34, 211, 238, 0.2) !important;
        border-radius: 16px !important;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.5) 0%, rgba(30, 41, 59, 0.3) 100%) !important;
        padding: 28px !important;
        transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        backdrop-filter: blur(10px) !important;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: rgba(34, 211, 238, 0.6) !important;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(30, 41, 59, 0.6) 100%) !important;
        box-shadow: 0 12px 40px rgba(34, 211, 238, 0.15) !important;
        transform: translateY(-4px) !important;
    }

    .heap-rank {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.08) 0%, rgba(245, 158, 11, 0.02) 100%);
        border-left: 4px solid #f59e0b;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 14px;
        font-family: 'JetBrains Mono', monospace;
        border-top: 1px solid rgba(245, 158, 11, 0.1);
        border-right: 1px solid rgba(245, 158, 11, 0.1);
        border-bottom: 1px solid rgba(245, 158, 11, 0.1);
        transition: all 0.3s ease;
    }

    .heap-rank:hover {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(245, 158, 11, 0.05) 100%);
        border-left-color: #fbbf24;
        padding-left: 22px;
    }

    .rank-label {
        color: #f59e0b;
        font-weight: 900;
        font-size: 12px;
        letter-spacing: 1px;
    }

    .rank-phrase {
        color: #cbd5e1;
        font-style: italic;
        margin-top: 8px;
        font-size: 13px;
    }

    .verdict-critical {
        background: rgba(239, 68, 68, 0.1) !important;
        border-left: 4px solid #ef4444 !important;
        color: #fca5a5 !important;
        padding: 20px !important;
        border-radius: 12px !important;
        margin-top: 30px !important;
    }

    .verdict-warning {
        background: rgba(245, 158, 11, 0.1) !important;
        border-left: 4px solid #f59e0b !important;
        color: #fed7aa !important;
        padding: 20px !important;
        border-radius: 12px !important;
        margin-top: 30px !important;
    }

    .verdict-success {
        background: rgba(34, 197, 94, 0.1) !important;
        border-left: 4px solid #22c55e !important;
        color: #86efac !important;
        padding: 20px !important;
        border-radius: 12px !important;
        margin-top: 30px !important;
    }

    .footer {
        text-align: center;
        color: #475569;
        font-size: 11px;
        letter-spacing: 2px;
        margin-top: 80px;
        padding-top: 40px;
        border-top: 1px solid rgba(34, 211, 238, 0.1);
    }

    .sidebar-title {
        background: linear-gradient(135deg, #00d9ff 0%, #0099ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
        font-size: 18px;
        letter-spacing: 1px;
        margin-bottom: 20px;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.95) 0%, rgba(13, 27, 42, 0.95) 100%) !important;
        border-right: 1.5px solid rgba(34, 211, 238, 0.15) !important;
        backdrop-filter: blur(20px) !important;
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > [style*="flex-direction"] {
        gap: 24px !important;
    }

    .sidebar-divider {
        border-top: 1.5px solid rgba(34, 211, 238, 0.2) !important;
        margin: 24px 0 !important;
    }

    .stSlider {
        margin-bottom: 32px !important;
    }

    .stSlider > div:first-child {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.4) 0%, rgba(20, 33, 47, 0.4) 100%) !important;
        border-radius: 16px !important;
        padding: 22px !important;
        backdrop-filter: blur(15px) !important;
        border: 1.5px solid rgba(34, 211, 238, 0.2) !important;
        transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.2), 0 8px 24px rgba(0, 0, 0, 0.1) !important;
        position: relative !important;
    }

    .stSlider > div:first-child::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(34, 211, 238, 0.3), transparent);
        border-radius: 16px 16px 0 0;
    }

    .stSlider > div:first-child:hover {
        background: linear-gradient(135deg, rgba(34, 211, 238, 0.08) 0%, rgba(34, 211, 238, 0.03) 100%) !important;
        border-color: rgba(34, 211, 238, 0.5) !important;
        box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.2), 0 12px 40px rgba(34, 211, 238, 0.15) !important;
    }

    .stSlider > div:first-child:hover::before {
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(34, 211, 238, 0.6), transparent);
    }

    .stSlider [role="slider"] {
        background: linear-gradient(135deg, #00d9ff 0%, #0099ff 100%) !important;
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.6), 0 4px 12px rgba(0, 153, 255, 0.4) !important;
        cursor: grab !important;
        width: 24px !important;
        height: 24px !important;
        transition: all 0.3s ease !important;
    }

    .stSlider [role="slider"]:hover {
        width: 28px !important;
        height: 28px !important;
        box-shadow: 0 0 30px rgba(0, 217, 255, 0.8), 0 8px 20px rgba(0, 153, 255, 0.6) !important;
    }

    .stSlider [role="slider"]:active {
        cursor: grabbing !important;
        box-shadow: 0 0 40px rgba(0, 217, 255, 1), 0 12px 30px rgba(0, 153, 255, 0.8) !important;
    }

    .stCaption {
        color: #94a3b8 !important;
        font-size: 12px !important;
        letter-spacing: 0.5px !important;
        margin-top: 16px !important;
        padding: 14px 16px !important;
        background: linear-gradient(135deg, rgba(34, 211, 238, 0.05) 0%, rgba(0, 153, 255, 0.02) 100%) !important;
        border-radius: 10px !important;
        border-left: 3px solid rgba(34, 211, 238, 0.4) !important;
        border-top: 1px solid rgba(34, 211, 238, 0.1) !important;
        border-right: 1px solid rgba(34, 211, 238, 0.1) !important;
        border-bottom: 1px solid rgba(34, 211, 238, 0.1) !important;
        transition: all 0.3s ease !important;
    }

    .stCaption:hover {
        background: linear-gradient(135deg, rgba(34, 211, 238, 0.1) 0%, rgba(0, 153, 255, 0.05) 100%) !important;
        border-left-color: rgba(0, 217, 255, 0.8) !important;
        color: #e2e8f0 !important;
        box-shadow: 0 4px 16px rgba(34, 211, 238, 0.1) !important;
    }

    /* Slider label styling */
    .stSlider > div:first-child label {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        letter-spacing: 0.5px !important;
        margin-bottom: 14px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<div class='sidebar-title'>⚙️ SCAN_CONFIG</div>", unsafe_allow_html=True)
    st.markdown("---")
    n_gram = st.slider("Shingle Size (N)", 2, 10, 4, help="Number of words in a sliding window hash.")
    win_w = st.slider("Winnowing Window (W)", 2, 10, 4, help="Size of window for fingerprint selection.")
    st.markdown("---")
    st.caption("🔧 Engine: Hybrid Core v5.0")
    st.caption("🎯 Algorithm: Rabin-Karp + Bloom + Winnowing")

# --- HEADER ---
st.markdown("<div class='header-section'>", unsafe_allow_html=True)
st.markdown("<h1 class='neon-text'>TEXTGUARD ULTRA</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>ADVANCED MIN-HEAP & BLOOM FILTER FORENSICS</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- INPUT AREA ---
col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-header'>📄 Source Repository A</div>", unsafe_allow_html=True)
    file_a = st.file_uploader("Upload Original (.txt)", type=['txt'], key="ua")
    text_a = st.text_area("Input Original Text", height=220, key="ta", placeholder="Enter repository text...")
    content_a = file_a.read().decode("utf-8") if file_a else text_a
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-header suspect'>🔍 Suspect Buffer B</div>", unsafe_allow_html=True)
    file_b = st.file_uploader("Upload Suspect (.txt)", type=['txt'], key="ub")
    text_b = st.text_area("Input Suspect Text", height=220, key="tb", placeholder="Enter analysis text...")
    content_b = file_b.read().decode("utf-8") if file_b else text_b
    st.markdown("</div>", unsafe_allow_html=True)

# --- ANALYSIS ---
if st.button("🔥 START FORENSIC SCAN", use_container_width=True):
    if content_a and content_b:
        with st.status("🚀 Initializing DSA Funnel...", expanded=False) as status:
            time.sleep(0.4)
            # 1. DSA Engine with Dynamic Parameters from Sidebar
            engine = TextGuardEngine(n=n_gram, w=win_w)
            res = engine.execute_scan(content_a, content_b)
            
            # 2. NLP Semantic Score
            vec = TfidfVectorizer(stop_words='english')
            tfidf = vec.fit_transform([content_a, content_b])
            nlp_score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0] * 100
            
            # 3. Style Comparison
            stA, stB = analyze_style(content_a), analyze_style(content_b)
            status.update(label="✅ Forensic Scan Complete", state="complete")

        # --- RESULTS DASHBOARD ---
        st.markdown("<div class='results-section'>", unsafe_allow_html=True)
        st.markdown("<h2 class='results-title'>📊 Forensic Intelligence Report</h2>", unsafe_allow_html=True)
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Verbatim Match", f"{res['score']:.1f}%")
        m2.metric("Semantic Overlap", f"{nlp_score:.1f}%")
        m3.metric("Bloom Efficiency", res['skips'])
        m4.metric("Unique Fingerprints", res['fps'])

        # --- HEAP RANKING DISPLAY ---
        st.markdown("<h3 style='color:#e2e8f0; font-weight:800; margin-top:40px; margin-bottom:24px;'>🧬 Ranking: Max Occurrence Analysis (Min-Heap)</h3>", unsafe_allow_html=True)
        if res['top_k']:
            fcol1, fcol2 = st.columns([2, 1])
            with fcol1:
                for idx, item in enumerate(res['top_k']):
                    st.markdown(f"""
                        <div class='heap-rank'>
                            <div class='rank-label'>RANK #{idx+1} | FREQUENCY: {item['count']}x</div>
                            <div class='rank-phrase'>"{item['phrase']}"</div>
                        </div>
                    """, unsafe_allow_html=True)
            with fcol2:
                st.info(f"📌 The Min-Heap maintains the Top 5 most frequent plagiarism segments based on your current N-gram ({n_gram}) and Window ({win_w}) settings.")
        else:
            st.info("✅ No recurring identical sequences identified.")

        # --- FINAL VERDICT ---
        if res['score'] > 25:
            st.markdown("<div class='verdict-critical'><strong>🚨 CRITICAL:</strong> High structural plagiarism detected. Massive verbatim clusters found.</div>", unsafe_allow_html=True)
        elif nlp_score > 60:
            st.markdown("<div class='verdict-warning'><strong>⚠️ WARNING:</strong> Significant semantic similarity. Likely intelligent paraphrasing.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='verdict-success'><strong>✅ AUTHENTIC:</strong> Low structural and thematic overlap detected.</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.warning("⚠️ Please provide input in both buffers to initiate analysis.")

# FOOTER
st.markdown("<div class='footer'>🔐 TECHNOLOGY: MIN-HEAP TOP-K RANKING | BLOOM FILTER GATEKEEPER | WINNOWING OPTIMIZATION | TF-IDF SEMANTICS</div>", unsafe_allow_html=True)