"""Two stills isolate legacy compositor artifacts; no timeline/video output."""
import bpy, sys, json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R))
from art import MaterialLibrary, CharacterFactory, box
from engine import LightingPresetManager, PixelRenderPipeline, CameraDirector
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
m=MaterialLibrary();rig=CharacterFactory(m).minsu()
for mat in m.materials.values():
    for node in mat.node_tree.nodes:
        if node.type=='TEX_IMAGE':node.projection_blend=0  # Explicit historical reproduction.
box('neutral_ground',(0,0,-.055),(200,200,.1),m['sand'])
LightingPresetManager().daylight();PixelRenderPipeline().configure();cam=CameraDirector().camera
cam.location=(2.5,-4,2);cam.rotation_euler=(Vector((0,0,.8))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO';cam.data.ortho_scale=2.1;cam.data.shift_y=0
s=bpy.context.scene;s.render.resolution_x=540;s.render.resolution_y=540
out=R/'design_revision';out.mkdir(exist_ok=True)
s.render.filepath=str(out/'legacy_outline.png');bpy.ops.render.render(write_still=True)
g=s.compositing_node_group;src=next(n for n in g.nodes if n.type=='R_LAYERS');dest=next(n for n in g.nodes if n.bl_idname=='NodeGroupOutput')
g.links.new(src.outputs['Image'],dest.inputs['Image'])
s.render.filepath=str(out/'legacy_raw.png');bpy.ops.render.render(write_still=True)
for obj in bpy.data.objects:
    for mod in list(obj.modifiers):
        if mod.type=='WEIGHTED_NORMAL':obj.modifiers.remove(mod)
s.render.filepath=str(out/'without_weighted_normals.png');bpy.ops.render.render(write_still=True)
for mat in m.materials.values():
    for n in mat.node_tree.nodes:
        if n.type=='TEX_IMAGE':n.projection_blend=.08
s.render.filepath=str(out/'box_blend_safe.png');bpy.ops.render.render(write_still=True)
for mat in m.materials.values():
    bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_DIFFUSE')
    for link in list(bs.inputs['Color'].links):mat.node_tree.links.remove(link)
s.render.filepath=str(out/'without_texture.png');bpy.ops.render.render(write_still=True)
print('TWO_DIAGNOSTIC_STILLS_COMPLETE')
