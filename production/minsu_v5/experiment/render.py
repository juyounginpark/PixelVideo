"""Sequential Blender fixture renderer with geometry completion receipts and asset cache."""
from pathlib import Path
import sys,os,time,json,math
E=Path(__file__).resolve().parent;sys.path.insert(0,str(E.parent));sys.path.insert(0,str(E))
import bpy
from mathutils import Vector
from common import read,write,sha,digest
from art_v5 import Materials,setup
from art import box,mesh
from operations import capture,apply,completion,geometry_record
from state import validate_object
from bpy_extras.object_utils import world_to_camera_view

def native_scene_inputs(spec):
    # Text, expected scientific claims and HUD coordinates cannot invalidate 3D.
    return {'assets':{k:spec['assetPresets'][k] for k in ['geometry','material','comparisonCamera']},
            'objects':[{k:o[k] for k in ['objectId','objectType','geometryVersion','operation']} for o in spec['objects']],
            'frames':spec['durationFrames']}

def check_viewport(s,obj,profile):
    evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
    try:
        ps=[world_to_camera_view(s,s.camera,evaluated.matrix_world@v.co) for v in mesh.vertices]
        rect=[min(v.x for v in ps)*1080,(1-max(v.y for v in ps))*1920-224,max(v.x for v in ps)*1080,(1-min(v.y for v in ps))*1920-224]
        vp=profile['frame']['viewport'];pad=12
        if rect[0]<vp[0]+pad or rect[1]<vp[1]+pad or rect[2]>vp[2]-pad or rect[3]>vp[3]-pad:raise ValueError('Geometry clipped by experiment viewport '+obj.name+' '+str(rect))
        return rect
    finally:evaluated.to_mesh_clear()

def main():
    started=time.perf_counter();spec=read(E/'fixture.json');profile=read(E/'profile.json');cache=E/'cache';cache.mkdir(exist_ok=True)
    for obj in spec['objects']:validate_object(obj)
    # Shares the V5 heavy-worker lock, so it cannot compete with episode rendering.
    lock=E.parent/'cache/render.lock';fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.write(fd,str(os.getpid()).encode());os.close(fd)
    try:
        inputs=native_scene_inputs(spec)
        assetkey=digest({'presets':inputs['assets'],'renderer':sha(Path(__file__)),'art':sha(E.parent/'art_v5.py'),'style':sha(E.parent.parent/'minsu_v31/style.py'),'blender':bpy.app.version_string})
        assets=cache/'assets'/assetkey;assets.mkdir(parents=True,exist_ok=True);blend=assets/'library.blend';manifest=assets/'manifest.json'
        asset_hit=blend.exists() and manifest.exists() and read(manifest)['sha256']==sha(blend)
        if asset_hit:bpy.ops.wm.open_mainfile(filepath=str(blend));s=bpy.context.scene
        else:
            bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=setup(profile['native']);m=Materials()
            # Geometry dimensions are baked into vertices, not parent scale: shared texel density.
            bar=box('bar',(-1.2,0,.36),(.42,1.8,.34),m['amber'])
            points=[(-.6,-.7),(.6,-.7),(.6,-.25),(-.15,-.25),(-.15,.7),(-.6,.7)]
            verts=[(x,y,z) for z in [-.17,.17] for x,y in points];n=len(points)
            faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
            elbow=mesh('elbow',verts,faces,m['mint']);elbow.location=(1.2,0,.36)
            floor=box('platform',(0,0,-.10),(7,7,.18),m['cream'])
            for obj in [bar,elbow]:
                obj.pass_index=1
                for poly in obj.data.polygons:poly.use_smooth=False
                # Apply only scaling, leaving object pivot/rotation available for reusable operations.
                bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
            bpy.ops.object.camera_add(location=(3.5,-6.5,7.5));cam=bpy.context.object;cam.name='comparison_camera';cam.data.type='ORTHO';cam.data.ortho_scale=9.6
            cam.rotation_euler=(Vector((0,0,.1))-cam.location).to_track_quat('-Z','Y').to_euler();s.camera=cam
            bpy.ops.wm.save_as_mainfile(filepath=str(blend));write(manifest,{'sha256':sha(blend),'assetKey':assetkey,'objects':['bar','elbow'],'source':'procedural reusable fixture presets'})
        s.render.resolution_x,s.render.resolution_y=profile['native'];s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.fps=30
        objects={o['objectId']:bpy.data.objects[o['objectId']] for o in spec['objects']};baselines={k:capture(o) for k,o in objects.items()}
        key=digest({'assetKey':assetkey,'operationCode':sha(E/'operations.py'),'objects':inputs['objects'],'native':profile['native'],'frames':inputs['frames']})
        frames=cache/'native'/key;frames.mkdir(parents=True,exist_ok=True);old=read(frames/'manifest.json') if (frames/'manifest.json').exists() else {};records={};receipts={};rendered=reused=0
        render_start=time.perf_counter()
        for f in range(spec['durationFrames']):
            path=frames/f'{f:04}.png';record=old.get('frames',{}).get(str(f))
            for state in spec['objects']:
                op=state['operation'];t=max(0,min(1,(f-op['startFrame'])/(op['completeFrame']-op['startFrame'])));smooth=t*t*(3-2*t)
                obj=objects[state['objectId']];apply(obj,op,smooth,baselines[state['objectId']])
                check_viewport(s,obj,profile)
                if f==op['completeFrame']:receipts[state['objectId']]=completion(obj,state,f,t)
            if record and path.exists() and record['sha256']==sha(path):reused+=1
            else:s.render.filepath=str(path);bpy.ops.render.render(write_still=True);rendered+=1
            records[str(f)]={'path':str(path),'sha256':sha(path)}
        write(frames/'manifest.json',{'frames':records,'key':key});write(E/'review/native.json',{'frames':records,'receipts':receipts,'key':key})
        write(E/'review/render_metrics.json',{'wallSeconds':time.perf_counter()-started,'renderLoopSeconds':time.perf_counter()-render_start,'renderedFrames':rendered,'reusedFrames':reused,'assetCache':'HIT' if asset_hit else 'MISS','assetKey':assetkey,'nativeSize':profile['native'],'blender':bpy.app.version_string})
    finally:lock.unlink(missing_ok=True)

if __name__=='__main__':main()
