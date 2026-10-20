import http from "node:http";
import { readFile, writeFile, appendFile, mkdir, mkdtemp, rm } from "node:fs/promises";
import { spawn } from "node:child_process";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";
import { build, TEMPLATES, parseModelLine } from "./model.mjs";
import { rigModel } from "./rig.mjs";
import { parseLine, expand } from "./vendor/boxes.js";
import { streamCodex, listCodexModels, BASE_INSTRUCTIONS, GENERATION_MODEL, GENERATION_EFFORT } from "./codex-stream.mjs";
const root = path.dirname(fileURLToPath(import.meta.url));
const port = Number(process.env.VOXEL_PORT || 8766);
const origin = `http://127.0.0.1:${port}`;
const codex = process.env.VOXEL_CODEX || "codex";
const logPath = path.resolve(root, "../../PROMPT_LOG.md");
const instructions = await readFile(path.join(root, "generation-instructions-v3.txt"), "utf8");
const catalog = Object.fromEntries(Object.entries(TEMPLATES).map(([k, v]) =>
  [k, { description: v.desc, defaults: v.defaults, parts: v.parts, code: v.build(v.defaults) }]));
let busy = false;
let modelCache = null, modelCacheAt = 0, modelQuery = null;
async function getModels() {
  if (modelCache && Date.now() - modelCacheAt < 300000) return modelCache;
  if (!modelQuery) modelQuery = listCodexModels(codex, root, AbortSignal.timeout(20000))
    .then(models => { modelCache = models; modelCacheAt = Date.now(); return models; })
    .finally(() => { modelQuery = null; });
  return modelQuery;
}
let progress = { phase: "준비", startedAt: null, lastError: null, model: GENERATION_MODEL, effort: GENERATION_EFFORT };
function run(args, input, cwd, signal, onEvent) {
  return new Promise((resolve, reject) => {
    const child = spawn(codex, args, { cwd, windowsHide: true, shell: false, signal,
      stdio: ["pipe", "pipe", "pipe"] });
    let stdout = "", stderr = "", eventBuffer = "", processError;
    child.stdout.on("data", d => {
      stdout = (stdout + d).slice(-500000);
      if (!onEvent) return;
      eventBuffer += d;
      const lines = eventBuffer.split("\n"); eventBuffer = lines.pop();
      for (const line of lines) { try { onEvent(JSON.parse(line)); } catch {} }
    });
    child.stderr.on("data", d => { stderr = (stderr + d).slice(-4000); });
    // Abort emits error before close; wait for process shutdown before removing its files.
    child.on("error", error => { processError = error; });
    child.stdin.on("error", () => {});
    child.on("close", code => processError ? reject(processError) : code === 0 ? resolve(stdout) : reject(new Error(`Codex 종료 코드 ${code}. ${stderr.slice(-1200)}`)));
    child.stdin.end(input || "");
  });
}
async function logPrompt(prompt, model, effort) {
  const log = await readFile(logPath, "utf8");
  const ids = [...log.matchAll(/\bP-(\d+)\b/g)].map(m => Number(m[1]));
  const id = `P-${String(Math.max(0, ...ids) + 1).padStart(3, "0")}`;
  await appendFile(logPath, `\n\n## ${id} — 로컬 OAuth 모델 생성\n날짜: ${new Date().toLocaleString("sv-SE", { timeZone: "Asia/Seoul" })} Asia/Seoul\n도구: Codex app-server, ChatGPT 로그인. 실행 전 원문 기록. 모델: ${model} / ${effort}. 원본 서버 프롬프트 아님.\n\nBASE INSTRUCTIONS:\n${BASE_INSTRUCTIONS}\n\nUSER INPUT:\n${prompt}\n`, "utf8");
  return id;
}
async function generate(body, signal, emit = () => {}) {
  if (typeof body.prompt !== "string" || !body.prompt.trim() || body.prompt.length > 2000)
    throw new Error("요청을 1~2000자로 입력하세요.");
  if (body.prev !== undefined && (typeof body.prev !== "string" || body.prev.length > 40000))
    throw new Error("이전 모델이 너무 큽니다.");
  const model = body.model || GENERATION_MODEL, effort = body.effort || GENERATION_EFFORT;
  const selected = (await getModels()).find(m => m.id === model);
  if (!selected || !selected.efforts.includes(effort)) throw new Error("선택한 모델 또는 추론 강도가 현재 모델 목록에 없습니다.");
  progress.model = model; progress.effort = effort;
  const prompt = `${instructions}\nTEMPLATE CATALOG:\n${JSON.stringify(catalog)}\nUSER DATA:\n${JSON.stringify({ request: body.prompt, previousModel: body.prev || "" })}`;
  const id = await logPrompt(prompt, model, effort);
  const dir = await mkdtemp(path.join(os.tmpdir(), "pixel-voxel-"));
  try {
    progress.phase = "Codex 연결 중";
    emit({ type: "status", phase: progress.phase, promptId: id });
    const buffers = new Map();
    let streamedLines = 0, firstLineMs = null, actualModel = null;
    const takeLine = line => {
      const value = line.trim();
      if (!value || !parseModelLine(value)) return;
      if (++streamedLines > 180) throw new Error("생성 명령이 180줄을 초과했습니다.");
      if (firstLineMs === null) firstLineMs = Date.now() - progress.startedAt;
      progress.phase = `부품 조립 중 · 명령 ${streamedLines}개`;
      emit({ type: "line", line: value });
    };
    const text = await streamCodex({
      executable: codex, cwd: dir, prompt, signal, model, effort,
      onStatus: (phase, extra = {}) => {
        progress.phase = phase;
        if (extra.model) { actualModel = extra.model; progress.model = actualModel; }
        if (extra.effort) progress.effort = extra.effort;
        emit({ type: "status", phase, ...extra });
      },
      onDelta: (delta, itemId) => {
        const buffer = (buffers.get(itemId) || "") + delta;
        if (buffer.length > 40000) throw new Error("생성 응답이 너무 큽니다.");
        const lines = buffer.split("\n"); buffers.set(itemId, lines.pop());
        lines.forEach(takeLine);
      },
    });
    for (const buffer of buffers.values()) takeLine(buffer);
    const code = text.split("\n").filter(line => line.trim() && !line.trim().startsWith("```")).join("\n");
    progress.phase = "모델 검사 및 저장 중";
    if (typeof code !== "string" || code.length > 40000 || code.split("\n").length > 180)
      throw new Error("생성 결과의 크기 또는 형식이 잘못되었습니다.");
    for (const line of code.split("\n").filter(l => l.trim())) {
      const parsed = parseModelLine(line);
      if (!parsed) throw new Error("생성 결과에 해석할 수 없는 명령이 있습니다.");
      if (parsed.kind === "motion") continue;
      for (const spec of expand(parsed))
        if (spec.kind === "box" && ![...spec.size, ...spec.pos, ...spec.rot].every(Number.isFinite))
          throw new Error("모델 좌표가 올바르지 않습니다.");
    }
    const modelRoot = build(code);
    progress.phase = "관절 연결 중";
    emit({ type: "stage", stage: "rig", phase: progress.phase });
    const rig = rigModel(modelRoot, body.prompt);
    emit({ type: "rig", rig: rig.summary });
    progress.phase = "기본 동작 클립 생성 완료";
    emit({ type: "animation", selected: rig.selected, clips: rig.available });
    await mkdir(path.join(root, "output"), { recursive: true });
    const filename = `${id}.boxes`;
    await writeFile(path.join(root, "output", filename), code + "\n");
    const result = { code, promptId: id, prompt: body.prompt, createdAt: new Date().toISOString(),
      model: actualModel, effort: progress.effort, rig: rig.summary,
      animations: modelRoot.animations.map(c => ({ name: c.name, duration: c.duration })),
      streaming: { firstLineMs, totalMs: Date.now() - progress.startedAt, lines: streamedLines } };
    await writeFile(path.join(root, "output", "latest.json"), JSON.stringify(result));
    await appendFile(logPath, `\n${id} 실행 완료. 결과: production/voxel_model/output/${filename}\n`);
    progress.phase = "완료";
    return result;
  } catch (error) {
    progress.lastError = error.name === "AbortError" ? "생성이 취소되었거나 대기 시간을 초과했습니다." : error.message;
    await appendFile(logPath, `\n${id} 실행 실패/취소. 원인: ${progress.lastError}. 모델 결과 미승인.\n`);
    throw error;
  } finally {
    const resolved = path.resolve(dir), tempRoot = path.resolve(os.tmpdir());
    if (path.dirname(resolved) !== tempRoot || !path.basename(resolved).startsWith("pixel-voxel-"))
      throw new Error("Unexpected temporary directory");
    await rm(resolved, { recursive: true, force: true, maxRetries: 5, retryDelay: 200 });
  }
}
const mime = { ".html": "text/html", ".js": "text/javascript", ".mjs": "text/javascript", ".css": "text/css" };
const server = http.createServer(async (req, res) => {
  const json = (status, data) => { res.writeHead(status, { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" }); res.end(JSON.stringify(data)); };
  try {
    if (req.headers.host !== `127.0.0.1:${port}` && req.headers.host !== `localhost:${port}`) return json(403, { error: "Invalid host" });
    const url = new URL(req.url, origin);
    if (url.pathname === "/api/health") return json(200, { app: "pixel-voxel-local", busy, ...progress,
      elapsedSeconds: busy ? Math.floor((Date.now() - progress.startedAt) / 1000) : 0 });
    if (url.pathname === "/api/models" && req.method === "GET")
      return json(200, { models: await getModels(), defaultModel: GENERATION_MODEL, defaultEffort: GENERATION_EFFORT });
    if (url.pathname === "/api/latest" && req.method === "GET") {
      try { return json(200, JSON.parse(await readFile(path.join(root, "output", "latest.json"), "utf8"))); }
      catch (error) { if (error.code === "ENOENT") return json(200, null); throw error; }
    }
    if (url.pathname === "/api/auth" && req.method === "GET") {
      const status = await run(["login", "status"], "", root, AbortSignal.timeout(10000));
      return json(200, { loggedIn: true, message: status.trim() || "Codex 로그인 사용" });
    }
    if (url.pathname === "/api/generate" && req.method === "POST") {
      if (req.headers.origin !== origin && req.headers.origin !== `http://localhost:${port}`) return json(403, { error: "Invalid origin" });
      if (!req.headers["content-type"]?.startsWith("application/json")) return json(415, { error: "JSON required" });
      if (busy) return json(409, { error: "현재 모델을 생성 중입니다." });
      busy = true;
      progress = { phase: "요청 준비 중", startedAt: Date.now(), lastError: null, model: GENERATION_MODEL, effort: GENERATION_EFFORT };
      let timedOut = false;
      const streaming = req.headers.accept?.includes("application/x-ndjson");
      const emit = event => { if (streaming && !res.destroyed) res.write(JSON.stringify(event) + "\n"); };
      const controller = new AbortController(), timer = setTimeout(() => { timedOut = true; controller.abort(); }, 180000);
      res.on("close", () => { if (!res.writableEnded) controller.abort(); });
      try {
        let raw = "";
        for await (const chunk of req) { raw += chunk; if (raw.length > 60000) throw new Error("요청이 너무 큽니다."); }
        const body = JSON.parse(raw);
        if (streaming) {
          res.writeHead(200, { "Content-Type": "application/x-ndjson; charset=utf-8", "Cache-Control": "no-store", "X-Accel-Buffering": "no" });
          res.flushHeaders();
        }
        const result = await generate(body, controller.signal, emit);
        if (!res.destroyed) { if (streaming) { emit({ type: "done", ...result }); res.end(); } else json(200, result); }
      } catch (error) {
        const message = timedOut ? "생성이 3분 안에 끝나지 않았습니다. 요청을 짧게 바꿔 다시 시도해 주세요."
          : error.name === "AbortError" ? "생성이 취소되었습니다." : error.message;
        progress.phase = "실패"; progress.lastError = message;
        console.error(JSON.stringify({ at: new Date().toISOString(), error: message }));
        if (!res.destroyed) {
          if (res.headersSent) { emit({ type: "error", error: message }); res.end(); }
          else json(timedOut ? 504 : 500, { error: message });
        }
      } finally { clearTimeout(timer); busy = false; }
      return;
    }
    if (req.method !== "GET") return json(405, { error: "Method not allowed" });
    const name = decodeURIComponent(url.pathname === "/" ? "/web/index.html" : url.pathname);
    if (!/^\/(web\/|vendor\/|node_modules\/three\/|(?:model|rig|motion|builder)\.mjs$)/.test(name) || name.split("/").includes("..")) return json(404, { error: "Not found" });
    const file = path.resolve(root, "." + name);
    if (!file.startsWith(root + path.sep) || !mime[path.extname(file)]) return json(404, { error: "Not found" });
    const data = await readFile(file);
    res.writeHead(200, { "Content-Type": mime[path.extname(file)] + "; charset=utf-8", "Cache-Control": "no-store" });
    res.end(data);
  } catch (e) { if (!res.destroyed && !res.headersSent) json(500, { error: e.message }); }
});
server.listen(port, "127.0.0.1", () => console.log(`PIXEL voxel local: ${origin}`));
