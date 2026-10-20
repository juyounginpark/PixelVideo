// 기본 캐릭터 틀. 쓸궁지 영상의 캐릭터(kit.mid.js의 mkPerson·mkChick, profile3d의 mkPoop) 비율을 따른다.
// 모두 바닥 y=0에 서고 정면은 +z. 공통 부품 이름(head, body, eyeL/R, armL/R …)이 있어 Claude가 거기에 소품을 붙인다.
const EYE = "#1b1b2b", WHITE = "#ffffff", BLUSH = "#ff9fb6", MOUTH = "#5a2a2a";

// 머리 기준 얼굴(눈 + 반짝이 + 볼터치 + 입). 머리 앞면 z = fz
function face({ fz = 1.25, ey = 0.1, ex = 0.62, by = -0.38, bx = 1.0, my = -0.5, mouth = true, mc = MOUTH } = {}) {
  return [
    `box eyeL head 0.42 0.52 0.1 ${-ex} ${ey} ${fz + 0.02} ${EYE} mirror`,
    `box _ eyeL 0.16 0.16 0.05 -0.07 0.11 0.06 ${WHITE}`,
    `box blushL head 0.5 0.24 0.08 ${-bx} ${by} ${fz + 0.01} ${BLUSH} mirror`,
    mouth ? `box mouth head 0.38 0.1 0.08 0 ${my} ${fz + 0.02} ${mc}` : "",
  ].filter(Boolean);
}

// 두 발로 선 동물 공통 몸: 몸통 + 큰 머리 + 팔 + 발. 머리 중심 y 3.35, 머리 윗면 y 4.65
function critter(p, o = {}) {
  const hw = o.hw ?? 3.0, hh = o.hh ?? 2.6, hd = o.hd ?? 2.5;
  return [
    `box body - 2.3 1.9 1.8 0 1.25 0 ${p.color} soft`,
    p.belly ? `box belly body 1.5 1.3 0.1 0 -0.1 0.92 ${p.belly}` : "",
    `box head - ${hw} ${hh} ${hd} 0 3.35 0 ${p.color} soft`,
    ...face({ fz: hd / 2, mouth: o.mouth !== false, bx: hw / 3 }),
    `box armL body 0.55 1.25 0.55 -1.38 -0.05 0.15 ${o.arm || p.color} rot 0 0 -14 mirror`,
    `box footL - 0.8 0.36 1.0 -0.56 0.18 0.15 ${p.feet || p.color} soft mirror`,
  ].filter(Boolean);
}

export const TEMPLATES = {
  poop: {
    desc: "the channel mascot, a cute 3-tier poop with arms (height ~4)",
    defaults: { color: "#9a5f2e" },
    parts: "tier1 head(the middle tier, face is here, front z=+1.15) tier3(top tier, its top surface y=+0.45) knob tip eyeL eyeR blushL blushR mouth armL armR. Hide knob tip before putting a hat/crown on tier3",
    build: (p) => [
      `box tier1 - 3.4 1.2 3.1 0 0.6 0 ${p.color} soft`,
      `box head - 2.6 1.05 2.3 0 1.7 0 ${shade(p.color, 0.96)} soft`,
      `box tier3 - 1.7 0.9 1.5 0 2.65 0 ${shade(p.color, 0.92)} soft`,
      `box knob - 0.75 0.6 0.75 0.15 3.35 0 ${shade(p.color, 0.92)}`,
      `box tip - 0.5 0.5 0.5 0.5 3.8 0 ${shade(p.color, 0.92)} rot 0 0 -29`,
      `box _ tier1 1.4 0.16 0.12 -0.6 0.48 1.53 ${shade(p.color, 1.35)}`,
      `box _ head 1.1 0.16 0.12 -0.47 0.4 1.13 ${shade(p.color, 1.35)}`,
      `box eyeL head 0.44 0.56 0.1 -0.52 0.1 1.17 ${EYE} mirror`,
      `box _ eyeL 0.16 0.16 0.05 -0.08 0.12 0.06 ${WHITE}`,
      `box _ eyeL 0.08 0.08 0.05 0.09 -0.12 0.06 ${WHITE}`,
      `box blushL head 0.42 0.22 0.08 -0.95 -0.3 1.17 ${BLUSH} mirror`,
      `box mouth head 0.42 0.13 0.1 0 -0.37 1.17 #3a1a10`,
      `box _ head 0.1 0.12 0.1 -0.24 -0.28 1.17 #3a1a10 mirror`,
      `box armL - 0.42 0.95 0.42 -1.75 1.55 0 ${p.color} rot 0 0 30 mirror`,
    ].join("\n"),
  },
  person: {
    desc: "a cute chibi person (height ~5). params skin hair shirt pants shoe, long=1 for long hair",
    defaults: { skin: "#ffdcc0", hair: "#6a4026", shirt: "#8fc8ff", pants: "#4a5a8a", shoe: "#ffffff" },
    parts: "body head hair eyeL eyeR blushL blushR mouth armL armR handL handR footL footR. Head top y≈4.9 (hair), face front z=1.2",
    build: (p) => [
      `box body - 2.2 1.8 1.6 0 1.25 0 ${p.shirt}`,
      `box _ body 2.24 0.5 1.64 0 -0.65 0 ${p.pants}`,
      `box head - 2.8 2.4 2.4 0 3.25 0 ${p.skin}`,
      `box hair head 3.0 0.9 2.66 0 1.3 -0.1 ${p.hair}`,
      `box _ head 3.0 0.5 0.4 0 0.85 1.1 ${p.hair}`,
      `box _ head 0.5 1.4 2.4 -1.45 0.4 -0.2 ${p.hair} mirror`,
      p.long == 1 ? `box _ head 3.0 2.6 0.6 0 -0.1 -1.3 ${p.hair}` : "",
      ...face({ fz: 1.2, ey: -0.3, ex: 0.6, by: -0.7, bx: 1.0, my: -0.95, mc: "#7a2a2a" }),
      `box armL body 0.5 1.3 0.5 -1.3 0.0 0.1 ${p.shirt} rot 0 0 -10 mirror`,
      `box handL armL 0.5 0.4 0.5 0 -0.8 0 ${p.skin}`,
      `box footL - 0.7 0.3 0.9 -0.55 0.15 0.2 ${p.shoe} mirror`,
      `box _ - 0.8 0.3 1.0 -0.55 0.3 0 ${p.pants} mirror`,
    ].filter(Boolean).join("\n"),
  },
  cat: {
    desc: "cat (pointy ears, tail). params color belly inner",
    defaults: { color: "#f2a65a", belly: "#fff1de", inner: "#ffb3c1" },
    parts: "body belly head earL earR nose eyeL eyeR blushL blushR mouth armL armR footL footR tail",
    build: (p) => [
      ...critter(p),
      `box earL head 0.85 0.85 0.5 -0.9 1.3 -0.2 ${p.color} rot 0 0 45 mirror`,
      `box _ earL 0.45 0.45 0.1 0.08 0.08 0.26 ${p.inner}`,
      `box nose head 0.28 0.18 0.1 0 -0.28 1.27 ${p.inner}`,
      `box tail body 0.42 0.42 1.9 0.5 -0.4 -1.45 ${p.color} rot 35 0 0`,
      `box _ tail 0.44 0.44 0.5 0 0 -0.75 ${p.belly}`,
    ].join("\n"),
  },
  dog: {
    desc: "puppy (floppy ears, muzzle). params color ear muzzle",
    defaults: { color: "#e8c08a", ear: "#9a6a3e", muzzle: "#fff4e4" },
    parts: "body head earL earR muzzle nose eyeL eyeR blushL blushR mouth armL armR footL footR tail",
    build: (p) => [
      ...critter(p, { mouth: false }),
      `box earL head 0.6 1.6 1.1 -1.62 0.0 -0.1 ${p.ear} soft rot 0 0 -10 mirror`,
      `box muzzle head 1.4 0.8 0.45 0 -0.55 1.35 ${p.muzzle} soft`,
      `box nose muzzle 0.5 0.32 0.16 0 0.22 0.25 ${EYE}`,
      `box mouth muzzle 0.36 0.1 0.08 0 -0.18 0.24 ${MOUTH}`,
      `box tail body 0.4 0.4 1.2 0 0.2 -1.2 ${p.color} rot 45 0 0`,
    ].join("\n"),
  },
  bear: {
    desc: "teddy bear (round ears, muzzle). params color muzzle",
    defaults: { color: "#a8754a", muzzle: "#f0d6b4", belly: "#e8c9a0" },
    parts: "body belly head earL earR muzzle nose eyeL eyeR blushL blushR mouth armL armR footL footR",
    build: (p) => [
      ...critter(p, { mouth: false }),
      `box earL head 0.9 0.9 0.5 -1.15 1.35 -0.2 ${p.color} soft mirror`,
      `box _ earL 0.5 0.5 0.1 0 0 0.26 ${p.muzzle}`,
      `box muzzle head 1.2 0.75 0.4 0 -0.5 1.3 ${p.muzzle} soft`,
      `box nose muzzle 0.46 0.3 0.14 0 0.18 0.22 ${EYE}`,
      `box mouth muzzle 0.32 0.1 0.08 0 -0.18 0.21 ${MOUTH}`,
    ].join("\n"),
  },
  bunny: {
    desc: "rabbit (long ears, puffy tail). params color inner",
    defaults: { color: "#f6f2ee", inner: "#ffb3c1", belly: "#ffffff" },
    parts: "body head earL earR nose eyeL eyeR blushL blushR mouth armL armR footL footR tail",
    build: (p) => [
      ...critter(p),
      `box earL head 0.65 2.2 0.45 -0.65 2.2 -0.25 ${p.color} soft rot 0 0 8 mirror`,
      `box _ earL 0.32 1.6 0.1 0 -0.05 0.24 ${p.inner}`,
      `box nose head 0.26 0.18 0.1 0 -0.28 1.27 ${p.inner}`,
      `box tail body 0.8 0.8 0.6 0 -0.4 -1.0 ${p.belly} soft`,
    ].join("\n"),
  },
  frog: {
    desc: "frog (eye bumps on top, wide smile). params color belly",
    defaults: { color: "#7ccf5a", belly: "#e8f7c8" },
    parts: "body belly head bumpL bumpR eyeL eyeR blushL blushR mouth armL armR footL footR",
    build: (p) => [
      `box body - 2.4 1.9 1.9 0 1.25 0 ${p.color} soft`,
      `box belly body 1.6 1.3 0.1 0 -0.1 0.97 ${p.belly}`,
      `box head - 3.4 2.2 2.6 0 3.2 0 ${p.color} soft`,
      `box bumpL head 1.15 1.0 1.05 -0.95 1.15 0.55 ${p.color} soft mirror`,
      `box eyeL bumpL 0.62 0.62 0.1 0 0 0.54 ${WHITE} mirror`,
      `box _ eyeL 0.36 0.4 0.05 0.05 -0.03 0.06 ${EYE}`,
      `box _ eyeL 0.12 0.12 0.04 -0.02 0.09 0.09 ${WHITE}`,
      `box blushL head 0.55 0.24 0.08 -1.15 -0.15 1.31 ${BLUSH} mirror`,
      `box mouth head 1.3 0.1 0.08 0 -0.35 1.32 ${MOUTH}`,
      `box _ head 0.1 0.18 0.08 -0.68 -0.27 1.32 ${MOUTH} mirror`,
      `box armL body 0.55 1.25 0.55 -1.42 -0.05 0.15 ${p.color} rot 0 0 -14 mirror`,
      `box footL - 1.1 0.3 1.2 -0.65 0.15 0.2 ${p.color} soft mirror`,
    ].join("\n"),
  },
  penguin: {
    desc: "penguin (white face and belly, beak, flippers). params color face beak",
    defaults: { color: "#2e3a52", face: "#ffffff", beak: "#ffa53a", belly: "#ffffff" },
    parts: "body belly head facepatch beak eyeL eyeR blushL blushR armL armR footL footR",
    build: (p) => [
      `box body - 2.6 2.0 2.0 0 1.3 0 ${p.color} soft`,
      `box belly body 1.8 1.6 0.1 0 -0.05 1.02 ${p.belly}`,
      `box head - 3.0 2.6 2.5 0 3.35 0 ${p.color} soft`,
      `box facepatch head 2.4 1.9 0.1 0 -0.2 1.24 ${p.face}`,
      `box eyeL head 0.42 0.52 0.1 -0.62 0.1 1.3 ${EYE} mirror`,
      `box _ eyeL 0.16 0.16 0.05 -0.07 0.11 0.06 ${WHITE}`,
      `box blushL head 0.5 0.24 0.08 -0.95 -0.42 1.3 ${BLUSH} mirror`,
      `box beak head 0.7 0.36 0.5 0 -0.38 1.45 ${p.beak}`,
      `box armL body 0.3 1.4 0.9 -1.42 0.0 0 ${p.color} rot 0 0 -18 mirror`,
      `box footL - 0.9 0.26 1.1 -0.6 0.13 0.35 ${p.beak} mirror`,
    ].join("\n"),
  },
  chick: {
    desc: "baby chick (beak, tuft, little wings). params color beak",
    defaults: { color: "#ffe04a", beak: "#ff9a3a" },
    parts: "body head tuft beak eyeL eyeR blushL blushR armL armR footL footR",
    build: (p) => [
      ...critter({ ...p, feet: p.beak }, { mouth: false, arm: shade(p.color, 0.92) }).map((l) => l.replace("box armL body 0.55 1.25 0.55", "box armL body 0.3 1.1 0.9")),
      `box beak head 0.8 0.42 0.6 0 -0.35 1.45 ${p.beak}`,
      `box tuft head 0.32 0.8 0.32 0 1.55 0 ${p.color} rot 0 0 15`,
      `box _ head 0.32 0.6 0.32 0.32 1.45 0 ${p.color} rot 0 0 -25`,
    ].join("\n"),
  },
  hamster: {
    desc: "hamster (round cheeks, tiny ears). params color belly",
    defaults: { color: "#f0b866", belly: "#fff3dc", inner: "#ffb3c1" },
    parts: "body belly head earL earR muzzle nose eyeL eyeR blushL blushR mouth armL armR footL footR",
    build: (p) => [
      ...critter(p, { hw: 3.3, hh: 2.6, hd: 2.6, mouth: false }),
      `box earL head 0.75 0.75 0.4 -1.15 1.35 -0.3 ${p.color} soft mirror`,
      `box _ earL 0.4 0.4 0.1 0 0 0.21 ${p.inner}`,
      `box muzzle head 1.9 1.0 0.3 0 -0.6 1.36 ${p.belly} soft`,
      `box nose muzzle 0.26 0.18 0.1 0 0.3 0.17 ${p.inner}`,
      `box mouth muzzle 0.3 0.1 0.08 0 0.0 0.17 ${MOUTH}`,
    ].join("\n"),
  },
};

// 색을 밝게/어둡게
export function shade(hex, k) {
  const v = parseInt(hex.slice(1), 16);
  const c = [v >> 16, (v >> 8) & 255, v & 255].map((x) => Math.max(0, Math.min(255, Math.round(x * k))));
  return "#" + c.map((x) => x.toString(16).padStart(2, "0")).join("");
}
