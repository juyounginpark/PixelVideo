// Local adapter. vendor/* preserves the publicly served implementation unchanged.
import * as THREE from "three";
import { parseLine, expand, Builder } from "./builder.mjs";
import { TEMPLATES } from "./vendor/templates.js";
import { parseMotionLine } from "./motion.mjs";
export { TEMPLATES };
export const parseModelLine = line => parseMotionLine(line) || parseLine(line);

export function build(code) {
  const root = new THREE.Group();
  const builder = new Builder(root);
  for (const [index, line] of code.split(/\r?\n/).entries()) {
    if (!line.trim() || line.trim().startsWith("//")) continue;
    const parsed = parseModelLine(line);
    if (!parsed) throw new Error(`Invalid box language at line ${index + 1}: ${line}`);
    if (parsed.kind === "motion") { root.userData.motion = parsed.preset; continue; }
    for (const spec of expand(parsed)) {
      const before = new Set(); root.traverse(n => { if (n.isGroup) before.add(n); });
      builder.add(spec);
      let occurrence = 0;
      root.traverse(n => {
        if (!n.isGroup || before.has(n)) return;
        const twin = occurrence++ > 0;
        const partName = twin ? spec.name.replace(/L$/, "R") + (spec.name.endsWith("L") ? "" : "_mirror") : spec.name;
        n.name = `part_${partName}_${index}_${occurrence}`;
        n.userData.part = { name: partName, sourceName: spec.name, mirror: twin, size: [...spec.size] };
      });
    }
  }
  root.updateMatrixWorld(true);
  let meshes = 0;
  root.traverse(node => {
    if (!node.isMesh) return;
    meshes++;
    if (!node.matrixWorld.elements.every(Number.isFinite)) throw new Error("Non-finite transform");
  });
  if (!meshes) throw new Error("Empty model");
  return root;
}

// OBJ/MTL is an interchange addition, not part of the original website.
// World transforms preserve hierarchy/mirroring in a flattened Y-up model.
export function toOBJ(root, materialFile = "model.mtl") {
  root.updateMatrixWorld(true);
  const obj = [`mtllib ${materialFile}`], mtl = [];
  const materials = new Map();
  let offset = 1, count = 0;
  root.traverse(node => {
    if (!node.isMesh) return;
    const mat = node.material;
    if (!materials.has(mat)) {
      const name = `material_${materials.size}`;
      materials.set(mat, name);
      const rgb = mat.color.clone().convertLinearToSRGB();
      mtl.push(`newmtl ${name}`, `Kd ${rgb.r} ${rgb.g} ${rgb.b}`,
        `d ${mat.opacity}`, `illum ${mat.isMeshBasicMaterial ? 0 : 1}`, "");
    }
    obj.push(`o part_${count++}`, `usemtl ${materials.get(mat)}`);
    const geom = node.geometry;
    const positions = geom.getAttribute("position");
    for (let i = 0; i < positions.count; i++) {
      const p = new THREE.Vector3().fromBufferAttribute(positions, i).applyMatrix4(node.matrixWorld);
      obj.push(`v ${p.x} ${p.y} ${p.z}`);
    }
    const indices = geom.index ? Array.from(geom.index.array) : Array.from({ length: positions.count }, (_, i) => i);
    for (let i = 0; i < indices.length; i += 3)
      obj.push(`f ${indices[i] + offset} ${indices[i + 1] + offset} ${indices[i + 2] + offset}`);
    offset += positions.count;
  });
  return { obj: obj.join("\n") + "\n", mtl: mtl.join("\n") + "\n", meshes: count };
}

export function bounds(root) {
  const b = new THREE.Box3().setFromObject(root);
  return { min: b.min.toArray(), max: b.max.toArray(), size: b.getSize(new THREE.Vector3()).toArray() };
}
