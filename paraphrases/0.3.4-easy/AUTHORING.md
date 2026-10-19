# Authoring and review requirements

## Scope and source

Complete all 66 books and 1,189 chapters under this edition's existing book folders. Read `comparison/bsb.txt` directly for every new chapter. Original ABLE files provide filenames, not source wording. Preserve existing Easy Read drafts and review them against BSB as the edition develops.

Keep every BSB verse address in its original order. Keep names, numbers, places, actions, speakers, promises, conditions, prayers, judgments, and difficult material. Do not shorten a chapter by dropping verses, lists, repeated teaching, or disturbing events. Do not replace full chapters with narrative summaries.

Sixteen BSB entries have a number but no verse text. At those addresses, use the verse heading followed by a bold `About this verse` editorial note explaining that the source has no text. Do not fill the gap from another translation. These entries remain flagged for edition review by the structural checker.

## Easy Read writing

Use the accessible information approach described in the edition README: Inclusion Europe and UK Easy Read guidance, supported by W3C clear-content guidance.

- Use familiar, concrete words and short, direct sentences. Aim for no more than 20 words per scripture sentence.
- Give each sentence its own paragraph, with a blank line between sentences.
- State who is speaking or acting. Repeat a name where a pronoun could confuse the reader.
- Keep one idea at a time and keep actions in a clear order.
- Retain a small emoji cue per verse with source text. Check that the cue does not introduce an unsupported meaning.
- Keep important Bible terms when replacing them would change the meaning. Explain them in familiar words nearby.
- Keep metaphors or strong images when they matter. Explain their intended sense in a labeled note, without presenting an interpretation as extra scripture.
- Explain religious terms such as clean and unclean without implying that illness or disability makes a person morally bad.
- Keep conditions and qualifications. A conditional promise must not become an unconditional promise.
- Preserve the source's distinction between what a narrator says, what a character says, and what God or Jesus says.

Use `**About this chapter**` before verse headings for setting. Within a verse, place all paraphrase text first, then a bold `**Help with...**` or `**About...**` note. Notes run to the next verse heading and are excluded from scripture checks. Do not resume scripture text after a note in the same verse.

## Review and evidence

Writing and checking are different stages. A complete file is a text draft; it has not automatically passed a meaning review or reader test.

For each chapter, compare the draft against the source for these five questions:

1. Is the source meaning preserved, including every detail needed to follow the passage?
2. Has anything unsupported been added?
3. Could the wording lead a reader to a wrong inference?
4. Has simplification added bias or stigma?
5. Are context and speakers clear?

After substantive edits, review the affected verses again. Existing recorded Mark 1 findings apply to the original wording, not automatically to these new drafts; stale findings request a fresh review. Keep unresolved interpretations visible for further editorial review.

[Author comparison records](AUTHOR_REVIEW.json) document provisional comparisons against BSB. Each record includes the draft hash, the chapter source hash, and notes about the comparison. An edit to either text makes the earlier comparison stale. These are AI author records, separate from independent editorial assessment and testing with readers; neither is claimed by an author-comparison record. Chapters without a record still need a recorded author comparison.

Use these offline checks from the repository root:

```sh
python3 scripts/easy_coverage.py --write
python3 scripts/easy_coverage.py --require-complete
python3 scripts/check_able.py paraphrases/0.3.4-easy --format json --output /tmp/able-easy-checks.json
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/easy_validate.py --write
```

The full-Bible inventory checks that every intended chapter exists, that each filename contains its intended chapter, and that every source address is present exactly once in order. The verse checker also checks text, sentence length, and known wording risks. Neither tool proves theological accuracy, vocabulary suitability, or learner comprehension. A zero-error result is not a meaning or accessibility certification.

Independent editorial assessment, review with intended readers, tested illustrations, and final font, spacing, and presentation checks remain pending. Emoji are supplementary cues and do not replace tested Easy Read illustrations.

The full text audit also verifies the edition's consistent 📖 cue and current hash-bound follow-ups in `REVIEW_FOLLOWUP.json`. Historical Mark 1 findings remain in their original file. Their checker snapshot warnings are not erased: the follow-up records document the fresh provisional comparison separately. A retained wording-risk phrase may remain when it preserves a source metaphor and has a labeled explanation; its context review must be recorded without claiming reader validation.

## Book commits

The user requested a commit after every book. Commit each newly finished book after all its chapter drafts, provisional source comparisons, coverage checks, and layout checks are complete. Include relevant tracking updates and keep unrelated user changes out of the commit. A book commit records completed text drafts, not independent editorial approval or reader testing. Do not commit a partial book merely because a goal turn ends.

The user has authorized continuing the full-Bible work and book commits without conversational confirmation questions. Continue within that scope. Required host permission prompts for Git metadata remain separate from task authorization.
