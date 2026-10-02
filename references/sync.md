# Cross-Directory and Git Sync

## Scope and ownership

Initialize `model-kb/` in each directory explicitly in scope. Use the directory's Git worktree root when it belongs to a repository. Do not search every directory on the machine. Record the related repository identifier and stable relative KB path in each relevant index; avoid absolute paths into temporary worktrees.

For facts shared by different projects, designate one canonical owner per topic. Copy only the facts another project needs, with source and verification date, and preserve project-specific status separately. When one copy changes, compare the other copies and update only affected material. Report directories that were inaccessible or not synchronized. No background process keeps them current after this task ends.

## Git cases

- **Same repository, multiple worktrees:** Each worktree has its own checkout. Commit KB changes on the appropriate branch, then integrate into the designated branch through the reviewed merge workflow. Updating or pushing one worktree does not update the others; they must incorporate that branch or commit. Ask for merge authorization as specified in the worktree workflow.
- **Different repositories:** Git has no automatic cross-repository synchronization. Update each repository's KB separately, retaining provenance and resolving conflicts before treating copies as current. Do not copy secrets or unrelated private context between repositories.
- **No Git:** Maintain local Markdown and report that Git sync is unavailable. Do not initialize a Git repository or invent a remote without a user request.

## Publish verified KB changes

For every Git repository changed, check branch, status, ignore rules, remote, and upstream. Stage only the intended KB and `AGENTS.md` edits and review the staged diff for secrets and unrelated changes. A request to run `model-kb` for synchronization authorizes a KB-only commit and normal push to an existing trusted upstream; ordinary read-only inspection does not. Ask before first publication to an unknown or public remote, before changing the target branch, or when authorization is unclear. Never force-push, silently merge divergent branches, or rewrite history. If there is no remote, no upstream, a rejected push, or a conflict, stop and report what remains local. Verify the remote state after a successful push; do not call a push a merge.

Report each directory as local-only, committed, pushed, or integrated, rather than saying all directories are synced when any remain behind.
