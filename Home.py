# Home.py
import os
import streamlit as st
from dotenv import load_dotenv
load_dotenv()
st.set_page_config(page_title="Home — Superteam Student Sprint", page_icon="🏠", layout="wide")

# --- Imports from your app (for live stats) ---
try:
    from src.db import db_init, recap_stats
    db_init()
    stats = recap_stats()
except Exception:
    stats = {"students": 0, "subs": 0, "approved": 0}

# --- HERO ---
st.markdown("# 🚀 Superteam Student Sprint")
st.markdown(
    """
Welcome! This sprint helps Irish university students join **Superteam Ireland** and the **Solana** developer ecosystem.
You’ll pick a track and complete **3 micro-quests** — fast, fun, and practical.
"""
)

# --- Quick CTAs (uses Streamlit's built-in page linking; adjust names if your files differ) ---
cta1, cta2, cta3 = st.columns([1,1,1])
with cta1:
    st.page_link("pages/1_Profile.py", label="Start → Profile")
with cta2:
    st.page_link("pages/2_Quests.py", label="Go to Quests")
#with cta3:
#   st.page_link("pages/3_Admin.py", label="Admin (password)")

st.info("Tip: Keep your **Telegram** & **X (Twitter)** handles handy for quick verification.")

st.divider()

# --- Live Snapshot ---
st.subheader("📈 Live Snapshot")
c1, c2, c3 = st.columns(3)
c1.metric("New Students", stats.get("students", 0))
c2.metric("Submissions", stats.get("subs", 0))
c3.metric("Approved Proofs", stats.get("approved", 0))

st.divider()

import streamlit.components.v1 as components

st.subheader("🔗 Superteam IE")

# Let you tune the frame height live (persists during session)
default_h = st.session_state.get("bento_height", 1100)
#h = st.slider("Embed height", 600, 2200, default_h, 50, help="Adjust if the page is clipped")
st.session_state["bento_height"] = default_h

# Try embed via raw HTML so we can force scrolling
bento_url = "https://bento.me/superteamie"
components.html(
    f"""
    <iframe
      src="{bento_url}"
      style="width:100%; height:{default_h}px; border:0;"
      loading="lazy"
      allow="clipboard-write *; autoplay *"
      scrolling="yes"
    ></iframe>
    """,
    height=default_h,
)

# Fallback / convenience
#st.link_button("Open Bento in new tab", bento_url)

st.divider()

# --- Why Solana + Web3 for students? ---
st.subheader("🌐 Why Solana + Web3 for Students?")
st.markdown(
    """
- **Fast & low-cost**: Solana’s high throughput and low fees make it ideal for student projects and rapid prototyping.  
- **Real-world bounties**: Learn by doing — ship tasks, submit proofs, and get paid.  
- **Network effects**: Ireland’s Solana builders are growing fast through Superteam IE meetups and online sprints.  
- **Career runway**: On-chain work is public and portable — great for portfolios, internships, and founding teams.
"""
)

st.divider()

# --- How it works ---
st.subheader("🧭 How This Sprint Works")
st.markdown(
    """
1. **Complete your Profile** — tell us your university and handles.  
2. **Pick your Track** — AI/Data, Dev, Design, or Growth (you can choose manually).  
3. **Do the 3 Micro-Quests** — two verification tasks + one track-specific task.  
4. **Get Reviewed** — Admin approves/rejects your proofs.  
5. **You’re In** — Join the community, stay for bounties & events.
"""
)

# --- Quick Links Row ---
st.markdown("### 🔗 Quick Links")
ql1, ql2, ql3, ql4 = st.columns([1,1,1,1])
with ql1:
    st.page_link("pages/1_Profile.py", label="Profile")
with ql2:
    st.page_link("pages/2_Quests.py", label="Quests")
with ql3:
    st.page_link("pages/4_About_&_Stats.py", label="About & Stats")
#with ql4:
    #st.page_link("pages/3_Admin.py", label="Admin")

st.divider()

# --- Tech stack footer ---
st.caption(
    "Built with Streamlit • OpenAI (agentic micro-quests) • Supabase (Postgres + Storage). "
    "Falls back to SQLite locally. Made for Superteam Ireland students."
)
