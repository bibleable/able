#!/usr/bin/env python3
"""Check 0.3.4 coverage against the local BSB and optionally refresh progress."""

import argparse
from collections import defaultdict
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "paraphrases" / "0.3.4"
SOURCE = ROOT / "comparison" / "bsb.txt"


def directory_name(book):
    return {"Psalm": "psalms", "Song of Solomon": "songofsongs"}.get(
        book, book.lower().replace(" ", "")
    )


def load_source():
    books = {}
    for line in SOURCE.read_text().splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r"(.+) (\d+):(\d+)\t(.*)", line)
        if not match:
            raise ValueError(f"Unrecognized BSB line: {line[:80]}")
        book, chapter, verse, text = match.groups()
        verses = books.setdefault(book, {}).setdefault(int(chapter), {})
        if int(verse) in verses:
            raise ValueError(f"Duplicate BSB address: {book} {chapter}:{verse}")
        verses[int(verse)] = text
    return books


def inspect(books):
    written = defaultdict(set)
    errors = []
    verse_total = 0
    longest = 0
    inverse = {directory_name(book): book for book in books}
    for path in sorted(DEST.rglob("*.md")):
        if path.parent == DEST:
            continue
        directory = path.parent.name
        book = inverse.get(directory)
        match = re.fullmatch(rf"{re.escape(directory)}(\d+)_(\d+)\.md", path.name)
        if book is None or match is None:
            errors.append(f"Unexpected chapter path: {path.relative_to(ROOT)}")
            continue
        chapter = int(match[1])
        if chapter not in books[book]:
            errors.append(f"Unknown chapter: {path.relative_to(ROOT)}")
            continue
        original_names = {
            p.name for p in (ROOT / "paraphrases" / "0.3.3" / directory).glob(f"{directory}{chapter}_*.md")
        }
        if original_names and path.name not in original_names:
            errors.append(f"Filename differs from 0.3.3: {path.relative_to(ROOT)}")
            continue
        if chapter in written[book]:
            errors.append(f"Duplicate output chapter: {book} {chapter}")
            continue
        expected_title = {"Psalm": "Psalms", "Song of Solomon": "Song of Songs"}.get(book, book)
        text = path.read_text()
        headings = re.findall(r"^## (.+) (\d+):(\d+)$", text, re.M)
        expected = [(expected_title, str(chapter), str(v)) for v in books[book][chapter]]
        file_errors = []
        if headings != expected:
            file_errors.append("verse headings differ from BSB addresses")
        blocks = re.split(r"^## .+ \d+:\d+\s*$", text, flags=re.M)
        if blocks[0].strip() or len(blocks) != len(expected) + 1:
            file_errors.append("unexpected text or verse blocks")
        for number, block in enumerate(blocks[1:], 1):
            if not re.search(r"[A-Za-z]", block):
                file_errors.append(f"empty verse block {number}")
            if ";" in block:
                file_errors.append(f"semicolon in verse block {number}")
            if re.search(r"\b(?:\w+n[’']t|I[’']m|\w+[’'](?:re|ve|ll|d)|it[’']s)\b", block, re.I):
                file_errors.append(f"contraction in verse block {number}")
            for paragraph in re.split(r"\n\s*\n", block.strip()):
                sentences = [s for s in re.split(r"[.!?]+", paragraph) if re.search(r"[A-Za-z]", s)]
                if len(sentences) > 6:
                    file_errors.append(f"more than six sentences in a paragraph in verse block {number}")
                for sentence in sentences:
                    words = re.findall(r"[A-Za-z0-9]+(?:[’'][A-Za-z]+)?", sentence)
                    longest = max(longest, len(words))
                    if len(words) > 25:
                        file_errors.append(f"sentence exceeds 25 words in verse block {number}")
        if file_errors:
            errors.extend(f"{path.relative_to(ROOT)}: {error}" for error in file_errors)
        else:
            written[book].add(chapter)
            verse_total += len(expected)
    return written, verse_total, longest, errors


def compact(numbers):
    numbers = sorted(numbers)
    groups = []
    for number in numbers:
        if groups and number == groups[-1][-1] + 1:
            groups[-1].append(number)
        else:
            groups.append([number])
    return ", ".join(str(g[0]) if len(g) == 1 else f"{g[0]}–{g[-1]}" for g in groups) or "—"


def write_progress(books, written, verses, longest):
    # Dict order supplies canonical Bible order when chapter counts tie.
    order = ["Psalm"] + sorted(
        (book for book in books if book != "Psalm"), key=lambda book: len(books[book])
    )
    total_chapters = sum(len(chapters) for chapters in books.values())
    total_verses = sum(len(v) for chapters in books.values() for v in chapters.values())
    chapter_count = sum(len(chapters) for chapters in written.values())
    next_book = next((book for book in order if set(books[book]) - written[book]), None)
    next_chapter = min(set(books[next_book]) - written[next_book]) if next_book else None
    lines = [
        "# ABLE 0.3.4 rewrite progress", "",
        "Source: `comparison/bsb.txt` (Berean Standard Bible).", "",
        "Finish all Psalms first. Then finish each remaining book in ascending chapter count. "
        "For equal chapter counts, use canonical Bible order. Within each book, use chapter order.", "",
        "Keep the `0.3.3/<book>/<book><chapter>_<timestamp>.md` layout under `0.3.4`. "
        "Keep verse addresses and emojis. Write directly from BSB, preserving meaning, speakers, "
        "names, numbers, conditions, prayers, and judgments. Use short sentences, active verbs, "
        "clear subjects, consistent terms, and no contractions. Explain difficult images briefly "
        "without turning them into new factual claims. Retain song headings and label musical "
        "directions separately. Keep terms with uncertain meanings rather than inventing definitions.", "",
        "Apply [ASD-STE100 principles](https://www.asd-ste100.org/STE_faq.html) to Bible language. "
        "Full controlled-dictionary compliance has not been verified. Structural checks do not "
        "establish meaning fidelity or dictionary compliance; compare each rewrite with BSB during authoring.", "",
        f"Written and structurally checked: **{chapter_count}/{total_chapters} chapters; "
        f"{verses}/{total_verses} source verse addresses**. Longest current sentence: {longest} words.", "",
        f"Next: **{next_book} {next_chapter}**." if next_book else "All source chapters have output files.", "",
        "Inventory differences to resolve for full coverage:", "",
        "- `0.3.3` has no 2 Samuel 21–24. Write these from BSB using the same filename pattern.",
        "- `0.3.3/ruth` has two Ruth 1 files. Compare them when reaching Ruth and record the output choice.", "",
        "The local BSB has 16 reserved verse addresses with no text. Keep those verse headings "
        "and add a clearly labeled BSB source note when reaching them. Do not invent Scripture text.", "",
        "Refresh and check with `python3 scripts/check_034.py --write-progress`.", "",
        "| Order | Book | Source chapters | Written chapters | Chapter numbers |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for number, book in enumerate(order, 1):
        lines.append(f"| {number} | {book} | {len(books[book])} | {len(written[book])} | {compact(written[book])} |")
    (DEST / "PROGRESS.md").write_text("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-progress", action="store_true")
    args = parser.parse_args()
    books = load_source()
    written, verses, longest, errors = inspect(books)
    if errors:
        for error in errors:
            print(error)
        raise SystemExit(1)
    if args.write_progress:
        write_progress(books, written, verses, longest)
    print(f"Checked {sum(map(len, written.values()))}/{sum(map(len, books.values()))} chapters, "
          f"{verses} source verse addresses; longest sentence: {longest} words.")
    print("Coverage and sentence checks passed. This is not a full STE or meaning-fidelity audit.")


if __name__ == "__main__":
    main()
