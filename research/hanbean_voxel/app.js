import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { parseLine, expand, Builder } from "./boxes.js";
import { createLook } from "./look.js";

const $ = (id) => document.getElementById(id);
const PAPER = 0xfff8f3;
const SWATCHES = ["#ff7b7b", "#ffd84a", "#7fd8be", "#8ec5ff", "#c3a6ff", "#ffb3c7", "#fff3d6", "#2b2433", "#ffffff", "#1f1f1f"];
const EXAMPLES = ["헤드폰 낀 졸린 고양이", "왕관 쓴 똥", "우주복 입은 햄스터", "떡볶이 먹는 펭귄", "선글라스 낀 비둘기", "기타 치는 개구리", "딸기 우유", "공룡 잠옷 입은 아기"];

// ---------- 3D 무대 ----------
const canvas = $("view");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: false });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
scene.background = new THREE.Color(PAPER);
const camera = new THREE.PerspectiveCamera(30, 1, 1, 200);
camera.position.set(6, 6, 20);

scene.add(new THREE.HemisphereLight(0xffffff, 0xc8b8b0, 2.2));
const sun = new THREE.DirectionalLight(0xffffff, 1.6);
sun.position.set(-6, 12, 8);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
Object.assign(sun.shadow.camera, { left: -9, right: 9, top: 9, bottom: -9, near: 1, far: 40 });
sun.shadow.bias = -0.0008;
sun.shadow.radius = 3;
scene.add(sun);

// 바닥은 그림자만 받고 깊이는 남기지 않는다(외곽선이 바닥 끝에 생기지 않게)
const ground = new THREE.Mesh(new THREE.PlaneGeometry(200, 200), new THREE.ShadowMaterial({ opacity: 0.14, depthWrite: false }));
ground.rotation.x = -Math.PI / 2;
ground.receiveShadow = true;
scene.add(ground);

const look = createLook(renderer, scene, camera);

// stage = 모델 받침. 다 만들면 모델 중심이 가운데 오도록 옮긴다.
const stage = new THREE.Group();
scene.add(stage);
const root = new THREE.Group();
stage.add(root);
const builder = new Builder(root);

// 고치는 동안 보이는 옛 모델(반투명)
const ghost = new THREE.Group();
const ghostMat = new THREE.MeshBasicMaterial({ color: 0xd9cfc8, transparent: true, opacity: 0.35, depthWrite: false });
stage.add(ghost);

// 작업대 바닥 격자
const grid = new THREE.GridHelper(12, 12, 0xe9cfc2, 0xf3e6de);
grid.position.y = 0.01;
Object.assign(grid.material, { transparent: true, opacity: 0.6, depthWrite: false }); // 외곽선이 안 생기게
grid.visible = false;
stage.add(grid);

// 첫 상자가 오기 전 통통 튀는 블록 셋
const hop = new THREE.Group();
["#ff7b7b", "#ffd84a", "#7fd8be"].forEach((c, k) => {
  const b = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), new THREE.MeshLambertMaterial({ color: c }));
  b.position.x = (k - 1) * 1.7;
  b.castShadow = true;
  hop.add(b);
});
hop.visible = false;
stage.add(hop);

const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true;
controls.enablePan = false;
controls.minDistance = 6;
controls.maxDistance = 60;
controls.target.set(0, 2.5, 0);
let idleTimer;
controls.addEventListener("start", () => { controls.autoRotate = false; clearTimeout(idleTimer); });
controls.addEventListener("end", () => { idleTimer = setTimeout(() => { if (state.mode === "make") controls.autoRotate = true; }, 4000); });
controls.autoRotateSpeed = 1.6;

// ---------- 상태 ----------
const state = { mode: "make", busy: false, code: "", prompt: "", size: [4, 5, 4], bg: "#ff7b7b" };

function resize() {
  const w = innerWidth, h = innerHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  if (state.mode === "profile") applyRing(); else applyBand();
  camera.updateProjectionMatrix();
}

// 머리(또는 안내 문구)와 아래 패널 사이 빈 공간. 캐릭터는 이 안에 들어오게 그린다.
function freeBand() {
  const empty = $("empty");
  const top = empty.hidden ? 72 : empty.getBoundingClientRect().bottom + 12;
  const bottom = innerHeight - $("sheet").offsetHeight + 24;
  return { top, h: Math.max(160, bottom - top), cy: (top + bottom) / 2 };
}
function applyBand(b = freeBand()) {
  camera.setViewOffset(innerWidth, innerHeight, 0, innerHeight / 2 - b.cy, innerWidth, innerHeight);
  camera.updateProjectionMatrix();
}
addEventListener("resize", resize);
new ResizeObserver(([e]) => document.documentElement.style.setProperty("--sheet-h", e.target.offsetHeight + "px")).observe($("sheet"));

renderer.setAnimationLoop((t) => {
  const now = performance.now();
  builder.update(now);
  if (hop.visible) hop.children.forEach((b, k) => {
    const ph = now / 260 + k * 1.1;
    b.position.y = 0.5 + Math.abs(Math.sin(ph)) * 1.8;
    b.rotation.y = ph * 0.6;
  });
  controls.update();
  look.render(t / 1000);
});

// 모델 크기·중심 재기
function measure() {
  root.updateMatrixWorld(true);
  const bb = new THREE.Box3().setFromObject(root);
  if (bb.isEmpty()) return { size: [4, 5, 4], offset: [0, 0, 0] };
  const s = bb.getSize(new THREE.Vector3()), c = bb.getCenter(new THREE.Vector3());
  const sp = stage.position;
  return { size: [s.x, s.y, s.z], offset: [sp.x - c.x, sp.y - bb.min.y, sp.z - c.z] };
}

// 모델 중심으로 받침을 옮긴다(완성 순간 살짝 통통)
function place(offset, animate) {
  const to = new THREE.Vector3(...offset);
  if (!animate) { stage.position.copy(to); stage.scale.setScalar(1); return; }
  const from = stage.position.clone(), start = performance.now();
  const step = (now) => {
    const k = Math.min(1, (now - start) / 600), e = 1 - (1 - k) ** 3;
    stage.position.lerpVectors(from, to, e);
    stage.scale.setScalar(1 + Math.sin(Math.min(1, k * 1.6) * Math.PI) * 0.06);
    if (k < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

// 코드 → 바로 조립(애니메이션 없이)
function show(code, animate = false) {
  builder.clear();
  stage.position.set(0, 0, 0);
  for (const line of code.split("\n")) for (const s of expand(parseLine(line))) builder.add(s);
  const m = measure();
  state.size = m.size;
  place(m.offset, animate);
  return root.children.length;
}

// 모델 크기에 맞춰 카메라를 부드럽게 옮긴다
function fit(animate = true, front = false, room = 1) {
  const [sx, sy, sz] = state.size;
  const r = Math.hypot(sx, sy, sz) / 2;
  const target = new THREE.Vector3(0, sy / 2, 0);
  let dist;
  if (state.mode === "profile") {
    const ring = ringRect();
    dist = (r * innerHeight) / (1.08 * ring.d * Math.tan(THREE.MathUtils.degToRad(camera.fov / 2)));
  } else {
    const band = freeBand();
    applyBand(band);
    const fit = Math.min(band.h, innerWidth) * 0.86;
    dist = (room * r * innerHeight) / (fit * Math.tan(THREE.MathUtils.degToRad(camera.fov / 2)));
  }
  // front: 완성 순간엔 얼굴이 보이는 3/4 정면에서 보여 준다
  const dir = front ? new THREE.Vector3(0.45, 0.3, 1).normalize() : camera.position.clone().sub(controls.target).normalize();
  const endPos = target.clone().add(dir.multiplyScalar(dist));
  if (!animate) { camera.position.copy(endPos); controls.target.copy(target); return; }
  const p0 = camera.position.clone(), t0 = controls.target.clone(), start = performance.now();
  const step = (now) => {
    const k = Math.min(1, (now - start) / 600), e = 1 - (1 - k) ** 3;
    camera.position.lerpVectors(p0, endPos, e);
    controls.target.lerpVectors(t0, target, e);
    if (k < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

// ---------- 만들기 ----------
const form = $("form"), input = $("prompt"), go = $("go");
const PHRASES = ["상자 나르는 중", "차곡차곡 쌓는 중", "색칠하는 중", "모양 다듬는 중", "얼굴 붙이는 중", "마무리하는 중"];

function setBusy(b, text = "만드는 중…") {
  state.busy = b;
  document.body.classList.toggle("busy", b);
  go.disabled = b;
  input.disabled = b;
  $("status").hidden = !b;
  $("statusText").textContent = text;
}

function startBuild(prev) {
  // 옛 모델은 반투명 그림자로 남겨 두고 빈 작업대에서 새로 쌓는다
  ghost.clear();
  if (prev) {
    const g = root.clone(true);
    g.traverse((o) => { if (o.isMesh) { o.material = ghostMat; o.castShadow = false; } });
    g.position.copy(stage.position);
    ghost.add(g);
  }
  builder.clear();
  stage.position.set(0, 0, 0);
  grid.visible = true;
  hop.visible = true;
  state.size = [4, 5, 4];
  fit();
  controls.autoRotateSpeed = 0.7;
  controls.autoRotate = true;
}

function endBuild() {
  grid.visible = false;
  hop.visible = false;
  ghost.clear();
  controls.autoRotateSpeed = 1.6;
}

async function generate(prompt) {
  const prev = state.code;
  setBusy(true, prev ? "고치는 중…" : "만드는 중…");
  $("empty").hidden = true;
  startBuild(prev);
  let code = "", buf = "", err = "", lines = 0, phrase = 0;
  const queue = [];
  // 줄이 한꺼번에 와도 상자를 하나씩 놓아 쌓이는 게 보이게 한다(틀의 부품은 더 빠르게)
  const pump = setInterval(() => {
    const s = queue.shift();
    if (!s) return;
    builder.add(s, performance.now());
    if (s.kind === "box") hop.visible = false;
    if (s.fast && queue[0]?.fast) builder.add(queue.shift(), performance.now() + 40);
  }, 90);
  const drained = () => new Promise((res) => { const chk = () => (queue.length ? setTimeout(chk, 50) : res()); chk(); });
  const settled = () => new Promise((res) => { const chk = () => (builder.busy ? requestAnimationFrame(chk) : res()); chk(); });
  const status = () => { $("statusText").textContent = `${PHRASES[phrase % PHRASES.length]}… ${lines ? `조각 ${lines}개` : ""}`; };
  const phraseT = setInterval(() => { phrase++; status(); }, 1700);
  status();
  try {
    const res = await fetch("/api/generate", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ prompt, prev: prev || undefined }),
    });
    if (!res.ok) {
      const j = await res.json().catch(() => ({}));
      throw new Error(j.error || "문제가 생겼어요. 다시 해 주세요.");
    }
    const reader = res.body.pipeThrough(new TextDecoderStream()).getReader();
    const take = (line) => {
      // !NO = Claude가 거절(선정적·무서운 요청), !ERR = 서버 오류
      if (line.startsWith("!NO") || line.startsWith("!ERR")) { err = line.replace(/^!(NO|ERR)\s*/, "").trim() || "만들 수 없는 요청이에요."; return; }
      const spec = parseLine(line);
      if (!spec) return;
      code += line.trim() + "\n";
      const parts = expand(spec);
      if (spec.kind === "use") parts.forEach((p) => (p.fast = true));
      queue.push(...parts);
      lines++;
      status();
    };
    for (;;) {
      const { value, done } = await reader.read();
      if (done || err) { if (err) reader.cancel().catch(() => {}); break; }
      buf += value;
      const parts = buf.split("\n");
      buf = parts.pop();
      parts.forEach(take);
    }
    if (buf && !err) take(buf);
    if (err) throw new Error(err);
    if (!lines) throw new Error("모델이 비어 있어요. 조금 다르게 적어 볼까요?");
    await drained();
    $("statusText").textContent = "마지막 상자 붙이는 중…";
    await settled();
  } catch (e) {
    clearInterval(phraseT); clearInterval(pump);
    endBuild();
    setBusy(false);
    if (prev) show(prev);
    else { show(MASCOT); fit(true, true, 1.1); $("empty").hidden = false; }
    toast(e.message);
    return;
  }
  clearInterval(phraseT); clearInterval(pump);
  endBuild();
  setBusy(false);
  state.code = code;
  state.prompt = prev ? `${state.prompt} + ${prompt}` : prompt;
  const m = measure();
  state.size = m.size;
  place(m.offset, true);
  controls.autoRotate = false;
  fit(true, true);
  idleTimer = setTimeout(() => { if (state.mode === "make") controls.autoRotate = true; }, 2500);
  toast("완성!");
  input.value = "";
  afterMade();
  setTimeout(saveRecent, 900);
}

function afterMade() {
  $("after").hidden = false;
  $("chips").hidden = true;
  input.placeholder = "어떻게 고칠까요? 예) 모자 씌워 줘";
  go.textContent = "고치기";
}

const MASCOT = "use poop";
function reset() {
  state.code = ""; state.prompt = "";
  show(MASCOT);
  fit(true, true, 1.1);
  $("after").hidden = true;
  $("chips").hidden = false;
  $("empty").hidden = false;
  input.placeholder = "예: 헤드폰 낀 졸린 고양이";
  go.textContent = "만들기";
  history.replaceState(null, "", location.pathname);
  input.focus();
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const p = input.value.trim();
  if (!p || state.busy) return;
  input.blur();
  generate(p);
});
$("btnNew").onclick = reset;

const chips = $("chips");
for (const ex of EXAMPLES) {
  const b = document.createElement("button");
  b.type = "button"; b.className = "chip"; b.textContent = ex;
  b.onclick = () => { input.value = ex; form.requestSubmit(); };
  chips.append(b);
}

// ---------- 프로필 사진 ----------
function ringRect() {
  const sheetH = $("sheet").getBoundingClientRect().height;
  const top = 70, avail = innerHeight - sheetH - top - 12;
  const d = Math.max(160, Math.min(innerWidth - 40, avail, 520));
  return { d, cx: innerWidth / 2, cy: top + avail / 2 };
}

function applyRing() {
  const r = ringRect(), ring = $("ring");
  Object.assign(ring.style, { width: r.d + "px", height: r.d + "px", left: r.cx - r.d / 2 + "px", top: r.cy - r.d / 2 + "px" });
  // 렌더 중심을 링 중심으로 옮긴다
  camera.setViewOffset(innerWidth, innerHeight, 0, innerHeight / 2 - r.cy, innerWidth, innerHeight);
  camera.updateProjectionMatrix();
}

function setBg(hex) {
  state.bg = hex;
  scene.background.set(hex);
  $("bgPick").value = hex;
  const preset = SWATCHES.includes(hex);
  document.querySelectorAll(".sw").forEach((s) => s.classList.toggle("on", s.dataset.c ? s.dataset.c === hex : !preset));
}

const sw = $("swatches");
for (const c of SWATCHES) {
  const b = document.createElement("button");
  b.className = "sw"; b.style.background = c; b.dataset.c = c; b.setAttribute("aria-label", c);
  b.type = "button";
  b.onclick = () => setBg(c);
  sw.insertBefore(b, sw.lastElementChild);
}
$("bgPick").addEventListener("input", (e) => setBg(e.target.value));
$("shadowOn").addEventListener("change", (e) => { ground.visible = e.target.checked; });
$("retroOn").addEventListener("change", (e) => { look.mode = e.target.checked ? 1 : 0; });

let enteredAt = 0;
function enterProfile() {
  state.mode = "profile";
  document.body.classList.add("profile");
  enteredAt = performance.now();
  $("makePanel").hidden = true;
  $("profilePanel").hidden = false;
  $("ring").hidden = false;
  controls.autoRotate = false;
  setBg(state.bg);
  look.mode = $("retroOn").checked ? 1 : 0;
  // 자동 회전의 남은 관성을 끊고 정면에서 살짝 위로
  controls.enableDamping = false; controls.update(); controls.enableDamping = true;
  const t = controls.target.clone();
  camera.position.copy(t).add(new THREE.Vector3(0.35, 0.28, 1).normalize().multiplyScalar(60));
  requestAnimationFrame(() => { applyRing(); fit(); });
}

function exitProfile() {
  state.mode = "make";
  document.body.classList.remove("profile");
  $("makePanel").hidden = false;
  $("profilePanel").hidden = true;
  $("ring").hidden = true;
  scene.background.set(PAPER);
  ground.visible = true;
  look.mode = 0;
  fit(true, true);
  controls.autoRotate = true;
}

// 화면 그대로를 크게 렌더한 뒤 링 부분만 잘라 낸다
function snapshot(out, rect) {
  const w = innerWidth, h = innerHeight;
  const s = Math.min(out / rect.d, 4096 / Math.max(w, h));
  const prevPR = renderer.getPixelRatio();
  renderer.setPixelRatio(s);
  renderer.setSize(w, h, false);
  look.render();
  const c = document.createElement("canvas");
  c.width = c.height = out;
  c.getContext("2d").drawImage(canvas, (rect.cx - rect.d / 2) * s, (rect.cy - rect.d / 2) * s, rect.d * s, rect.d * s, 0, 0, out, out);
  renderer.setPixelRatio(prevPR);
  renderer.setSize(w, h, false);
  return c;
}

$("btnProfile").onclick = enterProfile;
$("btnBack").onclick = exitProfile;
$("btnSave").onclick = () => {
  if (performance.now() - enteredAt < 500) return; // 패널이 바뀌는 순간의 겹친 탭 무시
  const c = snapshot(1080, ringRect());
  const url = c.toDataURL("image/png");
  $("saveImg").src = url;
  $("saveLink").href = url;
  $("saveDlg").showModal();
};

// ---------- 내 작품 (이 기기에만) ----------
const KEY = "ucbox.recent";
// 화면에서 모델이 차지하는 정사각형(썸네일용)
function modelRect(pad = 1.2) {
  root.updateMatrixWorld(true);
  const bb = new THREE.Box3().setFromObject(root), v = new THREE.Vector3();
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  for (let i = 0; i < 8; i++) {
    v.set(i & 1 ? bb.max.x : bb.min.x, i & 2 ? bb.max.y : bb.min.y, i & 4 ? bb.max.z : bb.min.z).project(camera);
    const sx = ((v.x + 1) / 2) * innerWidth, sy = ((1 - v.y) / 2) * innerHeight;
    x0 = Math.min(x0, sx); x1 = Math.max(x1, sx); y0 = Math.min(y0, sy); y1 = Math.max(y1, sy);
  }
  const d = Math.min(Math.max(x1 - x0, y1 - y0) * pad, innerWidth, innerHeight);
  return { d, cx: (x0 + x1) / 2, cy: (y0 + y1) / 2 };
}
const loadRecent = () => { try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch { return []; } };
function saveRecent() {
  if (!state.code) return;
  const thumb = snapshot(200, modelRect()).toDataURL("image/jpeg", 0.82);
  const list = [{ p: state.prompt, c: state.code, t: thumb }, ...loadRecent().filter((r) => r.c !== state.code)].slice(0, 18);
  try { localStorage.setItem(KEY, JSON.stringify(list)); } catch {}
}
$("btnRecent").onclick = () => {
  const box = $("recentList");
  box.textContent = "";
  const list = loadRecent();
  if (!list.length) box.innerHTML = '<p class="hint none">아직 만든 캐릭터가 없어요</p>';
  for (const r of list) {
    const b = document.createElement("button");
    b.type = "button";
    const img = document.createElement("img"); img.src = r.t; img.alt = "";
    const sp = document.createElement("span"); sp.textContent = r.p;
    b.append(img, sp);
    b.onclick = () => { $("recentDlg").close(); load(r.p, r.c); };
    box.append(b);
  }
  $("recentDlg").showModal();
};

function load(prompt, code) {
  if (state.mode === "profile") exitProfile();
  state.code = code; state.prompt = prompt;
  $("empty").hidden = true;
  show(code);
  fit(true, true);
  controls.autoRotate = true;
  afterMade();
}

// ---------- 링크 공유 (모델을 주소에 압축해 넣는다) ----------
const b64u = (bytes) => btoa(String.fromCharCode(...bytes)).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
const unb64u = (s) => Uint8Array.from(atob(s.replace(/-/g, "+").replace(/_/g, "/")), (c) => c.charCodeAt(0));
async function pack(obj) {
  const cs = new Blob([JSON.stringify(obj)]).stream().pipeThrough(new CompressionStream("deflate-raw"));
  return b64u(new Uint8Array(await new Response(cs).arrayBuffer()));
}
async function unpack(s) {
  const ds = new Blob([unb64u(s)]).stream().pipeThrough(new DecompressionStream("deflate-raw"));
  return JSON.parse(await new Response(ds).text());
}
$("btnShare").onclick = async () => {
  const url = `${location.origin}${location.pathname}#m=${await pack({ p: state.prompt, c: state.code })}`;
  history.replaceState(null, "", url);
  try {
    if (navigator.share) await navigator.share({ title: "쓸궁지 캐릭터 공방", text: `내가 만든 캐릭터: ${state.prompt}`, url });
    else { await navigator.clipboard.writeText(url); toast("링크를 복사했어요"); }
  } catch {}
};

// ---------- 기타 ----------
let toastT;
function toast(msg) {
  const t = $("toast");
  t.textContent = msg; t.hidden = false;
  clearTimeout(toastT);
  toastT = setTimeout(() => (t.hidden = true), 3200);
}

// 방문 알림(나중에 통계에서 방문자·접속자 수로 본다). 화면이 보일 때만 3분마다.
const hit = () => { if (document.visibilityState === "visible") fetch("/api/hit", { method: "POST", keepalive: true }).catch(() => {}); };
hit();
setInterval(hit, 180000);

resize();
show(MASCOT);
camera.position.set(0.45, 0.3, 1).multiplyScalar(20);
fit(false, true, 1.1);
controls.autoRotate = true;
const m = location.hash.match(/^#m=(.+)$/);
if (m) unpack(m[1]).then((o) => load(o.p, o.c)).catch(() => toast("링크가 깨졌어요"));
