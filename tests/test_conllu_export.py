import unittest
from pathlib import Path

import conllu

from conllu_export import (
    ConlluExportError,
    build_conllu_export,
    format_token_id,
    mark_matching_nodes,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_CORPUS = PROJECT_ROOT / "test" / "it_old-ud-test.conllu"

SENTENCE_WITH_SPECIAL_IDS = """\
# sent_id = special-ids
# text = I can't go there
1\tI\tI\tPRON\t_\t_\t4\tnsubj\t_\t_
2-3\tcan't\t_\t_\t_\t_\t_\t_\t_\t_
2\tca\tcan\tAUX\t_\t_\t4\taux\t_\t_
3\tn't\tnot\tPART\t_\t_\t4\tadvmod\t_\t_
3.1\treally\treally\tADV\t_\t_\t_\t_\t4:advmod\t_
4\tgo\tgo\tVERB\t_\t_\t0\troot\t_\tSpaceAfter=No
5\tthere\tthere\tADV\t_\t_\t4\tadvmod\t_\t_

"""


def token_by_id(sentence, token_id):
    return next(token for token in sentence if format_token_id(token["id"]) == token_id)


class TokenIdTests(unittest.TestCase):
    def test_formats_integer_range_and_empty_node_ids(self):
        sentence = conllu.parse(SENTENCE_WITH_SPECIAL_IDS)[0]

        self.assertEqual(
            [format_token_id(token["id"]) for token in sentence],
            ["1", "2-3", "2", "3", "3.1", "4", "5"],
        )

    def test_rejects_unsupported_token_id(self):
        with self.assertRaisesRegex(ConlluExportError, "Unsupported CoNLL-U token ID"):
            format_token_id(None)


class MarkMatchingNodesTests(unittest.TestCase):
    def test_marks_exact_ids_after_multiword_row_and_preserves_misc(self):
        sentence = conllu.parse(SENTENCE_WITH_SPECIAL_IDS)[0]

        mark_matching_nodes(
            sentence,
            {"X": "2", "Y": "4"},
            sent_id="special-ids",
        )

        self.assertIsNone(token_by_id(sentence, "2-3")["misc"])
        self.assertEqual(token_by_id(sentence, "2")["misc"], {"mark": "X"})
        self.assertEqual(
            token_by_id(sentence, "4")["misc"],
            {"SpaceAfter": "No", "mark": "Y"},
        )

    def test_marks_empty_node_id(self):
        sentence = conllu.parse(SENTENCE_WITH_SPECIAL_IDS)[0]

        mark_matching_nodes(sentence, {"E": "3.1"}, sent_id="special-ids")

        self.assertEqual(token_by_id(sentence, "3.1")["misc"], {"mark": "E"})

    def test_missing_id_reports_sentence_node_and_variable(self):
        sentence = conllu.parse(SENTENCE_WITH_SPECIAL_IDS)[0]

        with self.assertRaisesRegex(
            ConlluExportError,
            "Sentence 'special-ids'.*ID '99'.*variable 'Missing'",
        ):
            mark_matching_nodes(
                sentence,
                {"Missing": "99"},
                sent_id="special-ids",
            )

    def test_bundled_multiword_sentence_marks_token_17_not_range_17_18(self):
        sentence = conllu.parse(SAMPLE_CORPUS.read_text())[0]

        mark_matching_nodes(sentence, {"X": "17"}, sent_id=sentence.metadata["sent_id"])

        self.assertIsNone(token_by_id(sentence, "17-18")["misc"].get("mark"))
        self.assertEqual(token_by_id(sentence, "17")["misc"]["mark"], "X")


class FakeGraph:
    def to_conll(self):
        return SENTENCE_WITH_SPECIAL_IDS


class BuildExportTests(unittest.TestCase):
    def test_serializes_one_exactly_marked_sentence_per_match(self):
        corpus = {"special-ids": FakeGraph()}
        results = [
            {
                "sent_id": "special-ids",
                "matching": {"nodes": {"X": "4"}},
            }
        ]

        exported = conllu.parse(build_conllu_export(corpus, results))[0]

        self.assertEqual(token_by_id(exported, "4")["misc"]["mark"], "X")
        self.assertIsNone(token_by_id(exported, "3")["misc"])


if __name__ == "__main__":
    unittest.main()
