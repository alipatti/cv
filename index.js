import hbs from "handlebars";
import Spinnies from "spinnies";
import { parse } from "jsr:@std/yaml";

const OUTPUT_PDF_DIRECTORY = "pdfs";
const CV_BASE_NAME = "pattison-cv";

const getContent = async (tag) => {
  const content = parse(await Deno.readTextFile("main.yml"));

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
  // generate tex source
  const template = await Deno.readTextFile("template.tex.hbs");
  const texString = hbs.compile(template)(await getContent(tag));
  const texBytes = new TextEncoder().encode(texString);

  // build pdf
  const output_dir = `/tmp/com.alipatti.cv/${tag}`;
  await Deno.mkdir(output_dir, { recursive: true });

  // spawn tectonic subprocess
  const tectonic = new Deno.Command("tectonic", {
    args: [
      "-X",
      "compile",
      "--outdir",
      output_dir,
      "--keep-intermediates",
      "-",
    ],
    stdin: "piped",
    stderr: "piped",
    stdout: "piped",
  }).spawn();

  // pipe tex to stdin
  {
    const writer = tectonic.stdin.getWriter();
    await writer.write(texBytes);
    await writer.close();
  }

  // await compilation
  const { success, stderr } = await tectonic.output();

  if (!success) {
    throw new Error(
      `Failed to compile ${tag}:\n${new TextDecoder().decode(stderr)}`,
    );
  }

  // move pdf to output directory
  const outputPdf = `${OUTPUT_PDF_DIRECTORY}/${CV_BASE_NAME}-${tag}.pdf`;
  await Deno.mkdir(`${OUTPUT_PDF_DIRECTORY}`, { recursive: true });
  await Deno.copyFile(`${output_dir}/texput.pdf`, outputPdf);
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
    }),
  );
};

await main();
