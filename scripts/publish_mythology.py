#!/usr/bin/env python3
"""Import completed Hermes mythology reports and publish only the generated posts."""

import argparse
from datetime import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import time
from zoneinfo import ZoneInfo

JOB_ID = "d2def51e7f5e"
KST = ZoneInfo("Asia/Seoul")


def story(body):
    body = re.split(r"\n---\n(?:응답 모델:|Response model:)", body)[0].strip()
    labels = [re.search(r"(?m)^\s*[-*]?\s*\*\*(?:오늘의\s*)?" + label + r"\s*[:：]\s*\*\*\s*(.+)", body)
              for label in ("신", "인물")]
    if not all(labels) or body.startswith(("[CONTEXT COMPACTION", "[CRON_FAILURE]", "[SILENT]")):
        return None
    names = [re.split(r"[（(]|\s*[—–]", match[1], maxsplit=1)[0].strip() for match in labels]
    return body, names


def collect(home):
    records = {}
    skipped = []

    def add(body, at, source):
        parsed = story(body)
        if not parsed:
            skipped.append(source)
            return
        body, names = parsed
        day = at.strftime("%Y-%m-%d")
        digest = hashlib.sha256((day + "\n" + " ".join(body.split())).encode()).hexdigest()[:12]
        records[day + "-" + digest] = {"body": body, "names": names, "at": at, "source": source}

    database = home / "state.db"
    if database.exists():
        with sqlite3.connect(database.as_uri() + "?mode=ro", uri=True) as db:
            runs = db.execute("SELECT id, started_at FROM sessions WHERE id LIKE ? ORDER BY started_at",
                              (f"cron_{JOB_ID}_%",)).fetchall()
            for session_id, started in runs:
                row = db.execute("""SELECT content, timestamp FROM messages WHERE session_id=?
                    AND role='assistant' AND (tool_calls IS NULL OR tool_calls='[]')
                    AND content IS NOT NULL AND content!='' ORDER BY id DESC LIMIT 1""", (session_id,)).fetchone()
                if row:
                    add(row[0], datetime.fromtimestamp(row[1] or started, KST), session_id)
                else:
                    skipped.append(session_id)
    for path in sorted((home / "cron" / "output" / JOB_ID).glob("*.md")):
        _, marker, body = path.read_text(encoding="utf-8").partition("## Response\n")
        if marker:
            at = datetime.strptime(path.stem, "%Y-%m-%d_%H-%M-%S").replace(tzinfo=KST)
            add(body, at, path.name)
        else:
            skipped.append(path.name)
    return records, skipped


def render(record, archive_id):
    at = record["at"]
    title = f"{at.month}월 {at.day}일 신화이야기 — {' · '.join(record['names'])}"
    return ("---\nlayout: post\ntitle: " + json.dumps(title, ensure_ascii=False)
            + f"\ndate: {at.strftime('%Y-%m-%d %H:%M:%S %z')}\ncategory: 신화이야기"
            + "\ndescription: " + json.dumps("그리스·로마 신과 인물의 이야기", ensure_ascii=False)
            + f"\nmyth_archive_id: {archive_id}\n---\n\n" + record["body"] + "\n")


def import_posts(repo, records):
    created = []
    for archive_id, record in sorted(records.items()):
        day, digest = archive_id[:10], archive_id[11:]
        path = repo / "_posts" / f"{day}-mythology-{digest}.md"
        if path.exists():
            continue  # Published posts, including later human edits, are immutable to the importer.
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(record, archive_id), encoding="utf-8")
        created.append(str(path.relative_to(repo)))
    return created


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120).stdout.strip()


def sync_remote(repo):
    git(repo, "fetch", "origin", "main")
    try:
        git(repo, "merge", "--ff-only", "origin/main")
    except subprocess.CalledProcessError:
        # A concurrent publisher can advance main after our previous commit but before push.
        # Rebase only our generated mythology posts; never rewrite other local work.
        paths = git(repo, "diff", "--name-only", "origin/main...HEAD").splitlines()
        if not paths or any(not p.startswith("_posts/") or "-mythology-" not in Path(p).name for p in paths):
            raise RuntimeError("Local and remote main diverged outside mythology posts; manual reconciliation required.")
        git(repo, "rebase", "origin/main")


def publish(repo, records):
    if git(repo, "status", "--porcelain"):
        raise RuntimeError("Blog checkout has pending changes; preserve them and retry after they are committed.")
    if git(repo, "branch", "--show-current") != "main":
        raise RuntimeError("Blog checkout must be on main.")
    sync_remote(repo)
    created = import_posts(repo, records)
    if created:
        git(repo, "add", "--", *created)
        git(repo, "commit", "-m", f"신화이야기 자동 게시: {len(created)}편")
    # Retry a previously committed but unpushed publication even when no new report was imported.
    git(repo, "push", "origin", "main")
    return created


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path, default=Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))))
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--import-only", action="store_true")
    parser.add_argument("--wait-today", action="store_true")
    parser.add_argument("--wait-seconds", type=int, default=2700)
    args = parser.parse_args()
    home, repo = args.home.expanduser().resolve(), args.repo.expanduser().resolve()
    state = home / "state"
    state.mkdir(parents=True, exist_ok=True)
    with (state / "mythology-blog.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        deadline = time.monotonic() + args.wait_seconds
        today = datetime.now(KST).date()
        while True:
            records, skipped = collect(home)
            if not args.wait_today or any(r["at"].date() == today for r in records.values()):
                break
            if time.monotonic() >= deadline:
                raise RuntimeError("Today's mythology report is not ready; no post was fabricated or published.")
            time.sleep(15)
        created = publish(repo, records) if args.publish else import_posts(repo, records) if args.import_only else []
        dates = sorted(r["at"].strftime("%Y-%m-%d") for r in records.values())
        print(json.dumps({"reports": len(records), "created": len(created), "skipped_sources": len(skipped),
                          "from": dates[0] if dates else None, "through": dates[-1] if dates else None,
                          "published": args.publish}, ensure_ascii=False))


if __name__ == "__main__":
    main()
