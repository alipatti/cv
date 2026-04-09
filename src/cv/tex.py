import logging
import re
import subprocess
import sys
from collections.abc import Sequence
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from cv.schema import About, CVContent, Item, Section


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
        contact: list[str] = []

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


def compile_pdf(
    tex: str,
    pdf_path: Path,
    tex_file: Path | None = None,
) -> Path:
    if tex_file is not None:
        return _compile(tex, pdf_path, tex_file, keep_intermediates=True)

    with TemporaryDirectory() as tmp:
        return _compile(tex, pdf_path, Path(tmp) / "main.tex", keep_intermediates=False)


def _compile(
    tex: str, pdf_path: Path, tex_file: Path, keep_intermediates: bool
) -> Path:
    tex_file.write_text(tex)
    args = ["tectonic", tex_file, "-Z", f"search-path={Path.cwd()}"]

    if keep_intermediates:
        args.append("--keep-intermediates")

    args.extend(get_biblatex_args())

    process = subprocess.run(args, capture_output=True, encoding="utf-8")

    if process.returncode != 0:
        print(process.stdout)
        print(process.stderr)
        sys.exit(1)

    pdf_path.parent.mkdir(exist_ok=True, parents=True)
    return tex_file.with_suffix(".pdf").rename(pdf_path)


def get_biblatex_args() -> Sequence[str]:
    """
    awful hack to deal with conflicting biber/biblatex versioning.
    see https://github.com/tectonic-typesetting/tectonic/issues/1267
    """

    try:
        path = subprocess.check_output(["kpsewhich", "biblatex.sty"]).decode().strip()
        d = Path(path).parent
        return ["-Z", f"search-path={d}"]

    except FileNotFoundError:
        logging.debug("kpsewhich not found")
        return []


def md_to_tex(s: str) -> str:
    bold_italic_pattern = re.compile(r"(\*\*\*|___)(.*?)\1")
    bold_pattern = re.compile(r"(\*\*|__)(.*?)\1")
    italic_pattern = re.compile(r"(\*|_)(.*?)\1")

    s = bold_italic_pattern.sub(r"\\textbf{\\textit{\2}}", s)
    s = bold_pattern.sub(r"\\textbf{\2}", s)
    s = italic_pattern.sub(r"\\textit{\2}", s)
    return s
