# src/db.py
# # --- env bootstrap (must be first) ---
import os
from dotenv import load_dotenv, find_dotenv
import sqlite3, json, time, uuid
from typing import Optional, Dict

dotenv_path = find_dotenv(filename=".env", usecwd=True)
load_dotenv(dotenv_path=dotenv_path, override=True)

def env_bool(name: str, default: bool=False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return str(v).strip().lower() in ("1", "true", "yes", "on")

# Optional: debug prints during startup (shows in Streamlit terminal)
print("DB dotenv loaded from:", dotenv_path or "(not found)")
print("DB USE_SUPABASE raw:", repr(os.getenv("USE_SUPABASE")))

# Toggle: use Supabase backend or local SQLite
USE_SUPABASE = os.getenv("USE_SUPABASE", "false").lower() == "true"

if USE_SUPABASE:
    # Use the Supabase implementation ONLY
    from .db_supabase import (
        db_init,
        upsert_user, get_user, get_user_by_handle, get_or_create_track, set_track,
        save_event, save_submission, get_submissions,
        admin_list_subs, admin_set_status,
        export_csv, export_users_csv,
        recap_stats, list_social_posts,
    )

else:
    # ---------------------------
    # SQLite implementation
    # ---------------------------

    DB_PATH = os.getenv("DB_PATH", "sprint.db")
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    def db_conn():
        con = sqlite3.connect(DB_PATH, check_same_thread=False)
        con.execute("PRAGMA foreign_keys = ON;")
        return con

    def _dedupe_users_and_add_indexes(con):
        # 1) find duplicate groups by telegram and by x
        def groups(by_col):
            q = f"""
            SELECT {by_col} AS k, id, created_at
            FROM users WHERE {by_col} IS NOT NULL
            ORDER BY k, created_at DESC
            """
            rows = con.execute(q).fetchall()
            buckets = {}
            for k, uid, ts in rows:
                buckets.setdefault(k, []).append((uid, ts))
            return [v for v in buckets.values() if len(v) > 1]

        # survivor = newest created_at; reassign proofs/events from losers
        for col in ("telegram", "x"):
            for grp in groups(col):
                survivor = grp[0][0]                  # newest first
                losers   = [u for u, _ in grp[1:]]
                for lid in losers:
                    con.execute("UPDATE submissions SET user_id=? WHERE user_id=?", (survivor, lid))
                    con.execute("UPDATE events      SET user_id=? WHERE user_id=?", (survivor, lid))
                    con.execute("DELETE FROM users WHERE id=?", (lid,))
        con.commit()

        # 2) create unique indexes (now that dups are gone)
        con.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_users_telegram ON users(telegram) WHERE telegram IS NOT NULL;")
        con.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_users_x        ON users(x)       WHERE x IS NOT NULL;")
        con.commit()

    def db_init():
        con = db_conn()
        # tables only (no unique indexes here)
        con.executescript("""
        PRAGMA foreign_keys = ON;
        CREATE TABLE IF NOT EXISTS users (
          id TEXT PRIMARY KEY,
          name TEXT, uni TEXT, telegram TEXT, x TEXT, wallet TEXT, track TEXT,
          created_at REAL DEFAULT (strftime('%s','now'))
        );
        CREATE TABLE IF NOT EXISTS submissions (
          id TEXT PRIMARY KEY,
          user_id TEXT, quest_idx INTEGER, title TEXT, track TEXT,
          text TEXT, file_path TEXT, status TEXT,
          created_at REAL DEFAULT (strftime('%s','now')),
          FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS events (
          id TEXT PRIMARY KEY,
          user_id TEXT, type TEXT, meta_json TEXT,
          ts REAL DEFAULT (strftime('%s','now')),
          FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)
        con.commit()
        _dedupe_users_and_add_indexes(con)
        con.close()
        return True

    def upsert_user(name, uni, telegram, x, wallet) -> str:
        con = db_conn()
        row = con.execute(
            "SELECT id FROM users WHERE (telegram IS NOT NULL AND telegram=?) OR (x IS NOT NULL AND x=?)",
            (telegram or None, x or None)
        ).fetchone()
        if row:
            uid = row[0]
            con.execute("UPDATE users SET name=?, uni=?, wallet=? WHERE id=?", (name, uni, wallet, uid))
        else:
            uid = str(uuid.uuid4())
            con.execute(
                "INSERT INTO users (id,name,uni,telegram,x,wallet) VALUES (?,?,?,?,?,?)",
                (uid, name, uni, telegram or None, x or None, wallet)
            )
        con.commit(); con.close()
        return uid

    def get_user(uid: str) -> Dict:
        con = db_conn()
        cur = con.execute("SELECT id,name,uni,telegram,x,wallet,track FROM users WHERE id=?", (uid,))
        row = cur.fetchone(); con.close()
        if not row: return {}
        keys = ["id", "name", "uni", "telegram", "x", "wallet", "track"]
        return dict(zip(keys, row))

    def get_user_by_handle(tg_handle: Optional[str], x_handle: Optional[str]) -> Optional[Dict]:
        con = db_conn()
        if tg_handle:
            r = con.execute("SELECT id FROM users WHERE telegram=?", (tg_handle,)).fetchone()
        elif x_handle:
            r = con.execute("SELECT id FROM users WHERE x=?", (x_handle,)).fetchone()
        else:
            r = None
        con.close()
        return {"id": r[0]} if r else None

    def save_event(user_id, type, meta):
        con = db_conn()
        con.execute("INSERT INTO events (id,user_id,type,meta_json) VALUES (?,?,?,?)",
                    (str(uuid.uuid4()), user_id, type, json.dumps(meta or {})))
        con.commit(); con.close()

    def get_or_create_track(user_id) -> Optional[str]:
        con = db_conn()
        row = con.execute("SELECT track FROM users WHERE id=?", (user_id,)).fetchone()
        con.close()
        return row[0] if row and row[0] else None

    def set_track(user_id, track):
        con = db_conn()
        con.execute("UPDATE users SET track=? WHERE id=?", (track, user_id))
        con.commit(); con.close()

    def _save_file(content: bytes) -> str:
        path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.png")  # default to png
        with open(path, "wb") as f:
            f.write(content)
        return path

    def save_submission(user_id, quest_idx, title, track, text, file) -> str:
        file_path = _save_file(file) if file else None
        sid = str(uuid.uuid4())
        con = db_conn()
        con.execute("""INSERT INTO submissions
          (id,user_id,quest_idx,title,track,text,file_path,status)
          VALUES (?,?,?,?,?,?,?,?)""",
          (sid, user_id, quest_idx, title, track, text, file_path, "pending"))
        con.commit(); con.close()
        return sid

    def get_submissions(user_id):
        con = db_conn()
        cur = con.execute("""SELECT id,user_id,quest_idx,title,track,text,file_path,status
                             FROM submissions WHERE user_id=?
                             ORDER BY created_at DESC""", (user_id,))
        rows = cur.fetchall(); con.close()
        keys = ["id","user_id","quest_idx","title","track","text","file_path","status"]
        return [dict(zip(keys, r)) for r in rows]

    def admin_list_subs(status_filter=None):
        con = db_conn()
        q = "SELECT id,user_id,quest_idx,title,track,text,file_path,status FROM submissions"
        params = ()
        if status_filter:
            q += " WHERE status=?"
            params = (status_filter,)
        q += " ORDER BY created_at DESC"
        cur = con.execute(q, params)
        rows = cur.fetchall(); con.close()
        keys = ["id","user_id","quest_idx","title","track","text","file_path","status"]
        return [dict(zip(keys, r)) for r in rows]

    def admin_set_status(sub_id, status):
        con = db_conn()
        con.execute("UPDATE submissions SET status=? WHERE id=?", (status, sub_id))
        con.commit(); con.close()

    def export_csv() -> str:
        import csv
        path = "onboarding_proof.csv"
        con = db_conn()
        cur = con.execute("""
          SELECT u.name,u.uni,u.telegram,u.x,s.quest_idx,s.title,s.status,s.created_at
          FROM submissions s JOIN users u ON u.id=s.user_id
          ORDER BY s.created_at ASC
        """)
        rows = cur.fetchall(); con.close()
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["name","uni","telegram","x","quest_idx","title","status","created_at"])
            w.writerows(rows)
        return path

    def export_users_csv() -> str:
        import csv
        path = "onboarding_users.csv"
        con = db_conn()
        rows = con.execute("""
        WITH marks AS (
          SELECT user_id,
            MAX(CASE WHEN title LIKE 'Join Superteam%'    THEN status END) AS joined_telegram,
            MAX(CASE WHEN title LIKE 'Follow @Superteam%' THEN status END) AS followed_x,
            MAX(CASE WHEN quest_idx=3                     THEN status END) AS microquest
          FROM submissions GROUP BY user_id
        )
        SELECT u.name,u.uni,u.telegram,u.x,u.track,
               COALESCE(m.joined_telegram,'pending') AS joined_telegram,
               COALESCE(m.followed_x,'pending')      AS followed_x,
               COALESCE(m.microquest,'pending')      AS microquest
        FROM users u
        LEFT JOIN marks m ON m.user_id=u.id
        ORDER BY u.created_at ASC
        """).fetchall()
        headers = ["name","uni","telegram","x","track","joined_telegram","followed_x","microquest"]
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(headers); w.writerows(rows)
        return path

    def recap_stats():
        con = db_conn()
        students = con.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        subs = con.execute("SELECT COUNT(*) FROM submissions").fetchone()[0]
        approved = con.execute("SELECT COUNT(*) FROM submissions WHERE status='approved'").fetchone()[0]
        con.close()
        return {"students": students, "subs": subs, "approved": approved}

    def list_social_posts():
        con = db_conn()
        cur = con.execute("SELECT text FROM submissions WHERE text LIKE 'http%'")
        urls = [r[0] for r in cur.fetchall()]
        con.close()
        return urls
