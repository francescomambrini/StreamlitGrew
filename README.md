# StreamlitGrew

StreamlitGrew is a lightweight, local-only Streamlit interface for searching
CoNLL-U treebanks with GrewPy. It is intended for one user running the app on
their own computer. Corpus paths entered in the UI refer to that computer's
filesystem.

## Requirements

- macOS or Linux
- [uv](https://docs.astral.sh/uv/)
- OCaml and opam
- `grewpy_backend` available on `PATH`

GrewPy is composed of a Python package and a separate OCaml backend. `uv`
manages the Python package, but it does not install the backend. Follow the
[official Grew installation guide](https://grew.fr/usage/install/) to install
opam and OCaml, then install the backend:

```shell
opam remote add grew "https://opam.grew.fr"
opam update
opam install grewpy_backend
eval "$(opam env)"
```

Verify that the backend is visible in the shell used to run the app:

```shell
command -v grewpy_backend
```

## Install

The project uses `pyproject.toml` and `uv.lock` as its only dependency source.
GrewPy is pinned to version 0.7.1 because its request API has changed between
releases.

```shell
uv sync --locked
```

`uv` creates and manages the local `.venv` directory automatically. The
directory is ignored by Git and can be deleted at any time; the next `uv sync`
or `uv run` will recreate it from `uv.lock`.

## Run

```shell
uv run --locked streamlit run app.py
```

The query form accepts the contents of the Grew `pattern` and `without`
clauses, without their wrappers. For example, enter:

```grew
X [lemma="amore"]
```

instead of:

```grew
pattern { X [lemma="amore"] }
```

The app constructs the complete request through the GrewPy 0.7.1 builder API.

## Test

The integration tests start the local OCaml backend and search the bundled
sample corpus, so `grewpy_backend` must be available on `PATH`.

```shell
uv run --locked python -m unittest discover -s tests -v
```

## Updating dependencies

Use `uv add`, `uv remove`, and `uv lock` rather than editing or installing from
a `requirements.txt` file. For example:

```shell
uv add "streamlit>=1.59.1"
uv lock
uv sync --locked
```
