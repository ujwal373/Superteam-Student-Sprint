import os, streamlit as st
if os.getenv("APP_MODE") == "admin":
    st.stop()  # hide this page in the admin deployment


import streamlit as st
from src.db import db_init, get_user, save_event, get_or_create_track, save_submission, get_submissions
from src.agent import route_track, make_micro_quests
from datetime import datetime

st.title("🧭 Quests")
db = db_init()

user_id = st.session_state.get('user_id')
if not user_id:
    st.warning("Please complete your **Profile** first.")
    st.stop()

user = get_user(user_id)
st.write(f"Hello **{user.get('name','')}** from **{user.get('uni','')}**!")

from src.db import db_init, get_user, save_event, get_or_create_track, set_track, save_submission, get_submissions
from src.agent import route_track, make_micro_quests

track = get_or_create_track(user_id)  
st.success(f"Your track: **{track}**")
quests = make_micro_quests(track)


st.divider()
st.subheader("Your 3 Micro-Quests")
for i, q in enumerate(quests, start=1):
    with st.expander(f"Q{i}: {q['title']}", expanded=(i == 1)):
        st.markdown(q["instructions"])
        proof_text = st.text_area(
            "Paste link / handle / short note",
            key=f"proof_text_{i}",
        )
        proof_img = st.file_uploader("Upload screenshot (optional)", type=["png","jpg","jpeg"], key=f"img_{i}")
        file_bytes = proof_img.read() if proof_img else None

        if st.button(f"Submit Q{i}", key=f"submit_{i}"):
            save_submission(
            user_id=user_id,
            quest_idx=i,
            title=q["title"],
            track=track,
            text=proof_text.strip(),
            file=file_bytes,              # bytes (not UploadedFile)
            )
        st.success(f"Q{i} submitted!")

            #st.rerun()

st.divider()
st.subheader("Your Submissions")
subs = get_submissions(user_id)
if not subs:
    st.caption("Nothing yet. Submit above.")
else:
    for s in subs:
        st.write(f"• Q{s['quest_idx']}: {s['title']} — **{s['status']}**")


