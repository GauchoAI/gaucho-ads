---
name: menu
description: Show the Meta Ads workflow menu and route to a workflow — monitor, optimize, create-campaign, report, or onboard. Use when the user wants to see what they can do or isn't sure where to start.
argument-hint: ""
disable-model-invocation: true
---

Show the Meta Ads workflow menu.

Paths below are relative to the repo root (where Claude Code is running).

1. Read `workflows/README.md` — the menu and single source of truth.
2. Present the four categories and their workflows to the user as a concise, scannable menu
   (Monitor 🟢 · Optimize 🟡 · Create 🔴 · Report 🟢), noting the zone of each.
3. Ask which they'd like to run — or accept a free-form request — and route into the matching
   playbook under `workflows/`, honoring `workflows/guardrails.md`.

If the `meta-ads` MCP isn't connected yet (check `/mcp` or try `ads_get_ad_accounts`), suggest
`/onboard` first.
