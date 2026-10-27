#!/usr/bin/env python3
"""Create an idempotent model-kb entrypoint in one project directory.

Writes model-kb/README.md, a shared sync tool (model-kb/tools/kb_sync.py), a conflict-free log folder,
and a short pointer in each agent's instruction file so every agent working in the repository reads
and maintains the same KB. Existing files are never overwritten; pointers are appended once.
"""

import argparse
import os
import shutil
import subprocess
from pathlib import Path

SYNC_TOOL = Path(__file__).resolve().with_name("kb_sync.py")

# Instruction file each agent reads at the project root.
AGENT_FILES = {
    "agents": "AGENTS.md",                          # Codex, Cursor, Aider, Jules, and most others
    "claude": "CLAUDE.md",                          # Claude Code
    "gemini": "GEMINI.md",                          # Gemini CLI
    "copilot": ".github/copilot-instructions.md",   # GitHub Copilot
}
DEFAULT_AGENTS = ("agents", "claude", "gemini")

POINTER = """## Project knowledge (model-kb)

This repository keeps one shared KB in `model-kb/` for every person and every agent working here.

1. Before work, run `python3 model-kb/tools/kb_sync.py status`. If teammates pushed commits that are not yet in
   the KB, run `python3 model-kb/tools/kb_sync.py pull`, fold the digest it prints into the relevant `model-kb/`
   pages, then run `python3 model-kb/tools/kb_sync.py mark`.
2. Read `model-kb/README.md` and only the topics relevant to the task.
3. After a material change, update the relevant topic and add one entry with
   `python3 model-kb/tools/kb_sync.py log "<summary>"`; commit it together with the change.
4. Before pushing, run `status` again; if upstream moved, pull and reconcile the KB first.
"""

LOG_README = """# KB log

One file per entry, named `YYYY-MM-DD-HHMM-<author>-<slug>.md`, so people working in parallel never conflict.
Create entries with `python3 model-kb/tools/kb_sync.py log "<summary>"`. Lasting facts belong in topic pages;
an entry records what changed, why, and the evidence.
"""


def project_root(directory: Path) -> Path:
    directory = directory.expanduser().resolve()
    if not directory.is_dir():
        raise ValueError(f"Not a directory: {directory}")
    try:
        result = subprocess.run(
            ["git", "-C", str(directory), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return directory
    return Path(result.stdout.strip()) if result.returncode == 0 else directory


def create_if_missing(path: Path, content: str) -> bool:
    try:
        with path.open("x", encoding="utf-8") as output:
            output.write(content)
        return True
    except FileExistsError:
        return False


def add_pointer(path: Path) -> str:
    if path.exists():
        content = path.read_text(encoding="utf-8")
        if "model-kb/README.md" in content:
            return "existing pointer"
        with path.open("a", encoding="utf-8") as output:
            output.write(("\n" if content.endswith("\n") else "\n\n") + POINTER)
        return "updated"
    path.parent.mkdir(parents=True, exist_ok=True)
    create_if_missing(path, f"# Agent instructions\n\n{POINTER}")
    return "created"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--canonical-index", type=Path)
    parser.add_argument("--agents", default=",".join(DEFAULT_AGENTS),
                        help=f"comma list of {', '.join(AGENT_FILES)} or 'all' (default: %(default)s)")
    parser.add_argument("--update-tool", action="store_true", help="replace model-kb/tools/kb_sync.py with this version")
    args = parser.parse_args()

    wanted = list(AGENT_FILES) if args.agents == "all" else [a.strip() for a in args.agents.split(",") if a.strip()]
    unknown = [a for a in wanted if a not in AGENT_FILES]
    if unknown:
        raise ValueError(f"Unknown agent(s): {', '.join(unknown)}; choose from {', '.join(AGENT_FILES)}")

    root = project_root(args.directory)
    kb = root / "model-kb"
    pointers = [root / AGENT_FILES[a] for a in wanted]
    existing_indexes = [
        root / "docs" / "global-knowledge" / "README.md",
        root / "docs" / "model-kb" / "README.md",
    ]
    if args.canonical_index:
        if args.canonical_index.is_absolute():
            raise ValueError("--canonical-index must be relative to the project root")
        existing = (root / args.canonical_index).resolve()
        try:
            existing.relative_to(root)
        except ValueError as error:
            raise ValueError("--canonical-index must stay inside the project") from error
        if not existing.is_file() or existing == kb / "README.md":
            raise ValueError("--canonical-index must name an existing project Markdown index")
    else:
        existing = next((path for path in existing_indexes if path.is_file()), None)

    for path in [kb, *pointers]:
        if path.is_symlink():
            raise ValueError(f"Refusing to write through symlink: {path}")
    kb.mkdir(exist_ok=True)
    if not kb.is_dir():
        raise ValueError(f"Not a directory: {kb}")

    if existing:
        relative = os.path.relpath(existing, kb)
        index_content = f"# Model KB\n\nCanonical project knowledge: [{existing.parent.name}]({relative}).\n"
    else:
        index_content = "# Model KB\n\n## Current state\n\nNot yet consolidated.\n\n## Topics\n\nAdd links as verified topics are documented.\n"
    index = kb / "README.md"
    created_index = create_if_missing(index, index_content)

    tools = kb / "tools"
    tools.mkdir(exist_ok=True)
    tool = tools / "kb_sync.py"
    if args.update_tool or not tool.exists():
        shutil.copyfile(SYNC_TOOL, tool)
        tool.chmod(0o755)
        tool_state = "updated" if args.update_tool else "created"
    else:
        tool_state = "existing"
    (kb / "log").mkdir(exist_ok=True)
    create_if_missing(kb / "log" / "README.md", LOG_README)

    print(f"Project root: {root}")
    print(f"KB index: {index} ({'created' if created_index else 'existing'})")
    print(f"Sync tool: {tool.relative_to(root)} ({tool_state})")
    for path in pointers:
        print(f"{path.relative_to(root)}: {add_pointer(path)}")


if __name__ == "__main__":
    main()
