import { cpSync, mkdirSync, readFileSync, writeFileSync } from "fs";
import { spawnSync } from "child_process";
import yaml from "js-yaml";
import hbs from "handlebars";

const OUTPUT_DIR = ".out";
const TEMPLATES_DIR = "templates";

const buildTex = (cv_content) => {
  const template = readFileSync(`${TEMPLATES_DIR}/tex/main.tex.hbs`).toString();
  const latex = hbs.compile(template)(cv_content);

  // build latex
  mkdirSync(`${OUTPUT_DIR}/tex`, { recursive: true });
  writeFileSync(`${OUTPUT_DIR}/tex/main.tex`, latex);
  cpSync(`${TEMPLATES_DIR}/tex/resume.cls`, `${OUTPUT_DIR}/tex/resume.cls`);
  cpSync("publications.bib", `${OUTPUT_DIR}/tex/publications.bib`);
  const process = spawnSync("latexmk", ["-cd", `${OUTPUT_DIR}/tex/main.tex`]);

  if (process.status != 0) {
    throw process.error;
  }
};

const main = () => {
  const content = yaml.load(readFileSync("main.yml"));

  buildTex(content);
};

main();
