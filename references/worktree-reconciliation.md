# Worktree Reconciliation

Use this when related chats have divergent checkouts, unmerged KB changes, or meaningful disk use. A chat, Git branch, worktree, commit, push, and merge are separate states; do not equate them.

## Inventory before action

1. List Git worktrees and associate each with its chat when possible. Record path, size, branch or detached HEAD, starting commit, last activity, and whether the chat is active or pinned.
2. Inspect `git status` in each candidate. Compare commits with the intended integration branch and inspect the KB diff. Check untracked and ignored files, generated outputs, and files present only in that worktree; a clean Git diff alone does not prove the worktree is disposable.
3. Check whether KB pages link to an absolute worktree path. Replace such links with stable repository references before that worktree is removed.
4. Classify each worktree: active; contains unmerged commits; contains unique local files; fully represented elsewhere; or unresolved. Give the user a short inventory with the evidence behind each classification.

Do not modify a dirty checkout merely to simplify the inventory. Preserve unrelated user changes and respect a repository's existing KB governance.

## Integrate knowledge

Choose one canonical KB integration branch for the repository. Consolidate compatible facts into its topic files and resolve conflicting status claims against evidence. Prepare the intended commit or pull request, list exactly what it brings in, and verify the diff and relevant checks.

If the target, conflicting decision, or permission to merge is missing, ask the user after preparing this reviewable result. If the user has already authorized the specific merge, proceed and verify that the target branch contains the intended commits and KB content. A push alone does not establish that.

## Clean up only after integration

For each candidate, verify that wanted commits are in the target and that unique untracked or ignored files have been retained elsewhere or explicitly judged unnecessary. Report its path, size, associated chat, and any recovery option. Ask before archiving or deleting local files when the user has not already authorized cleanup of that candidate.

Prefer Codex-managed archive and cleanup for a completed managed worktree. The deletion may be asynchronous: verify the worktree disappears from `git worktree list` and measure disk use afterward. If it remains, report that honestly; do not force-remove it merely to make the number drop. Never bulk-delete worktrees based on age, chat title, or a merged branch alone.
