import os, streamlit as st
if os.getenv("APP_MODE") == "admin":
    st.stop()  # hide this page in the admin deployment


import streamlit as st
import os, socket
from src.db import db_init, recap_stats, list_social_posts

st.title("📊 About & Stats")
db_init()

# --- About the Developer ---
st.header("👨‍💻 About the Developer")

st.markdown("""
Hi! I'm **Ujwal Mojidra**, a Data & AI enthusiast who recently completed my **Master’s in Data and Computational Science at University College Dublin (UCD)**.  

I have hands-on experience across **Data Science, AI, Web3, and Cloud**. Currently, I’m exploring **Agentic AI frameworks** such as **LangChain, LangServe, LlamaIndex, AutoGen, and CrewAI**, with a strong focus on how these can power scalable, real-world applications.  

Alongside this project, I’ve worked on:
- 🚀 **Future Viability Index (FVI):** a sustainability-focused analytics framework during my internship at Darwin & Goliath. [▶️ Demo](https://www.youtube.com/watch?v=7mNofwNqJvU)  
- 🎮 **ExcelGame (Jan 2025):** an interactive game built entirely in Excel. [Play here](https://excelgame.streamlit.app/?)  
- 🔎 **Flowchart Decoder with AI (Aug 2025):** a single-agent tool for interpreting and simplifying flowcharts (currently being stabilized).  
- 📊 Multiple academic + industry projects in **machine learning, network analysis, and Bayesian statistics**.  

I am passionate about building **data-driven products** that bridge **AI, sustainability, and Web3 ecosystems**.
""")

# --- Links ---
st.subheader("🌐 Connect with Me")
st.markdown("""
- [![GitHub](https://img.icons8.com/material-outlined/24/000000/github.png) **GitHub**](https://github.com/ujwal373)  
- [![LinkedIn](https://img.icons8.com/ios-filled/24/0A66C2/linkedin.png) **LinkedIn**](https://www.linkedin.com/in/ujwal-mojidra-28098723a/)  
- [![Google Cloud](https://img.icons8.com/color/24/000000/google-cloud.png) **Google Cloud Profile**](https://www.cloudskillsboost.google/public_profiles/23ec8bf9-3116-4ea3-865a-d0811a56a26e)  
""")

# --- Skills ---
st.subheader("🛠️ Technical Skills")
st.markdown("""
| ![Python](https://img.icons8.com/color/48/000000/python.png) Python | ![R](https://img.icons8.com/external-becris-flat-becris/48/000000/external-r-data-science-becris-flat-becris.png) R Programming | ![SQL](https://img.icons8.com/ios-filled/48/000000/sql.png) SQL | ![Excel](https://img.icons8.com/color/48/000000/ms-excel.png) Excel & Spreadsheets |
|---|---|---|---|
| ![SAS](https://img.icons8.com/fluency/48/statistics.png) SAS | ![AWS](https://img.icons8.com/color/48/000000/amazon-web-services.png) AWS | ![Google Cloud](https://img.icons8.com/color/48/000000/google-cloud.png) Google Cloud | ![GitHub](https://img.icons8.com/material-outlined/48/000000/github.png) GitHub |
| ![Power BI](https://img.icons8.com/color/48/000000/power-bi.png) Power BI | ![Tableau](https://img.icons8.com/color/48/000000/tableau-software.png) Tableau | ![n8n](https://img.icons8.com/fluency/48/workflow.png) n8n | ![HTML CSS](https://img.icons8.com/color/48/000000/html-5.png) HTML & CSS |
""")

st.divider()

# --- Stats section ---
stats = recap_stats()
st.header("📈 Onboarding Stats")
c1, c2, c3 = st.columns(3)
c1.metric("New students", stats["students"])
c2.metric("Submissions", stats["subs"])
c3.metric("Approved proofs", stats["approved"])

st.divider()

st.subheader("Summary")
st.write(f"""
We launched the Superteam Student Sprint to onboard Irish university students.
The system routed participants into tracks and assigned 3 micro‑quests, including community join + X follow.
We onboarded **{stats['students']} students**, with **{stats['approved']} approved** proofs.
""")


