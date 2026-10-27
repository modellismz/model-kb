import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


INIT = Path(__file__).resolve().parents[1] / "scripts" / "init_kb.py"


def run(cwd, *args):
    return subprocess.run(list(args), cwd=cwd, capture_output=True, text=True)


def git(cwd, *args):
    result = run(cwd, "git", *args)
    if result.returncode != 0:
        raise AssertionError(f"git {' '.join(args)}: {result.stderr}")
    return result.stdout.strip()


def sync(cwd, *args):
    return run(cwd, sys.executable, "model-kb/tools/kb_sync.py", *args)


def commit(cwd, path, text, message):
    target = Path(cwd) / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)
    git(cwd, "add", "-A")
    git(cwd, "commit", "-q", "-m", message)


class TwoPeopleOneRepoTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.remote = base / "remote.git"
        git(base, "init", "-q", "--bare", "-b", "main", str(self.remote))
        self.alice = self.clone(base, "alice")
        self.assertEqual(run(self.alice, sys.executable, str(INIT), "--directory", ".").returncode, 0)
        git(self.alice, "add", "-A")
        git(self.alice, "commit", "-q", "-m", "Initialize model-kb")
        git(self.alice, "push", "-q", "-u", "origin", "main")
        self.bob = self.clone(base, "bob")
        self.assertEqual(sync(self.alice, "mark").returncode, 0)
        self.assertEqual(sync(self.bob, "mark").returncode, 0)

    def clone(self, base, name):
        path = base / name
        git(base, "clone", "-q", str(self.remote), str(path))
        git(path, "config", "user.email", f"{name}@example.com")
        git(path, "config", "user.name", name.title())
        git(path, "checkout", "-q", "-B", "main")
        return path

    def test_teammate_push_is_reported_digested_and_marked(self):
        commit(self.bob, "model-kb/gpu.md", "# GPUs\n\nWe have 4 H100.\n", "Record GPU count")
        commit(self.bob, "src/app.py", "print('hi')\n", "Add app entrypoint")
        git(self.bob, "push", "-q")

        status = sync(self.alice, "status", "--check")
        self.assertEqual(status.returncode, 1, status.stdout + status.stderr)
        self.assertIn("Teammate commits not yet in the KB: 2", status.stdout)
        self.assertIn("Record GPU count", status.stdout)
        self.assertIn("code only", status.stdout)

        pulled = sync(self.alice, "pull")
        self.assertEqual(pulled.returncode, 0, pulled.stderr)
        self.assertIn("We have 4 H100.", pulled.stdout)
        self.assertIn("Add app entrypoint", pulled.stdout)
        self.assertTrue((self.alice / "model-kb" / "gpu.md").is_file())

        self.assertEqual(sync(self.alice, "mark").returncode, 0)
        self.assertEqual(sync(self.alice, "status", "--check").returncode, 0)

    def test_own_commits_are_not_reported(self):
        commit(self.alice, "model-kb/own.md", "# Mine\n", "Alice note")
        git(self.alice, "push", "-q")
        status = sync(self.alice, "status", "--check")
        self.assertEqual(status.returncode, 0, status.stdout)
        self.assertNotIn("Alice note", status.stdout)

    def test_diverged_branches_are_left_for_the_user(self):
        commit(self.bob, "model-kb/a.md", "a\n", "Bob change")
        git(self.bob, "push", "-q")
        commit(self.alice, "model-kb/b.md", "b\n", "Alice local change")
        head = git(self.alice, "rev-parse", "HEAD")
        result = sync(self.alice, "pull")
        self.assertEqual(result.returncode, 2)
        self.assertIn("diverged", result.stderr)
        self.assertEqual(git(self.alice, "rev-parse", "HEAD"), head)
        # still visible as not ingested
        self.assertIn("Bob change", sync(self.alice, "status").stdout)

    def test_log_entries_never_collide_between_people(self):
        a = sync(self.alice, "log", "Tuned vLLM config", "--topic", "gpu.md")
        b = sync(self.bob, "log", "Tuned vLLM config")
        self.assertEqual((a.returncode, b.returncode), (0, 0), a.stderr + b.stderr)
        self.assertIn("-alice-tuned-vllm-config.md", a.stdout)
        self.assertIn("-bob-tuned-vllm-config.md", b.stdout)

    def test_mark_refuses_commit_not_in_branch(self):
        commit(self.bob, "x.md", "x\n", "Bob unpushed")
        sha = git(self.bob, "rev-parse", "HEAD")
        git(self.bob, "push", "-q")
        git(self.alice, "fetch", "-q")
        result = sync(self.alice, "mark", sha)
        self.assertEqual(result.returncode, 2)
        self.assertIn("not in the current branch", result.stderr)

    def test_hook_install_is_idempotent(self):
        self.assertEqual(sync(self.alice, "install-hook").returncode, 0)
        self.assertEqual(sync(self.alice, "install-hook").returncode, 0)
        hook = self.alice / ".git" / "hooks" / "post-merge"
        self.assertEqual(hook.read_text().count("kb_sync.py status"), 1)


if __name__ == "__main__":
    unittest.main()
