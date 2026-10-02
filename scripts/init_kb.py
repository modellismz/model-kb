#!/usr/bin/env python3
"""Create an idempotent model-kb entrypoint in one project directory."""

import argparse
import os
import subprocess
from pathlib import Path


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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--canonical-index", type=Path)
    args = parser.parse_args()

    root = project_root(args.directory)
    kb = root / "model-kb"
    agents = root / "AGENTS.md"
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

    if kb.is_symlink():
        raise ValueError(f"Refusing to write through symlink: {kb}")
    if agents.is_symlink():
        raise ValueError(f"Refusing to write through symlink: {agents}")
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

    pointer = "Read `model-kb/README.md` and only relevant topics; update the KB after material changes."
    if agents.exists():
        content = agents.read_text(encoding="utf-8")
        if "model-kb/README.md" not in content:
            with agents.open("a", encoding="utf-8") as output:
                output.write(f"\n## Project knowledge\n\n{pointer}\n")
            updated_agents = True
        else:
            updated_agents = False
    else:
        updated_agents = create_if_missing(agents, f"# Agent instructions\n\n{pointer}\n")

    print(f"Project root: {root}")
    print(f"KB index: {index} ({'created' if created_index else 'existing'})")
    print(f"AGENTS.md: {'updated' if updated_agents else 'existing pointer'}")


if __name__ == "__main__":
    main()
