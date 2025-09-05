import os, json
from openai import OpenAI
from .db import set_track

TRACKS = ["AI/Data", "Dev", "Design", "Growth"]

def _client():
    key = os.getenv("OPENAI_API_KEY")
    return OpenAI(api_key=key) if key else None

def route_track(profile: dict) -> str:
    """Pick one track; persist on the user record."""
    choice = "Growth"
    client = _client()
    if not client:
        if profile.get("id"): set_track(profile["id"], choice)
        return choice

    prompt = (
        f"Return JSON with a single key 'track' whose value is exactly one of "
        f"{TRACKS}. Use the student's profile:\n{json.dumps(profile)}"
    )
    try:
        r = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "Respond with valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        data = json.loads(r.choices[0].message.content or "{}")
        t = (data.get("track") or "").strip()
        if t in TRACKS:
            choice = t
    except Exception as e:
        print("router_error:", e)

    if profile.get("id"):
        set_track(profile["id"], choice)
    return choice

def make_micro_quests(track: str):
    """Two fixed quests + one AI-generated micro-quest with solid fallbacks."""
    quests = [
        {
            "title": "Join Superteam Ireland Telegram",
            "instructions": f"Join {os.getenv('SUPERTEAM_TELEGRAM','https://t.me/+f-_iNMLV4FNiMmJk')} and paste your @username. Upload a screenshot of the joined group."
        },
        {
            "title": "Follow @superteamIE on X",
            "instructions": f"Follow {os.getenv('SUPERTEAM_X_HANDLE','@superteamIE')} and paste your handle. Upload a screenshot of the follow."
        },
    ]

    hardcoded = {
        "AI/Data": {
            "title": "Mini Data Viz",
            "instructions": "Download a small Solana dataset (e.g., token prices on devnet) and create a simple chart. Upload PNG or share a Colab/Gist link."
        },
        "Dev": {
            "title": "Hello Solana Tx",
            "instructions": "Send a devnet transaction or run a Hello-Solana starter. Paste the tx hash or upload a screenshot of the confirmed tx."
        },
        "Design": {
            "title": "Bounty Card Mockup",
            "instructions": "Design a quick poster/banner or bounty card for a student sprint. Upload a PNG/JPG of your mock."
        },
        "Growth": {
            "title": "Tweet Hooks",
            "instructions": "Write 3 tweet ideas to promote Superteam Ireland onboarding. Paste the text or share a public doc link."
        },
    }
    default_fallback = {"title": "Share Your Why",
                        "instructions": "Post a short note (or tweet draft) on why you’re joining Superteam Ireland and paste the link or text here."}

    client = _client()
    if not client:
        quests.append(hardcoded.get(track, default_fallback))
        return quests

    prompt = (
        f"Create ONE short micro-quest for the '{track}' track. It must take <10 minutes and yield a shareable artifact "
        f"(text link, small image, tx hash, or gist). Return JSON: {{\"title\":\"...\",\"instructions\":\"...\"}}"
    )
    try:
        r = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "Respond with valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            response_format={"type": "json_object"},
        )
        third = json.loads(r.choices[0].message.content or "{}")
        title, instr = third.get("title"), third.get("instructions")
        if title and instr:
            quests.append({"title": title, "instructions": instr})
        else:
            quests.append(hardcoded.get(track, default_fallback))
    except Exception as e:
        print("quest_error:", e)
        quests.append(hardcoded.get(track, default_fallback))

    return quests
