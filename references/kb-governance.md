# KB Governance

## Choose the home

Create `model-kb/README.md` at the project directory root on use. If the project already has a canonical KB, make `model-kb/README.md` a small entrypoint to it and follow its existing evidence and status rules. The initializer detects common locations; pass `--canonical-index` for another project-relative Markdown index. In a project without an older KB, use `model-kb/README.md` as the canonical index and add topic files there only as needed. Keep project knowledge in the project directory, not in the skill folder or a chat transcript.

Each agent instruction file the project uses (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, optionally `.github/copilot-instructions.md`) carries the same short pointer: ingest teammates' commits, read the index and only relevant topics, and maintain them after material changes. Lasting facts go in topic pages; `model-kb/log/` holds one dated entry file per change. An old worktree still sees its old `AGENTS.md` and KB until its Git state is updated.

## What belongs in the KB

- Current verified state, with a verification date and source.
- Decisions, their rationale, owner or decision source when known, and consequences for future work.
- Stable constraints, operating procedures, unresolved questions, and the next action.
- Links to canonical code, configuration, tickets, and safe evidence. Use source references appropriate for the repository audience; a private chat ID alone is not durable evidence.

Leave out raw transcripts, speculative conclusions presented as facts, transient command output, secrets, and repeated summaries. If a source is inaccessible, label the claim unverified and list the gap.

For a material operational claim, retain enough to verify it again: date, environment or host, secret-free evidence, result, and status. Follow any stricter local schema. Do not overwrite an older observed state with a newer plan.

## Add, edit, and delete

- **Add** a topic page when a distinct subject would make the index or an existing page hard to scan. Link it from the index.
- **Edit** the smallest relevant section after checking its source and current Git state. Keep valid facts and history intact; date and label a superseding fact.
- **Remove** an incorrect or obsolete statement when its replacement and provenance are clear. Preserve material historical evidence in a dated history section or existing audit record. Check inbound links before removing or renaming a file.
- **Reconcile conflicts** by identifying which source is newer and better verified. If two active branches encode incompatible decisions, present the conflict and ask the owner which decision governs before declaring either current.

Documentation maintenance authorized by the user may include these reversible Markdown edits. Publishing, merging, and deletion of local worktrees are separate actions with their own authorization and verification.

## Finish the update

Check the changed-file list and diff, validate relative links, review dates and status labels, and scan changed content for accidental secrets. Verify that the index points to every current topic and that no link points into `~/.codex/worktrees/`, `.claude/worktrees/`, or another disposable checkout. Report source coverage and uncertainty rather than saying the KB contains everything.
