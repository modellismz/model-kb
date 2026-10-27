import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "init_kb.py"


def initialize(directory, *extra):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--directory", str(directory), *extra],
        capture_output=True,
        text=True,
    )


class InitKbTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_non_git_directory_is_idempotent(self):
        project = self.root / "project"
        project.mkdir()
        self.assertEqual(initialize(project).returncode, 0)
        index = project / "model-kb" / "README.md"
        agents = project / "AGENTS.md"
        before = (index.read_text(), agents.read_text())
        self.assertEqual(initialize(project).returncode, 0)
        self.assertEqual((index.read_text(), agents.read_text()), before)
        self.assertIn("model-kb/README.md", before[1])
        for name in ("CLAUDE.md", "GEMINI.md"):
            self.assertIn("model-kb/README.md", (project / name).read_text())
        self.assertTrue((project / "model-kb" / "tools" / "kb_sync.py").is_file())
        self.assertTrue((project / "model-kb" / "log" / "README.md").is_file())

    def test_agent_selection_and_existing_files_appended_once(self):
        project = self.root / "project"
        project.mkdir()
        (project / "CLAUDE.md").write_text("# Mine\n")
        self.assertEqual(initialize(project, "--agents", "claude,copilot").returncode, 0)
        self.assertEqual(initialize(project, "--agents", "claude,copilot").returncode, 0)
        claude = (project / "CLAUDE.md").read_text()
        self.assertTrue(claude.startswith("# Mine\n"))
        self.assertEqual(claude.count("model-kb/README.md"), 1)
        self.assertTrue((project / ".github" / "copilot-instructions.md").is_file())
        self.assertFalse((project / "AGENTS.md").exists())
        self.assertNotEqual(initialize(project, "--agents", "nope").returncode, 0)

    def test_nested_git_directory_uses_root_and_preserves_old_kb(self):
        project = self.root / "project"
        project.mkdir()
        subprocess.run(["git", "init", "-q", str(project)], check=True)
        nested = project / "nested"
        nested.mkdir()
        old = project / "docs" / "global-knowledge" / "README.md"
        old.parent.mkdir(parents=True)
        old.write_text("# Existing KB\n")
        agents = project / "AGENTS.md"
        agents.write_text("# Existing instructions\n")
        self.assertEqual(initialize(nested).returncode, 0)
        self.assertIn("../docs/global-knowledge/README.md", (project / "model-kb" / "README.md").read_text())
        self.assertEqual(old.read_text(), "# Existing KB\n")
        self.assertTrue(agents.read_text().startswith("# Existing instructions\n"))
        self.assertFalse((nested / "model-kb").exists())

    def test_explicit_canonical_index_must_be_inside_project(self):
        project = self.root / "project"
        project.mkdir()
        outside = initialize(project, "--canonical-index", "../outside.md")
        self.assertNotEqual(outside.returncode, 0)
        self.assertFalse((project / "model-kb").exists())
        old = project / "docs" / "knowledge" / "README.md"
        old.parent.mkdir(parents=True)
        old.write_text("# Existing KB\n")
        result = initialize(project, "--canonical-index", "docs/knowledge/README.md")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("../docs/knowledge/README.md", (project / "model-kb" / "README.md").read_text())

    def test_refuses_agents_symlink(self):
        project = self.root / "project"
        project.mkdir()
        target = self.root / "external.md"
        target.write_text("unchanged\n")
        (project / "AGENTS.md").symlink_to(target)
        result = initialize(project)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Refusing to write through symlink", result.stderr)
        self.assertEqual(target.read_text(), "unchanged\n")
        self.assertFalse((project / "model-kb").exists())


if __name__ == "__main__":
    unittest.main()
