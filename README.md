# model-kb

An agent skill for keeping project knowledge small, durable, and shared: across chats, Git worktrees, every coding agent (Codex, Claude Code, Gemini CLI, Cursor, Copilot), and every person working in the same repository. It creates a `model-kb/` entrypoint, maintains verified Markdown knowledge, ingests teammates' pushes into the KB, and guides Git synchronization without treating a push as a merge.

## Install

```bash
npx skills@latest add modellismz/model-kb
```

Or copy this repository's `SKILL.md`, `references/`, and `scripts/` as one `model-kb` folder into your agent's skills directory (for example `~/.codex/skills/model-kb` or `~/.claude/skills/model-kb`). Teammates do not need the skill to take part: the initializer puts the sync tool and the instructions inside the repository.

## Use

Invoke `model-kb` in a project when you want to initialize its KB, record a durable handoff, reconcile knowledge from other chats or worktrees, or sync related directories. The skill creates `model-kb/README.md` and a short `AGENTS.md` pointer unless the task is read-only. Existing KBs stay canonical; the new folder becomes an entrypoint rather than a duplicate.

The initializer can also be run directly:

```bash
python3 scripts/init_kb.py --directory /path/to/project
python3 scripts/init_kb.py --directory /path/to/project --canonical-index docs/knowledge/README.md
```

### Working as a team in one repository

```bash
python3 model-kb/tools/kb_sync.py status        # teammate commits not yet in the KB
python3 model-kb/tools/kb_sync.py pull          # fast-forward + digest to fold into model-kb/
python3 model-kb/tools/kb_sync.py mark          # after the KB reflects them
python3 model-kb/tools/kb_sync.py log "summary" # one conflict-free entry per change
python3 model-kb/tools/kb_sync.py install-hook  # optional: show status after every git pull
```

Every agent reads the same pointer from `AGENTS.md`, `CLAUDE.md`, or `GEMINI.md`. The ingest marker is stored per clone inside `.git` and is never committed. See `references/team-sync.md`.

Each directory keeps its own files. There is no background sync and no automatic access to old chats. A Git commit or push does not update another worktree or repository; the skill checks what is actually integrated. It asks before merging branches, using an unknown or public remote for the first time, or removing local worktrees.

## Test

```bash
python3 -m unittest discover -s tests -v
```

Licensed under MIT.
