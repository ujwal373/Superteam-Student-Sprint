import os
import streamlit as st
from datetime import datetime

# Hide this page in the admin deployment
if os.getenv("APP_MODE") == "admin":
    st.stop()

from src.db import (
    db_init, get_user, get_or_create_track, set_track,
    save_submission, get_submissions
)
from src.agent import make_micro_quests

st.title("🧭 Quests")
db_init()

# --- guard: need a user_id in session ---
user_id = st.session_state.get("user_id")
if not user_id:
    st.warning("Please complete your **Profile** first.")
    st.stop()

user = get_user(user_id)
st.write(f"Hello **{user.get('name','')}** from **{user.get('uni','')}**!")

# --- track & quests ---
track = get_or_create_track(user_id)
st.success(f"Your track: **{track}**")
quests = make_micro_quests(track)

# --- load prior submissions once ---
existing = {s["quest_idx"]: s for s in get_submissions(user_id)}

# remember which quest was just submitted (for success banner)
if "just_submitted" not in st.session_state:
    st.session_state.just_submitted = {}  # {quest_idx: True}

st.divider()
st.subheader("Your 3 Micro-Quests")

for i, q in enumerate(quests, start=1):
    with st.expander(f"Q{i}: {q['title']}", expanded=(i == 1)):
        st.markdown(q["instructions"])

        # Unique keys per user+quest so Streamlit doesn't mix state
        txt_key  = f"proof_text_u{user_id}_q{i}"
        file_key = f"proof_img_u{user_id}_q{i}"
        btn_key  = f"submit_u{user_id}_q{i}"

        proof_text = st.text_area("Paste link / handle / short note", key=txt_key)
        proof_img  = st.file_uploader(
            "Upload screenshot (optional)",
            type=["png", "jpg", "jpeg"],
            key=file_key
        )
        file_bytes = proof_img.read() if proof_img else None

        already = i in existing
        # Optional: block duplicate submits from UI side
        disabled = already

        if st.button(f"Submit Q{i}", key=btn_key, disabled=disabled):
            text_clean = (proof_text or "").strip()

            # basic validation: require either text or file
            if not text_clean and not file_bytes:
                st.warning("Please paste a link/handle or upload a screenshot.")
            else:
                save_submission(
                    user_id=user_id,
                    quest_idx=i,
                    title=q["title"],
                    track=track,
                    text=text_clean,
                    file=file_bytes,  # bytes (not UploadedFile)
                )
                st.session_state.just_submitted[i] = True
                st.rerun()

        # Messaging logic
        if st.session_state.just_submitted.get(i):
            st.success(f"Q{i} submitted!")
        elif already:
            st.info(f"Q{i} already submitted — **{existing[i]['status']}**.")

st.divider()
st.subheader("Your Submissions")
subs = get_submissions(user_id)
if not subs:
    st.caption("Nothing yet. Submit above.")
else:
    for s in subs:
        st.write(f"• Q{s['quest_idx']}: {s['title']} — **{s['status']}**")
