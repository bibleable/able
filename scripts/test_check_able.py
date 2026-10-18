"""Regression checks for meaningful failures and review provenance."""

import json
from pathlib import Path
import tempfile
import unittest

import check_able as checker


class AbleChecks(unittest.TestCase):
    def test_labeled_note_can_preserve_blank_reference_address(self):
        report = self.review("## Mark 7:16\n**About this verse:** BSB has no text here.",
                             {"Mark 7:16": ""})
        flags = report["verses"][0]["findings"]
        self.assertEqual([f["code"] for f in flags], ["empty_reference"])
        # Notes still cannot replace actual source text, or an unlabeled blank.
        for text, source in [
            ("## Mark 7:16\n**About this verse:** Explanation.", {"Mark 7:16": "Actual source text."}),
            ("## Mark 7:16\n", {"Mark 7:16": ""}),
        ]:
            with self.subTest(text=text):
                report = self.review(text, source)
                self.assertIn("empty_verse", [f["code"] for f in report["verses"][0]["findings"]])

    def test_blank_numbered_source_verses_require_edition_review(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "source.txt"
            path.write_text("Mark 1:1\tText.\nMark 1:2\t\n", encoding="utf-8")
            source = checker.load_source(path)
        report = self.review("## Mark 1:1\nText.", source)
        self.assertEqual(report["issues"], [])
        report = self.review("## Mark 1:1\nText.\n## Mark 1:2\nExtra text.", source)
        self.assertEqual(report["verses"][1]["findings"][0]["code"], "empty_reference")

    def review(self, text, source, reviews=None):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "mark1.md"
            path.write_text(text, encoding="utf-8")
            return checker.review_file(path, source, reviews or {})

    def test_missing_duplicate_out_of_order_and_unknown_verses(self):
        source = {f"Mark 1:{i}": "Reference." for i in range(1, 4)}
        report = self.review("## Mark 1:2\nTwo.\n## Mark 1:1\nOne.\n"
                             "## Mark 1:1\nAgain.\n## Mark 1:4\nExtra.", source)
        codes = {i["code"] for i in report["issues"]}
        self.assertTrue({"missing_verses", "duplicate_verse", "verse_order"} <= codes)
        self.assertIn("Mark 1:3", next(i["message"] for i in report["issues"] if i["code"] == "missing_verses"))
        self.assertEqual(report["verses"][-1]["findings"][0]["code"], "unknown_address")

    def test_explanatory_notes_do_not_trigger_verse_checks(self):
        text = "## Mark 1:1\nJesus spoke.\n\n**Help with words:**\n" + "word " * 30 + "bad skin."
        report = self.review(text, {"Mark 1:1": "Jesus spoke."})
        self.assertEqual(report["verses"][0]["findings"], [])
        self.assertTrue(report["verses"][0]["has_editorial_note"])

    def test_changed_text_or_source_invalidates_editorial_findings(self):
        body, original = "Tie His shoes.", "Untie His sandals."
        snapshots = {"Mark 1:1": {
            "text_sha256": checker.fingerprint(body),
            "source_sha256": checker.fingerprint(original),
            "findings": [{"tests": ["T1"], "message": "Action reversed."}],
        }}
        for current_body, current_source, expected in [
            (body, original, "recorded_concerns"),
            ("Untie His shoes.", original, "stale"),
            (body, "Changed source.", "stale"),
        ]:
            with self.subTest(expected=expected, text=current_body, source=current_source):
                report = self.review("## Mark 1:1\n" + current_body,
                                     {"Mark 1:1": current_source}, snapshots)
                verse = report["verses"][0]
                self.assertEqual(verse["editorial_review"], expected)
                self.assertEqual(verse["reader_review"], "pending")
                if expected == "stale":
                    self.assertNotIn("editorial_finding", [i["code"] for i in verse["findings"]])

    def test_wording_risks_are_review_prompts_not_bias_failures(self):
        report = self.review("## Mark 1:1\nA man with bad skin came. 👻", {"Mark 1:1": "Reference."})
        flags = report["verses"][0]["findings"]
        self.assertEqual(len(flags), 2)
        self.assertTrue(all(i["severity"] == "review" for i in flags))

    def test_empty_malformed_and_no_verse_inputs(self):
        report = self.review("## Mark 1:1\n<jesus></jesus> ✨", {"Mark 1:1": "Reference."})
        self.assertIn("empty_verse", [i["code"] for i in report["verses"][0]["findings"]])
        report = self.review("## Mark 1:two\nText", {})
        self.assertEqual({i["code"] for i in report["issues"]}, {"no_verses", "malformed_heading"})

    def test_sentence_length_and_singular_psalm_alias(self):
        report = self.review("## Psalm 1:1\n" + "word " * 21 + ".", {"Psalms 1:1": "Reference."})
        self.assertEqual(report["verses"][0]["address"], "Psalms 1:1")
        self.assertEqual(report["verses"][0]["longest_sentence_words"], 21)
        self.assertEqual(report["verses"][0]["findings"][0]["code"], "sentence_length")

    def test_mark_one_review_matches_repository_text(self):
        source = checker.load_source(checker.ROOT / "comparison/bsb.txt")
        snapshots = json.loads((checker.ROOT / "scripts/able_review_findings.json").read_text())["verses"]
        report = checker.review_file(checker.DEFAULT_CHAPTER, source, snapshots)
        self.assertEqual(len(report["verses"]), 45)
        self.assertEqual(report["issues"], [])
        self.assertEqual(sum(v["editorial_review"] == "recorded_concerns" for v in report["verses"]), 27)


if __name__ == "__main__":
    unittest.main()
