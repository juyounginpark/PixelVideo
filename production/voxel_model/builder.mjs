import { Builder as OriginalBuilder } from "./vendor/boxes.js";
export { parseLine, expand } from "./vendor/boxes.js";

// Preserve upstream methods. Register implicit twins so grandchildren mirror too.
export class Builder extends OriginalBuilder {
  add(spec, at) {
    const parentTwin = spec.kind === "box" && this.twins.get(spec.parent);
    const before = parentTwin ? new Set(parentTwin.children) : null;
    super.add(spec, at);
    if (parentTwin && !spec.mirror && spec.name !== "_") {
      const twin = parentTwin.children.find(node => !before.has(node));
      if (twin) this.twins.set(spec.name, twin);
    }
  }
}
