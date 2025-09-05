from src.db import db_init, upsert_user, set_track
import streamlit as st

st.title("👤 Profile")
db_init()
with st.form("profile"):
    name = st.text_input("Full Name")
    uni  = st.text_input("University / College")
    tg   = st.text_input("Telegram username (without @)")
    xh   = st.text_input("X (Twitter) handle (without @)")
    wallet = st.text_input("Phantom wallet (optional)")
    track_choice = st.selectbox("Which track fits you best?",
        ["AI/Data","Dev","Design","Growth"], index=1)
    #use_ai = st.checkbox("Suggest a track for me (AI)", value=False)
    submitted = st.form_submit_button("Save Profile")

if submitted:
    if not name or not tg or not xh:
        st.error("Name, Telegram and X handle are required.")
    else:
        uid = upsert_user(name, uni, tg, xh, wallet)
        st.session_state["user_id"] = uid
        # optional AI suggestion
        #if use_ai:
        #    from src.agent import route_track
        #   suggested = route_track({"id": uid, "name": name, "uni": uni, "telegram": tg, "x": xh})
        #  st.info(f"AI suggests: {suggested}")
        set_track(uid, track_choice)  # user’s choice wins
        st.success("Saved! Go to **Quests**.")
