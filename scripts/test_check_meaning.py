import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import check_meaning as checker


TARGET = {"address": "Mark 1:7", "able": "I tie His shoes.", "reference": "I untie His sandals."}


def response_for(targets, concern=False):
    results = []
    for target in targets:
        results.append({"address": target["address"],
                        "verdict": "needs_review" if concern else "no_issue_found",
                        "summary": "Action changed." if concern else "No material concern identified.",
                        "findings": [{"tests": ["T1"], "source_quote": "untie",
                                      "able_quote": "tie", "explanation": "The action is reversed.",
                                      "suggestion": "Use untie."}] if concern else []})
    return {"id": "test-response", "status": "completed", "model": "test-model",
            "output": [{"type": "message", "content": [{"type": "output_text", "text": json.dumps({"verses": results})}]}]}


class MeaningChecks(unittest.TestCase):
    def test_valid_evidence_and_reversed_action(self):
        results = checker.extract_results(response_for([TARGET], concern=True), [TARGET])
        self.assertEqual(results[0]["verdict"], "needs_review")

    def test_hallucinated_evidence_is_rejected(self):
        response = response_for([TARGET], concern=True)
        content = response["output"][0]["content"][0]
        data = json.loads(content["text"])
        for field in ("source_quote", "able_quote"):
            invalid = copy.deepcopy(data)
            invalid["verses"][0]["findings"][0][field] = "invented words"
            content["text"] = json.dumps(invalid)
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "evidence"):
                checker.extract_results(response, [TARGET])

    def test_missing_duplicate_and_unexpected_results_rejected(self):
        for targets in ([], [TARGET, TARGET], [dict(TARGET, address="Mark 1:8")]):
            with self.subTest(targets=targets), self.assertRaisesRegex(ValueError, "addresses"):
                checker.extract_results(response_for(targets), [TARGET])

    def test_incomplete_refused_and_malformed_responses_are_not_passes(self):
        cases = [
            {"status": "incomplete"},
            {"status": "completed", "output": [{"type": "message", "content": [{"type": "refusal"}]}]},
            {"status": "completed", "output": []},
        ]
        for response in cases:
            with self.subTest(response=response), self.assertRaises(ValueError):
                checker.extract_results(response, [TARGET])

    def test_contradictory_verdict_rejected(self):
        response = response_for([TARGET], concern=True)
        content = response["output"][0]["content"][0]
        data = json.loads(content["text"])
        data["verses"][0]["verdict"] = "no_issue_found"
        content["text"] = json.dumps(data)
        with self.assertRaisesRegex(ValueError, "contradicts"):
            checker.extract_results(response, [TARGET])

    def fixture(self, folder):
        chapter, source, output = [Path(folder) / name for name in ("mark1.md", "source.txt", "report.json")]
        chapter.write_text("## Mark 1:1\nOne.\n## Mark 1:2\nTwo.\n## Mark 1:3\nThree.", encoding="utf-8")
        source.write_text("Mark 1:1\tOne.\nMark 1:2\tTwo.\nMark 1:3\tThree.\n", encoding="utf-8")
        return chapter, source, output

    def invoke(self, args, environment=None):
        with patch("sys.argv", ["check_meaning.py", *map(str, args)]), \
                patch.dict("os.environ", environment or {}, clear=True), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return checker.main()

    def test_dry_run_needs_no_key_and_includes_neighbor_context(self):
        with tempfile.TemporaryDirectory() as folder:
            chapter, source, output = self.fixture(folder)
            with patch.object(checker, "call_api") as api:
                self.assertEqual(self.invoke([chapter, "--source", source, "--verse", "Mark 1:2", "--dry-run", "--output", output]), 0)
                api.assert_not_called()
            report = json.loads(output.read_text())
            self.assertEqual(report["api_calls"], 1)
            payload = report["requests"][0]
            self.assertFalse(payload["store"])
            self.assertTrue(payload["text"]["format"]["strict"])
            data = json.loads(payload["input"][0]["content"])
            self.assertEqual([t["address"] for t in data["targets"]], ["Mark 1:2"])
            self.assertEqual([t["address"] for t in data["context"]], ["Mark 1:1", "Mark 1:3"])

    def test_api_failure_preserves_prior_results_and_marks_rest_unchecked(self):
        with tempfile.TemporaryDirectory() as folder:
            chapter, source, output = self.fixture(folder)
            def api(payload, key, timeout):
                targets = json.loads(payload["input"][0]["content"])["targets"]
                if targets[0]["address"] == "Mark 1:2":
                    raise ValueError("Simulated API failure")
                return response_for(targets)
            with patch.object(checker, "call_api", side_effect=api):
                code = self.invoke([chapter, "--source", source, "--output", output, "--batch-size", "1"],
                                   {"OPENAI_API_KEY": "test-only-key", "OPENAI_MODEL": "test-model"})
            report = json.loads(output.read_text())
            self.assertEqual(code, 2)
            self.assertEqual([v["verdict"] for v in report["verses"]], ["no_issue_found", "not_checked", "not_checked"])
            self.assertEqual(len(report["errors"]), 1)
            self.assertNotIn("test-only-key", output.read_text())

    def test_missing_key_and_input_overwrite_fail_before_network(self):
        with tempfile.TemporaryDirectory() as folder:
            chapter, source, output = self.fixture(folder)
            before = chapter.read_text()
            with patch.object(checker, "call_api") as api:
                self.assertEqual(self.invoke([chapter, "--source", source, "--model", "test-model"]), 2)
                self.assertEqual(self.invoke([chapter, "--source", source, "--output", chapter, "--dry-run"]), 2)
                api.assert_not_called()
            self.assertEqual(chapter.read_text(), before)

    def test_missing_verse_is_rejected_before_api(self):
        with tempfile.TemporaryDirectory() as folder:
            chapter, source, output = self.fixture(folder)
            chapter.write_text("## Mark 1:1\nOne.", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "structural"):
                checker.build_batches(chapter, checker.load_source(source), [], None, 5)


if __name__ == "__main__":
    unittest.main()
