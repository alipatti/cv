#!/usr/bin/env deno --allow-all

import hbs from "handlebars";
import Spinnies from "spinnies";
import { parse } from "jsr:@std/yaml";
import { Command, Option, runExit } from "clipanion";
import chalk from "chalk";

type Content = { sections: Section[]; about: About };

type Section = { items?: Item[]; summary?: string };
type Item = { title: string; bullets?: string[]; tags?: string[] };

type About = any;

const markdownToLatex = (markdown: string) => {
  return markdown
    .replace(/(\*\*\*|___)(.*?)\1/g, "\\textbf{\\textit{$2}}") // Bold + Italics
    .replace(/(\*\*|__)(.*?)\1/g, "\\textbf{$2}") // Bold
    .replace(/(\*|_)(.*?)\1/g, "\\textit{$2}"); // Italics
};

const getTags = (content: Content) =>
  content.sections
    .map((section) => section.items?.map((item) => item.tags)) // find all tags in yaml
    .flat(2) // flatten
    .filter((tag, i, array) => array.indexOf(tag) === i) // remove dups
    .filter((val) => val !== undefined); // remove undefined

const processContent = (content: Content, tag?: string) => {
  tag = tag == "full" ? undefined : tag;

  return {
    about: content.about,
    sections: content.sections
      .map(({ items, ...rest }) => ({
        items: items
          // include only item that have the correct tag
          ?.filter((item) => tag == undefined || item.tags?.includes(tag))
          // convert markdown in bullets to latex
          .map(({ bullets, ...rest }) => ({
            bullets: bullets?.map(markdownToLatex),
            ...rest,
          })),
        ...rest,
      }))
      // remove sections with no items
      .filter((section) => section.items || section.summary),
  };
};

const createTexSource = (
  content: Content,
  tag: string,
  template: HandlebarsTemplateDelegate,
): Uint8Array => {
  const texString = template(processContent(content, tag));
  const texBytes = new TextEncoder().encode(texString);

  return texBytes;
};

const renderTexToPdf = async (
  texSource: Uint8Array,
  outputFilepath: string,
) => {
  const outputDirectory = await Deno.makeTempDir();

  // spawn tectonic subprocess
  const tectonic = new Deno.Command("tectonic", {
    args: ["-X", "compile", "--outdir", outputDirectory, "-"],
    stdin: "piped",
    stderr: "piped",
    stdout: "piped",
  }).spawn();

  // pipe tex to stdin
  {
    const writer = tectonic.stdin.getWriter();
    await writer.write(texSource);
    await writer.close();
  }

  // await compilation
  const { success, stderr } = await tectonic.output();

  if (!success) {
    throw new Error(
      `Failed to compile pdf:\n${new TextDecoder().decode(stderr)}`,
    );
  }

  // move pdf to output directory
  await Deno.copyFile(`${outputDirectory}/texput.pdf`, outputFilepath);
};

runExit(
  class CompileCommand extends Command {
    contentFile = Option.String("--input", "main.yml", {
      description: "File from which to read CV information.",
    });

    outputDirectory = Option.String("--input", "pdfs/", {
      description: "Where to save rendered pdfs.",
    });

    tags = Option.Array("--tags", {
      description: "Which versions to render.",
    });

    all = Option.Boolean("--all", false, {
      description: "Render all versions.",
    });

    prefix = Option.String("--prefix", "", {
      description: "String to prefix to pdf file name (e.g. your last name)",
    });

    templateFile = Option.String("--template", "template.tex.hbs", {
      description: "Handlebars LaTeX template file.",
    });

    watch = Option.Boolean("--watch", false);

    async execute() {
      // print intention
      this.context.stdout.write(
        `Rendering CV from ${chalk.bold(this.contentFile)}\n`,
      );

      // load content and template
      const content = parse(
        await Deno.readTextFile(this.contentFile),
      ) as Content;
      const template = hbs.compile(await Deno.readTextFile(this.templateFile));

      // process args
      if (!this.tags) {
        this.tags = ["full"];
      }

      if (this.all) {
        this.tags = await getTags(content);
        this.tags.push("full");
      }

      this.outputDirectory = this.outputDirectory.replace("/?$", "/"); // ensure tailing slash

      // compile pdfs
      await Deno.mkdir(`${this.outputDirectory}`, { recursive: true });
      const spinnies = new Spinnies();

      const renderPromises = this.tags.map(async (tag) => {
        const outputFilepath = this.outputDirectory +
          `${this.prefix.toString()}${this.prefix ? "-" : ""}` +
          `cv-${tag}.pdf`;

        spinnies.add(tag, {
          text: `${tag} ⇢ ${chalk.white(outputFilepath)}`,
          succeedColor: "white",
        });

        const tex = createTexSource(content, tag, template);
        await renderTexToPdf(tex, outputFilepath);

        spinnies.succeed(tag);
      });

      await Promise.all(renderPromises);
    }
  },
);
