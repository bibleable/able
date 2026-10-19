# ABLE 0.3.4-easy

Easy Read Bible paraphrase drafts written directly from the Berean Standard Bible in [`comparison/bsb.txt`](../../comparison/bsb.txt).

The existing ABLE book folders and chapter basenames supply the file structure. Their paraphrase wording is not the source for these drafts.

## Full-Bible scope and current progress

The active request is **all 66 books and all 1,189 chapters**. The edition is still in progress.

See [full-Bible progress](FULL_BIBLE_PROGRESS.md) for current counts, all drafted chapter links, missing chapters by book, and original filename gaps. Regenerate it with `python3 scripts/easy_coverage.py --write`. Use `--require-complete` to make the inventory command fail while any chapter remains absent or structurally incomplete.

The inventory also distinguishes current provisional author comparisons from missing or stale comparison records. It checks source and draft hashes, and flags likely sentences sharing a paragraph in both scripture and editorial explanations. These checks do not establish fidelity or reader comprehension. The JSON inventory exposes each chapter’s separate review and presentation stages.

The [earlier 50-chapter batch index](PROGRESS.md) records a completed historical request. That batch and three other existing Psalms supplied the initial **53 chapter files and 1,573 verse addresses**. Existing drafts are retained for review as the full edition is written.

Folder names and existing chapter filenames come from the original ABLE edition. BSB's `Psalm` maps to `psalms`, and `Song of Solomon` maps to `songofsongs`. The original structure has no chapter filenames for 2 Samuel 21–24; their planned paths follow the same naming convention and are listed in the full-Bible inventory. Ruth 1 has two historical filenames; the inventory records both and selects an existing Easy Read filename if present, otherwise the latest original timestamp.

The BSB source contains **31,102 numbered addresses**, including **16 entries without verse text**. Those entries retain their headings with clearly labeled editorial notes. No scripture is invented to fill them.

## Reading format

Use familiar words, short sentences, clear subjects, and space between ideas. Each sentence is a separate paragraph. Keep verse addresses, names, numbers, speakers, conditions, prayers, and judgments. Use a small emoji cue with each verse to retain ABLE's existing style.

Material headed **About this chapter** introduces the setting. Material labeled **Help with...** explains words, images, or background. These labels distinguish editorial explanations from the Bible paraphrase. Metaphors are retained or explained near their use. The drafts include difficult passages rather than silently removing them.

## Guidance and review

Writing and layout draw on [Inclusion Europe's Easy-to-read checklist](https://www.inclusion-europe.eu/wp-content/uploads/2020/06/Easy-to-read-checklist-Inclusion-Europe.pdf), [UK Easy Read guidance](https://www.gov.uk/government/publications/inclusive-communication/accessible-communication-formats#easy-read-and-makaton), and [W3C guidance on clear content](https://www.w3.org/WAI/WCAG2/supplemental/objectives/o3-clear-content/).

These are text drafts for review with intended readers. Emoji cues do not replace purpose-made, tested Easy Read illustrations. Font, text size, and page layout need checking in the final reading or print format. No Easy Read certification or logo is claimed.

Checks compare chapter filenames, verse counts, verse order, and sentence layout. The new chapters use sentences of no more than 20 words. Structural checks do not establish comprehension or replace reader review.

The [authoring and review requirements](AUTHORING.md) describe the consistent writing process and the remaining review work.
