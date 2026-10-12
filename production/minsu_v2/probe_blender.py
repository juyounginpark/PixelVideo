import bpy
s=bpy.context.scene
print('COMPOSITOR',[(x,hasattr(s,x)) for x in ['use_nodes','node_tree','compositing_node_group']])
print('EEVEE',hasattr(s,'eevee'))
g=bpy.data.node_groups.new('probe','CompositorNodeTree')
for name in ['CompositorNodeRLayers','CompositorNodeFilter','CompositorNodeMixRGB','CompositorNodeMath','CompositorNodeComposite','CompositorNodeOutputFile']:
    try:
        n=g.nodes.new(name);print(name,[(a.name,a.identifier) for a in n.inputs],[(a.name,a.identifier) for a in n.outputs])
    except Exception as e:print(name,str(e))
for name in ['ShaderNodeMath','ShaderNodeMix','ShaderNodeVectorMath','CompositorNodeRGBToBW','NodeGroupOutput','CompositorNodeSeparateColor','CompositorNodeCombineColor']:
    try:
        n=g.nodes.new(name);print(name,[(a.name,a.identifier) for a in n.inputs],[(a.name,a.identifier) for a in n.outputs])
    except Exception as e: print(name,str(e))
