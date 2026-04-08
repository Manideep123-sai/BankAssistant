import uuid
import time
import streamlit as st
from app import repositories
from app.graph import run_graph

# ──────────────────────────────────────────────────────────────
# Page config
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BankAI · Smart Banking Assistant",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────
BANKS = [
    {"name": "State Bank of India", "short": "SBI", "accent": "#2196F3", "bg": "#1565C0"},
    {"name": "HDFC Bank", "short": "HDFC", "accent": "#880E4F", "bg": "#6A0038"},
    {"name": "ICICI Bank", "short": "ICICI", "accent": "#F57C00", "bg": "#E65100"},
    {"name": "Axis Bank", "short": "AXIS", "accent": "#97144D", "bg": "#7B0D3F"},
    {"name": "Punjab National Bank", "short": "PNB", "accent": "#D32F2F", "bg": "#B71C1C"},
    {"name": "Kotak Mahindra Bank", "short": "KOTAK", "accent": "#E53935", "bg": "#C62828"},
    {"name": "Bank of Baroda", "short": "BOB", "accent": "#EF6C00", "bg": "#D84315"},
    {"name": "Canara Bank", "short": "CANARA", "accent": "#00897B", "bg": "#00695C"},
]

LANGUAGES = [
    "English", "Hindi", "Kannada", "Malayalam", "Tamil", "Telugu"
]

FEATURES = [
    ("", "AI Powered", "Instant answers to any banking query using advanced language models."),
    ("", "Multi Language", "Chat naturally in English, Hindi, Tamil, Telugu, and more."),
    ("", "Branch Locator", "Find nearby ATMs and branches with high precision Google Maps links."),
]

# ──────────────────────────────────────────────────────────────
# Session state & Theme
# ──────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "page": "landing",
        "user": None,
        "thread_id": None,
        "chat_history": [],
        "selected_bank": None,
        "qa_input": None,
        "theme": "dark",  # 'dark' or 'light'
        "language": "English",
        "auth_tab": "login",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

def toggle_theme():
    st.session_state["theme"] = "light" if st.session_state["theme"] == "dark" else "dark"
    st.rerun()

# ──────────────────────────────────────────────────────────────
# CSS & Theme (Premium Navy + Gold)
# ──────────────────────────────────────────────────────────────
is_dark = st.session_state["theme"] == "dark"

COLOR_NAVY = "#0A1628"
COLOR_GOLD = "#C9A84C"
COLOR_BG_LIGHT = "#F4F6FB"
COLOR_BG_DARK = "#0A1628"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=Inter:wght@300;400;500;600;700&display=swap');

:root {{
    --navy: {COLOR_NAVY};
    --gold: {COLOR_GOLD};
    --bg: {"#0A1628" if is_dark else "#F4F6FB"};
    --text: {"#E2E8F0" if is_dark else "#1F2937"};
    --text-muted: {"#94A3B8" if is_dark else "#64748B"};
    --card-bg: {"#112240" if is_dark else "#FFFFFF"};
    --border: {"rgba(201, 168, 76, 0.2)" if is_dark else "rgba(10, 22, 40, 0.08)"};
    --shadow: {"rgba(0,0,0,0.4)" if is_dark else "rgba(10, 22, 40, 0.05)"};
}}

/* === BASE === */
html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif !important;
}}
.stApp {{
    background: var(--bg);
    color: var(--text);
}}
h1, h2, h3, .brand-font {{
    font-family: 'Playfair Display', serif !important;
}}

/* Hide Streamlit Header/Footer */
#MainMenu, footer, header {{ visibility: hidden; }}
.stDeployButton {{ display: none; }}
[data-testid="stToolbar"] {{ display: block !important; }}

/* Restore Sidebar Control */
[data-testid="collapsedControl"] {{
    display: flex !important;
    color: var(--gold) !important;
}}

/* === ANIMATIONS === */
@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
.fade-in {{ animation: fadeIn 0.5s ease forwards; }}

/* === HERO === */
.hero-section {{
    background: var(--navy);
    background: linear-gradient(135deg, var(--navy) 0%, #152B46 100%);
    position: relative;
    padding: 100px 20px;
    text-align: center;
    border-radius: 0 0 40px 40px;
    margin: -6rem -5rem 3rem -5rem;
    overflow: hidden;
}}
.hero-section::after {{
    content: ""; position: absolute; top: -50%; right: -20%; width: 60%; height: 200%;
    background: linear-gradient(45deg, transparent, rgba(201, 168, 76, 0.08));
    transform: rotate(20deg); pointer-events: none;
}}
.hero-title {{ color: var(--gold); font-size: 3.5rem; margin-bottom: 1rem; }}
.hero-sub {{ color: var(--gold); opacity: 0.8; font-size: 1.2rem; margin-bottom: 2.5rem; }}

/* === BUTTONS === */
.stButton > button {{
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    padding: 0.6rem 2rem !important;
}}
.btn-gold button {{
    background-color: var(--gold) !important;
    color: var(--navy) !important;
    border: none !important;
}}
.btn-gold button:hover {{
    background-color: #D4B665 !important;
    box-shadow: 0 8px 20px rgba(201, 168, 76, 0.3) !important;
}}
.btn-navy-outline button {{
    background-color: transparent !important;
    color: var(--gold) !important;
    border: 2px solid var(--gold) !important;
}}
.btn-navy-outline button:hover {{
    background-color: rgba(201, 168, 76, 0.1) !important;
}}

/* === CARDS === */
.feature-card {{
    background: var(--card-bg);
    padding: 30px;
    border-radius: 20px;
    box-shadow: 0 10px 30px var(--shadow);
    border-left: 5px solid var(--gold);
    transition: transform 0.3s ease;
    height: 100%;
}}
.feature-card:hover {{ transform: translateY(-5px); }}

.bank-card-new {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 25px;
    text-align: center;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    position: relative;
    box-shadow: 0 4px 12px var(--shadow);
}}
.bank-card-new:hover {{
    transform: translateY(-4px);
    border-color: var(--gold);
    box-shadow: 0 12px 24px rgba(201, 168, 76, 0.2);
    background: {"#1A2D4D" if is_dark else "#FDF6E3"};
}}

/* === CHAT UI === */
.chat-container {{
    max-width: 800px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
}}
.bubble-row {{
    display: flex;
    width: 100%;
    margin: 5px 0;
}}
.user-row {{ justify-content: flex-end; }}
.ai-row {{ justify-content: flex-start; }}

.chat-bubble {{
    padding: 12px 18px;
    max-width: 75%;
    line-height: 1.5;
    position: relative;
    font-size: 0.95rem;
}}
.user-bubble {{
    background: var(--gold) !important;
    color: var(--navy) !important;
    border-radius: 18px 18px 0 18px;
}}
.ai-bubble {{
    background: {"#FFFFFF" if not is_dark else "#1E293B"} !important;
    color: {"#0A1628" if not is_dark else "#F1F5F9"} !important;
    border-radius: 18px 18px 18px 0;
    border-left: 3px solid var(--gold) !important;
    box-shadow: 0 4px 10px var(--shadow);
}}
.ai-badge {{
    background: var(--gold);
    color: var(--navy);
    font-size: 10px;
    padding: 2px 6px;
    border-radius: 4px;
    font-weight: 800;
    margin-bottom: 4px;
    display: inline-block;
}}
.timestamp {{ font-size: 11px; color: var(--text-muted); margin-top: 4px; text-align: inherit; }}

.chat-sticky-header {{
    position: sticky; top: 0; z-index: 1000;
    background: var(--navy); padding: 15px 30px;
    border-bottom: 2px solid var(--gold);
    display: flex; align-items: center; justify-content: space-between;
    margin: -1rem -1rem 1rem -1rem;
}}

/* Typing dots */
.dot-typing {{ position: relative; width: 6px; height: 6px; border-radius: 5px; background-color: var(--gold); color: var(--gold); animation: dotTyping 1.5s infinite linear; margin-left: 10px; }}
@keyframes dotTyping {{ 0% {{ box-shadow: 15px 0 0 0 var(--gold), 30px 0 0 0 var(--gold), 45px 0 0 0 var(--gold); }} 16.667% {{ box-shadow: 15px -10px 0 0 var(--gold), 30px 0 0 0 var(--gold), 45px 0 0 0 var(--gold); }} 33.333% {{ box-shadow: 15px 0 0 0 var(--gold), 30px 0 0 0 var(--gold), 45px 0 0 0 var(--gold); }} 50% {{ box-shadow: 15px 0 0 0 var(--gold), 30px -10px 0 0 var(--gold), 45px 0 0 0 var(--gold); }} 66.667% {{ box-shadow: 15px 0 0 0 var(--gold), 30px 0 0 0 var(--gold), 45px 0 0 0 var(--gold); }} 83.333% {{ box-shadow: 15px 0 0 0 var(--gold), 30px 0 0 0 var(--gold), 45px -10px 0 0 var(--gold); }} 100% {{ box-shadow: 15px 0 0 0 var(--gold), 30px 0 0 0 var(--gold), 45px 0 0 0 var(--gold); }} }}

/* Input Styling */
div[data-testid="stChatInput"] {{
    background: var(--card-bg) !important;
    border: 1px solid var(--navy) !important;
    border-radius: 50px !important;
    padding-left: 10px !important;
}}
div[data-testid="stChatInput"]:focus-within {{
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 1px var(--gold) !important;
}}

/* === SIDEBAR === */
[data-testid="stSidebar"] {{
    background-color: var(--navy) !important;
}}
[data-testid="stSidebar"] * {{
    color: #E2E8F0 !important;
}}
.sidebar-logo {{
    font-size: 24px; font-weight: 800; color: var(--gold) !important; margin-bottom: 5px;
}}
.sidebar-divider {{ height: 1px; background: var(--gold); opacity: 0.3; margin-bottom: 20px; }}
.section-label {{ font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: var(--gold) !important; opacity: 0.7; margin-bottom: 8px; }}

</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

def go(page):
    st.session_state["page"] = page

def get_bank_info(name):
    return next((b for b in BANKS if b["name"] == name), BANKS[0])

# ──────────────────────────────────────────────────────────────
# COMPONENTS
# ──────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">BankAI</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-label">Settings</div>', unsafe_allow_html=True)
        
        def _update_lang():
            st.session_state["language"] = st.session_state["side_lang_select"]
        
        current_lang = st.session_state.get("language", "English")
        try:
            idx = LANGUAGES.index(current_lang)
        except ValueError:
            idx = 0
            
        st.selectbox("Language", LANGUAGES, index=idx, key="side_lang_select", on_change=_update_lang)
        
        st.markdown('<div class="section-label" style="margin-top:20px;">Session</div>', unsafe_allow_html=True)
        
        if st.button("New Chat", use_container_width=True):
            st.session_state["chat_history"] = []
            uid = st.session_state["user"]["user_id"] if st.session_state["user"] else "guest"
            st.session_state["thread_id"] = f"{uid}-{uuid.uuid4().hex[:8]}"
            st.rerun()

        if st.session_state["user"]:
            if st.button("Logout", use_container_width=True, type="secondary"):
                st.session_state["user"] = None
                st.session_state["page"] = "landing"
                st.rerun()
        
        st.markdown('<div style="margin-top:auto; padding-top:20px;">', unsafe_allow_html=True)
        if st.session_state["user"]:
            st.markdown(f'<div style="font-size:12px; opacity:0.6;">{st.session_state["user"]["full_name"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-size:12px; opacity:0.6;">Guest Mode</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def render_top_bar():
    theme_text = "Mode: Light" if is_dark else "Mode: Dark"
    st.markdown(
        f'<div class="chat-sticky-header">'
        f'<div style="display:flex; align-items:center; gap:12px;">'
        f'<div style="background:var(--gold); color:var(--navy); padding:5px 10px; border-radius:8px; font-weight:800; font-family:\'Playfair Display\';">B</div>'
        f'<div style="color:white; font-weight:700; font-size:1.2rem;">{st.session_state["selected_bank"] or "BankAI"}</div>'
        f'</div>'
        f'</div',
        unsafe_allow_html=True
    )
    if st.button(theme_text, key="theme_toggle_hidden", help="Toggle Theme"):
        toggle_theme()

# ──────────────────────────────────────────────────────────────
# PAGES
# ──────────────────────────────────────────────────────────────
def page_landing():
    render_sidebar()
    st.markdown(
        f"""
        <div class="hero-section">
            <h1 class="hero-title">Your Intelligent Banking Assistant</h1>
            <p class="hero-sub">Powered by AI. Built for clarity.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    _, c1, c2, _ = st.columns([1, 1.5, 1.5, 1])
    with c1:
        st.markdown('<div class="btn-gold">', unsafe_allow_html=True)
        if st.button("Get Started", use_container_width=True):
            go("signup")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="btn-navy-outline">', unsafe_allow_html=True)
        if st.button("Try as Guest", use_container_width=True):
            go("bank_select")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown('<div class="feature-card"><h3>AI Powered</h3><p>Instant answers to any banking query using advanced language models.</p></div>', unsafe_allow_html=True)
    with f2:
        st.markdown('<div class="feature-card"><h3>Multi Language</h3><p>Chat naturally in English, Hindi, Tamil, Telugu, and more.</p></div>', unsafe_allow_html=True)
    with f3:
        st.markdown('<div class="feature-card"><h3>Branch Locator</h3><p>Find nearby ATMs and branches with high precision Google Maps links.</p></div>', unsafe_allow_html=True)

def page_signup_login():
    render_sidebar()
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown(
            f"""
            <div style="background: white; padding: 40px; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); border-top: 4px solid var(--gold); max-width: 420px; margin: 0 auto;">
                <div style="text-align:center; margin-bottom: 30px;">
                    <h2 style="color: var(--navy); margin-top: 10px;">Welcome</h2>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            with st.form("login_form"):
                em = st.text_input("Email Address", placeholder="name@company.com")
                pw = st.text_input("Password", type="password", placeholder="••••••••")
                if st.form_submit_button("Sign In", use_container_width=True):
                    user = repositories.verify_user(em, pw)
                    if user:
                        st.session_state["user"] = user
                        st.session_state["thread_id"] = f"user-{user['user_id']}-{uuid.uuid4().hex[:8]}"
                        go("bank_select")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
            
        with tab2:
            with st.form("signup_form"):
                fn = st.text_input("Full Name", placeholder="John Doe")
                em = st.text_input("Email Address", placeholder="name@company.com")
                ph = st.text_input("Phone Number", placeholder="+91 XXXXX XXXXX")
                pw = st.text_input("Create Password", type="password", placeholder="••••••••")
                if st.form_submit_button("Create Account", use_container_width=True):
                    if fn and em and ph and len(pw) >= 6:
                        try:
                            repositories.create_user(fn, em, ph, pw)
                            user = repositories.verify_user(em, pw)
                            if user:
                                st.session_state["user"] = user
                                st.session_state["thread_id"] = f"user-{user['user_id']}-{uuid.uuid4().hex[:8]}"
                                go("bank_select")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.error("Please fill all fields (Password min 6 chars)")

        if st.button("Continue as Guest", use_container_width=True):
            go("bank_select")
            st.rerun()

def page_bank_select():
    render_sidebar()
    st.markdown('<h1 style="text-align:center; color: var(--navy); margin-bottom: 10px;">Select Your Bank</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color: var(--text-muted); margin-bottom: 40px;">Choose your bank to get personalized assistance</p>', unsafe_allow_html=True)
    
    for i in range(0, len(BANKS), 4):
        cols = st.columns(4)
        for j in range(4):
            if i + j < len(BANKS):
                bank = BANKS[i + j]
                with cols[j]:
                    is_selected = st.session_state["selected_bank"] == bank["name"]
                    card_style = "background: var(--gold); color: var(--navy);" if is_selected else ""
                    st.markdown(
                        f"""
                        <div class="bank-card-new" style="{card_style}">
                            <div style="font-weight: 800; font-size: 1.2rem;">{bank['short']}</div>
                            <div style="font-size: 0.8rem; opacity: 0.8;">{bank['name']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    if st.button(f"Select {bank['short']}", key=f"btn_{bank['short']}", use_container_width=True):
                        st.session_state["selected_bank"] = bank["name"]
                        go("chat")
                        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Home", use_container_width=True):
        go("landing")
        st.rerun()

def page_dashboard():
    render_top_bar()
    user = st.session_state["user"]
    if not user:
        go("login")
        st.rerun()
        return
    st.markdown(f'<h2 style="text-align:center;margin:2rem 0;">Hello, {user["full_name"]}</h2>', unsafe_allow_html=True)
    if st.button("Go to Chat", use_container_width=True):
         go("chat" if st.session_state["selected_bank"] else "bank_select")
         st.rerun()

def page_chat():
    bank = st.session_state["selected_bank"]
    if not bank:
        go("bank_select")
        st.rerun()
        return
    
    render_top_bar()
    
    # Custom Chat Layout
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    for i, (role, text, ts) in enumerate(st.session_state["chat_history"]):
        if role == "user":
            st.markdown(
                f"""
                <div class="bubble-row user-row">
                    <div class="chat-bubble user-bubble">
                        {text}
                        <div class="timestamp" style="color: rgba(10, 22, 40, 0.6);">{ts}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            badge = '<div class="ai-badge">AI</div>' if i == 0 or st.session_state["chat_history"][i-1][0] == "user" else ""
            st.markdown(
                f"""
                <div class="bubble-row ai-row">
                    <div class="chat-bubble ai-bubble">
                        {badge}
                        <div>{text}</div>
                        <div class="timestamp">{ts}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    prompt = st.chat_input("Ask anything about banking...")
    if prompt:
        now = time.strftime("%I:%M %p")
        st.session_state["chat_history"].append(("user", prompt, now))
        st.rerun()

    # Handle AI Response
    if st.session_state["chat_history"] and st.session_state["chat_history"][-1][0] == "user":
        with st.markdown('<div class="dot-typing"></div>', unsafe_allow_html=True):
            uid = st.session_state["user"]["user_id"] if st.session_state["user"] else 0
            tid = st.session_state["thread_id"] or "guest"
            lang = st.session_state.get("language", "English")
            try:
                res = run_graph(uid, st.session_state["chat_history"][-1][1], tid, bank, language=lang)
                reply = res["reply"]
                st.session_state["thread_id"] = res["thread_id"]
            except Exception as e:
                reply = f"System Error: {str(e)}"
            
            st.session_state["chat_history"].append(("assistant", reply, time.strftime("%I:%M %p")))
            st.rerun()

# Router
PAGES = {
    "landing": page_landing,
    "signup": page_signup_login,
    "login": page_signup_login,
    "dashboard": page_dashboard,
    "bank_select": page_bank_select,
    "chat": page_chat
}

PAGES.get(st.session_state["page"], page_landing)()
