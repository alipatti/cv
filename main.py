import json
import logging
import subprocess
from pathlib import Path

import cyclopts
import pydantic
import yaml
from watchfiles import watch as watchfiles_watch

app = cyclopts.App()


class About(pydantic.BaseModel):
    name: str
    email: str = ""
    phone: str = ""
    website: str = ""


class Item(pydantic.BaseModel):
    title: str = ""
    subtitle: str = ""
    dates: int | str = ""
    bullets: list[str] = []
    citation: str = ""
    with_: str = pydantic.Field(alias="with", default="")
    details: str = ""


class Section(pydantic.BaseModel):
    title: str
    summary: str = ""
    items: list[Item] = []


class CVContent(pydantic.BaseModel):
    about: About
    sections: list[Section]


def _validate(path: Path) -> CVContent:
    """Validate the YAML data file against the Pydantic schema."""
    with path.open() as f:
        return CVContent.model_validate(yaml.full_load(f))


def _compile(template: Path, output: Path) -> None:
    """Invoke typst to compile the CV template."""
    subprocess.run(["typst", "compile", str(template), str(output)], check=True)


@app.command()
def schema(output: Path = Path("cv.schema.json")) -> None:
    """Generate JSON schema for YAML editor validation."""
    output.write_text(json.dumps(CVContent.model_json_schema()))
    print(f"Wrote schema to {output}.")


@app.command()
def build(
    input: Path = Path("main.yml"),
    template: Path = Path("cv.typ"),
    output: Path = Path("pattison-cv.pdf"),
    open: bool = True,
    app: str = "Skim",
) -> None:
    """Validate YAML and compile CV with Typst."""
    _validate(input)
    _compile(template, output)

    if open:
        subprocess.run(["open", str(output), "-a", app])


@app.command()
def watch(
    input: Path = Path("main.yml"),
    template: Path = Path("cv.typ"),
    output: Path = Path("pattison-cv.pdf"),
) -> None:
    """Watch for changes, validate YAML, and recompile."""
    logging.basicConfig(level=logging.INFO)
    logging.info(f"Watching {input} and {template}...")

    for _ in watchfiles_watch(input, template):
        try:
            _validate(input)
            _compile(template, output)
            logging.info("Rebuilt successfully.")
        except Exception as e:
            logging.error(str(e))


def main() -> None:
    app()
