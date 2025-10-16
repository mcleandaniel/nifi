# Agent Handbook

- Prefer scripted or programmatic workflows over manual steps. When demonstrating API calls (e.g., `curl`), load credentials automatically (from `.env`, token scripts, etc.) and avoid instructions that require the user to paste IDs or edit commands.
- Do **not** ask the user to set shell variables manually when you can do it for them. Either hardcode the values (when appropriate) or include the `export`/`source`/`TOKEN=…` steps in the script or command snippet.
- If you notice repeated attempts failing, revert to a focused workflow: write a small test or utility script, run it step-by-step, and surface deterministic reproduction steps before retrying larger flows.
