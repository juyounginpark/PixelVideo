"""Import the original JS Builder output into Blender's existing video director."""
from pathlib import Path
from types import SimpleNamespace
import json, subprocess, tempfile, math
import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parent
DEFAULT = ROOT / "assets/minsu.boxes"

class Face:
    def __init__(self, objects):
        self.eyes = [o for o in objects if (o.get("part_name") or "").startswith("eye")]
        self.rest = [(o, o.scale.copy()) for o in self.eyes]
        self.mouths = [(o,o.scale.copy()) for o in objects if o.get("part_name")=="mouth"]
    def set(self, expression, blink=False):
        # Facial geometry stays attached to the imported head. Blink is deterministic.
        for o, scale in self.rest:
            o.scale = scale.copy()
            if blink: o.scale.z *= .12
        for o,scale in self.mouths:
            o.scale=scale.copy()
            if expression=="Surprise": o.scale.z*=3; o.scale.x*=.7
            elif expression=="Happy": o.scale.x*=1.3
            elif expression=="Thinking": o.scale.x*=.65

def character(materials=None, source=None):
    source = Path(source or DEFAULT).resolve()
    with tempfile.TemporaryDirectory(prefix="pixel-video-") as temp:
        output = Path(temp) / "model.json"
        subprocess.run(["node", str(ROOT / "video-export.mjs"), str(source), str(output)],
                       check=True, cwd=ROOT, capture_output=True)
        data = json.loads(output.read_text(encoding="utf8"))
    # Change basis: website +Y up/+Z front -> Blender +Z up/-Y front.
    basis = Matrix.Rotation(math.pi / 2, 4, "X")
    objects, joints, parts = {}, {}, []
    for node in data["nodes"]:
        mesh = None
        if "vertices" in node:
            mesh = bpy.data.meshes.new("hanbean_box")
            v = node["vertices"]; idx = node["indices"]
            mesh.from_pydata([tuple(basis @ Vector(v[i:i+3])) for i in range(0,len(v),3)],
                             [], [idx[i:i+3] for i in range(0,len(idx),3)])
            mesh.update()
        obj = bpy.data.objects.new(node["name"] or "hanbean_root", mesh)
        bpy.context.collection.objects.link(obj)
        objects[node["id"]] = obj
        if node.get("parent") in objects: obj.parent = objects[node["parent"]]
        matrix = Matrix([node["matrix"][i:i+4] for i in range(0,16,4)]).transposed()
        obj.matrix_local = basis @ matrix @ basis.inverted()
        if node["bone"]: joints[node["name"].removeprefix("joint_")] = obj
        if node["part"]:
            obj["part_name"] = node["part"]["name"]; parts.append(obj)
        if mesh:
            mat = bpy.data.materials.new("hanbean_material");mat.diffuse_color=(*node["color"],node["opacity"])
            mat.use_nodes=True
            shader=next(n for n in mat.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
            shader.inputs["Base Color"].default_value=(*node["color"],1)
            shader.inputs["Alpha"].default_value=node["opacity"]
            shader.inputs["Roughness"].default_value=.82
            mesh.materials.append(mat)
    required = ["root","spine","neck","shoulderL","shoulderR","elbowL","elbowR","hipL","hipR"]
    missing = [key for key in required if key not in joints]
    if missing: raise ValueError("Video character needs humanoid joints: "+", ".join(missing))
    root=objects[data["nodes"][0]["id"]]
    bpy.context.view_layer.update()
    points=[o.matrix_world @ Vector(v) for o in root.children_recursive if o.type=="MESH" for v in o.bound_box]
    scale=1.9/(max(p.z for p in points)-min(p.z for p in points))
    # Bake normalization into every local translation and mesh so director scale remains 1.
    for obj in objects.values():
        obj.location *= scale
        if obj.type=="MESH":
            for vertex in obj.data.vertices: vertex.co *= scale
    for side in ("L","R"):
        for obj in parts:
            if obj.get("part_name")==f"foot{side}":
                for child in obj.children_recursive:
                    if child.type=="MESH": child.name="wide_boot_"+side
    moving=[root,*joints.values()]
    rig=SimpleNamespace(root=root,body=joints["spine"],head=joints["neck"],
        arms=[joints["shoulderL"],joints["shoulderR"]],
        elbows=[joints["elbowL"],joints["elbowR"]],
        legs=[joints["hipL"],joints["hipR"]],face=Face(parts),moving=moving)
    rig.rest={o.name:(o.location.copy(),o.rotation_euler.copy(),o.scale.copy()) for o in moving}
    root["model_id"]="HANBEAN_PUBLIC_BUILDER";root["boxes_source"]=str(source)
    return rig
