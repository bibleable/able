#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import re
import sys
from xml.etree.ElementTree import iterparse

# Minimal USFM/USFX book code → English name mapping (extend as desired)
BOOK_NAMES = {
    "GEN": "Genesis",
    "EXO": "Exodus",
    "LEV": "Leviticus",
    "NUM": "Numbers",
    "DEU": "Deuteronomy",
    "JOS": "Joshua",
    "JDG": "Judges",
    "RUT": "Ruth",
    "1SA": "1 Samuel", "2SA": "2 Samuel",
    "1KI": "1 Kings",  "2KI": "2 Kings",
    "1CH": "1 Chronicles", "2CH": "2 Chronicles",
    "EZR": "Ezra", "NEH": "Nehemiah", "EST": "Esther",
    "JOB": "Job", "PSA": "Psalms", "PRO": "Proverbs",
    "ECC": "Ecclesiastes", "SNG": "Song of Songs",
    "ISA": "Isaiah", "JER": "Jeremiah", "LAM": "Lamentations",
    "EZK": "Ezekiel", "DAN": "Daniel",
    "HOS": "Hosea", "JOL": "Joel", "AMO": "Amos",
    "OBA": "Obadiah", "JON": "Jonah", "MIC": "Micah",
    "NAM": "Nahum", "HAB": "Habakkuk", "ZEP": "Zephaniah",
    "HAG": "Haggai", "ZEC": "Zechariah", "MAL": "Malachi",
    "MAT": "Matthew", "MRK": "Mark", "LUK": "Luke", "JHN": "John",
    "ACT": "Acts", "ROM": "Romans",
    "1CO": "1 Corinthians", "2CO": "2 Corinthians",
    "GAL": "Galatians", "EPH": "Ephesians", "PHP": "Philippians",
    "COL": "Colossians", "1TH": "1 Thessalonians", "2TH": "2 Thessalonians",
    "1TI": "1 Timothy", "2TI": "2 Timothy",
    "TIT": "Titus", "PHM": "Philemon",
    "HEB": "Hebrews", "JAS": "James",
    "1PE": "1 Peter", "2PE": "2 Peter",
    "1JN": "1 John", "2JN": "2 John", "3JN": "3 John",
    "JUD": "Jude", "REV": "Revelation",
}

def normspace(s: str) -> str:
    # collapse whitespace but preserve CJK punctuation spacing naturally
    s = s.replace("\u00A0", " ")
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    # Trim around
    return s.strip()

def usfx_to_markdown(xml_path: str):
    """
    Stream-parse USFX and yield (book_name, chap, verse, text) tuples.
    Works by:
      - starting a verse on <v id="..."/>
      - collecting .text/.tail of all nodes until <ve/>
      - closing the verse on <ve/>
    """
    # Track where we are
    current_book_code = None
    current_book_name = None
    current_chapter = None

    in_verse = False
    current_verse = None
    buf_parts = []

    # We’ll use iterparse with start/end to capture text and tails
    # Important: expand namespaces off (USFX uses attributes; tags are usually un-namespaced)
    context = iterparse(xml_path, events=("start", "end"))

    for event, elem in context:
        tag = elem.tag

        # Normalize tag name if namespace appears (just in case)
        if "}" in tag:
            tag = tag.split("}", 1)[1]

        if event == "start":
            if tag == "book":
                current_book_code = elem.get("id")
                current_book_name = BOOK_NAMES.get(current_book_code, current_book_code or "UnknownBook")
            elif tag == "c":
                # <c id="1"/>
                cid = elem.get("id")
                current_chapter = int(cid) if cid and cid.isdigit() else cid
            elif tag == "v":
                # Begin a verse
                vid = elem.get("id")
                current_verse = int(vid) if vid and str(vid).isdigit() else vid
                in_verse = True
                buf_parts = []
                # text inside <v> ... (rare, but just in case)
                if elem.text and in_verse:
                    buf_parts.append(elem.text)
            elif in_verse:
                # Any other element starting inside a verse: capture its .text if present
                if elem.text:
                    buf_parts.append(elem.text)

            # Close verse on seeing <ve/> start
            if tag == "ve" and in_verse:
                # finalize current verse
                verse_text = normspace("".join(buf_parts))
                yield (current_book_name, current_chapter, current_verse, verse_text)
                in_verse = False
                current_verse = None
                buf_parts = []

        elif event == "end":
            if in_verse:
                # Collect tails as we close any element while inside a verse
                if elem.tail:
                    buf_parts.append(elem.tail)

            # We can safely clear large elements to keep memory down on huge files
            # but avoid clearing parents we still need. Here it's OK to clear leaves frequently.
            # Do not clear 'book' until after leaving it; but safe heuristic:
            if tag not in ("book",):
                elem.clear()

    # Safety: if file ends mid-verse without a <ve/>, flush what we have
    if in_verse and buf_parts:
        verse_text = normspace("".join(buf_parts))
        yield (current_book_name, current_chapter, current_verse, verse_text)

def main():
    ap = argparse.ArgumentParser(description="Convert USFX XML to Markdown per-verse lines.")
    ap.add_argument("input_xml", help="Path to USFX XML file")
    ap.add_argument("-o", "--output", help="Output Markdown file (default: stdout)")
    args = ap.parse_args()

    out_stream = open(args.output, "w", encoding="utf-8") if args.output else sys.stdout
    close_stream = (out_stream is not sys.stdout)

    try:
        for book, chap, verse, text in usfx_to_markdown(args.input_xml):
            # Skip empty verses just in case
            if not text:
                continue
            # Format like: ## Genesis 1:1\n<text>\n
            header = f"## {book} {chap}:{verse}"
            print(header, file=out_stream)
            print(text, file=out_stream)
    finally:
        if close_stream:
            out_stream.close()

if __name__ == "__main__":
    main()
