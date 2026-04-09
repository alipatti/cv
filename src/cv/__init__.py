import json
import logging
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

import cyclopts
import yaml
from watchfiles import watch as watchfiles_watch

from cv.schema import CVContent
from cv.tex import CVBuilder, compile_pdf

app = cyclopts.App()


def _build_once(input: Path, output: Path, tex_file: Path | None = None):
    with input.open() as f:
        content = CVContent.model_validate(yaml.full_load(f), extra="forbid")

    compile_pdf(CVBuilder.create_tex(content), output, tex_file=tex_file)


@app.command()
def schema(output: Path = Path("cv.schema.json")):
    """Generate the CV schema."""
    output.write_text(json.dumps(CVContent.model_json_schema()))
    print(f"Wrote schema to {output}.")


@app.command()
def build(
    input: Path = Path("main.yml"),
    output: Path = Path("pattison-cv.pdf"),
    open: bool = True,
    verbose: bool = True,
):
    if verbose:
        logging.basicConfig(level=logging.DEBUG)

    logging.info(f"Reading {input}...")
    logging.info("Creating intermediate tex...")
    logging.info(f"Compiling pdf to {output}...")
    _build_once(input, output)

    if open:
        logging.info(f"Opening {output}...")
        subprocess.check_output(["open", str(output)])


@app.command()
def watch(
    input: Path = Path("main.yml"),
    output: Path = Path("pattison-cv.pdf"),
    bib: Path = Path("publications.bib"),
    open: bool = True,
):
    """Watch for changes and rebuild the CV."""
    logging.basicConfig(level=logging.INFO)
    logging.info(f"Watching {input} and {bib}...")

    with TemporaryDirectory() as tmp:
        tex_file = Path(tmp) / "main.tex"

        if open:
            subprocess.check_output(["open", str(output)])

        for _ in watchfiles_watch(input, bib):
            _build_once(input, output, tex_file=tex_file)


def main():
    app()
