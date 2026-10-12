"""Reusable Blender geometry operations; parameters are scene data, not science claims.

Reset from a captured baseline before every evaluation, so seeking is deterministic.
Cut/Pierce/Join use exact Boolean meshes, not a visibility trick or scale animation.
"""
import math
from state import signature

def capture(obj):
    return {'location': list(obj.location), 'scale': list(obj.scale),
            'rotation': list(obj.rotation_euler), 'vertices':[list(v.co) for v in obj.data.vertices]}

def apply(obj, operation, progress, baseline, operands=None):
    import bpy
    from mathutils import Vector
    operands = operands or {}; t = max(0., min(1., progress)); typ=operation['type']; p=operation.get('parameters',{})
    obj.location=baseline['location']; obj.scale=baseline['scale']; obj.rotation_euler=baseline['rotation']
    for v,co in zip(obj.data.vertices,baseline['vertices']): v.co=co
    for mod in list(obj.modifiers):
        if mod.name.startswith('EXPERIMENT_'): obj.modifiers.remove(mod)
    if typ in {'Rotate','Open','Close'}:
        axis=p.get('axis',2); a=p.get('fromDegrees',0); b=p.get('toDegrees',90)
        obj.rotation_euler[axis]=baseline['rotation'][axis]+math.radians(a+(b-a)*t)
    elif typ in {'Squash','Stretch','Flatten'}:
        target=p.get('scale',{'Squash':[1.15,1.15,.55],'Stretch':[.8,.8,1.6],'Flatten':[1,1,.08]}[typ])
        if len(target)!=3 or min(target)<=0: raise ValueError('Scale must remain nondegenerate')
        obj.scale=[s*(1+(q-1)*t) for s,q in zip(baseline['scale'],target)]
    elif typ=='Bend':
        # Explicit geometric bend, no claim of elastic/volume conservation.
        angle=math.radians(p.get('degrees',60))*t
        length=max(v[2] for v in baseline['vertices'])-min(v[2] for v in baseline['vertices'])
        if length<=0: raise ValueError('Bend needs height')
        for v,co in zip(obj.data.vertices,baseline['vertices']):
            a=angle*co[2]/length; x,z=co[0],co[2]
            v.co=(math.cos(a)*x+math.sin(a)*z,co[1],-math.sin(a)*x+math.cos(a)*z)
    elif typ in {'Cut','Pierce','Join'}:
        operand=operands.get(p.get('operandId'))
        if operand is None or operand==obj: raise ValueError('Boolean requires a distinct mesh operand')
        # Operand path is defined by the preset, never inferred from a caption.
        start=p['operandFrom']; end=p['operandTo']; operand.location=Vector(start).lerp(Vector(end),t)
        operand.hide_render=True
        mod=obj.modifiers.new('EXPERIMENT_'+typ,'BOOLEAN'); mod.operation='UNION' if typ=='Join' else 'DIFFERENCE'; mod.solver='EXACT'; mod.object=operand
    elif typ=='Morph':
        target=p['targetVertices']
        if len(target)!=len(baseline['vertices']): raise ValueError('Morph requires matching topology')
        for v,co,end in zip(obj.data.vertices,baseline['vertices'],target): v.co=Vector(co).lerp(Vector(end),t)
    elif typ=='Compare':
        obj.location=Vector(baseline['location']).lerp(Vector(p['position']),t)
    elif typ!='ValueUpdate': raise ValueError('Unknown operation '+typ)
    obj.data.update(); bpy.context.view_layer.update()

def geometry_record(obj):
    import bpy
    evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get()); mesh=evaluated.to_mesh()
    try:
        vertices=[list(evaluated.matrix_world@v.co) for v in mesh.vertices]
        polygons=[list(p.vertices) for p in mesh.polygons]
        if not vertices or not polygons or any(not math.isfinite(v) for co in vertices for v in co): raise ValueError('Invalid or empty evaluated mesh')
        mesh.calc_loop_triangles();volume=0
        from mathutils import Vector
        for tri in mesh.loop_triangles:
            a,b,c=[Vector(vertices[i]) for i in tri.vertices];volume+=a.dot(b.cross(c))/6
        adjacent={i:set() for i in range(len(vertices))}
        for edge in mesh.edges:
            a,b=edge.vertices;adjacent[a].add(b);adjacent[b].add(a)
        unseen=set(adjacent);components=0
        while unseen:
            components+=1;stack=[unseen.pop()]
            while stack:
                for neighbor in adjacent[stack.pop()] & unseen:unseen.remove(neighbor);stack.append(neighbor)
        return {'geometryHash':signature([vertices,polygons]),'vertices':len(vertices),'polygons':len(polygons),'meshVolume':abs(volume),'connectedComponents':components,
                'properties':{'rotationZDegrees':math.degrees(obj.rotation_euler.z)}}
    finally: evaluated.to_mesh_clear()

def completion(obj,state,frame,progress):
    if progress<1 or frame<state['operation']['completeFrame']: raise ValueError('Premature completion')
    record=geometry_record(obj)
    return {**record,'objectId':state['objectId'],'stateSignature':signature(state),'frame':frame,'completed':True}
