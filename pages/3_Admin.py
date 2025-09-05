import os, io
import streamlit as st
from src.db import db_init, admin_list_subs, admin_set_status, export_users_csv

st.title("🛡️ Admin")
db_init()

pw = st.text_input("Enter admin password", type="password")
if pw != os.getenv("ADMIN_PASS", "changeme"):
    st.stop()

st.success("Admin unlocked")

# Review queue (keep this if you still approve proofs here)
subs = admin_list_subs(status_filter="pending")
st.write(f"Pending submissions: {len(subs)}")
for s in subs:
    with st.expander(f"User {s['user_id']} — Q{s['quest_idx']} {s['title']} ({s['track']})"):
        st.write(f"Note: {s['text'] or ''}")
        if s.get("file_path"):
            st.image(s["file_path"], caption="Uploaded proof", use_container_width=True)
        c1, c2 = st.columns(2)
        if c1.button("Approve", key=f"a_{s['id']}"):
            admin_set_status(s["id"], "approved"); st.rerun()
        if c2.button("Reject", key=f"r_{s['id']}"):
            admin_set_status(s["id"], "rejected"); st.rerun()

st.divider()

csv_path = export_users_csv()
with open(csv_path, "rb") as f:
    st.download_button(
        "Download USERS CSV",
        data=f,
        file_name="onboarding_users.csv",
        mime="text/csv",
    )
