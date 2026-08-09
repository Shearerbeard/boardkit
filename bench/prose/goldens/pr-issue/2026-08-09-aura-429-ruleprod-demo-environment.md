---
source: https://github.com/mezmo/aura/issues/429
date: 2026-08-09
artifact: ticket
note: "#424 child by charlesjohnson; one-sentence goal plus scope bullets that stage later needs without narration, specs delegated to links; org-sourced: keep-or-purge at gate"
---

# [FEATURE] Build and operate the ruleprod.com demo environment

Build and operate the isolated ruleprod.com environment required by selected 31 Days of AURA episodes.

## Scope
- Use separate AWS, GitHub, PagerDuty, and vendor accounts.
- Run the core application on EKS with RDS, synthetic traffic, Kubernetes MCP access, and OTel export.
- Add Fargate, Lambda, SQS, Argo CD, Terraform, canary deployment, and additional observability backends as scheduled episodes require them.
- Keep all data synthetic and free of Mezmo internal or customer identifiers.
- Document access, operating procedures, ownership, cost controls, and teardown.

Environment specification: https://app.notion.com/p/dc9ee437cb02420eb6e2c4cd3ca7966c
Campaign plan: https://app.notion.com/p/3a6f52b1578280edb034f4cc9961f008

The Kubernetes OOM episode currently uses the in-repository Kubernetes quickstart and requires no separate engineering issue.
