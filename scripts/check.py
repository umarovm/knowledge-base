#!/usr/bin/env python3
"""Валидатор консистентности базы. Ничего не меняет, только сообщает.

Проверки: битые wiki-ссылки (и в related:), неканонический frontmatter,
project: не совпадает с папкой, теги вне словаря CLAUDE.md, задачи в таблицах,
`- [ ]` в archived-файлах, inbox старше 7 дней.

Запуск: python3 scripts/check.py  Выход: 0 — чисто, 1 — есть проблемы.
Только стандартная библиотека.
"""
import datetime
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIRS = ["work", "job-search", "finance", "health", "learning", "ideas", "projects"]
NOTE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-.+\.md$")
LINK_RE = re.compile(r"\[\[([^\]|#]+)")
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
REQUIRED = ["date", "project", "tags", "status", "summary"]
STATUSES = {"raw", "processed", "archived"}
INBOX_MAX_AGE_DAYS = 7
TODAY = datetime.date.today()

problems = []


def report(path, msg):
    problems.append(f"{os.path.relpath(path, ROOT)}: {msg}")


def read(path):
    try:
        return open(path, encoding="utf-8").read()
    except (OSError, UnicodeDecodeError):
        return ""


def parse_frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n?", text, re.S)
    if not m:
        return None
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


def tag_dictionary():
    m = re.search(r"## Словарь тегов\n(.*?)(?=\n## )", read(os.path.join(ROOT, "CLAUDE.md")), re.S)
    tags = set()
    for group in re.findall(r"`([^`]+)`", m.group(1) if m else ""):
        tags.update(t.strip() for t in group.split(","))
    return tags


def all_md_files():
    """Все .md кроме captures/, inbox/ и скрытых папок."""
    out = []
    for cur, dirs, files in os.walk(ROOT):
        dirs[:] = [x for x in dirs if not x.startswith(".") and x not in ("captures", "inbox")]
        out += [os.path.join(cur, f) for f in files if f.endswith(".md")]
    return out


def main():
    tags_known = tag_dictionary()
    files = all_md_files()

    for path in files:
        rel = os.path.relpath(path, ROOT)
        text = read(path)
        fm = parse_frontmatter(text)
        top = rel.split(os.sep)[0]
        in_project = top in PROJECT_DIRS
        fname = os.path.basename(path)

        # 1. Битые wiki-ссылки (полный путь от корня, включая related:).
        # CLAUDE.md пропускаем: там ссылки-примеры из документации.
        for target in LINK_RE.findall(text) if fname != "CLAUDE.md" else []:
            target = target.strip()
            if not os.path.exists(os.path.join(ROOT, target + ".md")):
                if os.sep not in target and "/" not in target:
                    report(path, f"ссылка [[{target}]] без пути от корня или битая")
                else:
                    report(path, f"битая ссылка [[{target}]]")

        # 2–4. Канонический frontmatter заметок в проектных папках
        if in_project and NOTE_RE.match(fname):
            if fm is None:
                report(path, "нет frontmatter")
            else:
                for k in [k for k in REQUIRED if k not in fm]:
                    report(path, f"нет поля {k}: во frontmatter")
                if fm.get("status") and fm["status"] not in STATUSES:
                    report(path, f"неизвестный status: {fm['status']}")
                if fm.get("status") == "raw":
                    report(path, "status: raw в проектной папке — заметка не разобрана?")
                expected = os.path.dirname(rel).replace(os.sep, "/")
                if fm.get("project") and fm["project"] != expected:
                    report(path, f"project: {fm['project']} ≠ папка {expected}")
                tags = fm.get("tags", [])
                for t in (tags if isinstance(tags, list) else [tags]):
                    if t and t not in tags_known:
                        report(path, f"тег '{t}' вне словаря CLAUDE.md")

        # 5. Задачи в таблицах
        for i, line in enumerate(text.splitlines(), 1):
            if line.lstrip().startswith("|") and "- [ ]" in line:
                report(path, f"строка {i}: задача внутри таблицы — скрипт и плагин её не увидят")

        # 6. Чекбоксы в archived-файлах
        if fm and fm.get("status") == "archived" and re.search(r"^\s*- \[ \] ", text, re.M):
            report(path, "archived, но содержит '- [ ]' — заменить на '- ☐' или закрыть")

    # 7. Залежавшийся inbox
    inbox = os.path.join(ROOT, "inbox")
    if os.path.isdir(inbox):
        for f in sorted(os.listdir(inbox)):
            if not f.endswith(".md") or f == "CLAUDE.md":
                continue
            m = DATE_RE.search(f) or DATE_RE.search(read(os.path.join(inbox, f)))
            if m and (TODAY - datetime.date.fromisoformat(m.group(0))).days > INBOX_MAX_AGE_DAYS:
                report(os.path.join(inbox, f), f"лежит в inbox дольше {INBOX_MAX_AGE_DAYS} дней")

    if problems:
        print(f"Проблем: {len(problems)}\n")
        print("\n".join(f"- {p}" for p in problems))
        sys.exit(1)
    print("Всё чисто.")


if __name__ == "__main__":
    main()
