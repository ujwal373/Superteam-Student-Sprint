# src/db_supabase.py
import os, time, csv
from typing import Optional, Dict
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
STORAGE_BUCKET = os.getenv("SUPABASE_BUCKET", "proofs")

_sb: Optional[Client] = None
def sb() -> Client:
    global _sb
    if _sb is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise RuntimeError("Supabase credentials missing")
        _sb = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _sb

# --- required by src/db.py ---
def db_init() -> bool:
    # nothing to create here; tables are managed in Supabase
    return True

def get_user_by_handle(tg_handle: Optional[str], x_handle: Optional[str]) -> Optional[Dict]:
    if tg_handle:
        r = sb().table("users").select("id").eq("telegram", tg_handle).execute()
        if r.data: return {"id": r.data[0]["id"]}
    if x_handle:
        r = sb().table("users").select("id").eq("x", x_handle).execute()
        if r.data: return {"id": r.data[0]["id"]}
    return None

# --- users ---
def upsert_user(name, uni, telegram, x, wallet) -> str:
    if telegram:
        r = sb().table("users").select("id").eq("telegram", telegram).execute()
        if r.data:
            uid = r.data[0]["id"]
            sb().table("users").update({"name":name,"uni":uni,"wallet":wallet}).eq("id", uid).execute()
            return uid
    if x:
        r = sb().table("users").select("id").eq("x", x).execute()
        if r.data:
            uid = r.data[0]["id"]
            sb().table("users").update({"name":name,"uni":uni,"wallet":wallet}).eq("id", uid).execute()
            return uid
    r = sb().table("users").insert({"name":name,"uni":uni,"telegram":telegram,"x":x,"wallet":wallet}).execute()
    return r.data[0]["id"]

def get_user(uid: str) -> Dict:
    r = sb().table("users").select("*").eq("id", uid).single().execute()
    return r.data or {}

def get_or_create_track(user_id) -> Optional[str]:
    r = sb().table("users").select("track").eq("id", user_id).single().execute()
    return r.data.get("track") if r.data else None

def set_track(user_id, track):
    sb().table("users").update({"track": track}).eq("id", user_id).execute()

# --- events ---
def save_event(user_id, type, meta):
    sb().table("events").insert({"user_id": user_id, "type": type, "meta_json": meta}).execute()

# --- storage helper (optional preview) ---
def get_signed_url(path: str, seconds: int = 3600) -> str:
    return sb().storage.from_(STORAGE_BUCKET).create_signed_url(path, seconds)["signedURL"]

def _upload_bytes(folder: str, b: bytes, content_type: str = "image/png") -> str:
    # stable timestamp filename
    key = f"{folder}/{int(time.time()*1000)}.png"
    # IMPORTANT: all header values must be strings
    sb().storage.from_(STORAGE_BUCKET).upload(
        key,
        b,
        {
            "content-type": content_type,
            "x-upsert": "true",          # string, not bool
            "cache-control": "3600"      # optional but string
        },
    )
    return key

# --- submissions ---
def save_submission(user_id, quest_idx, title, track, text, file) -> str:
    file_path = _upload_bytes(f"user_{user_id}", file) if file else None
    r = sb().table("submissions").insert({
        "user_id": user_id,
        "quest_idx": quest_idx,
        "title": title,
        "track": track,
        "text": text,
        "file_path": file_path,
        "status": "pending",
    }).execute()
    return r.data[0]["id"]

def get_submissions(user_id):
    r = sb().table("submissions").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    return r.data or []

def admin_list_subs(status_filter=None):
    q = sb().table("submissions").select("*").order("created_at", desc=True)
    if status_filter:
        q = q.eq("status", status_filter)
    return q.execute().data or []

def admin_set_status(sub_id, status):
    sb().table("submissions").update({"status": status}).eq("id", sub_id).execute()

# --- CSV exports ---
def export_csv() -> str:
    # submission-level export
    subs = sb().table("submissions").select(
        "quest_idx,title,status,created_at,users!inner(name,uni,telegram,x)"
    ).execute().data
    flat = []
    for s in subs:
        u = s["users"]
        flat.append([u["name"], u["uni"], u["telegram"], u["x"], s["quest_idx"], s["title"], s["status"], s["created_at"]])
    path = "onboarding_proof.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["name","uni","telegram","x","quest_idx","title","status","created_at"])
        w.writerows(flat)
    return path

def export_users_csv() -> str:
    import csv
    # 1) fetch users & all submissions
    users = sb().table("users").select("*").order("created_at").execute().data
    subs  = sb().table("submissions").select("user_id,quest_idx,status,created_at").execute().data

    # 2) priority helper
    def better(cur, new):
        order = {"approved": 3, "rejected": 2, "pending": 1, None: 0}
        return new if order.get(new, 0) >= order.get(cur, 0) else cur

    # 3) fold subs by user and quest_idx
    from collections import defaultdict
    agg = defaultdict(lambda: {"joined_telegram": None, "followed_x": None, "microquest": None})
    for s in subs:
        uid = s["user_id"]
        stt = (s.get("status") or "pending").strip().lower()
        q   = int(s.get("quest_idx") or 0)
        if q == 1:
            agg[uid]["joined_telegram"] = better(agg[uid]["joined_telegram"], stt)
        elif q == 2:
            agg[uid]["followed_x"] = better(agg[uid]["followed_x"], stt)
        elif q == 3:
            agg[uid]["microquest"] = better(agg[uid]["microquest"], stt)

    # 4) build rows
    rows = []
    for u in users:
        m = agg[u["id"]]
        rows.append([
            u.get("name"), u.get("uni"), u.get("telegram"), u.get("x"), u.get("track"),
            m["joined_telegram"] or "pending",
            m["followed_x"] or "pending",
            m["microquest"] or "pending",
        ])

    # 5) write CSV
    path = "onboarding_users.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["name","uni","telegram","x","track","joined_telegram","followed_x","microquest"])
        w.writerows(rows)
    return path

# --- stats ---
def recap_stats():
    users = sb().table("users").select("id", count="exact").execute().count or 0
    subs  = sb().table("submissions").select("id", count="exact").execute().count or 0
    appr  = sb().table("submissions").select("id", count="exact").eq("status","approved").execute().count or 0
    return {"students": users, "subs": subs, "approved": appr}

def list_social_posts():
    r = sb().table("submissions").select("text").ilike("text", "http%").execute()
    return [x["text"] for x in (r.data or [])]
