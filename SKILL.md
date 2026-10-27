---
name: model-kb
description: Initialize and maintain a shared model-kb folder that every coding agent (Codex, Claude Code, Gemini CLI, Cursor, Copilot) and every person in a repository reads and updates. Use for KB handoffs, ingesting teammates' pushes into the KB, cross-directory synchronization, and unmerged worktree knowledge; not for ordinary one-off code edits.
---

# Model KB

Keep durable project knowledge in Markdown so a new chat — any agent, any teammate — can recover important state without replaying every conversation. A skill is a workflow, not automatic memory; a new chat sees the KB in its own directory or Git checkout.

## Initialize on use

1. Identify the current project directory: the Git worktree root when inside one, otherwise the current directory. Unless the user explicitly requested read-only work, run `python3 <skill-directory>/scripts/init_kb.py --directory <project-directory>` before doing KB work. This creates `model-kb/README.md`, the shared sync tool `model-kb/tools/kb_sync.py`, a `model-kb/log/` folder, and the same short pointer in `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` (`--agents all` adds `.github/copilot-instructions.md`); it never overwrites an existing KB and appends each pointer once. For another directory the user names, run it there too. Do not initialize unrelated directories.
2. If another KB already exists, pass its project-relative index via `--canonical-index` when the initializer does not detect it; `model-kb/README.md` is only an entrypoint to that canonical KB. Do not duplicate its facts or migrate it without a separate decision. Read the index and only relevant topic files. Respect project-specific evidence, security, and approval rules. Check `git status` before editing.
3. For a handoff, read the current chat and the related chats the user names. If asked to cover all related sessions, inventory accessible project chats and work through them in batches. Record which chats and sources were reviewed; identify any inaccessible or unreviewed history. Do not claim complete coverage from memory or a short summary.
4. Treat chat messages as leads, not as verified current state. Recheck code, documents, Git history, or live read-only evidence when a claim matters. Distinguish observed facts, decisions, plans, open questions, and superseded facts.

## Maintain a compact KB

- Keep the index short: purpose, current checkpoint, topic links, and the next relevant read. Put detail in topic Markdown files. Summarize decisions and constraints, not the chat transcript or every failed attempt.
- Add, edit, or remove material under the rules in [KB governance](references/kb-governance.md). Preserve provenance and uncertainty. Do not put credentials, unnecessary personal data, or raw sensitive logs in the KB.
- Use repository-relative links within a repository. For another repository, name that repository and its stable relative path. Never make an agent-managed worktree path (for example under `~/.codex/worktrees/` or `.claude/worktrees/`) the canonical KB link.
- The pointer in each agent file tells future chats to ingest teammates' commits, read the index and relevant topics, then update the KB when material state, decisions, or open questions change. Keep it small to avoid context growth.
- At the end of a material task, update the relevant topic or checkpoint with verified outcomes and next actions. Skip transcript-like recaps and facts that will not matter to a later chat.
- Review the Markdown diff, links, status labels, dates, and secret exposure before reporting completion. State which files changed and which facts remain unverified.

## Team sync: several people in one repository

When teammates push to the same repository, follow [team sync](references/team-sync.md): at the start of a session run `python3 model-kb/tools/kb_sync.py status`; if teammate commits are not yet in the KB, `pull`, fold the printed digest into the relevant `model-kb/` pages (their KB edits arrive with the pull; derive lasting facts from code-only commits and label them), and only then `mark`. Record each material change with `kb_sync.py log`, which writes one file per entry so parallel work never conflicts. Stop and ask when branches have diverged or teammates' claims contradict.

## Sync across directories and Git

Follow [cross-directory and Git sync](references/sync.md) when the user works across directories. Keep a `model-kb/` entrypoint in each participating directory and identify which copy owns each shared fact. A local copy is not automatically current: reconcile and propagate only verified, relevant changes. A request to run `model-kb` for synchronization authorizes KB-only commits and normal pushes to an existing trusted upstream after review; it does not authorize a new remote, branch merge, force-push, or deletion. A commit or push does not update a different worktree or repository by itself.

## Reconcile worktrees when relevant

When knowledge is split across chats or worktrees, or worktrees are accumulating, follow [worktree reconciliation](references/worktree-reconciliation.md). Inventory commits, dirty files, unique local artifacts, and KB differences before proposing a merge or cleanup. Pushing a branch does not merge it or free local disk space.

Prepare a reviewable merge target and diff. Ask the user to choose or authorize a merge when that specific merge has not already been authorized. After verifying the target contains the desired work, identify dispensable local worktrees and ask before archiving or deleting them when cleanup has not already been authorized. Never infer that an untracked file is disposable merely because the branch was merged.

At handoff, report the canonical KB location, reviewed source coverage, Git state (local, committed, pushed, merged), worktrees retained or archived, and any measured disk space recovered.
