import * as THREE from "three";
import { MOTIONS, inferMotion } from "./motion.mjs";

const V = (x = 0, y = 0, z = 0) => new THREE.Vector3(x, y, z);
const Q = () => new THREE.Quaternion();
const world = (node, xyz = [0, 0, 0]) => node.localToWorld(V(...xyz));
const sideOf = part => /(?:R|right|_mirror)$/i.test(part.userData.part.name) || part.userData.part.mirror ? "R" : "L";
const stem = part => part.userData.part.name.replace(/_mirror$/, "").replace(/^(left|right)/i, "").replace(/(?:left|right|[LR])$/, "").replace(/[_\d]/g, "").toLowerCase();

// Split the actual box surfaces at local y=0. The union is identical in the bind pose.
function splitSegment(node) {
  const meshes = node.children.filter(n => n.isMesh && n.geometry.type === "BoxGeometry");
  if (!meshes.length) return null;
  const lower = new THREE.Group();
  lower.name = node.name + "_lower";
  lower.userData.part = { ...node.userData.part, name: node.userData.part.name + "_lower" };
  node.add(lower);
  for (const mesh of meshes) {
    const { width, height, depth } = mesh.geometry.parameters;
    for (const sign of [1, -1]) {
      const piece = new THREE.Mesh(new THREE.BoxGeometry(width, height / 2, depth), mesh.material);
      piece.userData.rigOwnedGeometry = true;
      piece.position.set(0, sign * height / 4, 0);
      piece.castShadow = mesh.castShadow; piece.receiveShadow = mesh.receiveShadow; piece.renderOrder = mesh.renderOrder;
      (sign > 0 ? node : lower).add(piece);
    }
    node.remove(mesh);
  }
  for (const child of [...node.children])
    if (child !== lower && child.isGroup && child.position.y <= 0) lower.attach(child);
  return lower;
}

export function rigModel(root, prompt = "") {
  if (root.userData.rig) throw new Error("Model is already rigged");
  root.updateMatrixWorld(true);
  const originalBounds = new THREE.Box3().setFromObject(root);
  const parts = []; root.traverse(n => { if (n.userData.part && n.userData.part.sourceName !== "_") parts.push(n); });
  const find = (names, side) => parts.find(n => names.includes(stem(n)) && (!side || sideOf(n) === side));
  const bones = {}, rest = {}, notes = [], owned = new Set();
  const makeBone = (name, position, quaternion, parent, node) => {
    const bone = new THREE.Bone(); bone.name = "joint_" + name;
    bone.position.copy(position); bone.quaternion.copy(quaternion || Q());
    root.add(bone); root.updateMatrixWorld(true);
    if (parent) parent.attach(bone);
    if (node) { bone.attach(node); owned.add(node); }
    bones[name] = bone;
    return bone;
  };
  const motionRoot = makeBone("root", V(0, originalBounds.min.y, 0), Q(), null);
  const originalChildren = [...root.children].filter(n => n !== motionRoot);
  for (const node of originalChildren) motionRoot.attach(node);
  const body = find(["body", "torso", "potbody", "pot", "main", "chest"]) || parts[0];
  const torsoPivot = body ? world(body, [0, -(body.userData.part.size[1] || 1) * .35, 0]) : originalBounds.getCenter(V());
  const spine = makeBone("spine", torsoPivot, body?.getWorldQuaternion(Q()), motionRoot, body);
  if (body) for (const node of originalChildren) if (node !== body && node.parent === motionRoot) spine.attach(node);
  const head = find(["head"]);
  if (head && head !== body) {
    const h = head.userData.part.size[1];
    makeBone("neck", world(head, [0, -h * .5, 0]), head.getWorldQuaternion(Q()), spine, head);
  }
  for (const side of ["L", "R"]) {
    const arm = find(["upperarm", "arm", "flipper", "wing"], side);
    if (arm) {
      const h = arm.userData.part.size[1];
      let forearm = find(["forearm", "lowerarm"], side);
      if (!forearm) forearm = splitSegment(arm);
      root.updateMatrixWorld(true);
      const shoulder = makeBone("shoulder" + side, world(arm, [0, h / 2, 0]), arm.getWorldQuaternion(Q()), spine, arm);
      let elbow = shoulder;
      if (forearm) elbow = makeBone("elbow" + side, world(forearm, forearm.userData.part.name.endsWith("_lower") ? [0, 0, 0] : [0, forearm.userData.part.size[1] / 2, 0]), forearm.getWorldQuaternion(Q()), shoulder, forearm);
      const hand = find(["hand", "glove", "paw"], side);
      if (hand && !owned.has(hand)) makeBone("wrist" + side, world(hand, [0, hand.userData.part.size[1] / 2, 0]), hand.getWorldQuaternion(Q()), elbow, hand);
    }
    const leg = find(["leg", "upperleg", "thigh"], side);
    const foot = find(["foot", "boot", "shoe", "feet"], side);
    if (leg) {
      const h = leg.userData.part.size[1];
      let shin = find(["lowerleg", "shin", "calf"], side);
      if (!shin) shin = splitSegment(leg);
      root.updateMatrixWorld(true);
      const hip = makeBone("hip" + side, world(leg, [0, h / 2, 0]), leg.getWorldQuaternion(Q()), motionRoot, leg);
      let knee = hip;
      if (shin) knee = makeBone("knee" + side, world(shin, shin.userData.part.name.endsWith("_lower") ? [0, 0, 0] : [0, shin.userData.part.size[1] / 2, 0]), shin.getWorldQuaternion(Q()), hip, shin);
      if (foot && !owned.has(foot)) makeBone("ankle" + side, world(foot, [0, foot.userData.part.size[1] / 2, 0]), foot.getWorldQuaternion(Q()), knee, foot);
    } else if (foot) {
      // Stubby templates have feet but no leg mesh. Articulate the existing foot only.
      makeBone("ankle" + side, world(foot, [0, foot.userData.part.size[1] / 2, 0]), foot.getWorldQuaternion(Q()), motionRoot, foot);
      notes.push(`${side}: 짧은 발 구조 — 다리 메시가 없어 발목만 구성`);
    }
  }
  const tail = find(["tail"]);
  if (tail) makeBone("tail", world(tail, [0, 0, tail.userData.part.size[2] / 2]), tail.getWorldQuaternion(Q()), spine, tail);
  for (const [name, bone] of Object.entries(bones))
    rest[name] = { position: bone.position.clone(), quaternion: bone.quaternion.clone() };
  root.updateMatrixWorld(true);
  const feet = ["L", "R"].map(side => find(["foot", "boot", "shoe", "feet"], side)).filter(Boolean);
  const available = Object.keys(MOTIONS).filter(name => {
    if (["wave", "work", "eat"].includes(name)) return Boolean(bones.shoulderL || bones.shoulderR);
    if (["walk", "run"].includes(name)) return feet.length >= 2;
    return true;
  });
  const requested = root.userData.motion || inferMotion(prompt);
  const selected = available.includes(requested) ? requested : "idle";
  if (selected !== requested) notes.push(`${MOTIONS[requested]}에 필요한 부품이 없어 숨쉬기로 대체`);
  const summary = {
    version: 1, type: "rigid-bone-hierarchy", joints: Object.keys(bones), count: Object.keys(bones).length,
    selected, requested, available, notes,
  };
  root.userData.rig = summary;
  const rig = { root, bones, rest, feet, ground: originalBounds.min.y, summary, selected, available };
  root.animations = available.map(name => makeClip(rig, name));
  restorePose(rig);
  return rig;
}

export function restorePose(rig) {
  for (const [name, bone] of Object.entries(rig.bones)) {
    bone.position.copy(rig.rest[name].position); bone.quaternion.copy(rig.rest[name].quaternion);
  }
  rig.root.updateMatrixWorld(true);
}
const DURATIONS = { idle: 3, walk: 1.2, run: .72, wave: 2.4, talk: 2.4, dance: 1.8, jump: 1.5, surprised: 2, work: 2, eat: 2.6, sleep: 4 };

function makeClip(rig, preset) {
  const { bones, rest } = rig, duration = DURATIONS[preset], frames = Math.round(duration * 30);
  const times = [], positions = [], rotations = Object.fromEntries(Object.keys(bones).map(n => [n, []]));
  const rotate = (name, x = 0, y = 0, z = 0) => {
    if (bones[name]) bones[name].quaternion.copy(rest[name].quaternion).multiply(Q().setFromEuler(new THREE.Euler(x, y, z)));
  };
  for (let i = 0; i <= frames; i++) {
    const t = i / frames, s = Math.sin(t * Math.PI * 2), c = Math.cos(t * Math.PI * 2);
    restorePose(rig);
    rotate("spine", .018 * s, .025 * s, 0); rotate("neck", -.018 * s, .025 * s, 0);
    rotate("tail", 0, .16 * s, 0);
    let lift = 0;
    if (preset === "walk" || preset === "run") {
      const strength = preset === "run" ? .8 : .43;
      for (const [side, sign] of [["L", 1], ["R", -1]]) {
        rotate("hip" + side, strength * s * sign);
        rotate("knee" + side, Math.max(0, -s * sign) * strength);
        rotate("ankle" + side, (bones["hip" + side] ? -.12 : .25) * s * sign);
        // Short-foot templates step at the ankle without fabricating invisible legs.
        if (!bones["hip" + side] && bones["ankle" + side]) {
          bones["ankle" + side].position.z += strength * s * sign * .35;
          bones["ankle" + side].position.y += Math.max(0, -s * sign) * .13;
        }
        rotate("shoulder" + side, -strength * s * sign);
        rotate("elbow" + side, -.2 - (preset === "run" ? .65 : .1));
      }
      rotate("spine", preset === "run" ? .12 : .035, .04 * s, .025 * c);
    } else if (preset === "wave") {
      const side = bones.shoulderR ? "R" : "L", sign = side === "R" ? 1 : -1;
      rotate("shoulder" + side, -.15, 0, sign * 2.05);
      rotate("elbow" + side, 0, .1 * c, sign * (.3 + .32 * Math.sin(t * Math.PI * 4)));
      rotate("wrist" + side, 0, .2 * s); rotate("neck", 0, .08 * s, -.06);
    } else if (preset === "talk") {
      rotate("neck", .1 * Math.sin(t * Math.PI * 4), .12 * s);
      rotate("shoulderL", -.3 - .16 * s, 0, -.18); rotate("elbowL", -.5 - .2 * c);
      rotate("shoulderR", -.3 + .16 * s, 0, .18); rotate("elbowR", -.5 + .2 * c);
    } else if (preset === "dance") {
      rotate("spine", .05, .14 * s, .13 * s); rotate("neck", 0, -.14 * s, -.1 * s);
      rotate("shoulderL", .3 * c, 0, -.7 - .35 * s); rotate("shoulderR", -.3 * c, 0, .7 - .35 * s);
      rotate("elbowL", -.5 - .3 * c); rotate("elbowR", -.5 + .3 * c);
      rotate("hipL", .22 * s); rotate("hipR", -.22 * s);
    } else if (preset === "jump" || preset === "surprised") {
      const jump = Math.max(0, Math.sin(t * Math.PI * 2));
      lift = jump * (preset === "jump" ? .8 : .35);
      rotate("shoulderL", -.2, 0, -jump * 1.4); rotate("shoulderR", -.2, 0, jump * 1.4);
      rotate("hipL", -.18 * (1 - jump)); rotate("hipR", -.18 * (1 - jump));
      rotate("kneeL", .32 * (1 - jump)); rotate("kneeR", .32 * (1 - jump));
      rotate("neck", -.15 * jump);
    } else if (preset === "work") {
      const side = bones.shoulderR ? "R" : "L", other = side === "R" ? "L" : "R";
      rotate("shoulder" + side, -.6 + .22 * c, .18 * s, .15); rotate("elbow" + side, -.6 + .22 * s);
      rotate("shoulder" + other, -.35, 0, -.2); rotate("elbow" + other, -.5); rotate("neck", .08, .06 * s);
    } else if (preset === "eat") {
      const reach = (1 - c) / 2;
      const side = bones.shoulderR ? "R" : "L";
      rotate("shoulder" + side, -.25 - .7 * reach, -.2 * reach, .12);
      rotate("elbow" + side, -.2 - 1.05 * reach); rotate("wrist" + side, .25 * reach);
      rotate("neck", .08 * reach);
    } else if (preset === "sleep") {
      rotate("spine", .08 + .025 * s); rotate("neck", .23 + .08 * s, 0, .07);
      rotate("shoulderL", -.08); rotate("shoulderR", -.08);
    }
    rig.root.updateMatrixWorld(true);
    const contact = new THREE.Box3();
    if (rig.feet.length) rig.feet.forEach(foot => contact.union(new THREE.Box3().setFromObject(foot)));
    else contact.setFromObject(rig.root);
    bones.root.position.y += rig.ground - contact.min.y + lift;
    rig.root.updateMatrixWorld(true);
    times.push(t * duration);
    positions.push(...bones.root.position.toArray());
    for (const [name, bone] of Object.entries(bones)) rotations[name].push(...bone.quaternion.toArray());
  }
  // Bake ankle translation too for short-foot templates, in a separate deterministic pass.
  const tracks = [new THREE.VectorKeyframeTrack("joint_root.position", times, positions)];
  for (const name of Object.keys(bones)) tracks.push(new THREE.QuaternionKeyframeTrack(bones[name].name + ".quaternion", times, rotations[name]));
  if (["walk", "run"].includes(preset)) for (const [side, sign] of [["L", 1], ["R", -1]]) {
    if (bones["hip" + side] || !bones["ankle" + side]) continue;
    const values = [], strength = preset === "run" ? .8 : .43;
    for (let i = 0; i <= frames; i++) {
      const s = Math.sin(i / frames * Math.PI * 2), pos = rest["ankle" + side].position.clone();
      pos.z += strength * s * sign * .35; pos.y += Math.max(0, -s * sign) * .13; values.push(...pos.toArray());
    }
    tracks.push(new THREE.VectorKeyframeTrack(bones["ankle" + side].name + ".position", times, values));
  }
  return new THREE.AnimationClip(preset, duration, tracks);
}
