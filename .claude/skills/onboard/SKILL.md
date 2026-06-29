---
name: onboard
description: Connect this repo to the Meta Ads account — approve the MCP, browser OAuth, verify the account, check billing, and capture goals into account/defaults.md. Run this first, before any other workflow.
argument-hint: ""
disable-model-invocation: true
---

Run the onboarding workflow for the Meta Ads agent.

Paths below are relative to the repo root (where Claude Code is running).

1. Read `workflows/onboarding.md` and follow it step by step.
2. Honor `workflows/guardrails.md` throughout — this is a read/connect flow, so nothing here
   spends money, but keep the posture.
3. As you learn the user's goals (objective, landing destination, target CPA, ROAS floor, monthly
   budget, time zone), write them into `account/defaults.md`, replacing the
   `‹set during onboarding›` placeholders.

End state: the `meta-ads` MCP is connected, the account is verified
(`is_ads_mcp_enabled: true`, currency `ARS`), billing status is known, and `account/defaults.md`
is filled in. Then point the user to `/menu`.
