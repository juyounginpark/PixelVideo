export const MOTIONS = {
  idle: "숨쉬기", walk: "걷기", run: "달리기", wave: "손 흔들기", talk: "대화",
  dance: "춤추기", jump: "점프", surprised: "깜짝 놀라기", work: "작업하기", eat: "먹기", sleep: "졸기",
};
export function parseMotionLine(line) {
  const tokens = line.trim().split(/\s+/);
  if (tokens[0] !== "motion") return null;
  if (tokens.length !== 2 || !Object.hasOwn(MOTIONS, tokens[1])) throw new Error(`지원하지 않는 동작: ${line}`);
  return { kind: "motion", preset: tokens[1] };
}
// Used only for older saved models that predate the model-authored motion command.
export function inferMotion(prompt = "") {
  const rules = [
    ["sleep", /잠|졸|수면|sleep|sleepy/i], ["eat", /먹|식사|eat|eating/i],
    ["run", /달리|뛰어|달려|run|running/i], ["walk", /걷|걸어|walk/i],
    ["dance", /춤|댄스|dance|dancing/i], ["jump", /점프|폴짝|jump/i],
    ["surprised", /놀라|깜짝|무서|surpris|scared/i], ["wave", /인사|손.*흔|wave|waving|hello/i],
    ["work", /요리|찌개|가게|장사|작업|일하|낚시|cook|work|fish/i], ["talk", /말하|대화|설명|talk|speak/i],
  ];
  return rules.find(([, re]) => re.test(prompt))?.[0] || "idle";
}
