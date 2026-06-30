---
name: checkpoint
description: Safely prepare the memory store for commit — runs db.py checkpoint (secret-scan + wal_checkpoint(TRUNCATE) + VACUUM so the committed SQLite is self-contained and small), then stages memory/agent.sqlite + memory/audit-log.jsonl (git LFS) and shows what will be committed. Run this before committing memory changes.
argument-hint: ""
disable-model-invocation: true
---

Prepare the durable memory store for a clean git LFS commit. See
[`workflows/memory.md`](../../../workflows/memory.md).

1. **Checkpoint** — run `python3 memory/db.py checkpoint`. This:
   - runs a best-effort **secret scan** over the committed files and **aborts** if a token-shaped
     string is found (the store is NON-SECRET only) — if it aborts, surface what it found and stop;
   - folds the WAL into the main DB (`wal_checkpoint(TRUNCATE)`) so no committed data lives only in
     the gitignored `-wal` sidecar;
   - `VACUUM`s to keep the LFS blob small.
2. **Stage** — `git add memory/agent.sqlite memory/audit-log.jsonl` (plus any changed config/docs the
   user intends to commit).
3. **Verify LFS** — confirm they're staged as LFS pointers: `git lfs status` (expect both listed
   under "Objects to be committed"), and `git status --short` (the `-wal`/`-shm` sidecars must **not**
   appear — they're gitignored).
4. **Offer to commit** — show the staged summary and ask the user for a commit message (or confirm a
   suggested one). **Only commit when the user says so** — do not commit or push unprompted.

Never auto-run this mid-sweep; checkpointing/committing is a deliberate, user-initiated step.
