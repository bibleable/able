#!/usr/bin/env python3
"""Build a full-Bible draft inventory from BSB, including entirely absent chapters.

This checks file identity and verse coverage, not meaning or reader comprehension.
It never creates chapter drafts or treats a placeholder as a completed draft.
"""

import argparse
from collections import Counter
import json
from pathlib import Path
import re

from check_able import load_source, parse_verses, WORDS

ROOT = Path(__file__).resolve().parents[1]
EDITION = ROOT / "paraphrases/0.3.4-easy"
# Fixed suffix for chapters that have no original filename. Do not regenerate it.
NEW_FILENAME_SUFFIX = "1792322671"


def folder_for(book):
    return {"Psalms": "psalms", "Song of Solomon": "songofsongs"}.get(
        book, re.sub(r"[^a-z0-9]", "", book.lower()))


def chapter_inventory(root=ROOT):
    source = load_source(root / "comparison/bsb.txt")
    expected = {}
    for ref, text in source.items():
        chapter = ref.rsplit(":", 1)[0]
        expected.setdefault(chapter, {})[ref] = text
    edition = root / "paraphrases/0.3.4-easy"
    records = []
    planned_paths = set()
    for chapter, verses in expected.items():
        book, number = chapter.rsplit(" ", 1)
        folder = folder_for(book)
        pattern = re.compile(re.escape(folder) + number + r"_\d+\.md$")
        originals = sorted(p for p in (root / "paraphrases" / folder).glob("*.md")
                           if pattern.fullmatch(p.name))
        # Ruth 1 has two historical filenames. Prefer an existing Easy Read
        # filename; otherwise use the latest original timestamp, retaining the
        # full list in the inventory so the choice is visible.
        present = [p for p in originals if (edition / folder / p.name).exists()]
        candidates = present or originals
        selected = max(candidates, key=lambda p: int(p.stem.rsplit("_", 1)[1])) if candidates else None
        filename = (selected.name if selected else
                    f"{folder}{number}_{NEW_FILENAME_SUFFIX}.md")
        relative = f"{folder}/{filename}"
        planned_paths.add(relative)
        path = edition / relative
        issues = []
        found = []
        if path.exists():
            content = path.read_text(encoding="utf-8")
            parsed = parse_verses(content)
            found = [v["address"] for v in parsed]
            counts = Counter(found)
            if any(count > 1 for count in counts.values()):
                issues.append("Duplicate verse headings")
            if found != list(verses):
                issues.append("Verse addresses differ from BSB chapter or order")
            for verse in parsed:
                ref = verse["address"]
                if verses.get(ref) and not WORDS.search(verse["text"]):
                    issues.append(f"No paraphrase text at {ref}")
                if ref in verses and not verses[ref] and not verse["has_editorial_note"]:
                    issues.append(f"Blank BSB address needs a labeled note at {ref}")
                if ref in verses and not verses[ref] and WORDS.search(verse["text"]):
                    issues.append(f"Paraphrase supplied at blank BSB address {ref}")
            for line in content.splitlines():
                if re.match(r"^##\s+.*\d+\s*:", line) and not re.fullmatch(r"##\s+.+?\s+\d+:\d+\s*", line):
                    issues.append("Malformed verse heading")
        records.append({
            "chapter": chapter, "book": book, "number": int(number),
            "path": relative, "original_filename_exists": bool(originals),
            "original_filenames": [p.name for p in originals],
            "status": "missing" if not path.exists() else "needs_repair" if issues else "draft",
            "source_addresses": len(verses),
            "source_text_verses": sum(bool(v) for v in verses.values()),
            "blank_source_addresses": [ref for ref, text in verses.items() if not text],
            "present_addresses": len(found), "issues": issues,
        })
    unexpected = sorted(str(p.relative_to(edition)) for p in edition.glob("*/*.md")
                        if str(p.relative_to(edition)) not in planned_paths)
    return records, unexpected


def number_ranges(numbers):
    result = []
    for value in sorted(numbers):
        if result and result[-1][-1] + 1 == value:
            result[-1].append(value)
        else:
            result.append([value])
    return ", ".join(str(r[0]) if len(r) == 1 else f"{r[0]}–{r[-1]}" for r in result) or "—"


def render(records, unexpected):
    drafts = [r for r in records if r["status"] == "draft"]
    books = list(dict.fromkeys(r["book"] for r in records))
    finished_books = [b for b in books if all(r["status"] == "draft" for r in records if r["book"] == b)]
    lines = ["# Full-Bible Easy Read progress", "",
             "Scope: all 66 books and 1,189 chapters, written directly from `comparison/bsb.txt`.", "",
             f"**Structurally complete text drafts: {len(drafts)}/{len(records)} chapters.**",
             f"**Books with every chapter drafted: {len(finished_books)}/{len(books)}.**", "",
             f"These drafts contain {sum(r['source_addresses'] for r in drafts):,} of "
             f"{sum(r['source_addresses'] for r in records):,} source verse addresses.", "",
             "A draft status means the intended file contains the expected BSB verse addresses in order, "
             "with text at nonempty source verses. It does not certify meaning, Easy Read comprehension, "
             "illustrations, or final presentation. Reader testing remains pending.", "",
             "The BSB file has 16 numbered addresses without verse text. Preserve those addresses with "
             "labeled editorial notes; do not invent scripture or import wording from another translation.", "",
             "Regenerate this inventory with `python3 scripts/easy_coverage.py --write`.", "",
             "## Coverage by book", "",
             "| Book | Draft chapters | Total | Chapters still to draft or repair |",
             "| --- | ---: | ---: | --- |"]
    for book in books:
        rows = [r for r in records if r["book"] == book]
        done = sum(r["status"] == "draft" for r in rows)
        missing = number_ranges([r["number"] for r in rows if r["status"] != "draft"])
        lines.append(f"| {book} | {done} | {len(rows)} | {missing} |")
    lines += ["", "## Chapter drafts", ""]
    for book in books:
        rows = [r for r in drafts if r["book"] == book]
        if rows:
            links = ", ".join(f"[{r['number']}]({r['path']})" for r in rows)
            lines.append(f"- {book}: {links}")
    lines += ["", "## Original structure gaps", "",
              "The following chapters have no matching original filename. Planned filenames follow "
              "the original naming convention, using a fixed suffix. No empty chapter files are created.", ""]
    for r in records:
        if not r["original_filename_exists"]:
            lines.append(f"- {r['chapter']}: `{r['path']}`")
        if len(r["original_filenames"]) > 1:
            lines.append(f"- {r['chapter']} has historical filename variants: "
                         + ", ".join(f"`{name}`" for name in r["original_filenames"])
                         + f". Selected path: `{r['path']}`.")
    repairs = [r for r in records if r["issues"]]
    lines += ["", "## Inventory problems", ""]
    if not repairs and not unexpected:
        lines.append("None detected in the chapter files that are present.")
    for r in repairs:
        lines.append(f"- {r['chapter']}: {'; '.join(r['issues'])}")
    for path in unexpected:
        lines.append(f"- Unexpected chapter file: `{path}`")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Update edition FULL_BIBLE_PROGRESS.md")
    parser.add_argument("--json", action="store_true", help="Print the full chapter manifest as JSON")
    parser.add_argument("--require-complete", action="store_true", help="Exit 1 unless every chapter is drafted")
    args = parser.parse_args()
    records, unexpected = chapter_inventory()
    if args.write:
        path = EDITION / "FULL_BIBLE_PROGRESS.md"
        path.write_text(render(records, unexpected), encoding="utf-8")
        print(f"Updated {path}")
    elif args.json:
        print(json.dumps({"chapters": records, "unexpected_files": unexpected}, indent=2))
    else:
        print(render(records, unexpected), end="")
    problems = unexpected or any(r["status"] == "needs_repair" for r in records)
    incomplete = any(r["status"] != "draft" for r in records)
    return int(bool(problems or (args.require_complete and incomplete)))


if __name__ == "__main__":
    raise SystemExit(main())
