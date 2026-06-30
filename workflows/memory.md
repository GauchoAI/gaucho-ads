# Memory — the durable cross-session store

The project's memory lives in a small **SQLite database committed via git LFS**. It is the durable
record across sessions: who the account is, what the goals are, **what Claude did** (audit log), and
**what the account looked like over time** (monitoring snapshots/deltas).

## ⛔ Secrets boundary (read first)

**The committed store holds NON-SECRET data only.**

- The **Meta OAuth token is managed entirely by Claude Code's MCP auth store** (outside this repo,
  stored securely and auto-refreshed). We **never** read, copy, or persist it — not in the DB, not
  in git, not in the JSONL.
- The schema has **no token/credential columns** by design.
- **Any future secret** (e.g. if you ever self-host with a Meta App Secret + system-user token) goes
  in the **macOS Keychain** (`security` CLI), referenced by name — never the repo or the DB.
- `db.py checkpoint` runs a **best-effort secret scan** over the committed files and **aborts** if a
  token-shaped string (e.g. an `EAA…` Facebook token, `access_token`, `client_secret`) appears.
  `.gitignore` also blocks `.env*`.

## Files

| Path | What | Git |
|---|---|---|
| `memory/agent.sqlite` | Queryable store (schema below) | **LFS** |
| `memory/audit-log.jsonl` | Append-only, human-readable mirror of `audit_log` — the greppable, PR-reviewable "chronicle" (mirrors the sibling repo's `*.jsonl` convention) | **LFS** |
| `memory/db.py` | The only thing that touches the DB (stdlib Python, no deps) | tracked (text) |
| `memory/agent.sqlite-wal` / `-shm` | WAL runtime sidecars | **gitignored** (per-host) |

## Schema (tables)

- **`meta`** — schema_version, db_created_at, last_checkpoint_at.
- **`profile`** — singleton account facts (ad_account_id, business, currency, time_zone).
- **`goals`** — versioned snapshots of the goals from `account/defaults.md` (objective, landing,
  target_cpa, roas_floor, monthly_budget).
- **`defaults_snapshot`** — the editable thresholds blob over time (tracks when they change).
- **`audit_log`** — ts, session, actor (`claude`/`user`), action_type
  (read|propose|write|activate|onboard|monitor|checkpoint), entity, field, old→new, tool, approved_by,
  note. Every row is mirrored to the JSONL.
- **`monitor_snapshot`** — per-entity metrics per sweep (see [`awareness.md`](awareness.md)).
- **`monitor_delta`** — computed metric changes between sweeps + a human narrative.

## `db.py` command reference

```
python3 memory/db.py init                       # create schema + JSONL (idempotent)
python3 memory/db.py set-profile      --json '{…}'   # upsert account facts
python3 memory/db.py record-goals     --json '{…}'   # append a goals snapshot
python3 memory/db.py snapshot-defaults --json '{…}'  # append a thresholds snapshot
python3 memory/db.py record-audit     --json '{…}'   # audit row + JSONL line
python3 memory/db.py snapshot   --json '[{…}]' [--sweep-id ID]   # monitor snapshot rows
python3 memory/db.py compute-deltas             # diff the two most recent sweeps
python3 memory/db.py digest [--session-start]   # last-known state (offline)
python3 memory/db.py checkpoint                 # secret-scan + wal_checkpoint(TRUNCATE) + VACUUM
python3 memory/db.py query --sql 'SELECT …'     # read-only SELECT/WITH only
```
`--json -` reads JSON from stdin (handy for large snapshot payloads).

## Concurrency + commit discipline (important)

Several Claude Code sessions can share the DB. The helper handles it:
- **WAL** mode → concurrent readers + a single writer; **`busy_timeout=5000`** waits instead of
  failing; every writer uses **`BEGIN IMMEDIATE`** (the deadlock `busy_timeout` doesn't cover).
- **Never auto-commit mid-sweep.** Writes to the local DB are free and frequent; **committing** is a
  deliberate checkpoint, done via `/checkpoint` (or at session end).
- **Always `db.py checkpoint` before `git add`.** It folds the WAL into the main file (the `-wal`
  sidecar is gitignored, so an un-checkpointed commit would lose data) and VACUUMs to keep the LFS
  blob small. Then: `git add memory/agent.sqlite memory/audit-log.jsonl`.

## Relationship to `account/defaults.md`

No two sources of truth: **`account/defaults.md` is the authoritative, human-editable config** for
thresholds and goals. The DB **mirrors goals + snapshots the thresholds over time** and holds the
audit + monitoring data. Onboarding writes goals to **both**.
