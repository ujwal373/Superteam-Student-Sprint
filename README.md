# 🚀 Superteam Student Sprint

[![Streamlit App](https://img.shields.io/badge/Streamlit-Live%20App-brightgreen?logo=streamlit)](https://superteam-student-sprint.streamlit.app/)

A gamified onboarding platform to help Irish university students join **Superteam Ireland** and explore the **Solana ecosystem**.  
Built with **Streamlit + OpenAI + Supabase** (with SQLite fallback for local dev).

---

## 🌐 Live Demo
👉 [superteam-student-sprint.streamlit.app](https://superteam-student-sprint.streamlit.app/)

---

## 📖 Overview
This sprint is designed to be **completed in ~20 minutes**:

1. **Profile** — Fill in your name, university, wallet, and social handles.  
2. **Track** — Choose your focus: `AI/Data`, `Dev`, `Design`, or `Growth`.  
3. **Quests** — Complete **3 micro-quests**:  
   - ✅ Join the Telegram group  
   - ✅ Follow on X (Twitter)  
   - ✅ AI-generated track-specific quest  
4. **Submit Proof** — Upload screenshots or text for review.  
5. **Approval** — Admins review → you’re onboarded to Superteam Ireland 🎉  

Admins can:
- Approve/reject submissions  
- Export **CSV reports** (users + proofs)  
- Track live stats  

---

## ✨ Features
- 🧭 Personalized tracks & micro-quests  
- 🤖 OpenAI-powered adaptive quest generation  
- 📦 Supabase backend (users, submissions, events) with Storage for uploads  
- 🛡️ Admin portal with approval & CSV export  
- 📊 Recap & Stats page for bounty submissions  
- 🌐 Integrated links to [Superteam Ireland LinkedIn](https://www.linkedin.com/company/superteam-ireland/posts/?feedView=all&viewAsMember=true) and [Superteam Luma events](https://lu.ma/SuperteamIE)  

---

## 🛠️ Tech Stack
- **Frontend:** [Streamlit](https://streamlit.io)  
- **AI Agent:** [OpenAI GPT-4o-mini](https://platform.openai.com/)  
- **Database:** [Supabase](https://supabase.com) (Postgres + Storage)  
- **Auth:** Password-protected Admin portal  
- **Local Dev:** Fallback SQLite persistence  

---

## 🚦 Local Development

Clone & run locally:

```bash
git clone https://github.com/ujwal373/superteam-student-sprint.git
cd superteam-student-sprint
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env        # fill in your keys
streamlit run Home.py
```

---

## 🔐 Secrets

Configure these in .env (local) or Streamlit Cloud → Settings → Secrets:

```bash
# === OpenAI ===
OPENAI_API_KEY = "sk-..."
OPENAI_MODEL = "gpt-4o-mini"

# === Admin ===
ADMIN_PASS = "changeme"

# === Supabase ===
USE_SUPABASE = "true"
SUPABASE_URL = "https://<project>.supabase.co"
SUPABASE_SERVICE_KEY = "<service-role-key>"
SUPABASE_BUCKET = "proofs"

# === App Links ===
SUPERTEAM_TELEGRAM = "https://t.me/SuperteamIreland"
SUPERTEAM_X_HANDLE = "@SuperteamIE"

```
---

## 👨‍💻 Author
**Ujwal Mojidra**
- 🎓 MSc in Data & Computational Science, University College Dublin
- 🔬 Skilled in Data Science, AI/ML, and Agentic AI frameworks (LangChain, LangServe, AutoGen)
- 🌐 Passionate about Web3, Solana, and building student-driven communities

- [GitHub](https://github.com/ujwal373?utm_source=chatgpt.com)
- [LinkedIn](https://www.linkedin.com/in/ujwal-mojidra-28098723a/?utm_source=chatgpt.com)
- [Google-Cloud-Profile](https://www.cloudskillsboost.google/public_profiles/23ec8bf9-3116-4ea3-865a-d0811a56a26e?utm_source=chatgpt.com)

---

MIT License

Copyright (c) 2025 Ujwal Mojidra

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished.

[Full MIT license text continues…]



