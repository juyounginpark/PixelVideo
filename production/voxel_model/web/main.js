import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { createLook } from "/vendor/look.js";
import { build, toOBJ, TEMPLATES } from "/model.mjs";
import { Assembly } from "/web/assembly.js";
import { Playback } from "/web/playback.js";
import { MOTIONS } from "/motion.mjs";
import { GLTFExporter } from "three/addons/exporters/GLTFExporter.js";
const $ = id => document.getElementById(id);
const canvas = $("view"), renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
const scene = new THREE.Scene();
scene.background = new THREE.Color("#fff8f3");
const camera = new THREE.PerspectiveCamera(30, 1, .1, 200);
const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true;
controls.minDistance = 3;
controls.maxDistance = 70;
scene.add(new THREE.HemisphereLight(0xffffff, 0xc8b8b0, 2.2));
const sun = new THREE.DirectionalLight(0xffffff, 1.6);
sun.position.set(-6, 12, 8); sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
Object.assign(sun.shadow.camera, { left: -12, right: 12, top: 12, bottom: -12, near: 1, far: 50 });
sun.shadow.bias = -.0008; sun.shadow.radius = 3; scene.add(sun);
const floor = new THREE.Mesh(new THREE.PlaneGeometry(200, 200), new THREE.ShadowMaterial({ opacity: .14, depthWrite: false }));
floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; scene.add(floor);
const look = createLook(renderer, scene, camera);
let current, currentCode = "", controller, assembly, ghost, playback, currentPrompt = "", lastTime = null;
let modelList = [], modelReady = false;
let automaticCamera = true;
controls.addEventListener("start", () => { automaticCamera = false; });
function fit() {
  if (!current) return;
  const box = new THREE.Box3().setFromObject(current), center = box.getCenter(new THREE.Vector3()), size = box.getSize(new THREE.Vector3());
  const radius = size.length() / 2;
  const angle = Math.min(camera.fov * Math.PI / 360, Math.atan(Math.tan(camera.fov * Math.PI / 360) * camera.aspect));
  const distance = radius / Math.sin(angle) * 1.35;
  controls.target.copy(center);
  camera.position.copy(center).add(new THREE.Vector3(.32, .20, 1).normalize().multiplyScalar(distance));
  controls.update();
}
function stage(name) { document.querySelectorAll("#stages span").forEach(el => el.classList.toggle("active", el.dataset.stage === name)); }
function show(code, prompt = "", autoplay = true) {
  const next = build(code);
  const nextPlayback = new Playback(next, prompt, scene);
  if (playback) playback.dispose();
  if (current) scene.remove(current);
  current = next; currentCode = code; currentPrompt = prompt; playback = nextPlayback; scene.add(current);
  floor.position.y = new THREE.Box3().setFromObject(current).min.y - .015;
  $("code").value = code;
  let count = 0; current.traverse(n => { if (n.isMesh) count++; });
  $("count").textContent = `${count} 조각`;
  $("motionSelect").replaceChildren(...playback.rig.available.map(key => new Option(MOTIONS[key], key)));
  $("motionSelect").value = playback.current;
  $("rigInfo").textContent = `관절 ${playback.rig.summary.count}개 · ${playback.rig.available.length}가지 동작`;
  $("rigInfo").title = playback.rig.summary.notes.join("\n");
  $("motionInfo").textContent = `${MOTIONS[playback.current]} · ${playback.rig.summary.notes.some(n => n.includes("대체")) ? playback.rig.summary.notes.at(-1) : "상황에 맞춘 기본 반복 동작"}`;
  playback.speed = Number($("speed").value);
  playback.visuals.visible = $("showJoints").checked;
  playback.paused = !autoplay; $("playPause").textContent = autoplay ? "일시정지" : "재생";
  stage(autoplay ? "play" : "rig");
  fit();
  $("status").textContent = "모델 준비 완료";
}
new ResizeObserver(() => {
  const r = canvas.parentElement.getBoundingClientRect();
  renderer.setSize(r.width, r.height, false); camera.aspect = r.width / r.height; camera.updateProjectionMatrix(); fit();
}).observe(canvas.parentElement);
renderer.setAnimationLoop(t => {
  const dt = lastTime === null ? 0 : Math.min((t - lastTime) / 1000, .05); lastTime = t;
  if (playback && !assembly) {
    playback.tick(dt);
    canvas.dataset.clip = playback.current;
    canvas.dataset.clipTime = String(playback.action?.time || 0);
  }
  if (assembly) {
    assembly.tick(t);
    $("count").textContent = `${assembly.count} 조각 조립`;
    if (automaticCamera && assembly.count && !assembly.lastBounds.isEmpty()) {
      const center = assembly.lastBounds.getCenter(new THREE.Vector3());
      const radius = assembly.lastBounds.getSize(new THREE.Vector3()).length() / 2;
      const angle = Math.min(camera.fov * Math.PI / 360, Math.atan(Math.tan(camera.fov * Math.PI / 360) * camera.aspect));
      const distance = Math.max(6, radius / Math.sin(angle) * 1.16);
      const target = center.clone().add(new THREE.Vector3(.32, .20, 1).normalize().multiplyScalar(distance));
      camera.position.lerp(target, .045); controls.target.lerp(center, .045);
    }
  }
  controls.update(); look.render(t / 1000);
});
const labels = { person:"사람",cat:"고양이",dog:"강아지",bear:"곰",bunny:"토끼",frog:"개구리",penguin:"펭귄",chick:"병아리",hamster:"햄스터",poop:"똥 캐릭터" };
for (const key of Object.keys(TEMPLATES)) $("template").add(new Option(labels[key], key));
$("template").value = "cat";
$("load").onclick = () => show(`use ${$("template").value}\n`);
$("fit").onclick = fit;
$("background").oninput = e => { scene.background.set(e.target.value); };
$("retro").onchange = e => { look.mode = e.target.checked ? 1 : 0; };
$("apply").onclick = () => { try { show($("code").value); } catch (e) { $("status").textContent = e.message; } };
function download(name, text, type = "text/plain") {
  const url = URL.createObjectURL(new Blob([text], { type })), a = document.createElement("a");
  a.href = url; a.download = name; a.click(); setTimeout(() => URL.revokeObjectURL(url), 3000);
}
$("obj").onclick = () => download("character.obj", toOBJ(current, "character.mtl").obj);
$("mtl").onclick = () => download("character.mtl", toOBJ(current).mtl);
$("json").onclick = () => playback.withRestPose(() => download("character.three.json", JSON.stringify(current.toJSON()), "application/json"));
$("glb").onclick = async () => {
  $("glb").disabled = true;
  try { await playback.withRestPose(async () => download("character.glb", await new GLTFExporter().parseAsync(current, { binary: true, animations: current.animations }), "model/gltf-binary")); }
  catch (error) { $("status").textContent = `저장 실패: ${error.message}`; }
  finally { $("glb").disabled = false; }
};
$("boxes").onclick = () => download("character.boxes", currentCode);
$("png").onclick = () => { look.render(); canvas.toBlob(blob => download("character.png", blob, "image/png")); };
$("cancel").onclick = () => controller?.abort();
$("motionSelect").onchange = () => { playback.select($("motionSelect").value); $("playPause").textContent = "일시정지"; $("motionInfo").textContent = `${MOTIONS[playback.current]} 재생 중`; stage("play"); };
$("playPause").onclick = () => {
  if (!playback.action) playback.select($("motionSelect").value);
  else playback.paused = !playback.paused;
  $("playPause").textContent = playback.paused ? "재생" : "일시정지";
};
$("restPose").onclick = () => { playback.reset(); $("playPause").textContent = "재생"; };
$("speed").oninput = () => { playback.speed = Number($("speed").value); $("speedValue").value = playback.speed.toFixed(2) + "×"; };
$("showJoints").onchange = () => { playback.visuals.visible = $("showJoints").checked; };
function updateEfforts(preferred) {
  const model = modelList.find(m => m.id === $("modelSelect").value);
  $("effortSelect").replaceChildren(...model.efforts.map(e => new Option(e, e)));
  $("effortSelect").value = model.efforts.includes(preferred) ? preferred : model.defaultEffort;
  $("modelInfo").textContent = `${model.label} / ${$("effortSelect").value}`;
}
function saveSelection() {
  try { localStorage.setItem("pixel-voxel-model-v2", JSON.stringify({ model: $("modelSelect").value, effort: $("effortSelect").value })); } catch {}
  $("modelInfo").textContent = `${$("modelSelect").selectedOptions[0].text} / ${$("effortSelect").value}`;
}
async function refreshModels() {
  modelReady = false; $("generate").disabled = true; $("refreshModels").disabled = true;
  try {
    const r = await fetch("/api/models"); const data = await r.json();
    if (!r.ok || !data.models?.length) throw new Error(data.error || "모델 목록이 비어 있습니다.");
    modelList = data.models;
    let saved; try { saved = JSON.parse(localStorage.getItem("pixel-voxel-model-v2")); } catch {}
    $("modelSelect").replaceChildren(...modelList.map(m => new Option(m.label, m.id)));
    const wanted = saved?.model || data.defaultModel;
    $("modelSelect").value = modelList.some(m => m.id === wanted) ? wanted : modelList[0].id;
    updateEfforts(saved?.effort || data.defaultEffort);
    $("modelSelect").disabled = false; $("effortSelect").disabled = false; modelReady = true;
  } catch (error) { $("modelInfo").textContent = `목록 조회 실패: ${error.message}`; }
  finally { $("refreshModels").disabled = false; $("generate").disabled = !modelReady || Boolean(controller); }
}
$("modelSelect").onchange = () => { updateEfforts($("effortSelect").value); saveSelection(); };
$("effortSelect").onchange = saveSelection;
$("refreshModels").onclick = refreshModels;
$("form").onsubmit = async e => {
  e.preventDefault();
  controller = new AbortController();
  const previousCode = currentCode;
  const previousPrompt = currentPrompt;
  const savedCamera = camera.position.clone(), savedTarget = controls.target.clone();
  if ($("edit").checked) {
    ghost = current.clone(true);
    const ghostMaterial = new THREE.MeshBasicMaterial({ color: 0xbca99e, transparent: true, opacity: .12, depthWrite: false });
    ghost.traverse(n => { if (n.isMesh) { n.material = ghostMaterial; n.castShadow = false; } });
    ghost.userData.material = ghostMaterial; scene.add(ghost);
  }
  scene.remove(current);
  playback.visuals.visible = false;
  assembly = new Assembly(scene); automaticCamera = true;
  document.body.dataset.building = "true";
  stage("model");
  const locked = ["load", "apply", "obj", "mtl", "json", "boxes", "png", "glb", "motionSelect", "playPause", "restPose", "speed", "showJoints", "modelSelect", "effortSelect", "refreshModels"];
  locked.forEach(id => { $(id).disabled = true; });
  $("generate").disabled = true; $("cancel").hidden = false;
  const started = Date.now(), requestController = controller;
  $("status").textContent = "생성 시작 · 0초 / 최대 3분";
  $("generate").textContent = "생성 중…";
  const timer = setInterval(async () => {
    const elapsed = Math.floor((Date.now() - started) / 1000);
    $("status").textContent = `생성 중 · ${elapsed}초 / 최대 3분`;
    try {
      const r = await fetch("/api/health", { signal: AbortSignal.timeout(3000) });
      const state = await r.json();
      if (controller === requestController && state.busy)
        $("status").textContent = `${state.phase} · ${elapsed}초 / 최대 3분`;
    } catch {}
  }, 1000);
  const deadline = setTimeout(() => requestController.abort("timeout"), 190000);
  try {
    const response = await fetch("/api/generate", { method: "POST", headers: { "Content-Type": "application/json", "Accept": "application/x-ndjson" },
      body: JSON.stringify({ prompt: $("prompt").value, prev: $("edit").checked ? currentCode : undefined, model: $("modelSelect").value, effort: $("effortSelect").value }), signal: controller.signal });
    if (!response.ok) { const error = await response.json(); throw new Error(error.error); }
    let data, buffer = "", liveCode = "";
    const receive = line => {
      if (!line.trim()) return;
      const event = JSON.parse(line);
      if (event.type === "error") throw new Error(event.error);
      if (event.type === "status") $("status").textContent = event.phase;
      if (event.type === "line") {
        assembly.enqueue(event.line); liveCode += event.line + "\n"; $("code").value = liveCode;
        $("status").textContent = `상자를 붙이는 중 · ${assembly.count} 조각`;
      }
      if (event.type === "done") data = event;
    };
    const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();
    for (;;) {
      const chunk = await reader.read();
      if (chunk.done) break;
      buffer += chunk.value;
      const lines = buffer.split("\n"); buffer = lines.pop(); lines.forEach(receive);
    }
    if (buffer.trim()) receive(buffer);
    if (!data) throw new Error("완료 응답을 받기 전에 연결이 끊겼습니다.");
    $("status").textContent = "마지막 부품을 붙이는 중…";
    await new Promise((resolve, reject) => {
      const check = () => {
        if (requestController.signal.aborted) return reject(new DOMException("Cancelled", "AbortError"));
        assembly.busy ? requestAnimationFrame(check) : resolve();
      }; check();
    });
    // Final validation uses the authoritative result; keep the smoothly reached camera.
    assembly.dispose(); assembly = null;
    clearInterval(timer);
    $("status").textContent = "관절 연결 상태 확인 중…"; stage("rig");
    await new Promise(resolve => requestAnimationFrame(resolve));
    show(data.code, data.prompt, false);
    playback.visuals.visible = true;
    await new Promise(resolve => setTimeout(resolve, 600));
    if (requestController.signal.aborted) throw new DOMException("Cancelled", "AbortError");
    stage("motion"); $("status").textContent = `${MOTIONS[playback.current]} 동작 준비`;
    await new Promise(resolve => requestAnimationFrame(resolve));
    playback.visuals.visible = $("showJoints").checked; playback.paused = false;
    $("playPause").textContent = "일시정지"; stage("play");
    $("status").textContent = `완성 · ${data.promptId}`;
  } catch (err) {
    if (assembly) { assembly.dispose(); assembly = null; }
    show(previousCode, previousPrompt); camera.position.copy(savedCamera); controls.target.copy(savedTarget); controls.update();
    $("status").textContent = requestController.signal.aborted
      ? requestController.signal.reason === "timeout" ? "응답 대기 시간이 초과되었습니다. 잠시 후 다시 시도해 주세요." : "생성을 취소했습니다."
      : `생성 실패: ${err.message}`;
  }
  finally {
    clearInterval(timer); clearTimeout(deadline);
    if (ghost) { scene.remove(ghost); ghost.userData.material.dispose(); ghost = null; }
    document.body.dataset.building = "false";
    locked.forEach(id => { $(id).disabled = false; });
    $("generate").disabled = !modelReady; $("generate").textContent = "캐릭터 만들기 ↗";
    $("cancel").hidden = true; controller = null;
  }
};
show("use cat\n");
fetch("/api/latest").then(r => r.json()).then(data => {
  if (data?.code && !controller && currentCode === "use cat\n") {
    show(data.code, data.prompt); $("prompt").value = data.prompt || "";
    $("status").textContent = `마지막 생성 결과 복원 · ${data.promptId}`;
  }
}).catch(() => {});
fetch("/api/auth").then(r => r.json()).then(data => {
  $("auth").textContent = data.loggedIn ? "● Codex 로그인 연결됨" : "로그인 필요 · 터미널에서 codex login";
}).catch(() => { $("auth").textContent = "Codex 로그인 상태를 확인하지 못했습니다."; });
refreshModels();
