#!/usr/bin/env python3
"""gaucho-ads durable memory store — SQLite helper (stdlib only, Python 3.9+).

This is the single place that touches the project's SQLite memory DB, so the
concurrency + commit discipline lives in ONE file instead of being hand-written
in prompts. The DB (``memory/agent.sqlite``) is the queryable store; every
``audit_log`` row is also mirrored to an append-only, human-readable JSONL log
(``memory/audit-log.jsonl``) — the reviewable "chronicle" that a binary DB can't
provide. Both are committed via git LFS.

NON-SECRET DATA ONLY. The Meta OAuth token is managed by Claude Code's MCP auth
store and never appears here. The ``checkpoint`` command refuses to proceed if a
token-shaped string is found in the committed memory files (best-effort guard).

Concurrency model (multiple Claude Code sessions may share the DB):
  * WAL journal  -> concurrent readers + a single writer
  * busy_timeout -> wait rather than fail on contention
  * BEGIN IMMEDIATE on every writer -> avoids the deferred->write upgrade
    deadlock that busy_timeout does NOT cover
  * checkpoint(TRUNCATE)+VACUUM before any git commit -> the committed .db is
    self-contained (WAL-only data would otherwise be lost, since the -wal/-shm
    sidecars are gitignored).

Run ``python3 memory/db.py <command> --help`` for usage.
"""

import argparse
import json
import os
import re
import sqlite3
import sys
from contextlib import contextmanager
from datetime import datetime, timezone

SCHEMA_VERSION = 1

# --- paths ------------------------------------------------------------------

_HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB = os.path.join(_HERE, "agent.sqlite")


def jsonl_path_for(db_path):
    """The audit JSONL mirror lives beside the DB: <stem>-... -> audit-log.jsonl."""
    return os.path.join(os.path.dirname(os.path.abspath(db_path)), "audit-log.jsonl")


# --- time -------------------------------------------------------------------

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def new_sweep_id():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")


# --- schema -----------------------------------------------------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (
  key   TEXT PRIMARY KEY,
  value TEXT
);

CREATE TABLE IF NOT EXISTS profile (
  id            INTEGER PRIMARY KEY CHECK (id = 1),
  ad_account_id TEXT,
  business      TEXT,
  currency      TEXT,
  time_zone     TEXT,
  created_at    TEXT NOT NULL,
  updated_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS goals (
  id                  INTEGER PRIMARY KEY AUTOINCREMENT,
  captured_at         TEXT NOT NULL,
  objective           TEXT,
  landing_destination TEXT,
  target_cpa          REAL,
  roas_floor          REAL,
  monthly_budget      REAL,
  source              TEXT
);

CREATE TABLE IF NOT EXISTS defaults_snapshot (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  captured_at     TEXT NOT NULL,
  thresholds_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_log (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  ts          TEXT NOT NULL,
  session_id  TEXT,
  actor       TEXT,                 -- 'claude' | 'user'
  action_type TEXT,                 -- read|propose|write|activate|onboard|monitor|checkpoint
  entity_type TEXT,
  entity_id   TEXT,
  field       TEXT,
  old_value   TEXT,
  new_value   TEXT,
  tool_name   TEXT,
  approved_by TEXT,
  note        TEXT
);

CREATE TABLE IF NOT EXISTS monitor_snapshot (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  ts           TEXT NOT NULL,
  sweep_id     TEXT NOT NULL,
  scope        TEXT,                 -- account|campaign|adset|ad
  entity_id    TEXT,
  entity_name  TEXT,
  status       TEXT,
  metrics_json TEXT,                 -- {metric: value, ...}
  source_tool  TEXT
);

CREATE TABLE IF NOT EXISTS monitor_delta (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  ts            TEXT NOT NULL,
  sweep_id      TEXT,
  prev_sweep_id TEXT,
  entity_id     TEXT,
  entity_name   TEXT,
  metric        TEXT,
  prev_value    TEXT,
  new_value     TEXT,
  change_pct    REAL,
  direction     TEXT,                -- up|down|flat
  significance  TEXT,                -- high|medium|low
  narrative     TEXT
);

CREATE INDEX IF NOT EXISTS idx_snapshot_sweep  ON monitor_snapshot(sweep_id);
CREATE INDEX IF NOT EXISTS idx_snapshot_entity ON monitor_snapshot(entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_ts        ON audit_log(ts);
CREATE INDEX IF NOT EXISTS idx_delta_sweep     ON monitor_delta(sweep_id);
"""


# --- connection -------------------------------------------------------------

def _ensure_not_lfs_pointer(db_path):
    """A fresh clone without git-lfs materialized leaves the DB as a text LFS
    pointer. Fail with actionable guidance instead of a cryptic 'not a database'."""
    try:
        with open(db_path, "rb") as fh:
            head = fh.read(45)
    except OSError:
        return
    if head.startswith(b"version https://git-lfs"):
        raise SystemExit(
            "ERROR: %s is an unresolved Git LFS pointer.\n"
            "Run:  git lfs install && git lfs pull\n"
            "then retry (the memory store is stored via Git LFS)." % db_path
        )


def connect(db_path):
    """Open a connection in autocommit mode with the production PRAGMA triple.

    isolation_level=None puts pysqlite in autocommit so we control transactions
    explicitly (and can issue BEGIN IMMEDIATE for writers).
    """
    parent = os.path.dirname(os.path.abspath(db_path))
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    if os.path.exists(db_path):
        _ensure_not_lfs_pointer(db_path)
    conn = sqlite3.connect(db_path, isolation_level=None, timeout=5.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA busy_timeout = 5000")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def write_txn(conn):
    """Serializable write transaction. BEGIN IMMEDIATE acquires the write lock
    up front, so a concurrent writer waits (busy_timeout) instead of failing the
    deferred->write upgrade."""
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise


def get_meta(conn, key, default=None):
    row = conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else default


def set_meta(conn, key, value):
    conn.execute(
        "INSERT INTO meta(key, value) VALUES(?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, str(value)),
    )


# --- input helpers ----------------------------------------------------------

def load_json_arg(value):
    """Accept a JSON string, or '-' to read JSON from stdin."""
    if value == "-":
        value = sys.stdin.read()
    return json.loads(value)


def as_float(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


# --- commands ---------------------------------------------------------------

def cmd_init(args):
    conn = connect(args.db)
    try:
        conn.executescript(SCHEMA)
        with write_txn(conn):
            if get_meta(conn, "schema_version") is None:
                set_meta(conn, "schema_version", SCHEMA_VERSION)
                set_meta(conn, "db_created_at", now_iso())
            set_meta(conn, "last_init_at", now_iso())
    finally:
        conn.close()
    # Ensure the JSONL mirror exists so LFS tracking / first commit is clean.
    jp = jsonl_path_for(args.db)
    if not os.path.exists(jp):
        open(jp, "a", encoding="utf-8").close()
    print("Initialized %s (schema v%d) + %s" % (args.db, SCHEMA_VERSION, os.path.basename(jp)))


def cmd_set_profile(args):
    d = load_json_arg(args.json)
    conn = connect(args.db)
    try:
        ts = now_iso()
        with write_txn(conn):
            conn.execute(
                """
                INSERT INTO profile(id, ad_account_id, business, currency, time_zone,
                                    created_at, updated_at)
                VALUES(1, :ad_account_id, :business, :currency, :time_zone, :ts, :ts)
                ON CONFLICT(id) DO UPDATE SET
                  ad_account_id = COALESCE(excluded.ad_account_id, profile.ad_account_id),
                  business      = COALESCE(excluded.business,      profile.business),
                  currency      = COALESCE(excluded.currency,      profile.currency),
                  time_zone     = COALESCE(excluded.time_zone,     profile.time_zone),
                  updated_at    = excluded.updated_at
                """,
                {
                    "ad_account_id": d.get("ad_account_id"),
                    "business": d.get("business"),
                    "currency": d.get("currency"),
                    "time_zone": d.get("time_zone"),
                    "ts": ts,
                },
            )
    finally:
        conn.close()
    print("profile updated")


def cmd_record_goals(args):
    d = load_json_arg(args.json)
    conn = connect(args.db)
    try:
        with write_txn(conn):
            conn.execute(
                """INSERT INTO goals(captured_at, objective, landing_destination,
                                     target_cpa, roas_floor, monthly_budget, source)
                   VALUES(?, ?, ?, ?, ?, ?, ?)""",
                (
                    now_iso(),
                    d.get("objective"),
                    d.get("landing_destination"),
                    as_float(d.get("target_cpa")),
                    as_float(d.get("roas_floor")),
                    as_float(d.get("monthly_budget")),
                    d.get("source", "onboarding"),
                ),
            )
    finally:
        conn.close()
    print("goals recorded")


def cmd_snapshot_defaults(args):
    d = load_json_arg(args.json)
    conn = connect(args.db)
    try:
        with write_txn(conn):
            conn.execute(
                "INSERT INTO defaults_snapshot(captured_at, thresholds_json) VALUES(?, ?)",
                (now_iso(), json.dumps(d, sort_keys=True)),
            )
    finally:
        conn.close()
    print("defaults snapshot recorded")


AUDIT_FIELDS = (
    "session_id", "actor", "action_type", "entity_type", "entity_id",
    "field", "old_value", "new_value", "tool_name", "approved_by", "note",
)


def cmd_record_audit(args):
    d = load_json_arg(args.json)
    ts = d.get("ts") or now_iso()
    conn = connect(args.db)
    try:
        with write_txn(conn):
            cur = conn.execute(
                """INSERT INTO audit_log(ts, session_id, actor, action_type, entity_type,
                                         entity_id, field, old_value, new_value, tool_name,
                                         approved_by, note)
                   VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    ts, d.get("session_id"), d.get("actor"), d.get("action_type"),
                    d.get("entity_type"), d.get("entity_id"), d.get("field"),
                    d.get("old_value"), d.get("new_value"), d.get("tool_name"),
                    d.get("approved_by"), d.get("note"),
                ),
            )
            row_id = cur.lastrowid
        # Mirror to the append-only JSONL log (one line per row), after commit.
        record = {"id": row_id, "ts": ts}
        for f in AUDIT_FIELDS:
            record[f] = d.get(f)
        with open(jsonl_path_for(args.db), "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    finally:
        conn.close()
    print("audit #%s recorded + mirrored to JSONL" % row_id)


def cmd_snapshot(args):
    rows = load_json_arg(args.json)
    if isinstance(rows, dict):
        rows = [rows]
    sweep_id = args.sweep_id or new_sweep_id()
    ts = now_iso()
    conn = connect(args.db)
    try:
        with write_txn(conn):
            for r in rows:
                metrics = r.get("metrics", {})
                conn.execute(
                    """INSERT INTO monitor_snapshot(ts, sweep_id, scope, entity_id,
                                                    entity_name, status, metrics_json, source_tool)
                       VALUES(?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        ts, sweep_id, r.get("scope"), r.get("entity_id"),
                        r.get("entity_name"), r.get("status"),
                        json.dumps(metrics, sort_keys=True), r.get("source_tool"),
                    ),
                )
    finally:
        conn.close()
    print("sweep %s: %d snapshot row(s)" % (sweep_id, len(rows)))


def _recent_sweeps(conn, limit=2):
    # Order by MAX(id), not MAX(ts): ts is second-granular, so two sweeps in the
    # same second would order ambiguously. rowid is monotonic with insertion.
    return [
        r["sweep_id"]
        for r in conn.execute(
            "SELECT sweep_id, MAX(id) AS mid FROM monitor_snapshot "
            "GROUP BY sweep_id ORDER BY mid DESC LIMIT ?",
            (limit,),
        ).fetchall()
    ]


def _snapshot_map(conn, sweep_id):
    """entity_id -> {'name','status','metrics':{...}} for one sweep."""
    out = {}
    for r in conn.execute(
        "SELECT entity_id, entity_name, status, metrics_json "
        "FROM monitor_snapshot WHERE sweep_id = ?",
        (sweep_id,),
    ).fetchall():
        try:
            metrics = json.loads(r["metrics_json"] or "{}")
        except json.JSONDecodeError:
            metrics = {}
        out[r["entity_id"]] = {
            "name": r["entity_name"],
            "status": r["status"],
            "metrics": metrics,
        }
    return out


def _significance(change_pct):
    a = abs(change_pct)
    if a >= 20:
        return "high"
    if a >= 10:
        return "medium"
    return "low"


def cmd_compute_deltas(args):
    conn = connect(args.db)
    deltas = []
    try:
        sweeps = _recent_sweeps(conn, 2)
        if len(sweeps) < 2:
            print("need >=2 sweeps to diff (have %d)" % len(sweeps))
            return
        cur_sweep, prev_sweep = sweeps[0], sweeps[1]
        cur, prev = _snapshot_map(conn, cur_sweep), _snapshot_map(conn, prev_sweep)
        ts = now_iso()
        with write_txn(conn):
            for eid, cur_e in cur.items():
                prev_e = prev.get(eid)
                if not prev_e:
                    continue
                for metric, new_v in cur_e["metrics"].items():
                    old_v = prev_e["metrics"].get(metric)
                    nf, of = as_float(new_v), as_float(old_v)
                    if nf is None or of is None:
                        continue
                    if nf == of:
                        continue
                    change_pct = ((nf - of) / of * 100.0) if of != 0 else None
                    direction = "up" if nf > of else "down"
                    sig = _significance(change_pct) if change_pct is not None else "high"
                    pct_txt = ("%+.1f%%" % change_pct) if change_pct is not None else "n/a"
                    narrative = "%s %s %s -> %s (%s)" % (
                        cur_e["name"] or eid, metric, old_v, new_v, pct_txt,
                    )
                    conn.execute(
                        """INSERT INTO monitor_delta(ts, sweep_id, prev_sweep_id, entity_id,
                                entity_name, metric, prev_value, new_value, change_pct,
                                direction, significance, narrative)
                           VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (ts, cur_sweep, prev_sweep, eid, cur_e["name"], metric,
                         str(old_v), str(new_v), change_pct, direction, sig, narrative),
                    )
                    deltas.append(narrative)
    finally:
        conn.close()
    if deltas:
        print("\n".join(deltas))
    else:
        print("no changes between the two most recent sweeps")


def cmd_digest(args):
    conn = connect(args.db)
    try:
        prof = conn.execute("SELECT * FROM profile WHERE id = 1").fetchone()
        goal = conn.execute(
            "SELECT * FROM goals ORDER BY id DESC LIMIT 1"
        ).fetchone()
        last_sweep_row = conn.execute(
            "SELECT sweep_id, MAX(ts) AS t, MAX(id) AS mid FROM monitor_snapshot "
            "GROUP BY sweep_id ORDER BY mid DESC LIMIT 1"
        ).fetchone()
        recent = conn.execute(
            "SELECT narrative, significance FROM monitor_delta "
            "ORDER BY id DESC LIMIT ?",
            (args.limit,),
        ).fetchall()
    finally:
        conn.close()

    lines = []
    if args.session_start:
        lines.append("=== gaucho-ads memory digest (last known state) ===")
    if prof:
        lines.append("Account %s · %s · %s" % (
            prof["ad_account_id"] or "?", prof["currency"] or "?",
            prof["business"] or "",
        ))
    if goal:
        lines.append("Goals: objective=%s landing=%s target_cpa=%s roas_floor=%s monthly=%s" % (
            goal["objective"], goal["landing_destination"], goal["target_cpa"],
            goal["roas_floor"], goal["monthly_budget"],
        ))
    if last_sweep_row and last_sweep_row["t"]:
        lines.append("Last sweep: %s" % last_sweep_row["t"])
    if recent:
        lines.append("Recent changes:")
        for r in recent:
            lines.append("  [%s] %s" % (r["significance"], r["narrative"]))
    if not (prof or goal or recent):
        lines.append("No memory yet — run /onboard to connect and seed the store.")
    elif args.session_start:
        lines.append("(Offline snapshot. Run /watch for a live read-only refresh.)")
    print("\n".join(lines))


# Best-effort secret guard. NON-SECRET data only is committed; this catches
# accidental token leakage before it reaches git.
SECRET_PATTERNS = [
    re.compile(r"EAA[0-9A-Za-z_\-]{20,}"),                 # Facebook access tokens
    re.compile(r"\baccess_token\b\s*[\"':=]"),
    re.compile(r"\b(app_secret|client_secret|refresh_token)\b", re.IGNORECASE),
    re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{20,}"),
]


def _scan_secrets(text):
    hits = []
    for pat in SECRET_PATTERNS:
        if pat.search(text):
            hits.append(pat.pattern)
    return hits


def cmd_checkpoint(args):
    # 1) Secret scan over the committed memory files (JSONL + all DB text values).
    blobs = []
    jp = jsonl_path_for(args.db)
    if os.path.exists(jp):
        with open(jp, "r", encoding="utf-8", errors="replace") as fh:
            blobs.append(fh.read())
    conn = connect(args.db)
    try:
        for tbl, col in (("audit_log", "*"), ("profile", "*"), ("goals", "*"),
                         ("defaults_snapshot", "*"), ("monitor_snapshot", "*")):
            for row in conn.execute("SELECT * FROM %s" % tbl).fetchall():
                blobs.append(" ".join("" if v is None else str(v) for v in row))
        combined = "\n".join(blobs)
        hits = _scan_secrets(combined)
        if hits:
            print("ABORT: token-shaped string(s) found in memory files: %s" % ", ".join(hits),
                  file=sys.stderr)
            print("The committed store must hold NON-SECRET data only. Remove and retry.",
                  file=sys.stderr)
            sys.exit(2)
        # 2) Fold WAL into the main DB so the committed file is self-contained.
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        with write_txn(conn):
            set_meta(conn, "last_checkpoint_at", now_iso())
        conn.execute("VACUUM")
    finally:
        conn.close()
    db_sz = os.path.getsize(args.db) if os.path.exists(args.db) else 0
    jl_sz = os.path.getsize(jp) if os.path.exists(jp) else 0
    print("checkpoint OK · secret-scan clean · db=%d B · jsonl=%d B" % (db_sz, jl_sz))
    print("ready to: git add %s %s" % (args.db, jp))


_FORBIDDEN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|REPLACE|ATTACH|DETACH|PRAGMA|VACUUM|REINDEX)\b",
    re.IGNORECASE,
)


def cmd_query(args):
    sql = args.sql.strip().rstrip(";")
    if not re.match(r"(?is)^\s*(SELECT|WITH)\b", sql):
        print("ERROR: query only accepts read-only SELECT/WITH statements", file=sys.stderr)
        sys.exit(2)
    if ";" in sql or _FORBIDDEN.search(sql):
        print("ERROR: refused — multiple statements or a write keyword detected", file=sys.stderr)
        sys.exit(2)
    conn = connect(args.db)
    try:
        rows = conn.execute(sql).fetchall()
        for r in rows:
            print(json.dumps({k: r[k] for k in r.keys()}, ensure_ascii=False))
    finally:
        conn.close()


# --- CLI --------------------------------------------------------------------

def build_parser():
    p = argparse.ArgumentParser(description="gaucho-ads memory store helper")
    p.add_argument("--db", default=DEFAULT_DB, help="path to the SQLite DB (default: memory/agent.sqlite)")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="create schema + JSONL mirror (idempotent)")

    sp = sub.add_parser("set-profile", help="upsert the singleton account profile")
    sp.add_argument("--json", required=True, help="JSON object (or '-' for stdin)")

    sp = sub.add_parser("record-goals", help="append a versioned goals snapshot")
    sp.add_argument("--json", required=True)

    sp = sub.add_parser("snapshot-defaults", help="append a thresholds snapshot")
    sp.add_argument("--json", required=True)

    sp = sub.add_parser("record-audit", help="insert an audit row + mirror to JSONL")
    sp.add_argument("--json", required=True)

    sp = sub.add_parser("snapshot", help="insert monitor snapshot rows for one sweep")
    sp.add_argument("--json", required=True, help="JSON array of entity objects (or '-')")
    sp.add_argument("--sweep-id", default=None)

    sub.add_parser("compute-deltas", help="diff the two most recent sweeps")

    sp = sub.add_parser("digest", help="print last-known state (offline)")
    sp.add_argument("--session-start", action="store_true")
    sp.add_argument("--limit", type=int, default=15)

    sub.add_parser("checkpoint", help="secret-scan + wal_checkpoint(TRUNCATE) + VACUUM")

    sp = sub.add_parser("query", help="run a read-only SELECT and print JSON rows")
    sp.add_argument("--sql", required=True)

    return p


HANDLERS = {
    "init": cmd_init,
    "set-profile": cmd_set_profile,
    "record-goals": cmd_record_goals,
    "snapshot-defaults": cmd_snapshot_defaults,
    "record-audit": cmd_record_audit,
    "snapshot": cmd_snapshot,
    "compute-deltas": cmd_compute_deltas,
    "digest": cmd_digest,
    "checkpoint": cmd_checkpoint,
    "query": cmd_query,
}


def main(argv=None):
    args = build_parser().parse_args(argv)
    HANDLERS[args.command](args)


if __name__ == "__main__":
    main()
