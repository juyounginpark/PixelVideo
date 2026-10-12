"""Native camera effects and projected mesh masks from the actual Blender scene."""
import bpy,math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
from effects import punch_scale

def descendants(obj):return [obj,*obj.children_recursive]

def projected(scene,obj):
    points=[];polygons=[]
    for o in descendants(obj):
        if o.type!='MESH' or o.hide_render or min(o.matrix_world.to_scale())<.0001:continue
        ps=[world_to_camera_view(scene,scene.camera,o.matrix_world@v.co) for v in o.data.vertices]
        points.extend(p for p in ps if p.z>0)
        for face in o.data.polygons:
            if all(ps[i].z>0 for i in face.vertices):polygons.append([(round(ps[i].x*1080),round((1-ps[i].y)*1920)) for i in face.vertices])
    if not points:raise ValueError('No visible geometry for '+obj.name)
    rect=[min(p.x for p in points)*1080,(1-max(p.y for p in points))*1920,max(p.x for p in points)*1080,(1-min(p.y for p in points))*1920]
    return {'point':[(rect[0]+rect[2])/2,(rect[1]+rect[3])/2],'rect':rect,'depth':min(p.z for p in points),
            'polygons':polygons,'maskMethod':'projected mesh faces; occlusion not solved','protect':True}

class NativeCameraEffects:
    def apply(self,scene,frame,timeline,targets):
        cam=scene.camera;records=[]
        for event in timeline['CameraEffectTimeline']:
            if not event['frame']<=frame<event['endFrame']:continue
            target=targets[event['target']];base_scale=cam.data.ortho_scale;base_lens=cam.data.lens;base_rot=cam.rotation_euler.copy()
            scale=punch_scale((frame-event['frame'])/timeline['fps'],event['intensity'])
            # Native lens/orthographic scale, aimed toward the actual target, no 2D upscale.
            aim=target.matrix_world.translation
            desired=(aim-cam.location).to_track_quat('-Z','Y')
            cam.rotation_euler=base_rot.to_quaternion().slerp(desired,min(.15,(scale-1)*1.5)).to_euler()
            if cam.data.type=='ORTHO':cam.data.ortho_scale=base_scale/scale
            else:cam.data.lens=base_lens*scale
            bpy.context.view_layer.update();b=projected(scene,target)['rect']
            accepted=70<=b[0] and b[2]<=970 and 170<=b[1] and b[3]<=1500
            if not accepted:cam.data.ortho_scale=base_scale;cam.data.lens=base_lens;cam.rotation_euler=base_rot
            records.append({'eventId':event['eventId'],'frame':frame,'zoom':scale if accepted else 1,'clamped':not accepted})
        return records
