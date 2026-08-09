---
source: https://github.com/mezmo/aura/issues/430
date: 2026-08-09
artifact: ticket
note: "#424 child by charlesjohnson; verification-shaped scope (invoke, verify, repeatable test incident) in 71 body words; org-sourced: keep-or-purge at gate"
---

# [FEATURE] Build the PagerDuty-triggered AURA demo path

Build and validate the AURA path triggered by a PagerDuty incident workflow.

## Scope
- Configure the isolated PagerDuty demo account and incident workflow.
- Define the webhook action and payload carrying the required incident context.
- Authenticate and invoke AURA reliably.
- Verify the resulting investigation is visible and attributable to the incident.
- Provide a repeatable test incident, setup instructions, and cleanup.

Notion use case: https://app.notion.com/p/a21def8fdeb54e9f9908f590c4250db9
Parent project: https://app.notion.com/p/3a6f52b1578280439b31e880f9e054d3
