import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import * as THREE from "three";
import { build, bounds, toOBJ, TEMPLATES } from "./model.mjs";
import { Builder, parseLine } from "./vendor/boxes.js";
import { rigModel, restorePose } from "./rig.mjs";
import { Builder as FixedBuilder } from "./builder.mjs";

test("implicit twins propagate through forearm/hand and shin/foot in live and final builds", () => {
  const code=readFileSync(new URL("assets/minsu.boxes",import.meta.url),"utf8");
  const root=build(code);
  const names=[];root.traverse(n=>{if(n.userData.part)names.push(n.userData.part.name);});
  for(const name of ["arm","forearm","hand","leg","shin","foot"])
    for(const side of ["L","R"])assert.equal(names.filter(n=>n===name+side).length,1);
  const live=new THREE.Group(),builder=new FixedBuilder(live);
  for(const line of code.split("\n")){const spec=parseLine(line);if(spec?.kind==="box")builder.add(spec,0);}
  builder.update(1000);
  for(const name of ["handL","footL"]) {
    const original=builder.parts.get(name),twin=builder.twins.get(name);
    assert.ok(original && twin);
    live.updateMatrixWorld(true);
    const a=original.getWorldPosition(new THREE.Vector3()),b=twin.getWorldPosition(new THREE.Vector3());
    assert.ok(Math.abs(a.x+b.x)<1e-6 && a.x*b.x<0);
    assert.ok(Math.abs(a.y-b.y)<1e-6);
  }
  builder.add(parseLine("box handL forearmL .5 .4 .5 0 -.6 0 #ffffff"),1000);
  assert.equal(builder.twins.get("forearmL").children.filter(n=>n.isGroup).length,1);
  builder.add(parseLine("hide handL"));
  assert.equal(builder.parts.get("handL").parent,null);
  assert.equal(builder.twins.get("handL").parent,null);
});

for (const name of Object.keys(TEMPLATES)) test(`${name}: rig preserves shape, clips animate and survive JSON export`, () => {
  const root = build(`use ${name}\nmotion wave`);
  const before = new THREE.Box3().setFromObject(root), rig = rigModel(root);
  const after = new THREE.Box3().setFromObject(root);
  assert.ok(before.min.distanceTo(after.min) < 1e-6 && before.max.distanceTo(after.max) < 1e-6);
  assert.equal(rig.bones.elbowL.parent, rig.bones.shoulderL);
  const loaded = new THREE.ObjectLoader().parse(root.toJSON());
  assert.equal(loaded.animations.length, root.animations.length);
  const mixer = new THREE.AnimationMixer(loaded);
  for (const clip of loaded.animations) {
    mixer.stopAllAction();
    const action = mixer.clipAction(clip).play();
    for (const fraction of [0, .25, .5, .75, .999]) {
      action.time = fraction * clip.duration; mixer.update(0); loaded.updateMatrixWorld(true);
      loaded.traverse(n => assert.ok(n.matrixWorld.elements.every(Number.isFinite)));
    }
    for (const track of clip.tracks) {
      const width = track.getValueSize();
      for (let j = 0; j < width; j++)
        assert.ok(Math.abs(track.values[j] - track.values[track.values.length - width + j]) < 1e-5);
    }
  }
  const wave = root.animations.find(c => c.name === "wave");
  assert.ok(wave.tracks.some(t => Array.from(t.values).some((v, i) => i >= 4 && Math.abs(v - t.values[i % 4]) > .01)));
  restorePose(rig);
});
test("explicit limbs connect knee and wrist and retain held objects", () => {
  const root = build(`box body - 2 2 1 0 3 0 #ffffff
box head body 1 1 1 0 1.5 0 #ffffff
box armL body .5 1 .5 -1.3 0 0 #ffffff mirror
box forearmL armL .5 1 .5 0 -1 0 #ffffff
box handL forearmL .5 .4 .5 0 -.7 0 #ffffff
box prop handL .2 1 .2 0 0 .4 #ff0000
box legL body .5 1 .5 -.5 -1.5 0 #ffffff mirror
box shinL legL .5 1 .5 0 -1 0 #ffffff
box footL shinL .5 .3 1 0 -.65 .2 #ffffff
motion walk`);
  const rig = rigModel(root);
  assert.equal(rig.bones.kneeL.parent, rig.bones.hipL);
  assert.equal(rig.bones.wristL.parent, rig.bones.elbowL);
  const prop = []; rig.bones.wristL.traverse(n => { if(n.userData.part?.sourceName === "prop") prop.push(n); });
  assert.ok(prop.length);
  const original = prop[0].getWorldPosition(new THREE.Vector3());
  rig.bones.elbowL.rotateX(.8); root.updateMatrixWorld(true);
  assert.ok(original.distanceTo(prop[0].getWorldPosition(new THREE.Vector3())) > .1);
});

test("vendor files match captured public bytes", () => {
  for (const file of ["boxes.js", "templates.js", "look.js"]) {
    assert.deepEqual(readFileSync(new URL(`vendor/${file}`, import.meta.url)),
      readFileSync(new URL(`../../research/hanbean_voxel/${file}`, import.meta.url)));
  }
});
for (const name of Object.keys(TEMPLATES)) {
  test(`${name}: finite geometry and valid OBJ indices`, () => {
    const root = build(`use ${name}`);
    assert.ok(bounds(root).size.every(v => Number.isFinite(v) && v > 0));
    const { obj } = toOBJ(root);
    const lines = obj.split("\n");
    const vertices = lines.filter(l => l.startsWith("v ")).length;
    for (const line of lines.filter(l => l.startsWith("f ")))
      for (const index of line.slice(2).split(" ").map(Number))
        assert.ok(index >= 1 && index <= vertices);
    const roundTrip = new THREE.ObjectLoader().parse(root.toJSON());
    const before = bounds(root), after = bounds(roundTrip);
    for (const key of ["min", "max", "size"])
      before[key].forEach((value, i) => assert.ok(Math.abs(value - after[key][i]) < 1e-10));
  });
}
test("mirror transforms, soft boxes, hiding and animation completion", () => {
  const root = new THREE.Group(), builder = new Builder(root);
  builder.add(parseLine("box parent - 2 2 2 3 2 0 #ffffff mirror soft"), 0);
  assert.equal(root.children.length, 2);
  assert.equal(root.children[0].children.length, 3);
  builder.update(400);
  assert.equal(builder.busy, false);
  assert.equal(builder.parts.get("parent").position.x, 3);
  assert.equal(builder.twins.get("parent").position.x, -3);
  builder.add(parseLine("hide parent"));
  assert.equal(root.children.length, 0);
});
test("invalid input fails explicitly", () => {
  assert.throws(() => build("use unknown"));
  assert.throws(() => build("not a box"));
});
