"""Ensure whole-Bible inventory cannot hide missing or misidentified chapters."""

from pathlib import Path
import hashlib
import json
import tempfile
import unittest

from easy_coverage import chapter_inventory, folder_for, number_ranges, sentence_layout_findings


class CoverageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "comparison").mkdir()
        (self.root / "comparison/bsb.txt").write_text(
            "Mark 1:1\tFirst verse.\nMark 1:2\tSecond verse.\nMark 2:1\tNext chapter.\n",
            encoding="utf-8")

    def draft(self, text, name="mark1_123.md"):
        original = self.root / "paraphrases/mark" / name
        original.parent.mkdir(parents=True, exist_ok=True)
        original.write_text("Original wording is not used.", encoding="utf-8")
        easy = self.root / "paraphrases/0.3.4-easy/mark" / name
        easy.parent.mkdir(parents=True, exist_ok=True)
        easy.write_text(text, encoding="utf-8")
        return easy

    def inventory(self):
        return chapter_inventory(self.root)

    def test_entirely_absent_chapter_stays_missing(self):
        self.draft("## Mark 1:1\nFirst.\n## Mark 1:2\nSecond.\n")
        records, unexpected = self.inventory()
        self.assertEqual([r["status"] for r in records], ["draft", "missing"])
        self.assertEqual(records[0]["path"], "mark/mark1_123.md")
        self.assertEqual(unexpected, [])

    def test_complete_wrong_chapter_cannot_pass(self):
        self.draft("## Mark 2:1\nNext chapter.\n")
        records, _ = self.inventory()
        self.assertEqual(records[0]["status"], "needs_repair")

    def test_duplicate_or_out_of_order_verses_fail(self):
        for text in ["## Mark 1:2\nSecond.\n## Mark 1:1\nFirst.\n",
                     "## Mark 1:1\nFirst.\n## Mark 1:1\nAgain.\n## Mark 1:2\nSecond.\n"]:
            with self.subTest(text=text):
                self.draft(text)
                self.assertEqual(self.inventory()[0][0]["status"], "needs_repair")

    def test_help_note_is_not_a_paraphrase(self):
        self.draft("## Mark 1:1\n**Help with a word:** Explanation.\n## Mark 1:2\nSecond.\n")
        self.assertEqual(self.inventory()[0][0]["status"], "needs_repair")

    def test_blank_source_address_needs_labeled_note(self):
        (self.root / "comparison/bsb.txt").write_text("Mark 1:1\t\n", encoding="utf-8")
        self.draft("## Mark 1:1\n**About this verse:** BSB has no text here.\n")
        self.assertEqual(self.inventory()[0][0]["status"], "draft")
        self.draft("## Mark 1:1\nImported words.\n")
        self.assertEqual(self.inventory()[0][0]["status"], "needs_repair")
        self.draft("## Mark 1:1\nImported words.\n**About this verse:** BSB has no text here.\n")
        self.assertEqual(self.inventory()[0][0]["status"], "needs_repair")

    def test_unexpected_file_is_reported(self):
        self.draft("## Mark 1:1\nFirst.\n", name="mark99_123.md")
        self.assertEqual(self.inventory()[1], ["mark/mark99_123.md"])

    def test_original_variants_prefer_existing_draft(self):
        self.draft("## Mark 1:1\nFirst.\n## Mark 1:2\nSecond.\n", name="mark1_123.md")
        (self.root / "paraphrases/mark/mark1_456.md").write_text("Later original.", encoding="utf-8")
        records, _ = self.inventory()
        self.assertEqual(records[0]["path"], "mark/mark1_123.md")
        self.assertEqual(len(records[0]["original_filenames"]), 2)

    def test_book_aliases_and_ranges(self):
        self.assertEqual(folder_for("Psalms"), "psalms")
        self.assertEqual(folder_for("Song of Solomon"), "songofsongs")
        self.assertEqual(number_ranges([1, 2, 3, 5, 7, 8]), "1–3, 5, 7–8")

    def test_layout_detects_scripture_and_editorial_joins(self):
        self.assertEqual(len(sentence_layout_findings(
            '## Mark 1:1\n\nFirst. 📖 Second.\n\n**Help:** A word. Another idea.')), 2)
        self.assertEqual(sentence_layout_findings(
            '## Mark 1:1\n\n“Who?” he asked. 📖\n\nThey answered.\n\n**Help:** A word.'), [])
        self.assertEqual(sentence_layout_findings('There are 1,000 people. 📖'), [])
        repeated = sentence_layout_findings('First. Second.\n\nFirst. Second.')
        self.assertEqual([item['line'] for item in repeated], [1, 3])

    def test_review_stales_when_source_draft_or_identity_changes(self):
        p = self.draft('## Mark 1:1\n\nFirst. 📖\n\n## Mark 1:2\n\nSecond. 📖\n')
        review_path = self.root / 'paraphrases/0.3.4-easy/AUTHOR_REVIEW.json'
        record = {
            'path': 'mark/mark1_123.md', 'source': 'comparison/bsb.txt',
            'source_addresses': 2, 'author_comparison': 'performed; provisional',
            'source_sha256': hashlib.sha256(b'Mark 1:1\tFirst verse.\nMark 1:2\tSecond verse.\n').hexdigest(),
            'draft_sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
        }
        def save(value):
            review_path.write_text(json.dumps({'chapters': {'Mark 1': value}}))
        save(record)
        self.assertEqual(self.inventory()[0][0]['author_comparison'], 'current_provisional')
        for key, value in [('path', 'wrong.md'), ('source_sha256', 'changed'), ('draft_sha256', 'changed')]:
            with self.subTest(key=key):
                save({**record, key: value})
                self.assertEqual(self.inventory()[0][0]['author_comparison'], 'stale')
        save(record)
        p.write_text(p.read_text() + '\n')
        self.assertEqual(self.inventory()[0][0]['author_comparison'], 'stale')
        p.write_text(p.read_text().rstrip('\n') + '\n')
        source = self.root / 'comparison/bsb.txt'
        source.write_text(source.read_text().replace('First verse.', 'Changed source.'))
        self.assertEqual(self.inventory()[0][0]['author_comparison'], 'stale')
        self.assertEqual(self.inventory()[0][1]['author_comparison'], 'not_recorded')


if __name__ == "__main__":
    unittest.main()
