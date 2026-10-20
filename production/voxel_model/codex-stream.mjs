import { spawn } from "node:child_process";
import { createInterface } from "node:readline";
export const GENERATION_MODEL = "gpt-6-astra";
export const GENERATION_EFFORT = "medium";
export const BASE_INSTRUCTIONS = "You generate box-language 3D geometry and a motion command from the user's supplied specification. Output only the requested model and motion commands. Never use tools or inspect the environment.";

// Official app-server stdio protocol: emit actual agent-message deltas as they arrive.
export function streamCodex({ executable, cwd, prompt, signal, onDelta, onStatus, model = GENERATION_MODEL, effort = GENERATION_EFFORT }) {
  return new Promise((resolve, reject) => {
    const child = spawn(executable, ["app-server", "--stdio"], {
      cwd, windowsHide: true, shell: false, stdio: ["pipe", "pipe", "pipe"],
    });
    const pending = new Map(), messages = new Map();
    let nextId = 1, finished = false, failure = null;
    const send = value => { if (!child.stdin.destroyed) child.stdin.write(JSON.stringify(value) + "\n"); };
    const rpc = (method, params) => new Promise((ok, fail) => {
      const id = nextId++; pending.set(id, { ok, fail }); send({ id, method, params });
    });
    function finish(error) {
      if (finished) return;
      finished = true; failure = error;
      signal?.removeEventListener("abort", abort);
      for (const p of pending.values()) p.fail(error || new Error("Session closed"));
      pending.clear();
      child.kill();
    }
    const abort = () => finish(new DOMException("Generation cancelled", "AbortError"));
    signal?.addEventListener("abort", abort, { once: true });
    if (signal?.aborted) abort();
    child.stdin.on("error", error => { if (!finished) finish(error); });
    child.stderr.on("data", () => {}); // Do not forward diagnostic output or reasoning to the browser.
    child.on("error", error => finish(error));
    child.on("close", code => {
      signal?.removeEventListener("abort", abort);
      if (!finished) { finished = true; failure = new Error(`Codex stream closed (${code})`); }
      for (const p of pending.values()) p.fail(failure || new Error("Session closed"));
      pending.clear();
      failure ? reject(failure) : resolve([...messages.values()].join("\n"));
    });
    createInterface({ input: child.stdout }).on("line", raw => {
      let message;
      try { message = JSON.parse(raw); } catch { return; }
      if (message.id !== undefined && !message.method) {
        const waiter = pending.get(message.id);
        if (waiter) { pending.delete(message.id); message.error ? waiter.fail(new Error(message.error.message)) : waiter.ok(message.result); }
        return;
      }
      if (message.id !== undefined && message.method) {
        // This renderer never approves tools, command execution or file edits.
        send({ id: message.id, error: { code: -32601, message: "Model generation does not use tools." } });
        return;
      }
      try {
        const p = message.params || {};
        if (message.method === "turn/started") onStatus("캐릭터 구상 중");
        if (message.method === "item/agentMessage/delta") {
          messages.set(p.itemId, (messages.get(p.itemId) || "") + p.delta);
          onDelta(p.delta, p.itemId);
        }
        if (message.method === "item/completed" && p.item?.type === "agentMessage") {
          const streamed = messages.get(p.item.id) || "";
          if (!streamed && p.item.text) onDelta(p.item.text, p.item.id);
          messages.set(p.item.id, p.item.text || streamed);
        }
        if (message.method === "turn/completed")
          finish(p.turn.status === "completed" ? null : new Error(p.turn.error?.message || `Generation ${p.turn.status}`));
      } catch (error) { finish(error); }
    });
    (async () => {
      await rpc("initialize", { clientInfo: { name: "pixel_voxel_local", title: "PIXEL Voxel Local", version: "0.2.0" } });
      send({ method: "initialized", params: {} });
      const started = await rpc("thread/start", {
        cwd, ephemeral: true, approvalPolicy: "never", sandbox: "read-only",
        model, config: { model_reasoning_effort: effort },
        baseInstructions: BASE_INSTRUCTIONS,
      });
      if (started.model !== model || started.reasoningEffort !== effort)
        throw new Error(`모델 설정 불일치: ${started.model} / ${started.reasoningEffort}`);
      onStatus("캐릭터 구상 중", { model: started.model, effort: started.reasoningEffort });
      await rpc("turn/start", {
        threadId: started.thread.id, model, effort,
        input: [{ type: "text", text: prompt }],
      });
    })().catch(error => finish(error));
  });
}

export function listCodexModels(executable, cwd, signal) {
  return new Promise((resolve, reject) => {
    const child = spawn(executable, ["app-server", "--stdio"], { cwd, windowsHide: true, stdio: ["pipe", "pipe", "pipe"] });
    let result = [], error, complete = false, nextId = 2;
    const send = value => child.stdin.write(JSON.stringify(value) + "\n");
    const abort = () => { error = new Error("모델 목록 조회 시간이 초과되었습니다."); child.kill(); };
    signal.addEventListener("abort", abort, { once: true });
    child.stderr.on("data", () => {});
    child.stdin.on("error", e => { error = e; child.kill(); });
    child.on("error", e => { error = e; });
    child.on("close", () => {
      signal.removeEventListener("abort", abort);
      error ? reject(error) : complete ? resolve(result) : reject(new Error("모델 목록 연결이 종료되었습니다."));
    });
    createInterface({ input: child.stdout }).on("line", line => {
      try {
        const m = JSON.parse(line);
        if (m.error) { error = new Error(m.error.message); child.kill(); return; }
        if (m.id === 1) {
          send({ method: "initialized", params: {} });
          send({ id: nextId++, method: "model/list", params: { limit: 100 } });
        } else if (m.id && m.result?.data) {
          result.push(...m.result.data.filter(x => !x.hidden).map(x => ({
            id: x.model, label: x.displayName, defaultEffort: x.defaultReasoningEffort,
            efforts: x.supportedReasoningEfforts.map(e => e.reasoningEffort),
          })));
          if (m.result.nextCursor) send({ id: nextId++, method: "model/list", params: { limit: 100, cursor: m.result.nextCursor } });
          else { complete = true; child.kill(); }
        }
      } catch (e) { error = e; child.kill(); }
    });
    if (signal.aborted) return abort();
    send({ id: 1, method: "initialize", params: { clientInfo: { name: "pixel_voxel_local", version: "0.3.0" } } });
  });
}
