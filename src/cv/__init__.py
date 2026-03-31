import json
import logging
import subprocess
from pathlib import Path

import cyclopts
import yaml

from .schema import CVContent
from .tex import CVBuilder, compile_pdf

app = cyclopts.App()


@app.command()
def schema(output: Path = Path("cv.schema.json")):
    """Generate the CV schema."""
    output.write_text(json.dumps(CVContent.model_json_schema()))
    print(f"Wrote schema to {output}.")


@app.command()
def build(
    input: Path = Path("main.yml"),
    output: Path = Path("pattison-cv.pdf"),
    preview: bool = True,
    verbose: bool = True,
):

    if verbose:
        logging.basicConfig(level=logging.DEBUG)

    logging.info(f"Reading {input}...")
    with input.open() as f:
        content = CVContent.model_validate(
            yaml.full_load(f),
            extra="forbid",
        )

    logging.info("Creating intermediate tex...")
    cv_tex = CVBuilder.create_tex(content)

    logging.info(f"Compiling pdf to {output}...")
    pdf_path = compile_pdf(cv_tex, output)

    if preview:
        logging.info(f"Opening {output}...")
        subprocess.check_output(["open", str(pdf_path)])

    return pdf_path


def main():
    app()
