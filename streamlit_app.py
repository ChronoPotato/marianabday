# app.py
"""
Mariana's Birthday Quiz - A beautiful riddle game with progress tracking

DEPLOYMENT OPTIONS:
1. Streamlit Community Cloud (FREE):
   - Push this file to GitHub
   - Visit share.streamlit.io
   - Connect your repo and deploy

2. Local Testing:
   - Install: pip install streamlit
   - Run: streamlit run app.py

Note: Cannot be hosted on GitHub Pages (static sites only)
Progress is automatically saved in the URL - users can bookmark to resume!
"""

import re
import base64, mimetypes
from pathlib import Path
import streamlit as st
import json
from datetime import datetime

# -------------------------------
# Page setup
# -------------------------------
st.set_page_config(
    page_title="Mariana's Birthday Quiz 🎂",
    page_icon="🎉",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------
# Local Storage Functions
# -------------------------------
def load_progress():
    """Load progress from browser localStorage via JavaScript"""
    local_storage_code = """
    <script>
    // Function to load data from localStorage
    function loadFromLocalStorage() {
        const data = localStorage.getItem('mariana_quiz_progress');
        if (data) {
            const progress = JSON.parse(data);
            // Send data to Streamlit
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                data: progress
            }, '*');
        }
    }
    
    // Load on page load
    window.addEventListener('load', loadFromLocalStorage);
    </script>
    """
    st.components.v1.html(local_storage_code, height=0)

def save_progress(idx, tries, total_attempts, perfect_solves):
    """Save progress to browser localStorage via JavaScript"""
    progress_data = {
        'idx': idx,
        'tries': tries,
        'total_attempts': total_attempts,
        'perfect_solves': perfect_solves,
        'last_updated': datetime.now().isoformat()
    }
    
    save_code = f"""
    <script>
    // Save progress to localStorage
    localStorage.setItem('mariana_quiz_progress', JSON.stringify({json.dumps(progress_data)}));
    </script>
    """
    st.components.v1.html(save_code, height=0)

# -------------------------------
# Page setup
# -------------------------------
st.set_page_config(
    page_title="Mariana's Birthday Quiz 🎂",
    page_icon="🎉",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------
# Utilities
# -------------------------------
def _rerun():
    try:
        st.rerun()
    except Exception:
        st.experimental_rerun()

@st.cache_data(show_spinner=False)
def video_to_data_uri(path: str) -> str:
    """Read a video file and return a base64 data URI string."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Video not found at: {p.resolve()}")
    mime = mimetypes.guess_type(p.name)[0] or "video/mp4"
    data64 = base64.b64encode(p.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{data64}"

def normalize_text(s: str) -> str:
    # Lower, strip, collapse whitespace, remove punctuation (keep letters/numbers with accents)
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9À-ÿ\s'-]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s

def check_answer(riddle, user_input=None, selected=None):
    if riddle["type"] == "mcq":
        return selected == riddle["answer"]
    else:
        if not user_input:
            return False
        user_norm = normalize_text(user_input)
        valid = [normalize_text(a) for a in riddle["answers"]]
        return user_norm in valid

# -------------------------------
# Enhanced Styling
# -------------------------------
st.markdown("""
<style>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Inter:wght@400;500;600&display=swap');

/* Main background - blue gradient */
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #e0f2fe 0%, #f0f9ff 50%, #dbeafe 100%);
    color: #0c4a6e;
}

/* Remove default header background */
[data-testid="stHeader"] { 
    background: transparent; 
}

/* Container adjustments */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 950px;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
    .main .block-container {
        padding: 1rem 0.5rem;
    }
    
    .hero {
        height: 35vh;
        min-height: 250px;
        margin: 0 0 1.5rem 0;
        border-radius: 16px;
    }
    
    .hero h1 {
        font-size: clamp(2rem, 8vw, 3rem);
    }
    
    .question-card {
        padding: 1.5rem;
        border-radius: 16px;
    }
    
    .question-text {
        font-size: 1.4rem;
    }
    
    .stats-card {
        padding: 1.25rem;
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    
    .completion-card {
        padding: 2rem 1.5rem;
    }
    
    .completion-title {
        font-size: 2rem;
    }
}

/* Hero Banner */
.hero {
    position: relative;
    width: 100%;
    height: 45vh;
    min-height: 350px;
    max-height: 500px;
    overflow: hidden;
    border-radius: 24px;
    box-shadow: 0 20px 60px rgba(14, 165, 233, 0.15);
    margin: 0 0 2.5rem 0;
    background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
}

.hero video {
    position: absolute;
    top: 50%;
    left: 50%;
    min-width: 100%;
    min-height: 100%;
    transform: translate(-50%, -50%);
    object-fit: cover;
    filter: brightness(0.6) contrast(1.1) saturate(1.2);
    mix-blend-mode: multiply;
}

.hero .title {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 2rem;
    background: linear-gradient(to bottom, rgba(0,0,0,0.1), rgba(0,0,0,0.3));
}

.hero h1 {
    font-family: 'Playfair Display', serif;
    font-weight: 900;
    font-size: clamp(2.5rem, 7vw, 4.5rem);
    color: #ffffff;
    text-shadow: 0 4px 20px rgba(0,0,0,0.3);
    margin: 0;
    line-height: 1.1;
    letter-spacing: -0.02em;
}

.hero p {
    font-family: 'Inter', sans-serif;
    font-size: clamp(1rem, 2vw, 1.25rem);
    color: rgba(255, 255, 255, 0.95);
    margin-top: 1rem;
    font-weight: 500;
    text-shadow: 0 2px 10px rgba(0,0,0,0.2);
}

/* Progress Section */
.progress-container {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 4px 20px rgba(14, 165, 233, 0.1);
    border: 1px solid rgba(14, 165, 233, 0.1);
}

/* Stats Card */
.stats-card {
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(20px);
    border: 2px solid rgba(14, 165, 233, 0.15);
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 10px 40px rgba(14, 165, 233, 0.08);
    margin-bottom: 2rem;
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 2rem;
    text-align: center;
}

.stat-item {
    padding: 0.5rem;
}

.stat-number {
    font-family: 'Playfair Display', serif;
    font-size: 2.5rem;
    font-weight: 900;
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
    margin-bottom: 0.5rem;
}

.stat-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.875rem;
    color: #6b46c1;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.progress-text {
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    color: #6b46c1;
    font-weight: 600;
    margin-bottom: 0.75rem;
}

/* Progress bar styling */
.stProgress > div > div {
    background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
    height: 12px;
    border-radius: 100px;
}

.stProgress > div {
    background-color: rgba(99, 102, 241, 0.1);
    border-radius: 100px;
}

/* Question Card */
.question-card {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border: 2px solid rgba(99, 102, 241, 0.15);
    border-radius: 20px;
    padding: 2.5rem;
    box-shadow: 0 10px 40px rgba(99, 102, 241, 0.08);
    margin-bottom: 2rem;
}

/* Question Title */
.question-number {
    font-family: 'Inter', sans-serif;
    font-size: 0.875rem;
    font-weight: 600;
    color: #7c3aed;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
}

.question-text {
    font-family: 'Playfair Display', serif;
    font-size: 1.75rem;
    font-weight: 700;
    color: #1e1b4b;
    line-height: 1.4;
    margin-bottom: 2rem;
}

/* Form inputs */
.stTextInput > div > div > input {
    font-family: 'Inter', sans-serif;
    font-size: 1.1rem;
    padding: 0.75rem 1.25rem;
    border: 2px solid rgba(14, 165, 233, 0.2);
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.8);
    color: #0c4a6e;
    transition: all 0.3s ease;
}

.stTextInput > div > div > input:focus {
    border-color: #0ea5e9;
    box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1);
}

/* Radio buttons */
.stRadio > label {
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 1rem;
}

.stRadio > div > label {
    font-family: 'Inter', sans-serif;
    font-size: 1.05rem;
    color: #ffffff;
    padding: 0.75rem 1.25rem;
    margin: 0.5rem 0;
    background: rgba(14, 165, 233, 1);
    border: 2px solid transparent;
    border-radius: 12px;
    transition: all 0.3s ease;
    cursor: pointer;
}

.stRadio > div > label:hover {
    background: rgba(14, 165, 233, 0.1);
    border-color: rgba(14, 165, 233, 0.3);
}

/* Submit button */
.stButton > button {
    font-family: 'Inter', sans-serif;
    font-size: 1.1rem;
    font-weight: 600;
    padding: 0.875rem 2.5rem;
    background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%);
    color: #ffffff;
    border: none;
    border-radius: 100px;
    box-shadow: 0 4px 20px rgba(14, 165, 233, 1);
    transition: all 0.3s ease;
    width: 100%;
    margin-top: 1rem;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 30px rgba(14, 165, 233, 1);
}

/* Alert messages */
.stAlert {
    border-radius: 12px;
    border: none;
    font-family: 'Inter', sans-serif;
}

/* Success message */
div[data-baseweb="notification"][kind="positive"] {
    background: linear-gradient(135deg, #10b981 100%, #6366f1 100%);
    color: #ffffff;
}

/* Error message */
div[data-baseweb="notification"][kind="negative"] {
    background: linear-gradient(135deg, #ef4444 100%, #6366f1 100%);
    color: #ffffff;
}

/* Warning message */
div[data-baseweb="notification"][kind="warning"] {
    background: linear-gradient(135deg, #f59e0b 100%, #6366f1 100%);
    color: #ffffff;
}

/* Hint expander */
.streamlit-expanderHeader {
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    color: #ffffff;
    background: rgba(139, 92, 246, 1);
    border-radius: 8px;
    padding: 0.5rem 1rem;
}

.streamlit-expanderContent {
    font-family: 'Inter', sans-serif;
    background: rgba(139, 92, 246, 1);
    border-radius: 0 0 8px 8px;
    padding: 1rem;
}

/* Completion card */
.completion-card {
    background: linear-gradient(135deg, rgba(99, 102, 241, 1) 100%, rgba(1, 1, 1, 1) 100%);
    border: 2px solid rgba(99, 102, 241, 1);
    border-radius: 24px;
    padding: 3rem;
    text-align: center;
    box-shadow: 0 20px 60px rgba(99, 102, 241, 1);
}

.completion-title {
    font-family: 'Playfair Display', serif;
    font-size: 3rem;
    font-weight: 900;
    background: linear-gradient(135deg, #6366f1 100%, #8b5cf6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1.5rem;
}

.completion-message {
    font-family: 'Inter', sans-serif;
    font-size: 1.25rem;
    line-height: 1.6;
    color: #ffffff;
    font-weight: 500;
}

/* Reset button */
.reset-button button {
    background: rgba(139, 92, 246, 0.1);
    color: #7c3aed;
    border: 2px solid rgba(139, 92, 246, 0.2);
    padding: 0.5rem 1.25rem;
    font-size: 0.9rem;
}

.reset-button button:hover {
    background: rgba(139, 92, 246, 0.2);
    border-color: rgba(139, 92, 246, 0.3);
}

/* Footer */
.footer-text {
    text-align: center;
    font-family: 'Inter', sans-serif;
    color: #9272b0;
    font-size: 0.875rem;
    margin-top: 3rem;
    padding-top: 2rem;
    border-top: 1px solid rgba(139, 92, 246, 1);
}
            
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Hero banner (looping video + title)
# -------------------------------
VIDEO_PATH = "seavid.mp4"
try:
    VIDEO_SRC = video_to_data_uri(VIDEO_PATH)
    st.markdown(f"""
    <div class="hero">
      <video autoplay muted loop playsinline>
        <source src="{VIDEO_SRC}" type="video/mp4">
      </video>
      <div class="title">
        <h1>Mariana's Birthday Quiz</h1>
        <p>✨ Solve each riddle to unlock your birthday surprise ✨</p>
      </div>
    </div>
    """, unsafe_allow_html=True)
except FileNotFoundError as e:
    # Fallback without video
    st.markdown("""
    <div class="hero" style="background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);">
      <div class="title">
        <h1>Mariana's Birthday Quiz</h1>
        <p>✨ Solve each riddle to unlock your birthday surprise ✨</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------
# Riddles configuration
# -------------------------------
RIDDLES = [
    {
        "type": "mcq",
        "question": "I have cities but no houses, forests but no trees, and water but no fish. What am I?",
        "options": ["A dream", "A desert", "A map", "Google"],
        "answer": "A map",
        "hint": "You might fold me to carry me."
    },
    {
        "type": "text",
        "question": "(Atbash Cypher) DSZG BVZI DZH QZMV ZFHGVM YLIM?",
        "answers": ["1775"],
        "hint": "Fold the alphabet"
    },
    {
        "type": "text",
        "question": "Who's the best boy of them all",
        "answers": ["Loki", "loki"],
        "hint": "Dee dou"
    },
    {
        "type": "mcq",
        "question": "When did Lord Grantham first meet Mr Bates",
        "options": ["100 year war", "boer war", "world war 1", "bolchevik war"],
        "answer": "boer war",
        "hint": "south african war"
    },
    {
        "type": "text",
        "question": "What title does Isobel receive when she remarries?",
        "answers": ["baroness"],
        "hint": "Ghost US Robber Bs"
    },
    {
        "type": "mcq",
        "question": "What does Molesley's father excel in?",
        "options": ["gardening", "cooking", "raising hogs"],
        "answer": "gardening",
        "hint": "It increases every birthday."
    },
    {
        "type": "text",
        "question": "What has many keys but can't open a single lock?",
        "answers": ["piano", "a piano", "keyboard", "a keyboard"],
        "hint": "It makes music… or types emails."
    },
    {
        "type": "text",
        "question": "Type your name in binary.",
        "answers": ["01101101 01100001 01110010 01101001 01100001 01101110 01100001"],
        "hint": "you know...0s and 1s"
    },
    {
        "type": "mcq",
        "question": "I'm always in front of you but can't be seen. What am I?",
        "options": ["The future", "Your reflection", "Your nose", "Air"],
        "answer": "The future",
        "hint": "It hasn't happened yet."
    },
    {
        "type": "text",
        "question": "(Ceasar cypher) - AHP FTGR IETGXML TKX BG MAX LHETK LRLMXF?",
        "answers": ["1775"],
        "hint": "Ceasar ROT7 Right"
    },
]

TOTAL = len(RIDDLES)

# -------------------------------
# Session state
# -------------------------------
if "idx" not in st.session_state:
    st.session_state.idx = 0  # current riddle index (0-based)
if "tries" not in st.session_state:
    st.session_state.tries = 0  # wrong attempts for current riddle
if "total_attempts" not in st.session_state:
    st.session_state.total_attempts = 0  # total attempts across all riddles
if "perfect_solves" not in st.session_state:
    st.session_state.perfect_solves = 0  # riddles solved on first try

# Check URL parameters for saved progress
query_params = st.query_params
if "progress" in query_params and "resumed" not in st.session_state:
    try:
        saved_idx = int(query_params["progress"])
        if 0 <= saved_idx <= TOTAL and saved_idx != st.session_state.idx:
            st.session_state.idx = saved_idx
            st.session_state.resumed = True
            st.info(f"📚 Welcome back! Resuming from Riddle #{saved_idx + 1}")
    except:
        pass

idx = st.session_state.idx
progress = (idx / TOTAL)

# Progress display
st.markdown('<div class="progress-container">', unsafe_allow_html=True)
st.markdown(f'<div class="progress-text">🎯 Progress: {idx} of {TOTAL} riddles solved</div>', unsafe_allow_html=True)
st.progress(progress)
st.markdown('</div>', unsafe_allow_html=True)

# Controls
col1, col2 = st.columns([1, 5])
with col1:
    st.markdown('<div class="reset-button">', unsafe_allow_html=True)
    if st.button("🔄 Reset"):
        st.session_state.idx = 0
        st.session_state.tries = 0
        st.session_state.total_attempts = 0
        st.session_state.perfect_solves = 0
        if "resumed" in st.session_state:
            del st.session_state.resumed
        if "progress" in st.query_params:
            del st.query_params["progress"]
        _rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Stats Card
if idx > 0:  # Only show stats after at least one riddle is solved
    accuracy = (idx / max(st.session_state.total_attempts, 1)) * 100
    st.markdown(f"""
    <div class="stats-card">
        <div class="stat-item">
            <div class="stat-number">{idx}</div>
            <div class="stat-label">Riddles Solved</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">{st.session_state.perfect_solves}</div>
            <div class="stat-label">Perfect Solves</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">{accuracy:.0f}%</div>
            <div class="stat-label">Accuracy</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------
# Main flow
# -------------------------------
if idx < TOTAL:
    r = RIDDLES[idx]
    
    st.markdown('<div class="question-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="question-number">Riddle #{idx + 1}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="question-text">{r["question"]}</div>', unsafe_allow_html=True)
    
    correct = False
    wrong = False

    # Use forms so Enter submits nicely
    with st.form(key=f"riddle_form_{idx}", clear_on_submit=False):
        if r["type"] == "mcq":
            choice = st.radio("Choose your answer:", r["options"], index=None)
            submit = st.form_submit_button("Submit Answer ✨", use_container_width=True)
            if submit:
                if choice is None:
                    st.warning("Please select an option first! 🤔")
                else:
                    correct = check_answer(r, selected=choice)
                    wrong = not correct
        else:
            val = st.text_input("Your answer:", value="", placeholder="Type your answer here...")
            submit = st.form_submit_button("Submit Answer ✨", use_container_width=True)
            if submit:
                if not val.strip():
                    st.warning("Please type an answer first! 🤔")
                else:
                    correct = check_answer(r, user_input=val)
                    wrong = not correct

    # Feedback + hint
    if correct:
        st.success("🎉 Brilliant! That's correct!")
        st.balloons()
        if st.session_state.tries == 0:
            st.session_state.perfect_solves += 1
        st.session_state.total_attempts += st.session_state.tries + 1
        st.session_state.idx += 1
        st.session_state.tries = 0
        # Auto-save progress to URL
        st.query_params["progress"] = str(st.session_state.idx)
        _rerun()
    elif wrong:
        st.session_state.tries += 1
        st.error("Not quite right... Give it another try! 💭")
        with st.expander("💡 Need a hint?"):
            st.info(r.get("hint", "Think outside the box..."))

    st.markdown('</div>', unsafe_allow_html=True)

else:
    # Completed!
    final_accuracy = (TOTAL / max(st.session_state.total_attempts, 1)) * 100
    st.markdown(f"""
    <div class="completion-card">
        <div class="completion-title">🎂 Congratulations, Mariana! 🎂</div>
        <div class="completion-message">
            You solved every riddle we're so proud!<br>
            <br>
            <strong>Final Score:</strong> {st.session_state.perfect_solves} perfect solves out of {TOTAL} riddles<br>
            <strong>Accuracy:</strong> {final_accuracy:.0f}%<br>
            <br>
            We love you dear, hope you have a great day!<br>
            <br>
            Happy Birthday, Amazing! 💖✨
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.snow()

# Footer
st.markdown("""
<div class="footer-text">
    Made with 💙 for the most wonderful person • Happy Birthday, Mariana!<br>
    <small style="opacity: 0.7;">Progress auto-saves in the URL - bookmark this page to resume anytime!</small>
</div>
""", unsafe_allow_html=True)