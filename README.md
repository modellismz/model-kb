# model-kb

A Codex skill for keeping project knowledge small, durable, and usable across chats and Git worktrees. It creates a `model-kb/` entrypoint in the project, maintains verified Markdown knowledge, and guides cross-directory Git synchronization without treating a push as a merge.

## Install

```bash
npx skills@latest add modellismz/model-kb
```

Or copy this repository's `SKILL.md`, `references/`, and `scripts/` into your Codex skills directory as one `model-kb` folder.

## Use

Invoke `model-kb` in a project when you want to initialize its KB, record a durable handoff, reconcile knowledge from other chats or worktrees, or sync related directories. The skill creates `model-kb/README.md` and a short `AGENTS.md` pointer unless the task is read-only. Existing KBs stay canonical; the new folder becomes an entrypoint rather than a duplicate.

The initializer can also be run directly:

```bash
python3 scripts/init_kb.py --directory /path/to/project
python3 scripts/init_kb.py --directory /path/to/project --canonical-index docs/knowledge/README.md
```

Each directory keeps its own files. There is no background sync and no automatic access to old chats. A Git commit or push does not update another worktree or repository; the skill checks what is actually integrated. It asks before merging branches, using an unknown or public remote for the first time, or removing local worktrees.

## Test

```bash
python3 -m unittest discover -s tests -v
```

Licensed under MIT.
