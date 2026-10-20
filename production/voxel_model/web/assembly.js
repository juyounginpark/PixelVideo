import * as THREE from "three";
import { Builder, parseLine, expand } from "/builder.mjs";
import { parseMotionLine } from "/motion.mjs";

export class Assembly {
  constructor(scene) {
    this.scene = scene;
    this.root = new THREE.Group();
    this.builder = new Builder(this.root);
    this.queue = [];
    this.particles = [];
    this.next = 0;
    this.count = 0;
    this.lastBounds = new THREE.Box3(new THREE.Vector3(-2, 0, -2), new THREE.Vector3(2, 5, 2));
    this.grid = new THREE.GridHelper(12, 24, 0xe5b5a1, 0xf0ddd1);
    this.grid.position.y = -.04;
    this.grid.material.transparent = true; this.grid.material.opacity = .45; this.grid.material.depthWrite = false;
    scene.add(this.grid, this.root);
    this.hops = new THREE.Group();
    [0xf17f66, 0xffd15d, 0x8acbb1].forEach((color, i) => {
      const cube = new THREE.Mesh(new THREE.BoxGeometry(.42, .42, .42), new THREE.MeshLambertMaterial({ color }));
      cube.position.set((i - 1) * .8, .5, 0); this.hops.add(cube);
    });
    scene.add(this.hops);
    this.sparkGeo = new THREE.BoxGeometry(.065, .065, .065);
    this.sparkMat = new THREE.MeshBasicMaterial({ color: 0xffc06c, transparent: true });
  }
  enqueue(line) {
    if (parseMotionLine(line)) return;
    const spec = parseLine(line);
    if (!spec) throw new Error("실시간 모델 명령을 해석하지 못했습니다.");
    for (const part of expand(spec)) this.queue.push({ part, fast: spec.kind === "use" });
  }
  captureBounds() {
    // Measure final positions, not the temporarily tiny entrance scales.
    const saved = this.builder.anim.map(({ node }) => ({ node, scale: node.scale.clone(), pos: node.position.clone() }));
    for (const { node } of saved) { node.scale.setScalar(1); node.position.copy(node.userData.home); }
    this.root.updateMatrixWorld(true);
    this.lastBounds.setFromObject(this.root);
    for (const { node, scale, pos } of saved) { node.scale.copy(scale); node.position.copy(pos); }
    this.root.updateMatrixWorld(true);
  }
  spark(node, now, amount = 4) {
    const pos = new THREE.Vector3(); node.getWorldPosition(pos);
    for (let i = 0; i < amount && this.particles.length < 80; i++) {
      const mesh = new THREE.Mesh(this.sparkGeo, this.sparkMat);
      mesh.position.copy(pos);
      const velocity = new THREE.Vector3(Math.cos(i * 2.4 + now) * 1.3, 1 + (i % 3) * .4, Math.sin(i * 2.4 + now) * 1.3);
      this.scene.add(mesh); this.particles.push({ mesh, velocity, start: now, origin: pos.clone() });
    }
  }
  tick(now) {
    this.builder.update(now);
    this.hops.children.forEach((cube, i) => {
      cube.position.y = .55 + Math.abs(Math.sin(now * .004 - i * .65)) * .7;
      cube.rotation.y = now * .001;
    });
    if (this.queue.length && now >= this.next) {
      const item = this.queue.shift(), before = this.builder.anim.length;
      this.builder.add(item.part, now);
      if (item.part.kind === "box") this.hops.visible = false;
      this.count = 0;
      this.root.traverse(node => { if (node.isMesh) this.count++; });
      this.captureBounds();
      const added = this.builder.anim[before]?.node;
      if (added) this.spark(added, now);
      this.next = now + (item.fast ? 48 : 90);
    }
    this.particles = this.particles.filter(p => {
      const t = (now - p.start) / 650;
      if (t >= 1) { this.scene.remove(p.mesh); return false; }
      p.mesh.position.copy(p.origin).addScaledVector(p.velocity, t);
      p.mesh.position.y -= t * t * 1.5;
      p.mesh.scale.setScalar(1 - t);
      p.mesh.rotation.set(t * 4, t * 2, 0);
      return true;
    });
  }
  get busy() { return this.queue.length > 0 || this.builder.busy; }
  dispose(keepRoot = false) {
    if (!keepRoot) this.scene.remove(this.root);
    this.scene.remove(this.grid, this.hops);
    this.grid.geometry.dispose(); this.grid.material.dispose();
    this.hops.children.forEach(n => { n.geometry.dispose(); n.material.dispose(); });
    this.particles.forEach(p => this.scene.remove(p.mesh));
    this.sparkGeo.dispose(); this.sparkMat.dispose();
    this.queue = []; this.particles = [];
  }
}
