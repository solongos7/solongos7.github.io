import importlib.util
from pathlib import Path
import sqlite3
import subprocess
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "scripts" / "publish_mythology.py"
SPEC = importlib.util.spec_from_file_location("publisher", SOURCE)
pub = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pub)
BODY = "## 오늘의 그리스·로마 신화\n- **신:** 아테나(Minerva) — 지혜의 신.\n- **인물:** 오디세우스 — 이타카의 왕."


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home"
        self.outputs = self.home / "cron" / "output" / pub.JOB_ID
        self.outputs.mkdir(parents=True)
        self.outputs.joinpath("2026-08-01_09-01-00.md").write_text(
            "## Prompt\nprivate prompt not for publication\n## Response\n" + BODY
            + "\n---\n응답 모델: synthetic\nProvider: synthetic\n")
        self.repo = self.root / "blog"
        self.repo.mkdir()

    def git(self, repo, *args):
        return pub.git(repo, *args)

    def init_git(self):
        remote = self.root / "remote.git"
        self.git(self.root, "init", "--bare", str(remote))
        self.git(self.repo, "init", "-b", "main")
        self.git(self.repo, "config", "user.name", "Synthetic Test")
        self.git(self.repo, "config", "user.email", "test@example.invalid")
        self.repo.joinpath("README.md").write_text("fixture\n")
        self.git(self.repo, "add", "README.md")
        self.git(self.repo, "commit", "-m", "fixture")
        self.git(self.repo, "remote", "add", "origin", str(remote))
        self.git(self.repo, "push", "-u", "origin", "main")
        return remote

    def test_recovers_database_history_deduplicates_and_preserves_edits(self):
        with sqlite3.connect(self.home / "state.db") as db:
            db.execute("CREATE TABLE sessions (id TEXT, started_at REAL)")
            db.execute("CREATE TABLE messages (id INTEGER, session_id TEXT, role TEXT, tool_calls TEXT, content TEXT, timestamp REAL)")
            sid = f"cron_{pub.JOB_ID}_20260801_090000"
            ts = pub.datetime(2026, 8, 1, 9, tzinfo=pub.KST).timestamp()
            db.execute("INSERT INTO sessions VALUES (?,?)", (sid, ts))
            db.execute("INSERT INTO messages VALUES (1,?,'assistant',NULL,?,?)", (sid, BODY, ts))
            db.execute("INSERT INTO sessions VALUES (?,?)", (f"cron_{pub.JOB_ID}_20260731_090000", ts-86400))
            db.execute("INSERT INTO messages VALUES (2,?,'assistant',NULL,?,?)",
                       (f"cron_{pub.JOB_ID}_20260731_090000", BODY, ts-86400))
        self.outputs.joinpath("2026-08-02_09-00-00.md").write_text("## Response\n[CRON_FAILURE]\ninterrupted")
        records, skipped = pub.collect(self.home)
        self.assertEqual(len(records), 2)
        self.assertEqual(len(skipped), 1)
        paths = pub.import_posts(self.repo, records)
        self.assertEqual(len(paths), 2)
        for path in paths:
            text = self.repo.joinpath(path).read_text()
            self.assertNotIn("private prompt", text)
            self.assertNotIn("Provider:", text)
            self.assertIn(BODY, text)
        edited = self.repo / paths[0]
        edited.write_text("human edit")
        self.assertEqual(pub.import_posts(self.repo, records), [])
        self.assertEqual(edited.read_text(), "human edit")

    def test_push_is_idempotent_and_retries_after_remote_race(self):
        remote = self.init_git()
        records, _ = pub.collect(self.home)
        reject = remote / "hooks" / "pre-receive"
        reject.write_text("#!/bin/sh\nexit 1\n")
        reject.chmod(0o755)
        with self.assertRaises(subprocess.CalledProcessError):
            pub.publish(self.repo, records)
        local_head = self.git(self.repo, "rev-parse", "HEAD")
        reject.unlink()
        other = self.root / "other"
        self.git(self.root, "clone", "--branch", "main", str(remote), str(other))
        self.git(other, "config", "user.name", "Synthetic Test")
        self.git(other, "config", "user.email", "test@example.invalid")
        other.joinpath("music.html").write_text("other publisher's work")
        self.git(other, "add", "music.html")
        self.git(other, "commit", "-m", "other publisher")
        self.git(other, "push", "origin", "main")
        self.assertEqual(pub.publish(self.repo, records), [])
        self.assertNotEqual(self.git(self.repo, "rev-parse", "HEAD"), local_head)
        self.assertEqual(self.repo.joinpath("music.html").read_text(), "other publisher's work")
        head = self.git(self.repo, "rev-parse", "HEAD")
        self.assertEqual(head, self.git(remote, "rev-parse", "main"))
        self.assertEqual(pub.publish(self.repo, records), [])
        self.assertEqual(head, self.git(self.repo, "rev-parse", "HEAD"))

    def test_does_not_commit_unrelated_pending_work(self):
        self.init_git()
        records, _ = pub.collect(self.home)
        self.repo.joinpath("README.md").write_text("human work in progress")
        with self.assertRaisesRegex(RuntimeError, "pending changes"):
            pub.publish(self.repo, records)
        self.assertFalse(list(self.repo.glob("_posts/*")))


if __name__ == "__main__":
    unittest.main()
