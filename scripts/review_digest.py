#!/usr/bin/env python3
"""Дайджест для еженедельного разбора (WEEKLY_REVIEW.md).

Печатает по каждому проекту: заметки новее даты последнего разбора (по `date:`
из frontmatter, не mtime), свежие строки логов living-файлов, открытые задачи
(просроченные помечены), related-связи новых заметок. Плюс: inbox, секция
«Заметки для еженедельного обзора», задачи PLAN.md.

Роль: быстрый срез между глубокими разборами проектов (см. WEEKLY_REVIEW.md),
тела заметок не читает. Запуск: python3 scripts/review_digest.py [--since YYYY-MM-DD]
Дата по умолчанию — самая старая дата из таблицы «Последние разборы»
WEEKLY_REVIEW.md; если разборов не было — 14 дней. Только стандартная библиотека.
"""
import datetime
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORDER = ["job-search", "work", "finance", "projects", "learning", "ideas", "health"]
NOTE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-.+\.md$")
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
TASK_RE = re.compile(r"^\s*- \[ \] (.+)$")
DUE_RE = re.compile(r"📅\s*(\d{4}-\d{2}-\d{2})")
LOG_ROW_RE = re.compile(r"^\|\s*(\d{4}-\d{2}-\d{2})\s*\|")
TODAY = datetime.date.today().isoformat()


def read(path):
    try:
        return open(path, encoding="utf-8").read()
    except (OSError, UnicodeDecodeError):
        return ""


def parse_frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n?", text, re.S)
    if not m:
        return {}
    fm, key = {}, None
    for line in m.group(1).splitlines():
        if re.match(r"^\s+-\s+", line) and key:
            fm.setdefault(key, [])
            if isinstance(fm[key], list):
                fm[key].append(line.split("-", 1)[1].strip().strip('"'))
            continue
        kv = re.match(r"^([\w-]+):\s*(.*)$", line)
        if kv:
            key, val = kv.group(1), kv.group(2).strip()
            val = re.sub(r"\s+#.*$", "", val)
            if val.startswith("[") and val.endswith("]"):
                fm[key] = [v.strip().strip('"') for v in val[1:-1].split(",") if v.strip()]
            elif val == "":
                fm[key] = []
            else:
                fm[key] = val.strip('"')
    return fm


def last_review_date():
    for a, b in zip(sys.argv, sys.argv[1:]):
        if a == "--since" and DATE_RE.fullmatch(b):
            return b
    text = read(os.path.join(ROOT, "WEEKLY_REVIEW.md"))
    m = re.search(r"## Последние разборы\n(.*?)\n## ", text, re.S)
    dates = re.findall(r"\|\s*(\d{4}-\d{2}-\d{2})\s*\|", m.group(1)) if m else []
    if dates:
        return min(dates)
    return (datetime.date.today() - datetime.timedelta(days=14)).isoformat()


def note_date(fname, fm):
    d = fm.get("date", "")
    if isinstance(d, str) and DATE_RE.fullmatch(d):
        return d
    return fname[:10]


def open_tasks(text):
    out = []
    for line in text.splitlines():
        m = TASK_RE.match(line)
        if not m:
            continue
        task = m.group(1).strip()
        due = DUE_RE.search(task)
        overdue = bool(due and due.group(1) < TODAY)
        out.append(("ПРОСРОЧЕНО  " if overdue else "") + task)
    return out


def digest_project(d, since):
    base = os.path.join(ROOT, d)
    if not os.path.isdir(base):
        return
    new_notes, livings = [], []
    for cur, dirs, files in os.walk(base):
        dirs[:] = [x for x in dirs if not x.startswith(".")]
        for f in sorted(files):
            if not f.endswith(".md") or f in ("index.md", "CLAUDE.md"):
                continue
            path = os.path.join(cur, f)
            text = read(path)
            fm = parse_frontmatter(text)
            rel = os.path.relpath(path, ROOT)[:-3]
            if fm.get("type") == "living":
                if fm.get("status") == "archived":
                    continue
                fresh = [ln.strip() for ln in text.splitlines()
                         if (m := LOG_ROW_RE.match(ln.strip())) and m.group(1) >= since]
                livings.append((rel, fresh, open_tasks(text)))
            elif NOTE_RE.match(f) and note_date(f, fm) >= since:
                new_notes.append((rel, fm.get("summary", "—"), fm.get("related", [])))

    if not new_notes and not any(fr or t for _, fr, t in livings):
        print(f"\n## {d} — без изменений, задач нет\n")
        return
    print(f"\n## {d}\n")
    if new_notes:
        print("Новые заметки:")
        for rel, summary, related in new_notes:
            print(f"- [[{rel}]] — {summary}")
            for r in related if isinstance(related, list) else [related]:
                print(f"    related: {r}")
    for rel, fresh, tasks in livings:
        if not fresh and not tasks:
            continue
        print(f"\n{rel} (living):")
        for ln in fresh:
            print(f"  лог: {ln}")
        for t in tasks:
            print(f"  - [ ] {t}")


def main():
    since = last_review_date()
    print(f"# Дайджест разбора — с {since} по {TODAY}")

    inbox = [f for f in sorted(os.listdir(os.path.join(ROOT, "inbox")))
             if f.endswith(".md") and f != "CLAUDE.md"] if os.path.isdir(os.path.join(ROOT, "inbox")) else []
    print(f"\nInbox: {len(inbox)} шт." + (" — РАЗОБРАТЬ ДО ДАЙДЖЕСТА:" if inbox else ""))
    for f in inbox:
        print(f"- inbox/{f}")

    for d in ORDER:
        digest_project(d, since)

    stale_cutoff = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
    stale = []
    for cur, dirs, files in os.walk(os.path.join(ROOT, "ideas")):
        dirs[:] = [x for x in dirs if not x.startswith(".")]
        for f in sorted(files):
            if not NOTE_RE.match(f):
                continue
            path = os.path.join(cur, f)
            fm = parse_frontmatter(read(path))
            if fm.get("status") != "archived" and note_date(f, fm) < stale_cutoff:
                stale.append((os.path.relpath(path, ROOT)[:-3], fm.get("summary", "—")))
    if stale:
        print(f"\n## Идеи без движения 30+ дней ({len(stale)}) — архив или действие\n")
        for rel, summary in stale:
            print(f"- [[{rel}]] — {summary}")

    idx = read(os.path.join(ROOT, "index.md"))
    m = re.search(r"## Заметки для еженедельного обзора\n(.*?)(?=\n## |\n_|\Z)", idx, re.S)
    items = [ln for ln in (m.group(1).splitlines() if m else []) if ln.strip().startswith("-")]
    print(f"\n## Заметки для еженедельного обзора ({len(items)})\n")
    for ln in items:
        print(ln)

    plan_tasks = open_tasks(read(os.path.join(ROOT, "PLAN.md")))
    print(f"\n## PLAN.md — открытые задачи ({len(plan_tasks)})\n")
    for t in plan_tasks:
        print(f"- [ ] {t}")


if __name__ == "__main__":
    main()
