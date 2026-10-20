import * as THREE from "three";
import { rigModel, restorePose } from "/rig.mjs";

export class Playback {
  constructor(root, prompt, scene) {
    this.root = root; this.scene = scene;
    this.rig = rigModel(root, prompt);
    this.mixer = new THREE.AnimationMixer(root);
    this.speed = 1; this.paused = false; this.current = null;
    this.visuals = new THREE.Group(); this.visuals.name = "joint_preview";
    this.helper = new THREE.SkeletonHelper(root);
    this.helper.material.depthTest = false; this.helper.material.transparent = true; this.helper.material.opacity = .8;
    this.helper.renderOrder = 20; this.visuals.add(this.helper);
    this.markerGeometry = new THREE.SphereGeometry(.055, 8, 6);
    this.markerMaterial = new THREE.MeshBasicMaterial({ color: 0x39b9a0, depthTest: false });
    this.markers = Object.values(this.rig.bones).map(bone => {
      const mesh = new THREE.Mesh(this.markerGeometry, this.markerMaterial);
      mesh.renderOrder = 21; this.visuals.add(mesh);
      return { mesh, bone };
    });
    this.visuals.visible = false; scene.add(this.visuals);
    this.select(this.rig.selected, false);
  }
  select(name, autoplay = true) {
    const clip = this.root.animations.find(c => c.name === name);
    if (!clip) throw new Error("이 모델에서 지원하지 않는 동작입니다.");
    if (this.action) this.action.fadeOut(.2);
    this.action = this.mixer.clipAction(clip);
    this.action.reset().setLoop(THREE.LoopRepeat, Infinity).fadeIn(.2).play();
    this.current = name; this.paused = !autoplay;
  }
  tick(dt) {
    if (!this.paused) this.mixer.update(dt * this.speed);
    this.root.updateMatrixWorld(true);
    for (const { mesh, bone } of this.markers) bone.getWorldPosition(mesh.position);
    this.helper.updateMatrixWorld(true);
  }
  reset() {
    this.mixer.stopAllAction(); restorePose(this.rig);
    this.action = null; this.paused = true;
  }
  async withRestPose(operation) {
    const paused = this.paused;
    const saved = Object.values(this.rig.bones).map(bone => ({ bone, p: bone.position.clone(), q: bone.quaternion.clone() }));
    this.paused = true; restorePose(this.rig);
    try { return await operation(); }
    finally {
      for (const { bone, p, q } of saved) { bone.position.copy(p); bone.quaternion.copy(q); }
      this.root.updateMatrixWorld(true); this.paused = paused;
    }
  }
  dispose() {
    this.mixer.stopAllAction(); this.mixer.uncacheRoot(this.root);
    this.scene.remove(this.visuals);
    this.helper.geometry.dispose(); this.helper.material.dispose();
    this.markerGeometry.dispose(); this.markerMaterial.dispose();
    this.root.traverse(n => { if (n.userData.rigOwnedGeometry) n.geometry.dispose(); });
  }
}
