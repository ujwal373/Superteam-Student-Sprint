# admin_app.py
import os, streamlit as st
# Hide the auto-generated "Pages" nav so only Admin UI shows
st.markdown("""
<style>
/* Hide the entire pages navigation block */
div[data-testid="stSidebarNav"] { display: none !important; }

/* Optional: also hide the "Pages" heading if present */
section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
  display: none !important;
}

/* Optional: keep the sidebar itself (for future widgets) but slim it down */
/* section[data-testid="stSidebar"] { width: 300px; } */
</style>
""", unsafe_allow_html=True)


from src.db import db_init, admin_list_subs, admin_set_status, export_users_csv

st.set_page_config(page_title="Admin — Superteam Sprint", page_icon="🛡️", layout="wide")
st.title("🛡️ Admin")

db_init()

pw = st.text_input("Enter admin password", type="password")
if pw != os.getenv("ADMIN_PASS", "superteamsolana"):
    st.stop()

st.success("Admin unlocked")

try:
    subs = admin_list_subs(status_filter="pending")
except Exception as e:
    st.error(f"Backend error while listing submissions: {e}")
    subs = []

st.write(f"Pending submissions: {len(subs)}")
for s in subs:
    with st.expander(f"User {s.get('user_id')} — Q{s.get('quest_idx')} {s.get('title')} ({s.get('track')})"):
        st.write(f"Note: {s.get('text') or ''}")
        if s.get("file_path"):
            try:
                from src.db_supabase import get_signed_url
                st.image(get_signed_url(s["file_path"]), use_container_width=True)
            except Exception:
                st.write("Uploaded file:", s["file_path"])
        c1, c2 = st.columns(2)
        if c1.button("Approve", key=f"a_{s['id']}"):
            try:
                admin_set_status(s["id"], "approved"); st.rerun()
            except Exception as e:
                st.error(f"Approve failed: {e}")
        if c2.button("Reject", key=f"r_{s['id']}"):
            try:
                admin_set_status(s["id"], "rejected"); st.rerun()
            except Exception as e:
                st.error(f"Reject failed: {e}")

st.divider()
try:
    csv_path = export_users_csv()
    with open(csv_path, "rb") as f:
        st.download_button(
            "Download USERS CSV (one row per student)",
            data=f, file_name="onboarding_users.csv", mime="text/csv",
        )
except Exception as e:
    st.error(f"Export failed: {e}")

import os, streamlit as st
st.caption(f"[Admin] USE_SUPABASE={os.getenv('USE_SUPABASE')} • URL set={bool(os.getenv('SUPABASE_URL'))} • SERVICE={bool(os.getenv('SUPABASE_SERVICE_KEY'))}")
