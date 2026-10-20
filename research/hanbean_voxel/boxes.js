// 상자 언어 → three.js. 쓸궁지 영상처럼 크기가 제각각인 상자를 부모 기준으로 붙인다.
//   box 이름 부모 가로 세로 깊이 x y z #색 [rot rx ry rz] [mirror] [soft] [glass]
//   use 틀이름 [키=값 ...]      (templates.js의 기본 캐릭터를 펼친다)
//   hide 이름 [이름 ...]        (틀의 부품 숨기기)
// 이름 "_" = 이름 없음, 부모 "-" = 바닥(맨 위). x y z는 부모 상자 중심 기준, 회전은 도.
import * as THREE from "three";
import { TEMPLATES } from "./templates.js";

const n = (s) => (s === undefined || s === "" || isNaN(+s) ? null : +s);
const NAME = /^[A-Za-z_][\w]*$/;

export function parseLine(raw) {
  const t = raw.trim().split(/\s+/);
  const kind = t[0]?.toLowerCase();
  if (kind === "use") {
    const tpl = t[1]?.toLowerCase();
    if (!TEMPLATES[tpl]) return null;
    const params = {};
    for (const kv of t.slice(2)) { const [k, v] = kv.split("="); if (k && v) params[k.toLowerCase()] = v; }
    return { kind, tpl, params };
  }
  if (kind === "hide") return t.length > 1 ? { kind, names: t.slice(1).filter((x) => NAME.test(x)) } : null;
  if (kind !== "box" || t.length < 10) return null;
  const [, name, parent] = t;
  if (!NAME.test(name) || !(parent === "-" || NAME.test(parent))) return null;
  const nums = t.slice(3, 9).map(n);
  if (nums.some((v) => v === null)) return null;
  const color = t[9];
  if (!/^#[0-9a-f]{6}$/i.test(color)) return null;
  const spec = { kind, name, parent, size: nums.slice(0, 3).map((v) => Math.min(14, Math.max(0.04, Math.abs(v)))), pos: nums.slice(3, 6).map((v) => Math.max(-14, Math.min(14, v))), color: color.toLowerCase(), rot: [0, 0, 0], mirror: false, soft: false, glass: false };
  for (let i = 10; i < t.length; i++) {
    const w = t[i].toLowerCase();
    if (w === "mirror") spec.mirror = true;
    else if (w === "soft") spec.soft = true;
    else if (w === "glass") spec.glass = true;
    else if (w === "rot") { spec.rot = [n(t[i + 1]) || 0, n(t[i + 2]) || 0, n(t[i + 3]) || 0]; i += 3; }
  }
  return spec;
}

// use 줄은 틀의 box 줄들로 펼친다. 나머지는 그대로.
export function expand(spec) {
  if (spec?.kind !== "use") return spec ? [spec] : [];
  const tpl = TEMPLATES[spec.tpl];
  return tpl.build({ ...tpl.defaults, ...spec.params }).split("\n").map(parseLine).filter(Boolean);
}

// ---------- 재질: 얇은 판(눈·볼·입)은 조명 없이 납작하게, 나머지는 은은한 음영 ----------
const lit = {}, flat = {}, glass = {};
const mat = (c, decal, isGlass) => isGlass
  ? (glass[c] ||= new THREE.MeshLambertMaterial({ color: c, transparent: true, opacity: 0.28, depthWrite: false }))
  : decal
    ? (flat[c] ||= new THREE.MeshBasicMaterial({ color: c }))
    : (lit[c] ||= new THREE.MeshLambertMaterial({ color: c }));
const GEO = {};
const geo = (w, h, d) => (GEO[`${w},${h},${d}`] ||= new THREE.BoxGeometry(w, h, d));

function makePart(spec) {
  const [w, h, d] = spec.size;
  const decal = Math.min(w, h, d) <= 0.13;
  const m = mat(spec.color, decal, spec.glass);
  const node = new THREE.Group();
  if (spec.soft && !decal) {
    // 모서리를 깎은 통통한 상자(영상의 똥처럼 상자 셋을 겹친다)
    const c = Math.min(w, h, d) * 0.22;
    for (const [a, b, e] of [[w, h - c, d - c], [w - c, h, d - c], [w - c, h - c, d]]) {
      const mesh = new THREE.Mesh(geo(a, b, e), m);
      mesh.castShadow = !spec.glass;
      if (spec.glass) mesh.renderOrder = 5;
      node.add(mesh);
    }
  } else {
    const mesh = new THREE.Mesh(geo(w, h, d), m);
    mesh.castShadow = !decal && !spec.glass;
    if (spec.glass) mesh.renderOrder = 5;
    node.add(mesh);
  }
  node.position.set(...spec.pos);
  node.rotation.set(...spec.rot.map(THREE.MathUtils.degToRad));
  return node;
}

// ---------- 조립기: 줄이 올 때마다 상자를 붙이고, 톡 튀어나오는 애니메이션을 준다 ----------
export class Builder {
  constructor(root) {
    this.root = root;
    this.parts = new Map();   // 이름 → node
    this.twins = new Map();   // 이름 → mirror로 생긴 짝
    this.anim = [];           // { node, start, delay }
  }
  clear() {
    this.root.clear();
    this.parts.clear(); this.twins.clear(); this.anim = [];
  }
  // spec 하나를 붙인다. at = 애니메이션 시작 시각(없으면 바로 보임)
  add(spec, at) {
    if (spec.kind === "hide") {
      for (const nm of spec.names) for (const node of [this.parts.get(nm), this.twins.get(nm)]) node?.removeFromParent();
      return;
    }
    const parentOf = (nm, twin) => (nm === "-" ? this.root : (twin && this.twins.get(nm)) || this.parts.get(nm) || this.root);
    const node = makePart(spec);
    parentOf(spec.parent, false).add(node);
    // 같은 이름을 다시 쓰면 틀의 부품을 갈아 끼운다(짝도 같이 뺀다)
    if (spec.name !== "_") {
      this.parts.get(spec.name)?.removeFromParent();
      this.twins.get(spec.name)?.removeFromParent();
      this.twins.delete(spec.name);
      this.parts.set(spec.name, node);
    }
    this.pop(node, at);
    if (spec.mirror) {
      const tw = makePart({ ...spec, pos: [-spec.pos[0], spec.pos[1], spec.pos[2]], rot: [spec.rot[0], -spec.rot[1], -spec.rot[2]] });
      parentOf(spec.parent, true).add(tw);
      if (spec.name !== "_") this.twins.set(spec.name, tw);
      this.pop(tw, at === undefined ? undefined : at + 40);
    } else if (this.twins.has(spec.parent)) {
      // 대칭 부품의 자식은 짝에도 똑같이 붙인다(눈 반짝이 등)
      const tw = makePart({ ...spec, pos: [-spec.pos[0], spec.pos[1], spec.pos[2]], rot: [spec.rot[0], -spec.rot[1], -spec.rot[2]] });
      this.twins.get(spec.parent).add(tw);
      this.pop(tw, at === undefined ? undefined : at + 40);
    }
  }
  pop(node, at) {
    if (at === undefined) return;
    node.userData.home = node.position.clone();
    node.scale.setScalar(0.001);
    this.anim.push({ node, at });
  }
  get busy() { return this.anim.length > 0; }
  update(now) {
    const D = 320;
    this.anim = this.anim.filter(({ node, at }) => {
      const t = (now - at) / D;
      if (t < 0) return true;
      if (t >= 1) { node.scale.setScalar(1); node.position.copy(node.userData.home); return false; }
      const k = 1 + 2.7 * (t - 1) ** 3 + 1.7 * (t - 1) ** 2; // 살짝 넘쳤다 돌아오기
      node.scale.setScalar(Math.max(0.001, k));
      node.position.copy(node.userData.home);
      node.position.y += (1 - t) ** 3 * 1.2;
      return true;
    });
  }
}
