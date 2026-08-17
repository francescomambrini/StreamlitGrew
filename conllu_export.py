"""CoNLL-U export helpers for GrewMatch results."""

from collections.abc import Mapping, Sequence
from typing import Any

import conllu


class ConlluExportError(ValueError):
    """Raised when Grew results cannot be represented in a CoNLL-U export."""


def format_token_id(token_id: Any) -> str:
    """Return the textual CoNLL-U representation of a parsed token ID."""
    if isinstance(token_id, int):
        return str(token_id)

    if (
        isinstance(token_id, tuple)
        and len(token_id) == 3
        and token_id[1] in {"-", "."}
    ):
        return f"{token_id[0]}{token_id[1]}{token_id[2]}"

    raise ConlluExportError(f"Unsupported CoNLL-U token ID: {token_id!r}")


def mark_matching_nodes(
    sentence: conllu.TokenList,
    matching_nodes: Mapping[str, str],
    *,
    sent_id: str,
) -> conllu.TokenList:
    """Add Grew variable names to the exact matching CoNLL-U token IDs."""
    tokens_by_id = {format_token_id(token["id"]): token for token in sentence}

    for variable, node_id in matching_nodes.items():
        node_id = str(node_id)
        token = tokens_by_id.get(node_id)
        if token is None:
            raise ConlluExportError(
                f"Sentence {sent_id!r} has no CoNLL-U token with ID {node_id!r} "
                f"for Grew variable {variable!r}."
            )

        misc = token.get("misc")
        if misc is None:
            misc = {}
            token["misc"] = misc
        elif not isinstance(misc, dict):
            raise ConlluExportError(
                f"Sentence {sent_id!r}, token {node_id!r} has an unsupported "
                f"MISC value: {misc!r}."
            )

        misc["mark"] = variable

    return sentence


def build_conllu_export(corpus: Any, results: Sequence[Mapping[str, Any]]) -> str:
    """Serialize one marked CoNLL-U sentence for each Grew match."""
    serialized_sentences = []

    for result in results:
        try:
            sent_id = result["sent_id"]
            matching_nodes = result["matching"]["nodes"]
        except (KeyError, TypeError) as error:
            raise ConlluExportError(
                f"Malformed Grew result; expected sent_id and matching.nodes: {result!r}"
            ) from error

        try:
            parsed_sentences = conllu.parse(corpus[sent_id].to_conll())
        except Exception as error:
            raise ConlluExportError(
                f"Could not read sentence {sent_id!r} from the Grew corpus: {error}"
            ) from error

        if len(parsed_sentences) != 1:
            raise ConlluExportError(
                f"Expected one CoNLL-U sentence for {sent_id!r}, "
                f"received {len(parsed_sentences)}."
            )

        sentence = mark_matching_nodes(
            parsed_sentences[0],
            matching_nodes,
            sent_id=sent_id,
        )
        serialized_sentences.append(sentence.serialize())

    return "".join(serialized_sentences)
