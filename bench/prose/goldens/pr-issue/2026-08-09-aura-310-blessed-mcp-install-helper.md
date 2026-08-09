---
source: https://github.com/mezmo/aura/issues/310
date: 2026-08-09
artifact: ticket
note: "The exemplar that #383 was hand-tuned against per the S10 card; charlesjohnson-authored epic with user-outcome framing; org-sourced: keep-or-purge at gate"
---

# [EPIC] Blessed MCP Install Helper

### Overview

A fresh AURA install can reason, but it cannot do useful work against a practitioner’s environment until it is connected to real data. Today, that connection requires the user to manually edit the `config.toml` file and add MCP servers, and then configure the per-worker allow & deny lists.

The goal is to build a supported, opinionated MCP install helper that turns this work into a guided flow. The helper should take a user from “AURA is installed” to “AURA can successfully use tools against my data” without cloning a repository, building from source, or hand-authoring MCP configuration.

This epic serves the five-minute-install goal in #370 and provides the reusable integration path consumed by the quick-start experience in #311.

### User outcome

A practitioner with AURA and the credentials required by a supported data source can:

- Discover the MCP setup flow from within the aura chat interface.
- Install or configure the MCP server through a guided interaction.
- See its prerequisites and the access AURA will require.
- Provide credentials without leaking them
- Have AURA update its configuration without destroying unrelated settings.
- Run an automatic connection and tool-discovery check.
- Receive a useful starter prompt that exercises the newly connected integration.

For the primary supported path, this journey must fit within the initiative’s five-minute install-to-value target.
