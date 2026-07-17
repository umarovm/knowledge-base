#!/usr/bin/env python3
"""Генерирует index.md всех проектных папок из frontmatter заметок.

Единственный источник истины — frontmatter (summary, status, tags, related).
Индексы руками не редактировать: они перезаписываются этим скриптом.
Исключения, которые скрипт сохраняет из существующих файлов:
- строки таблиц для файлов без канонического frontmatter (CV, docx, csv и т.п.);
- секция «Заметки для еженедельного обзора» в корневом index.md.

Запуск: python3 scripts/rebuild_indexes.py  (из любого места)
Только стандартная библиотека.
"""
import os
import re
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIRS = ["work", "job-search", "finance", "health", "learning", "ideas", "projects"]
NOTE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-.+\.md$")
TODAY = datetime.date.today().isoformat()
TASK_RE = re.compile(r"^\s*- \[ \] (.+)$")
DUE_RE = re.compile(r"📅\s*(\d{4}-\d{2}-\d{2})")


def parse_frontmatter(path):
    """Минимальный YAML-парсер под канонический frontmatter (без PyYAML)."""
    try:
        text = open(path, encoding="utf-8").read()
    except (OSError, UnicodeDecodeError):
        return None
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
            val = re.sub(r"\s+#.*$", "", val)  # инлайн-комментарии
            if val.startswith("[") and val.endswith("]"):
                fm[key] = [v.strip().strip('"') for v in val[1:-1].split(",") if v.strip()]
            elif val == "":
                fm[key] = []
            else:
                fm[key] = val.strip('"')
    return fm


def existing_rows(index_path):
    """Строки таблицы из текущего индекса: имя файла -> полная строка."""
    rows = {}
    if not os.path.exists(index_path):
        return rows
    for line in open(index_path, encoding="utf-8"):
        cells = [c.strip() for c in line.strip().split("|")]
        if len(cells) >= 6 and cells[1] and not cells[1].startswith("-") and cells[1] != "Файл":
            rows[cells[1]] = line.rstrip("\n")
    return rows


def collect():
    """Все заметки и living-файлы: relpath (без .md) -> frontmatter."""
    registry = {}
    for d in PROJECT_DIRS:
        base = os.path.join(ROOT, d)
        if not os.path.isdir(base):
            continue
        for cur, dirs, files in os.walk(base):
            dirs[:] = [x for x in dirs if not x.startswith(".")]
            for f in files:
                if not f.endswith(".md") or f in ("index.md", "CLAUDE.md"):
                    continue
                fm = parse_frontmatter(os.path.join(cur, f))
                if fm and (NOTE_RE.match(f) or fm.get("type") == "living"):
                    rel = os.path.relpath(os.path.join(cur, f), ROOT)[:-3]
                    registry[rel] = fm
    return registry


def links_of(fm):
    out = []
    for item in fm.get("related", []) or []:
        m = re.search(r"\[\[(.+?)\]\]", item)
        if m:
            out.append(m.group(1))
    return out


def trunc(s, n=90):
    s = s or "—"
    return s if len(s) <= n else s[: n - 1] + "…"


def gen_dir_index(dirpath, registry):
    rel_dir = os.path.relpath(dirpath, ROOT)
    index_path = os.path.join(dirpath, "index.md")
    old = existing_rows(index_path)

    local = {r: fm for r, fm in registry.items() if os.path.dirname(r) == rel_dir}
    living = sorted((r, fm) for r, fm in local.items() if fm.get("type") == "living")
    notes = sorted(
        ((r, fm) for r, fm in local.items() if fm.get("type") != "living"),
        key=lambda x: x[1].get("date", ""), reverse=True,
    )

    lines = [f"# Индекс: {rel_dir}", "", "| Файл | Дата | Summary | Статус | Теги |",
             "|---|---|---|---|---|"]
    listed = set()
    for r, fm in living + notes:
        name = os.path.basename(r) + ".md"
        tags = ", ".join(fm.get("tags", [])) if isinstance(fm.get("tags"), list) else (fm.get("tags") or "—")
        status = "living" if fm.get("type") == "living" else fm.get("status", "—")
        lines.append(f"| {name} | {fm.get('date', '—')} | {trunc(fm.get('summary'))} | {status} | {tags or '—'} |")
        listed.add(name)
    # файлы без канонического frontmatter — переносим строки из старого индекса
    for f in sorted(os.listdir(dirpath)):
        if f in ("index.md", "CLAUDE.md") or f.startswith(".") or f in listed:
            continue
        if os.path.isfile(os.path.join(dirpath, f)) and f in old:
            lines.append(old[f])

    subdirs = [s for s in sorted(os.listdir(dirpath))
               if os.path.isdir(os.path.join(dirpath, s)) and not s.startswith(".")]
    sub_lines = []
    for s in subdirs:
        sub_rel = os.path.join(rel_dir, s)
        sub_notes = [(r, fm) for r, fm in registry.items() if os.path.dirname(r) == sub_rel]
        if not sub_notes and not os.path.exists(os.path.join(dirpath, s, "index.md")):
            continue
        n = len(sub_notes)
        last = max((fm.get("date", "—") for _, fm in sub_notes), default="—")
        sub_lines.append(f"| {s}/ | {n} | {last} |")
    if sub_lines:
        lines += ["", "## Подпапки", "", "| Подпапка | Файлов | Обновлён |", "|---|---|---|"] + sub_lines

    # Связи — генерируются из related: во frontmatter; одна пара = одна строка
    pairs = {}  # frozenset(local, remote) -> (local, remote)
    for r, fm in sorted(registry.items()):
        for target in links_of(fm):
            here, there = os.path.dirname(r) == rel_dir, os.path.dirname(target) == rel_dir
            if here and not there:
                pairs.setdefault(frozenset((r, target)), (r, target))
            elif there and not here:
                pairs.setdefault(frozenset((r, target)), (target, r))
    link_lines = []
    for local_note, remote in pairs.values():
        r_sum = registry.get(remote, {}).get("summary", "")
        link_lines.append(f"- [[{local_note}]] ↔ [[{remote}]] — {trunc(r_sum, 80)}")
    if link_lines:
        lines += ["", "## Связи", ""] + sorted(link_lines)

    lines += ["", f"_Сгенерировано scripts/rebuild_indexes.py: {TODAY}. Руками не редактировать._", ""]
    open(index_path, "w", encoding="utf-8").write("\n".join(lines))
    return len(living) + len(notes)


def first_desc(claude_md):
    """Первая содержательная строка папочного CLAUDE.md — описание папки."""
    if not os.path.exists(claude_md):
        return "—"
    for line in open(claude_md, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#"):
            return trunc(line.rstrip("."), 70)
    return "—"


def gen_root_index(counts, registry):
    index_path = os.path.join(ROOT, "index.md")
    review = "- (пусто)"
    if os.path.exists(index_path):
        m = re.search(r"## Заметки для еженедельного обзора\n\n(.*?)(?:\n##|\n_Сгенерировано|\Z)",
                      open(index_path, encoding="utf-8").read(), re.S)
        if m and m.group(1).strip():
            review = m.group(1).strip()

    lines = ["# Индекс knowledge-base", "",
             "Каталог проектов. Генерируется scripts/rebuild_indexes.py.", "",
             "| Проект | Что внутри | Заметок+living | Обновлён |", "|---|---|---|---|"]
    for d in PROJECT_DIRS:
        base = os.path.join(ROOT, d)
        if not os.path.isdir(base):
            continue
        in_dir = [(r, fm) for r, fm in registry.items() if r.split(os.sep)[0] == d]
        last = max((fm.get("date") or "" for _, fm in in_dir if fm.get("date")), default="—")
        lines.append(f"| {d} | {first_desc(os.path.join(base, 'CLAUDE.md'))} | {len(in_dir)} | {last or '—'} |")
    lines += ["", "## Контекст в корне", "",
              "- `ABOUT_ME.md` — полный контекст о пользователе (роль, цели, ценности)",
              "- `PLAN.md` — стратегический план до переезда в Узбекистан (2027)", "",
              "## Заметки для еженедельного обзора", "", review, "",
              f"_Сгенерировано scripts/rebuild_indexes.py: {TODAY}. Таблица и связи — руками не редактировать; секция обзора — можно._", ""]
    open(index_path, "w", encoding="utf-8").write("\n".join(lines))


def collect_tasks(registry):
    """Открытые задачи `- [ ] …` из PLAN.md и living-файлов (кроме archived)."""
    sources = ["PLAN"]
    sources += sorted(r for r, fm in registry.items()
                      if fm.get("type") == "living" and fm.get("status") != "archived")
    tasks = []  # (text, due|None, weekly, source_rel)
    for rel in sources:
        path = os.path.join(ROOT, rel + ".md")
        if not os.path.exists(path):
            continue
        for line in open(path, encoding="utf-8"):
            m = TASK_RE.match(line)
            if not m:
                continue
            text = m.group(1).strip()
            due = DUE_RE.search(text)
            tasks.append((text, due.group(1) if due else None, "🔁" in text, rel))
    return tasks


def gen_todo(tasks):
    """Корневой TODO.md — производная сводка, руками не редактировать."""
    def item(t):
        text, _, _, rel = t
        return f"- {text} · [[{rel}]]"

    overdue = sorted((t for t in tasks if not t[2] and t[1] and t[1] < TODAY), key=lambda t: t[1])
    dated = sorted((t for t in tasks if not t[2] and t[1] and t[1] >= TODAY), key=lambda t: t[1])
    weekly = [t for t in tasks if t[2]]
    undated = [t for t in tasks if not t[1] and not t[2]]

    lines = ["# TODO — сводка открытых задач", "",
             "_Генерируется scripts/rebuild_indexes.py из `- [ ]` в PLAN.md и living-файлах._",
             "_Руками не редактировать. Закрывать задачи `[x]` в файле-хозяине (ссылка у каждой), затем перегенерировать._", ""]
    if overdue:
        lines += ["## 🔥 Просрочено", ""] + [item(t) for t in overdue] + [""]
    if dated:
        lines += ["## По дедлайнам", ""] + [item(t) for t in dated] + [""]
    if weekly:
        lines += ["## Еженедельный ритм", ""] + [item(t) for t in weekly] + [""]
    if undated:
        lines += ["## Без даты", ""] + [item(t) for t in undated] + [""]
    lines += ["## Живые срезы (плагин Obsidian Tasks)", "",
              "### Горит: ближайшие 2 недели", "",
              "```tasks", "not done", "due on or before in two weeks",
              "sort by due", "path does not include TODO", "```", "",
              "### Все с дедлайном", "",
              "```tasks", "not done", "has due date",
              "group by due", "path does not include TODO", "```", "",
              "### Без даты", "",
              "```tasks", "not done", "no due date",
              "group by path", "path does not include TODO", "```", "",
              f"_Сгенерировано scripts/rebuild_indexes.py: {TODAY}. Задач открыто: {len(tasks)}._", ""]
    open(os.path.join(ROOT, "TODO.md"), "w", encoding="utf-8").write("\n".join(lines))
    return len(tasks), len(overdue)


def main():
    registry = collect()
    # битые related-ссылки
    for r, fm in registry.items():
        for t in links_of(fm):
            if t not in registry and not os.path.exists(os.path.join(ROOT, t + ".md")):
                print(f"WARN: битая ссылка {t} в {r}")
    counts = {}
    for d in PROJECT_DIRS:
        base = os.path.join(ROOT, d)
        if not os.path.isdir(base):
            continue
        for cur, dirs, _ in os.walk(base):
            dirs[:] = [x for x in dirs if not x.startswith(".")]
            counts[cur] = gen_dir_index(cur, registry)
    gen_root_index(counts, registry)
    n_tasks, n_overdue = gen_todo(collect_tasks(registry))
    print(f"OK: {len(counts)} индексов перегенерировано, {len(registry)} файлов в реестре, "
          f"TODO.md: {n_tasks} задач ({n_overdue} просрочено)")


if __name__ == "__main__":
    main()
