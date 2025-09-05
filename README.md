# Superteam Student Sprint (Streamlit + OpenAI)

A 20‑minute, gamified onboarding that routes students to a track, assigns 3 micro‑quests, verifies joins (Telegram + X), and generates a recap + CSV for bounty proof. Optional NFT badge.

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate   # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
cp .env.example .env  # fill values
streamlit run streamlit_app.py
```
Default DB = SQLite file `sprint.db`. If `SUPABASE_URL` + `SUPABASE_ANON_KEY` present and `USE_SUPABASE=true`, the app switches to Supabase.

## Pages
- **Profile**: capture name, uni, Telegram, X, wallet.
- **Quests**: agent picks a track (AI/Data, Dev, Design, Growth) + generates 3 micro‑quests (incl. join Telegram + follow X). Upload proofs.
- **Admin**: password‑gated approvals, CSV export.
- **Recap**: auto 1–2 paragraph report, counts, gallery, tweet helper.

## KPIs
- 5+ new members with Telegram/X handles.
- At least 1 social post tagging `@SuperteamIE`.
- Unique, repeatable student sprint flow.
```