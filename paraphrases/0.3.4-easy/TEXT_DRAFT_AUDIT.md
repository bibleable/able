# Full-Bible text-draft audit

All 66 books and 1,189 chapters have text drafts written from `comparison/bsb.txt`. All 31,102 source addresses appear exactly once in their chapters, in source order. Each chapter has a current, hash-bound provisional AI author comparison, including the retained drafts.

These are completed text drafts and provisional comparisons. They are not independently approved or reader-tested Easy Read publications.

## Recorded checks

| Check | Result |
| --- | --- |
| Chapter drafts | 1,189 / 1,189 |
| Books with every chapter drafted | 66 / 66 |
| Source verse addresses | 31,102 / 31,102 |
| Current provisional author comparisons | 1,189 / 1,189 |
| Missing chapters or chapters needing structural repair | 0 |
| Verse structure errors | 0 |
| Scripture sentences over 20 words | 0 |
| Possible sentences sharing a paragraph | 0 |
| Inconsistent or missing scripture cues | 0 |
| Stale chapter author comparisons or review follow-ups | 0 |
| Unexpected chapter files | 0 |
| Checker regression tests | 28 passed |

[VALIDATION.json](VALIDATION.json) binds this checkpoint to the source, every chapter file, and the review-follow-up file. [FULL_BIBLE_PROGRESS.md](FULL_BIBLE_PROGRESS.md) links every chapter and records the book totals. Re-run the audit after any source, chapter, or review-record edit:

```sh
python3 scripts/easy_validate.py --write
python3 scripts/easy_coverage.py --require-complete
```

## Structure and retained material

Existing book folders and selected original chapter basenames are preserved. The original structure lacked filenames for 2 Samuel 21–24. Those four chapters are supplied with the original naming pattern and fixed suffix `1792322671`; the progress inventory lists their paths. Ruth 1's two historical filenames remain documented, with the existing Easy Read filename selected.

Retained drafts were compared against BSB and corrected where needed. [AUTHOR_REVIEW.json](AUTHOR_REVIEW.json) records the chapter-specific comparisons, source hashes, and draft hashes. Comparisons address meaning, unsupported additions, possible wrong inferences, bias, and clarity of speakers. Difficult material remains in the drafts; explanatory notes are labeled separately from scripture.

## Visible review flags

The checker still produces 44 review prompts. These are accounted for; they are not hidden to obtain a zero-flag result.

- **16 blank BSB addresses:** Each has its source verse heading and an editorial note, with no invented scripture or imported translation text.
- **27 historical Mark 1 snapshot warnings:** The original desk findings remain unchanged in `scripts/able_review_findings.json`. A fresh provisional comparison of each concern is recorded in [REVIEW_FOLLOWUP.json](REVIEW_FOLLOWUP.json), bound to the current chapter and source. The historical checker snapshots still differ from the new text.
- **1 Luke 5:10 wording prompt:** The source's fishing metaphor is retained. A labeled note explains following Jesus rather than trapping people. Its provisional context review is recorded in the same follow-up file.

None of these follow-ups is independent editorial approval or evidence that readers understood the wording or cues.

## Stages still pending

- Independent editorial and source-fidelity assessment, including difficult and interpretively disputed passages.
- Comprehension testing with intended readers and revisions informed by that testing.
- Purpose-made illustrations and testing of their meaning; emoji are supplementary cues.
- Validation of final fonts, text size, line length, spacing, navigation, and page or screen presentation.

No successful reader testing, accessibility certification, or certification logo is claimed. The text follows the writing approach linked in the [edition README](README.md), but automated structural checks and provisional AI comparisons cannot establish comprehension, complete semantic accuracy, or final presentation quality.
