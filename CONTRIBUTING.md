# Contributing

## Skill shape

- Put one Skill in skills/<skill-name>/SKILL.md.
- Give it a specific trigger, a minimal procedure, clear evidence requirements, and explicit safety boundaries.
- Load linked references only when they change the current decision. Avoid manuals that every task must read.
- Ask one concise question only when an unresolved fact materially changes scope, target, permission, acceptance, or risk.

## Before opening a pull request

1. Verify commands and paths against the current tool or runtime.
2. Remove credentials, cookies, tokens, private keys, user data, private endpoints, raw logs, and local machine assumptions.
3. Ensure the Skill does not silently launch a browser, bypass a safety gate, repeat an external mutation after a timeout, or claim unverified live state.
4. Keep examples fictional and concise.

## Scope

This repository contains reusable instructions and small helper scripts, not personal knowledge bases, browser bridges, login sessions, cloud inventories, or application source trees.
