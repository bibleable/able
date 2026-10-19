#!/usr/bin/env python3
"""Reproduce the full-Bible text audit; never certify meaning or reader access."""

import argparse
from collections import Counter
import hashlib
import json
import re
import subprocess
import sys

from check_able import fingerprint, load_source, review_file
from easy_coverage import ROOT, EDITION, chapter_inventory, render


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Save validation and progress snapshots')
    args = parser.parse_args()
    source_path = ROOT / 'comparison/bsb.txt'
    source = load_source(source_path)
    records, unexpected = chapter_inventory()
    snapshots = json.loads((ROOT / 'scripts/able_review_findings.json').read_text())['verses']
    drafts = [r for r in records if r['status'] == 'draft']
    files = [review_file(EDITION / r['path'], source, snapshots) for r in drafts]
    verses = {v['address']: v for f in files for v in f['verses']}
    flags = [{'address': v['address'], **flag}
             for f in files for v in f['verses'] for flag in v['findings']]
    structure_errors = sum(i['severity'] == 'error' for f in files for i in f['issues'])
    structure_errors += sum(f['severity'] == 'error' for f in flags)
    hashes = {r['path']: sha(EDITION / r['path']) for r in drafts}
    cue_issues = [ref for ref, v in verses.items()
                  if v['text'].count('📖') != int(bool(source.get(ref)))]
    other_cues = [ref for ref, v in verses.items()
                  if re.search(r'[\u2300-\u27bf\U0001f300-\U0001f4d5\U0001f4d7-\U0001faff]', v['text'])]
    followup = json.loads((EDITION / 'REVIEW_FOLLOWUP.json').read_text())
    current_followups = set()
    stale_followups = []
    for case in followup['cases']:
        ref = case['address']
        if (case['path'] in hashes and case['draft_sha256'] == hashes[case['path']]
                and ref in verses and case['text_sha256'] == fingerprint(verses[ref]['text'])
                and case['source_sha256'] == fingerprint(source.get(ref, ''))):
            current_followups.add((ref, case['checker_code']))
        else:
            stale_followups.append(ref)
    unaccounted = [f for f in flags if f['code'] != 'empty_reference'
                   and (f['address'], f['code']) not in current_followups]
    tests = subprocess.run(
        [sys.executable, '-m', 'unittest', 'discover', '-s', 'scripts', '-p', 'test_*.py'],
        cwd=ROOT, capture_output=True, text=True)
    test_count = re.search(r'Ran (\d+) tests?', tests.stdout + tests.stderr)
    complete = subprocess.run(
        [sys.executable, 'scripts/easy_coverage.py', '--require-complete'],
        cwd=ROOT, capture_output=True, text=True)
    books = list(dict.fromkeys(r['book'] for r in records))
    pending = [r['chapter'] for r in records if r['author_comparison'] != 'current_provisional']
    joins = sum(len(r['layout_findings']) for r in records)
    long_sentences = sum(f['code'] == 'sentence_length' for f in flags)
    problems = bool(len(records) != 1189 or len(books) != 66 or len(source) != 31102
                    or complete.returncode or unexpected or len(drafts) != len(records) or structure_errors
                    or set(verses) != set(source) or len(verses) != sum(len(f['verses']) for f in files)
                    or pending or joins or long_sentences or cue_issues or other_cues
                    or stale_followups or unaccounted or tests.returncode)
    result = {
        'schema_version': 1,
        'status': ('text audit needs repair' if problems else
                   'all full-Bible text drafts and provisional author comparisons complete; external review stages pending'),
        'source': {'path': 'comparison/bsb.txt', 'sha256': sha(source_path),
                   'books': len(books), 'chapters': len(records), 'addresses': len(source),
                   'blank_addresses': [r for r, t in source.items() if not t]},
        'counts': {'draft_chapters': len(drafts), 'complete_book_structures': sum(
            all(r['status'] == 'draft' for r in records if r['book'] == b) for b in books),
            'draft_addresses': sum(r['source_addresses'] for r in drafts),
            'missing_chapters': sum(r['status'] == 'missing' for r in records),
            'chapters_needing_structural_repair': sum(r['status'] == 'needs_repair' for r in records),
            'current_provisional_author_comparisons': len(records) - len(pending)},
        'checks': {'verse_structure_errors': structure_errors,
                   'scripture_sentences_over_20_words': long_sentences,
                   'possible_sentence_paragraph_joins': joins,
                   'stale_author_comparisons': sum(r['author_comparison'] == 'stale' for r in records),
                   'unexpected_files': unexpected, 'cue_count_issues': cue_issues,
                   'inconsistent_cues': other_cues, 'stale_review_followups': stale_followups,
                   'unaccounted_review_flags': unaccounted,
                   'require_complete_exit_code': complete.returncode,
                   'checker_regression_tests': {
                       'command': "python3 -m unittest discover -s scripts -p 'test_*.py'",
                       'tests': int(test_count[1]) if test_count else None,
                       'result': 'passed' if tests.returncode == 0 else 'failed'}},
        'pending_author_comparisons': pending,
        'review_flags': flags,
        'review_followup': {'path': 'REVIEW_FOLLOWUP.json',
                           'sha256': sha(EDITION / 'REVIEW_FOLLOWUP.json'),
                           'current_provisional_followups': len(current_followups)},
        'stages': {'independent_editorial_review': 'pending',
                   'intended_reader_testing': 'pending; no successful tests evidenced',
                   'tested_illustrations': 'pending', 'final_presentation_validation': 'pending',
                   'accessibility_certification': 'not claimed'},
        'limitations': [
            'Verse structure checks cannot establish meaning or source fidelity.',
            'Author comparisons and review follow-ups are provisional AI self-reviews, not independent editorial approval.',
            'Sentence-length checks exclude labeled editorial explanations.',
            'Paragraph and cue checks inspect text, not rendered typography or reader comprehension.',
            'The 27 stale_review flags concern original Mark 1 desk snapshots. REVIEW_FOLLOWUP.json documents a current provisional comparison of each concern without changing that historical evidence.',
            'The Luke 5:10 wording prompt remains visible; its labeled metaphor explanation has a current provisional follow-up.',
            'All sixteen blank BSB addresses retain editorial notes without invented scripture.'
        ],
        'chapter_sha256': hashes,
        'reproduce': ['python3 scripts/easy_validate.py --write',
                      'python3 scripts/easy_coverage.py --require-complete']
    }
    if args.write:
        (EDITION / 'VALIDATION.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        (EDITION / 'FULL_BIBLE_PROGRESS.md').write_text(render(records, unexpected))
    print(json.dumps({k: result[k] for k in ['status', 'counts', 'checks']}, indent=2))
    print('Review flag types:', dict(Counter(f['code'] for f in flags)))
    if tests.returncode:
        print(tests.stdout + tests.stderr, file=sys.stderr)
    return int(problems)


if __name__ == '__main__':
    raise SystemExit(main())
