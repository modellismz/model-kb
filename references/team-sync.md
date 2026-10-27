# Team Sync: Several People, One Repository, One KB

Use this when more than one person (each with their own agent: Codex, Claude Code, Gemini CLI, Cursor, Copilot, or
another) works in the same Git repository. Everyone shares one `model-kb/`; each clone ingests teammates' pushes into
it before building on them.

## How it fits together

- **One KB, committed with the code.** `model-kb/README.md` (index), topic pages, and `model-kb/log/` live on the
  shared branch. Whoever changes something material updates the KB in the same commit or the next one.
- **Every agent finds it.** The initializer writes the same pointer into `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md`
  (add `--agents all` for `.github/copilot-instructions.md`). Agents that read none of these can be told to read
  `AGENTS.md`.
- **The tool travels with the repo.** `model-kb/tools/kb_sync.py` is copied into the project, so a teammate's agent
  can follow the pointer without installing this skill. Refresh it with `init_kb.py --update-tool`.
- **Per-clone marker.** `kb_sync.py mark` records, inside `.git` (never committed), the last commit this clone has
  folded into the KB. Commits after it by other authors are "not ingested".
- **Conflict-free log.** `kb_sync.py log "<summary>"` creates one file per entry,
  `model-kb/log/YYYY-MM-DD-HHMM-<author>-<slug>.md`, so parallel work never collides in a shared changelog.

## Start of a session: teammates first

1. `python3 model-kb/tools/kb_sync.py status` — fetches and lists teammate commits not yet in the KB, flagging
   commits that changed code without touching `model-kb/`.
2. If any: `python3 model-kb/tools/kb_sync.py pull` — fast-forwards and prints a digest (message, files, and the
   `model-kb/` diff of each commit). If local and upstream have diverged it stops; merging or rebasing is the user's
   call. After the user integrates, run `kb_sync.py digest`.
3. Fold the digest into the KB before starting your own task:
   - Teammate KB edits are already in the files after the pull. Read them; reconcile any page that now disagrees
     with your local understanding or with another page.
   - For code-only commits, add the lasting fact (a decision, a changed interface, a new constraint) to the relevant
     topic, labelled with the commit and "from commit, not re-verified" unless you verified it.
   - Contradictions between teammates' claims go to the user with both sources; do not pick one silently.
4. `python3 model-kb/tools/kb_sync.py mark` — only after the KB reflects those commits.

## End of a material change

1. Update the smallest relevant topic page and the index checkpoint if the current state changed.
2. `python3 model-kb/tools/kb_sync.py log "<summary>" --topic <page>` and fill in what changed, why, and evidence.
3. Commit KB and code together. Before pushing, run `status`; if upstream moved, pull and repeat the ingest steps,
   then push. Never force-push a shared branch.

## Merge conflicts in KB pages

Resolve by evidence, not by side: keep both facts with their dates and sources, mark the superseded one, and ask
the user when two current decisions contradict. Prefer adding topic pages over growing the index, which keeps the
index (the most shared file) small and rarely edited.

## Optional reminder for people

`python3 model-kb/tools/kb_sync.py install-hook` adds a local `post-merge` hook that prints `status` after every
`git pull`. Hooks are per clone; each person installs their own.
