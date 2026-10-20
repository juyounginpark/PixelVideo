import { readFile, mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { build, toOBJ, bounds, TEMPLATES } from "./model.mjs";

const args = process.argv.slice(2);
if (!args.length || args[0] === "--help") {
  console.log("node generate.mjs --list\nnode generate.mjs --template cat output/cat [color=#ffcc88]\nnode generate.mjs --file character.boxes output/character");
} else if (args[0] === "--list") {
  for (const [key, tpl] of Object.entries(TEMPLATES)) console.log(`${key}: ${tpl.desc}`);
} else {
  if (!["--file", "--template"].includes(args[0]) || !args[1])
    throw new Error("Expected --file PATH or --template NAME; see --help");
  const code = args[0] === "--file" ? await readFile(args[1], "utf8")
    : `use ${args[1]} ${args.slice(3).join(" ")}\n`;
  const root = build(code);
  const base = path.resolve(args[2] || "output/model");
  await mkdir(path.dirname(base), { recursive: true });
  const exported = toOBJ(root, `${path.basename(base)}.mtl`);
  await writeFile(`${base}.obj`, exported.obj);
  await writeFile(`${base}.mtl`, exported.mtl);
  await writeFile(`${base}.boxes`, code);
  await writeFile(`${base}.three.json`, JSON.stringify(root.toJSON()));
  const summary = { meshes: exported.meshes, bounds: bounds(root), naturalLanguageServerReproduced: false };
  await writeFile(`${base}.json`, JSON.stringify(summary, null, 2));
  console.log(JSON.stringify({ output: base, ...summary }, null, 2));
}
