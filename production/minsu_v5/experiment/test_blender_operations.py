"""Evaluated-mesh smoke/contract tests; not a material physics validation."""
from pathlib import Path
import sys,math
E=Path(__file__).resolve().parent;sys.path.insert(0,str(E.parent));sys.path.insert(0,str(E))
import bpy
from common import write
from operations import capture,apply,geometry_record

def main():
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.ops.mesh.primitive_cube_add();obj=bpy.context.object;obj.name='test_subject';base=capture(obj)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=.35,depth=4);cutter=bpy.context.object
    bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,0));operand=bpy.context.object
    cases={
        'Rotate':{'toDegrees':90},'Squash':{},'Stretch':{},'Flatten':{},'Bend':{'degrees':60},
        'Cut':{'operandId':'box','operandFrom':[5,0,0],'operandTo':[.75,0,0]},
        'Pierce':{'operandId':'cylinder','operandFrom':[5,0,0],'operandTo':[0,0,0]},
        'Join':{'operandId':'box','operandFrom':[5,0,0],'operandTo':[1.25,0,0]},
        'Open':{'toDegrees':90},'Close':{'fromDegrees':90,'toDegrees':0},
        'Morph':{'targetVertices':[[x*1.4,y,z*.7] for x,y,z in base['vertices']]},
        'Compare':{'position':[2,0,0]},'ValueUpdate':{}
    }
    results=[]
    for name,params in cases.items():
        op={'type':name,'parameters':params};operands={'box':operand,'cylinder':cutter}
        apply(obj,op,0,base,operands);initial=geometry_record(obj)
        apply(obj,op,1,base,operands);final=geometry_record(obj)
        apply(obj,op,.5,base,operands);middle=geometry_record(obj)
        apply(obj,op,1,base,operands);again=geometry_record(obj)
        assert again['geometryHash']==final['geometryHash'],name+' seek nondeterminism'
        if name!='ValueUpdate': assert initial['geometryHash']!=final['geometryHash'],name+' did not change geometry'
        if name in {'Cut','Pierce'}:assert final['meshVolume']<initial['meshVolume'],name+' did not remove material'
        if name=='Join':assert initial['connectedComponents']==2 and final['connectedComponents']==1,'Join did not connect meshes'
        if name=='Rotate':assert math.isclose(final['properties']['rotationZDegrees'],90,abs_tol=1e-5)
        results.append({'operation':name,'result':'PASS','initial':initial,'final':final,'middle':middle,'scope':'deterministic evaluated mesh only; scientific conservation and art not approved'})
    from render import native_scene_inputs
    from common import read
    from copy import deepcopy
    spec=read(E/'fixture.json');changed=deepcopy(spec);changed['objects'][0]['label']='changed caption';changed['ui']['after']='changed';changed['audio']['enabled']=True;changed['assetPresets']['labelPositions'][0][0]=320
    assert native_scene_inputs(spec)==native_scene_inputs(changed),'UI/audio invalidates native scene'
    changed['objects'][0]['operation']['parameters']['toDegrees']=45
    assert native_scene_inputs(spec)!=native_scene_inputs(changed),'Operation change did not invalidate scene'
    write(E/'review/operation_tests.json',{'results':results,'cacheContracts':2,'scientificApproval':False});print('13 operation contracts + 2 native cache contracts PASS')

if __name__=='__main__':main()
