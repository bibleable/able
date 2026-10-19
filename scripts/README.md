# Checking ABLE

Run with Python 3. No packages, network access, or API keys are needed.

```sh
# Original Mark 1, including the 27 recorded editorial concerns
python3 scripts/check_able.py

# All original Mark chapters
python3 scripts/check_able.py paraphrases/mark

# Easy Read edition, machine-readable report
python3 scripts/check_able.py paraphrases/0.3.4-easy --format json --output /tmp/able-checks.json

# Full-Bible inventory, including chapters with no draft file yet
python3 scripts/easy_coverage.py --write

# Fail while any of the 1,189 chapters is missing or needs structural repair
python3 scripts/easy_coverage.py --require-complete

# Save a readable Mark 1 report
python3 scripts/check_able.py --output /tmp/able-mark1-review.md

# Fail a CI check for review flags as well as structural errors
python3 scripts/check_able.py --fail-on-review

# Checker regression tests
python3 -m unittest discover -s scripts -p 'test_*.py'
```

The default reference is `comparison/bsb.txt`. Supply `--source PATH` for another
reference using the same `Book chapter:verse<TAB>text` format. Differences in
verse numbering between reference editions require human review.
Blank numbered entries in a reference are retained but not required for coverage;
an ABLE verse at such an address receives an edition-review flag.

## What is tested

Structural checks detect missing/duplicate/out-of-order verses, unknown addresses,
empty verses, malformed verse headings, and mixed chapters. Coverage is checked
against the reference for each chapter present in a file; it cannot detect an
entirely absent chapter or prove that a file contains its intended chapter.
Directory inputs scan Markdown filenames containing a digit, skipping indexes.
Repeated addresses in different files are allowed because editions may coexist.

Readability checks flag sentences exceeding 20 words (configurable with
`--max-sentence-words`). Context-sensitive wording patterns flag possible
misunderstanding or stigma. These are review prompts, not automatic failures of
meaning or bias. Short sentences do not establish vocabulary level or comprehension.

The five editorial tests are meaning, unsupported additions, comprehension,
added bias/stigma, and context/speaker clarity. The script includes the 27
provisional Mark 1 concerns from the desk review in `able_review_findings.json`.
These are recorded human-review judgments, not newly computed semantic tests.
Matching normalized ABLE and source hashes keep findings tied to the wording
reviewed. If either changes, the script requests fresh review rather than declaring
the issue resolved. Other verses have no recorded editorial assessment.

The Markdown report lists findings with ABLE and reference text. JSON also includes
every verse, review provenance, and pending reader-review status. No result means
"all five tests passed": even an unflagged verse requires human judgment and testing
with intended readers. Emoji interpretations also require reader testing.

Supported verse headings look like `## Mark 1:1`. Inline `<jesus>` tags are removed
for analysis. In Easy Read files, a bold `Help...` or `About...` label inside a verse
starts editorial notes extending to the next verse; notes are excluded from verse
checks. Scripture should precede these notes. These format assumptions should be
updated if the authoring format changes.

A blank BSB numbered entry can be represented by its heading and a labeled
editorial note alone. This retains an `empty_reference` review flag without
requiring invented paraphrase text. Notes cannot replace a nonempty source verse.
`easy_coverage.py` requires all numbered source addresses, including these blank
entries, and rejects paraphrase text supplied at a blank source address. Its
`draft` status means structural coverage only; it does not certify meaning.

The full-Bible inventory also checks `AUTHOR_REVIEW.json` against the exact draft
file hash, chapter source hash, selected path, source address count, and review
type. It distinguishes `current_provisional`, `stale`, and `not_recorded` author
comparisons. It reports likely sentences sharing a paragraph, including editorial
notes, without treating that heuristic as proof of accessibility. JSON includes
review stages and line references for every chapter; the Markdown inventory
summarizes current comparisons and pending review work. Independent editorial
review, intended-reader testing, tested illustrations, and final presentation
validation remain separate pending stages. Regenerate the inventory after edits.

Exit codes: **0** means no structural errors were found; **1** means structural
errors (or review flags with `--fail-on-review`); **2** means an input/configuration
error. Exit 0 does not certify accuracy, lack of bias, or reader comprehension.
The script reads drafts without modifying them.

## AI meaning checks

`check_meaning.py` makes fresh AI assessments using the OpenAI Responses API and
[Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses).
It uses Python's standard library; no packages are required. It does not load the
recorded Mark 1 findings. Choose a model available to your API account that supports
Responses and Structured Outputs. Configure `OPENAI_API_KEY` and `OPENAI_MODEL`
in your environment; never put an API key in a command argument or commit it.

```sh
# Preview all requests for original Mark 1 without credentials or network access
python3 scripts/check_meaning.py --dry-run --output /tmp/able-meaning-requests.json

# Review one verse first, using the model/key configured in your environment
python3 scripts/check_meaning.py --verse 'Mark 1:7' --output /tmp/able-meaning.json

# Review all 45 verses of original Mark 1 (9 API requests by default)
python3 scripts/check_meaning.py --format markdown --output /tmp/able-meaning.md

# Choose another chapter or override the configured model
python3 scripts/check_meaning.py paraphrases/mark/mark2_1757488422.md --model YOUR_MODEL --limit 5
```

Live runs send selected ABLE text, reference text, and up to two nearby verses on
each side within the same chapter to OpenAI and incur API usage charges. Notes
are excluded using the same formatting rules as `check_able.py`. The request sets
`store: false`. Dry-run output includes the complete instructions, schema, and texts
to be sent; its placeholder model must be configured before making live calls.

Each verse receives `no_issue_found`, `needs_review`, or `uncertain`, a summary,
and findings tagged with the five tests. Findings include reference and ABLE
evidence, an explanation, and a suggested change. Exact quotes are checked against
the target verse; an empty ABLE quote represents an omission. This validation
detects fabricated quotations, not incorrect interpretations. The AI is asked to
accept faithful simplification and distinguish added bias from difficult source
content. It cannot establish theological truth or actual learner comprehension.

The default is one chapter file, original Mark 1. Repeat `--verse` to select
addresses. `--limit` caps targets; `--batch-size` defaults to 5. Structural errors
must be fixed before AI calls. Missing reference text requires manual handling.
Use `--source` for a different tab-separated reference. Context is local to the
chapter; uncertain interpretations may need wider context and expert review.

With `--output`, results are saved after each completed batch. A failed, refused,
incomplete, or invalid AI response stops the run with exit **2**, preserving prior
results and leaving remaining verses `not_checked`. There are no automatic retries
or resume/cache features; rerunning performs fresh calls. JSON reports record text
hashes, prompt version, requested/returned model, response IDs, and token usage.
Markdown reports show the text, findings, and unchecked verses for reading.

Exit **0** means the requested run completed, not that every verse was approved.
With `--fail-on-review`, `needs_review` or `uncertain` gives exit **1**. All results,
including `no_issue_found`, remain provisional and require human review.
