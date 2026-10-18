#!/usr/bin/env python3
"""Offline ABLE checks and a review queue; never a semantic/bias certification."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CHAPTER = ROOT / "paraphrases/mark/mark1_1757488307.md"
HEADER = re.compile(r"^##\s+(.+?)\s+(\d+):(\d+)\s*$", re.MULTILINE)
ADDRESS = re.compile(r"^(.+?)\s+(\d+):(\d+)$")
WORDS = re.compile(r"[^\W_]+(?:['’][^\W_]+)*", re.UNICODE)
TESTS = {
    "T1": "Meaning preserved",
    "T2": "Nothing unsupported added",
    "T3": "Understandable without a wrong inference",
    "T4": "No added bias or stigma",
    "T5": "Context and speaker clear",
}
# These are prompts to inspect the context, not prohibited words or proof of bias.
RISKS = [
    (r"\bbad skin\b", ["T3", "T4"], "Explain the disease and check for added stigma."),
    (r"\bhot head\b|\bthe hot left\b", ["T3"], "Check whether the reader understands fever rather than anger or a headache."),
    (r"\bfish men\b", ["T3"], "Check whether this means people who catch fish to the reader."),
    (r"\bcatch people\b", ["T3"], "Explain the metaphor; check for an inference of trapping people."),
    (r"\blaw men\b", ["T3", "T5"], "Identify the people; check for confusion with police."),
    ("👻", ["T3", "T4"], "Check whether the emoji introduces a cartoon-ghost interpretation."),
]


def clean(text):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", text)).strip()


def fingerprint(text):
    return hashlib.sha256(clean(text).encode("utf-8")).hexdigest()


def address(book, chapter, verse):
    # Accept singular Psalm headings against this repository's Psalms source.
    book = "Psalms" if book == "Psalm" else book
    return f"{book} {int(chapter)}:{int(verse)}"


def load_source(path):
    source = {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        ref, sep, text = line.partition("\t")
        match = ADDRESS.fullmatch(ref)
        if not sep or not match:
            raise ValueError(f"Malformed source line {number}: expected address, tab, text")
        ref = address(*match.groups())
        if ref in source:
            raise ValueError(f"Duplicate source address: {ref}")
        source[ref] = text.strip()
    if not source:
        raise ValueError("Source contains no verses")
    return source


def parse_verses(text):
    headers = list(HEADER.finditer(text))
    verses = []
    for index, header in enumerate(headers):
        end = headers[index + 1].start() if index + 1 < len(headers) else len(text)
        body = text[header.end():end].strip()
        # Easy Read notes run from their label to the next verse. Do not treat
        # their vocabulary, sentence length, or explanations as scripture text.
        parts = re.split(r"(?m)^\*\*(?:Help\b|About\b)", body, maxsplit=1)
        verses.append({
            "address": address(*header.groups()),
            "line": text.count("\n", 0, header.start()) + 1,
            "text": clean(parts[0]),
            "has_editorial_note": len(parts) > 1,
        })
    return verses


def finding(code, severity, message, tests=None, **extra):
    return dict(code=code, severity=severity, message=message, tests=tests or [], **extra)


def review_file(path, source, snapshots, max_words=20):
    text = path.read_text(encoding="utf-8")
    verses = parse_verses(text)
    issues = []
    if not verses:
        issues.append(finding("no_verses", "error", "No valid verse headings found."))
    for number, line in enumerate(text.splitlines(), 1):
        if re.match(r"^##\s+.*\d+\s*:", line) and not HEADER.fullmatch(line):
            issues.append(finding("malformed_heading", "error", "Malformed verse heading.", line=number))
    refs = [v["address"] for v in verses]
    counts = Counter(refs)
    for ref, count in counts.items():
        if count > 1:
            issues.append(finding("duplicate_verse", "error", f"{ref} occurs {count} times."))
    chapters = list(dict.fromkeys(ref.rsplit(":", 1)[0] for ref in refs))
    if len(chapters) > 1:
        issues.append(finding("mixed_chapters", "error", "Expected one chapter per Markdown file."))
    for chapter in chapters:
        expected = [ref for ref in source if ref.rsplit(":", 1)[0] == chapter and source[ref]]
        actual = [ref for ref in refs if ref.rsplit(":", 1)[0] == chapter]
        missing = sorted(set(expected) - set(actual), key=lambda ref: int(ref.rsplit(":", 1)[1]))
        if missing:
            issues.append(finding("missing_verses", "error", "Missing: " + ", ".join(missing)))
        numbers = [int(ref.rsplit(":", 1)[1]) for ref in actual]
        if numbers != sorted(numbers):
            issues.append(finding("verse_order", "error", f"Verses in {chapter} are out of order."))
    for verse in verses:
        ref, body = verse["address"], verse["text"]
        flags = []
        verse["source"] = source.get(ref)
        if ref not in source:
            flags.append(finding("unknown_address", "error", "Address not found in the reference text."))
        elif not source[ref]:
            flags.append(finding("empty_reference", "review", "Reference has an address but no verse text; review the edition/numbering difference.", ["T1"]))
        # A numbered entry with no BSB text can retain its address using only
        # a labeled editorial note. Do not require invented scripture there.
        source_gap_note = (ref in source and not source[ref] and verse["has_editorial_note"])
        if not WORDS.search(body) and not source_gap_note:
            flags.append(finding("empty_verse", "error", "Verse has no words."))
        sentences = re.split(r"[.!?]+(?:[\s\"'’”]|$)", body)
        longest = max((len(WORDS.findall(s)) for s in sentences), default=0)
        verse["longest_sentence_words"] = longest
        if longest > max_words:
            flags.append(finding("sentence_length", "review", f"Longest sentence has {longest} words; configured limit is {max_words}.", ["T3"]))
        for pattern, tests, message in RISKS:
            match = re.search(pattern, body, re.IGNORECASE)
            if match:
                flags.append(finding("wording_risk", "review", message, tests, evidence=match.group()))
        snapshot = snapshots.get(ref)
        if snapshot:
            unchanged = (snapshot["text_sha256"] == fingerprint(body)
                         and snapshot["source_sha256"] == fingerprint(source.get(ref, "")))
            verse["editorial_review"] = "recorded_concerns" if unchanged else "stale"
            if unchanged:
                for item in snapshot["findings"]:
                    flags.append(finding("editorial_finding", "review", item["message"], item["tests"], origin="Recorded Mark 1 desk review"))
            else:
                flags.append(finding("stale_review", "review", "ABLE wording or reference changed. Earlier findings need fresh editorial review.", list(TESTS)))
        else:
            verse["editorial_review"] = "not_recorded"
        verse["reader_review"] = "pending"
        verse["findings"] = flags
    return {"path": str(path), "issues": issues, "verses": verses}


def markdown(report):
    lines = ["# ABLE checks", "", report["limitations"], "",
             f"Files: {len(report['files'])}; verses: {report['summary']['verses']}; "
             f"structural errors: {report['summary']['errors']}; "
             f"verses flagged for review: {report['summary']['flagged_verses']}.", "",
             "Tests: " + "; ".join(f"{key}: {value}" for key, value in TESTS.items()), ""]
    for file in report["files"]:
        lines.extend([f"## {file['path']}", ""])
        for issue in file["issues"]:
            lines.append(f"- ERROR [{issue['code']}]: {issue['message']}")
        for verse in file["verses"]:
            if not verse["findings"]:
                continue
            lines.extend(["", f"### {verse['address']} (line {verse['line']})", "",
                          f"ABLE: {verse['text']}", "", f"Reference: {verse['source'] or '(not found)'}", ""])
            for item in verse["findings"]:
                tests = ", ".join(item["tests"]) or "structure"
                lines.append(f"- {item['severity'].upper()} [{item['code']}; {tests}]: {item['message']}")
        remaining = [v["address"] for v in file["verses"] if not v["findings"]]
        if remaining:
            lines.extend(["", "No flags (not a semantic or reader-test pass): " + ", ".join(remaining)])
        lines.append("")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="Chapter files or directories; default: original Mark 1")
    parser.add_argument("--source", type=Path, default=ROOT / "comparison/bsb.txt", help="Tab-separated reference text")
    parser.add_argument("--reviews", type=Path, default=ROOT / "scripts/able_review_findings.json")
    parser.add_argument("--max-sentence-words", type=int, default=20)
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--output", type=Path, help="Write report here instead of stdout")
    parser.add_argument("--fail-on-review", action="store_true", help="Also exit 1 for review flags (does not assess unflagged verses)")
    args = parser.parse_args()
    if args.max_sentence_words < 1:
        parser.error("--max-sentence-words must be positive")
    try:
        source = load_source(args.source)
        snapshots = json.loads(args.reviews.read_text(encoding="utf-8"))["verses"]
        paths = []
        for path in args.paths or [DEFAULT_CHAPTER]:
            if not path.exists():
                raise ValueError(f"Input does not exist: {path}")
            if path.is_dir():
                # Skip chapter indexes/documentation, but keep malformed chapter
                # files so they cannot silently disappear from validation.
                paths.extend(p.resolve() for p in path.rglob("*.md")
                             if re.search(r"\d", p.stem))
            else:
                paths.append(path.resolve())
        paths = sorted(set(paths))
        if not paths:
            raise ValueError("No chapter Markdown files found")
        files = [review_file(p, source, snapshots, args.max_sentence_words) for p in paths]
        verses = [v for file in files for v in file["verses"]]
        all_findings = [item for file in files for item in file["issues"]]
        all_findings.extend(item for verse in verses for item in verse["findings"])
        report = {
            "reference": str(args.source.resolve()),
            "limitations": "Automatic checks find structural errors and possible wording risks. "
                "Recorded editorial concerns apply only to matching text and source snapshots. "
                "No automatic semantic, theological, or bias pass is issued. "
                "All five tests need human judgment; comprehension testing with intended readers remains pending for every verse.",
            "tests": TESTS,
            "summary": {
                "verses": len(verses),
                "errors": sum(item["severity"] == "error" for item in all_findings),
                "flagged_verses": sum(bool(v["findings"]) for v in verses),
                "reader_reviews_pending": len(verses),
            },
            "files": files,
        }
        output = json.dumps(report, ensure_ascii=False, indent=2) + "\n" if args.format == "json" else markdown(report)
        if args.output:
            args.output.write_text(output, encoding="utf-8")
        else:
            print(output, end="")
        return int(bool(report["summary"]["errors"]) or
                   (args.fail_on_review and any(i["severity"] == "review" for i in all_findings)))
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"check_able: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
