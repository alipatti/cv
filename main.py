from __future__ import annotations

import logging
from io import StringIO
from pathlib import Path
import subprocess
import re
import cyclopts
import json
import sys

import pydantic
import yaml


class CVContent(pydantic.BaseModel):
    about: About
    sections: list[Section]


class About(pydantic.BaseModel):
    name: str
    email: str = ""
    phone: str = ""
    website: str = ""


class Section(pydantic.BaseModel):
    title: str
    summary: str = ""
    items: list[Item] = []


class Item(pydantic.BaseModel):
    title: str = ""
    subtitle: str = ""
    dates: str | int = ""
    bullets: list[str] = []
    citation: str = ""
    with_: str = pydantic.Field(alias="with", default="")
    details: str = ""


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


def compile_pdf(
    tex: str,
    pdf_path: Path,
    tex_file=Path("main.tex"),
) -> Path:
    tex_file.parent.mkdir(exist_ok=True, parents=True)
    tex_file.write_text(tex)

    args = ["tectonic", tex_file] + get_biblatex_args()

    process = subprocess.run(
        args,
        capture_output=True,
        encoding="utf-8",
    )

    if process.returncode != 0:
        print(process.stdout)
        print(process.stderr)
        sys.exit(1)

    pdf_path.parent.mkdir(exist_ok=True, parents=True)
    return tex_file.with_suffix(".pdf").rename(pdf_path)


class CVBuilder(StringIO):
    @classmethod
    def create_tex(cls, content: CVContent) -> str:
        cv = cls()
        cv.write_content(content)
        return cv.getvalue()

    def write_content(self, content: CVContent):
        self.write_header(content.about)

        for section in content.sections:
            self.write_section(section)

        self.write_footer()

    def write_header(self, about: About):
        contact = []

        if about.email:
            contact.append(rf"\faicon{{envelope}} {about.email}")

        if about.phone:
            contact.append(rf"\faicon{{phone}} {about.phone}")

        if about.website:
            contact.append(
                rf"\faicon{{globe}} \href{{http://{about.website}}}{{{about.website}}}"
            )

        self.write(rf"""
            \documentclass{{cv}}

            \begin{{document}}

            \begin{{center}}
                {{\Huge \scshape {about.name} }}

                \medskip

                \itshape

                {r" \ | \ ".join(contact)}
            \end{{center}}
            """)

    def write_section(self, section: Section):
        self.write(rf"""
            \section{{{section.title}}}

            {section.summary}
            """)

        for item in section.items:
            self.write_item(item)

    def write_item(self, item: Item):
        if item.citation:
            self.write(rf"""
                \begin{{adjustwidth}}{{1em}}{{0cm}}
                \begin{{refsection}}
                    \nocite{{{item.citation}}}
                    \printbibliography[heading=none]
                \end{{refsection}} 
                \end{{adjustwidth}}
                """)
            return

        if item.title and item.subtitle:
            self.write(
                rf"\subsection{{\textbf{{{item.title}}}, {md_to_tex(item.subtitle)}}}"
            )

        elif item.title:
            self.write(rf"\subsection{{\textbf{{{item.title}}}}}")

        if item.details:
            self.write(rf"~---~{item.details}")

        if item.dates:
            self.write(rf"\hfill \textsl{{{item.dates}}}")

        if item.with_:
            self.write(rf"\\ \hspace{{1em}}\textit{{\quad with {item.with_}}}")

        if item.bullets:
            self.write("\\begin{itemize}\n")

            for b in item.bullets:
                self.write(rf"\item {md_to_tex(b)}")

            self.write("\\end{itemize}\n")

    def write_footer(self):
        self.write("\n\n\\end{document}")


def md_to_tex(s: str) -> str:
    bold_italic_pattern = re.compile(r"(\*\*\*|___)(.*?)\1")
    bold_pattern = re.compile(r"(\*\*|__)(.*?)\1")
    italic_pattern = re.compile(r"(\*|_)(.*?)\1")

    s = bold_italic_pattern.sub(r"\\textbf{\\textit{\2}}", s)
    s = bold_pattern.sub(r"\\textbf{\2}", s)
    s = italic_pattern.sub(r"\\textit{\2}", s)
    return s


def get_biblatex_args():
    """
    awful hack to deal with conflicting biber/biblatex versioning.
    see https://github.com/tectonic-typesetting/tectonic/issues/1267
    """

    try:
        path = subprocess.check_output(["kpsewhich", "biblatex.sty"]).decode().strip()
        d = Path(path).parent
        return ["-Z", f"search-path={d}"]

    except FileNotFoundError:
        print("kpsewhich not found")
        return []


def main():
    app()
