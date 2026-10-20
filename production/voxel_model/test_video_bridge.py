"""Run with Blender --background --python-exit-code 1 --python this-file."""
from pathlib import Path
import sys, math
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT.parent/"minsu_v5"))
import bpy
from video_bridge import character
from character_director import CharacterDirector
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
source=Path(sys.argv[sys.argv.index("--")+1]) if "--" in sys.argv else None
rig=character(source=source)
assert all(any(o.get("part_name")==name+side for o in rig.root.children_recursive)
           for name in ("hand","foot") for side in ("L","R"))
director=CharacterDirector(rig)
for action in ("OBSERVE","REACT","POINT","LOOK_AROUND","CONFUSED","THINK","WALK","TURN","EXPLAIN","DISCOVER","CELEBRATE"):
    for phase in (0,.25,.5,.75,1):
        director.pose(action,phase,round(phase*100))
        assert all(math.isfinite(v) for o in rig.moving for row in o.matrix_world for v in row)
print("PASS: Blender import, bilateral hands/feet and 11 existing director actions")
# Also construct the actual latest episode adapter with the new factory.
import art_v5, importlib.util
art_v5.character=lambda materials: character(materials,source)
episode=ROOT.parent/"minsu_v6/ep10"
spec=importlib.util.spec_from_file_location("qa_episode",episode/"scene.py")
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
scene=module.Scene([270,480])
import json
shots=json.loads((episode/"episode.json").read_text(encoding="utf8"))["shots"]
for shot in shots:scene.pose(shot,shot["startFrame"])
scene.pose(shots[0],45)
scene.s.render.filepath=str(ROOT/"output/video-character.png")
bpy.ops.render.render(write_still=True)
print("PASS: V6 actual scene all shot starts and rendered frame 45")
