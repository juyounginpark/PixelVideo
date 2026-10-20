// Blender interchange uses the original website Builder, never a second parser.
import { readFileSync, writeFileSync } from "node:fs";
import { build } from "./model.mjs";
import { rigModel } from "./rig.mjs";
const root = build(readFileSync(process.argv[2], "utf8"));
rigModel(root);
root.updateMatrixWorld(true);
const nodes = [];
root.traverse(n => {
  const record = { id: n.uuid, parent: n.parent?.uuid, name: n.name,
    matrix: n.matrix.toArray(), part: n.userData.part || null, bone: !!n.isBone };
  if (n.isMesh) {
    record.vertices = Array.from(n.geometry.attributes.position.array);
    record.indices = n.geometry.index ? Array.from(n.geometry.index.array) : Array.from({length:record.vertices.length/3},(_,i)=>i);
    record.color = n.material.color.toArray();
    record.opacity = n.material.opacity;
  }
  nodes.push(record);
});
writeFileSync(process.argv[3], JSON.stringify({ version: 1, nodes, rig: root.userData.rig }));
