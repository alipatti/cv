import { readFile, copyFile, writeFile, mkdir } from "fs/promises";
import yaml from "js-yaml";
import hbs from "handlebars";
import Spinnies from "spinnies";
import { promisify } from "util";
import { exec as execCallback } from "child_process";

const exec = promisify(execCallback);

const OUT_DIR = ".out";
const TEMP_DIR = ".temp";
const TEMPLATES_DIR = "templates";
const CV_BASE_NAME = "pattison-cv";

const getContent = async (tag) => {
  const content = yaml.load(await readFile("main.yml"));
  if (!tag || tag === "full") return content;
  return filterContent(content, tag);
};

const getTags = async () =>
  (await getContent()).sections
    .map((section) => section.items?.map((item) => item.tags)) // find all tags in yaml
    .flat(2) // flatten
    .filter((tag, i, array) => array.indexOf(tag) === i) // remove dups
    .filter((val) => val !== undefined); // remove undefined

const filterSections = (sections, tag) =>
  sections
    // include only tagged items
    .map(({ items, ...rest }) => ({
      items: items?.filter((item) => item.tags?.includes(tag)),
      ...rest,
    }))
    // remove sections with no items
    .filter((section) => section.items?.length > 0);

const filterContent = (content, tag) => ({
  about: content.about,
  sections: filterSections(content.sections, tag),
});

const buildTex = async (tag) => {
  const content = await getContent(tag);

  // generate tex source
  const template = (await readFile(`${TEMPLATES_DIR}/tex.hbs`)).toString();
  const latex = hbs.compile(template)(content);

  // setup file structure
  const workingDir = `${TEMP_DIR}/${tag}`;
  const fileNameRoot = `${CV_BASE_NAME}-${tag}`;
  await mkdir(`${workingDir}`, { recursive: true });
  await writeFile(`${workingDir}/${fileNameRoot}.tex`, latex);
  await copyFile("publications.bib", `${workingDir}/publications.bib`);

  // build pdf
  await exec(`latexmk -cd ${workingDir}/${fileNameRoot}.tex`);

  // move pdf to output directory
  await mkdir(`${OUT_DIR}`, { recursive: true });
  await copyFile(
    `${workingDir}/${fileNameRoot}.pdf`,
    `${OUT_DIR}/${fileNameRoot}.pdf`
  );
};

const main = async () => {

  const tags = await getTags();
  tags.push("full");

  const spinnies = new Spinnies();

  await Promise.all(
    tags.map(async (tag) => {
      spinnies.add(tag);
      await buildTex(tag);
      spinnies.succeed(tag);
    })
  );
};

await main();
