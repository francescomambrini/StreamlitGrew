import unittest
from pathlib import Path

import grewpy
from grewpy import Corpus
from streamlit.testing.v1 import AppTest

from request_builder import EmptyPatternError, build_request


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_CORPUS = PROJECT_ROOT / "test" / "it_old-ud-test.conllu"


class RequestBuilderTests(unittest.TestCase):
    def test_builds_request_from_bare_pattern(self):
        request = build_request('  X [lemma="amore"]  ')

        self.assertEqual(
            request.json_data(),
            [{"pattern": ['X [lemma="amore"]']}],
        )

    def test_adds_without_clause_to_request(self):
        request = build_request(
            'X [lemma="amore"]',
            '  X [upos=NOUN]  ',
        )

        self.assertEqual(
            request.json_data(),
            [
                {"pattern": ['X [lemma="amore"]']},
                {"without": ["X [upos=NOUN]"]},
            ],
        )

    def test_ignores_whitespace_only_without_clause(self):
        request = build_request('X [lemma="amore"]', "  \n  ")

        self.assertEqual(
            request.json_data(),
            [{"pattern": ['X [lemma="amore"]']}],
        )

    def test_builds_one_multiline_without_block(self):
        request = build_request(
            'X [lemma="amore"]',
            "X [upos=NOUN];\nX -[nsubj]-> Y",
        )

        self.assertEqual(
            request.json_data(),
            [
                {"pattern": ['X [lemma="amore"]']},
                {"without": ["X [upos=NOUN]", "X -[nsubj]-> Y"]},
            ],
        )

    def test_rejects_empty_pattern(self):
        with self.assertRaisesRegex(EmptyPatternError, "Enter a GrewMatch pattern"):
            build_request("   ")


class RequestSearchIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        grewpy.set_config("ud")
        cls.corpus = Corpus(str(SAMPLE_CORPUS))

    @classmethod
    def tearDownClass(cls):
        cls.corpus.clean()

    def test_without_clause_changes_search_results(self):
        matches = self.corpus.search(build_request('X [lemma="amore"]'))
        excluded_matches = self.corpus.search(
            build_request('X [lemma="amore"]', "X [upos=NOUN]")
        )

        self.assertGreater(len(matches), 0)
        self.assertEqual(excluded_matches, [])


class QueryFormTests(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(PROJECT_ROOT / "app.py", default_timeout=20).run()
        self.app.text_input[0].input(str(SAMPLE_CORPUS))
        self.app.button[0].click().run()

    def test_bare_pattern_with_exclusion_returns_no_results(self):
        self.app.text_area[0].input('X [lemma="amore"]')
        self.app.text_area[1].input("X [upos=NOUN]")
        self.app.button[1].click().run()

        self.assertEqual(list(self.app.exception), [])
        self.assertEqual(self.app.session_state["results"], [])
        self.assertIn("No results found", [message.value for message in self.app.warning])
        self.assertEqual(
            self.app.session_state["request_preview"],
            'pattern {X [lemma="amore"]}\nwithout {X [upos=NOUN]}',
        )
        self.assertIn(
            self.app.session_state["request_preview"],
            [code.value for code in self.app.code],
        )

    def test_invalid_pattern_is_reported_without_crashing(self):
        self.app.text_area[0].input("X [")
        self.app.button[1].click().run()

        self.assertEqual(list(self.app.exception), [])
        self.assertTrue(
            any(
                message.value.startswith("Invalid GrewMatch query:")
                for message in self.app.error
            )
        )

    def test_invalid_exclusion_clears_previous_results_and_shows_preview(self):
        self.app.text_area[0].input('X [lemma="amore"]')
        self.app.button[1].click().run()
        self.assertGreater(len(self.app.session_state["results"]), 0)

        self.app.text_area[1].input("X [")
        self.app.button[1].click().run()

        self.assertEqual(list(self.app.exception), [])
        self.assertIsNone(self.app.session_state["results"])
        self.assertIn("without {X [}", self.app.session_state["request_preview"])
        self.assertTrue(
            any(
                message.value.startswith("Invalid GrewMatch query:")
                for message in self.app.error
            )
        )


if __name__ == "__main__":
    unittest.main()
