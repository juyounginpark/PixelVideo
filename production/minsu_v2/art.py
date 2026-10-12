"""Reusable native Blender assets: one rig and palette across all shots."""
import bpy, math, random
from mathutils import Vector

def empty(name,loc=(0,0,0),parent=None):
    o=bpy.data.objects.new(name,None);bpy.context.scene.collection.objects.link(o);o.parent=parent;o.location=loc;return o

def box(name,loc,dim,mat,parent=None,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1);o=bpy.context.object;o.name=name;o.parent=parent;o.location=loc
    # Mesh dimensions, unit object scale: clean pivot animation, constant bevel.
    for v in o.data.vertices:v.co=Vector((v.co.x*dim[0],v.co.y*dim[1],v.co.z*dim[2]))
    o.data.materials.append(mat)
    if bevel:
        m=o.modifiers.new('single-step corners','BEVEL');m.width=bevel;m.segments=1
        m=o.modifiers.new('weighted face normals','WEIGHTED_NORMAL');m.keep_sharp=True
    return o

def cone(name,loc,radius,height,mat,parent=None,rotation=(0,0,0)):
    bpy.ops.mesh.primitive_cone_add(vertices=4,radius1=radius,radius2=0,depth=height)
    o=bpy.context.object;o.name=name;o.parent=parent;o.location=loc;o.rotation_euler=rotation;o.data.materials.append(mat);return o

def mesh(name,verts,faces,mat,parent=None):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
    o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o);o.parent=parent;o.data.materials.append(mat);return o

def line(name,points,mat,width=.012,parent=None):
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=width;cu.bevel_resolution=0;cu.resolution_u=1
    sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
    for p,co in zip(sp.points,points):p.co=(*co,1)
    o=bpy.data.objects.new(name,cu);bpy.context.scene.collection.objects.link(o);o.parent=parent;o.data.materials.append(mat);return o

def droplet(name,loc,mat):
    verts=[]
    for z,radius in [(-.025,.006),(-.015,.012),(-.003,.010),(.006,.005)]:
        for j in range(8):verts.append((radius*math.cos(j*math.tau/8),radius*math.sin(j*math.tau/8),z))
    verts.append((0,0,.016));faces=[tuple(range(7,-1,-1))]
    for row in range(3):
        for j in range(8):faces.append((row*8+j,row*8+(j+1)%8,(row+1)*8+(j+1)%8,(row+1)*8+j))
    for j in range(8):faces.append((24+j,24+(j+1)%8,32))
    o=mesh(name,verts,faces,mat);o.location=loc;return o

class MaterialLibrary:
    COLORS={'skin':(.93,.76,.53),'hair':(.15,.095,.065),'mint':(.22,.57,.43),'cream':(.94,.85,.64),
            'navy':(.045,.07,.09),'shoe':(.28,.20,.14),'cheek':(.85,.38,.32),'sand':(.66,.44,.24),
            'rock':(.48,.29,.15),'ochre':(.55,.28,.095),'amber':(.75,.44,.16),'pale':(.88,.65,.31),
            'brown':(.20,.11,.045),'wet':(.29,.24,.16),'water':(.075,.40,.57),'cyan':(.14,.75,.82)}
    def __init__(self):
        self.materials={}
        for name,col in self.COLORS.items():self.materials[name]=self.make(name,col,name not in ('navy','cheek','cyan','water'))
    def __getitem__(self,k):return self.materials[k]
    def make(self,name,color,textured):
        m=bpy.data.materials.new('V2_'+name);m.diffuse_color=(*color,1);m.use_nodes=True
        nodes=m.node_tree.nodes;nodes.clear();out=nodes.new('ShaderNodeOutputMaterial');bs=nodes.new('ShaderNodeBsdfDiffuse')
        bs.inputs['Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=.9
        m.node_tree.links.new(bs.outputs[0],out.inputs[0])
        if textured:
            im=bpy.data.images.new(name+'_32px',width=32,height=32);pixels=[];rng=random.Random(name)
            levels=[.95,.98,1,1.02] if name in ('skin','hair','mint','cream','shoe') else [.89,.96,1,1.05]
            tiles={(x,y):rng.choice(levels) for x in range(8) for y in range(8)}
            for y in range(32):
                for x in range(32):
                    f=tiles[(x//4,y//4)];pixels.extend([min(1,c*f) for c in color]+[1])
            # Zero blend produced white corner triangles on equal-axis bevel normals
            # in the local EEVEE 5.0.1 A/B stills. Keep nearest texels, blend only
            # the narrow projection boundary (not the image pixels).
            im.pixels=pixels;im.pack();tex=nodes.new('ShaderNodeTexImage');tex.image=im;tex.interpolation='Closest';tex.projection='BOX';tex.projection_blend=.08
            coord=nodes.new('ShaderNodeTexCoord');m.node_tree.links.new(coord.outputs['Generated'],tex.inputs[0]);m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Color'])
        return m

class FacialExpressionController:
    STATES=['Neutral','Curious','Surprise','Confused','Happy','Worried','Thinking','Determined','Laughing','Scared']
    def __init__(self,head,m):
        self.groups={};self.eyes=[]
        for state in self.STATES:
            g=empty('face_'+state,parent=head);self.groups[state]=g
            for sign in (-1,1):
                x=sign*.14;z=-.025
                if state in ('Happy','Laughing'):
                    eye=line(state+'_eye',[(x-.045,-.287,z),(x,-.293,z+.035),(x+.045,-.287,z)],m['navy'],.012,g)
                else:
                    h=.085 if state in ('Surprise','Scared') else .060
                    eye=box(state+'_eye',(x,-.29,z),(.047,.015,h),m['navy'],g,.005)
                    box(state+'_glint',(x-.008,-.301,z+.014),(.013,.008,.014),m['cream'],g)
                self.eyes.append(eye)
                if state in ('Worried','Confused','Thinking','Determined','Scared'):
                    brow=box(state+'_brow',(x,-.296,.064),(.085,.014,.019),m['hair'],g)
                    brow.rotation_euler.y=sign*(.26 if state!='Determined' else -.27)
            if state in ('Surprise','Scared'):
                box(state+'_mouth',(0,-.29,-.15),(.063,.014,.067),m['navy'],g,.009)
            elif state in ('Happy','Laughing'):
                line(state+'_mouth',[(-.065,-.294,-.12),(0,-.296,-.16),(.065,-.294,-.12)],m['navy'],.013,g)
            else:box(state+'_mouth',(0,-.294,-.15),(.064,.012,.014),m['navy'],g)
        self.set('Neutral')
    def set(self,state,blink=False):
        if state not in self.groups:raise ValueError(state)
        for k,g in self.groups.items():g.scale=(1,1,1) if k==state else (0,0,0)
        for eye in self.eyes:eye.scale.z=.1 if blink else 1

class CharacterRig:
    def __init__(self,root,body,head,arms,legs,face):
        self.root=root;self.body=body;self.head=head;self.arms=arms;self.legs=legs;self.face=face
        self.moving=[root,body,head,*arms,*legs,*face.groups.values(),*face.eyes]

class CharacterFactory:
    def __init__(self,m):self.m=m
    def minsu(self):
        m=self.m;root=empty('MINSU_CUTE_V2');body=empty('minsu_torso_pivot',(0,0,.43),root)
        box('mint_jacket',(0,0,.235),(.51,.33,.48),m['mint'],body,.04)
        box('jacket_zip',(0,-.175,.23),(.025,.012,.39),m['cream'],body)
        box('jacket_pocket',(.14,-.178,.16),(.11,.015,.1),m['mint'],body,.007)
        box('collar',(0,-.09,.46),(.22,.22,.045),m['cream'],body,.02)
        head=empty('minsu_head',(0,0,.81),body)
        box('large_flat_face',(0,0,0),(.69,.55,.63),m['skin'],head,.065)
        # Continuous fitted cap plus hairline/side pieces; no disconnected floating fringe.
        box('continuous_hair_cap',(0,.025,.25),(.724,.586,.22),m['hair'],head,.055)
        box('hair_back',(0,.244,.02),(.70,.105,.49),m['hair'],head,.025)
        for sign in (-1,1):
            box('side_hair',(sign*.333,.055,.10),(.085,.42,.37),m['hair'],head,.025)
            box('ear',(sign*.352,-.005,-.07),(.095,.15,.16),m['skin'],head,.025)
            box('cheek',(sign*.236,-.286,-.10),(.076,.012,.026),m['cheek'],head)
        for i,(x,z,w) in enumerate([(-.245,.145,.15),(-.07,.185,.20),(.14,.205,.23)]):
            box('fitted_fringe',(x,-.254,z),(w,.085,.17),m['hair'],head,.014)
        face=FacialExpressionController(head,m);arms=[];legs=[]
        for sign in (-1,1):
            a=empty('shoulder', (sign*.29,0,.39),body);arms.append(a)
            box('sleeve',(sign*.012,0,-.15),(.16,.22,.32),m['mint'],a,.023)
            box('hand',(sign*.014,-.012,-.335),(.17,.19,.16),m['skin'],a,.025)
            l=empty('hip',(sign*.143,0,.43),root);legs.append(l)
            box('short_trouser',(0,0,-.16),(.21,.28,.32),m['navy'],l,.02)
            box('boot',(0,-.045,-.36),(.25,.36,.14),m['shoe'],l,.025)
            box('sole',(0,-.048,-.417),(.26,.37,.025),m['cream'],l,.004)
        root['model_id']='MINSU_CUTE_V2';root['head_ratio']=.40
        return CharacterRig(root,body,head,arms,legs,face)

    def thorny(self):
        m=self.m;root=empty('THORNY_V2');body=empty('thorny_body',(0,0,.21),root)
        verts=[]
        for y,w,h in [(-.30,.16,.105),(-.09,.28,.13),(.18,.25,.13),(.34,.12,.08)]:
            for j in range(8):
                a=j*math.tau/8;verts.append((w*math.cos(a),y,h*math.sin(a)))
        faces=[]
        for r in range(3):
            for j in range(8):faces.append((r*8+j,r*8+(j+1)%8,(r+1)*8+(j+1)%8,(r+1)*8+j))
        faces.extend([tuple(range(7,-1,-1)),tuple(range(24,32))]);o=mesh('flattened_armoured_body',verts,faces,m['ochre'],body)
        o.data.materials.append(m['amber'])
        for f in o.data.polygons:f.material_index=f.index%2
        head=empty('thorny_head',(0,-.36,.045),body)
        verts=[(-.16,.075,-.04),(.16,.075,-.04),(.10,-.23,-.065),(-.10,-.23,-.065),(-.14,.08,.09),(.14,.08,.09),(.08,-.23,.01),(-.08,-.23,.01)]
        mesh('pointed_wedge_head',verts,[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],m['amber'],head)
        for sign in (-1,1):
            cone('eyebrow_horn',(sign*.12,.05,.15),.043,.19,m['brown'],head,(0,sign*.3,0))
            eye=box('animal_eye',(sign*.147,-.025,.028),(.023,.055,.036),m['navy'],head,.005)
            box('animal_eye_glint',(sign*.162,-.035,.038),(.007,.012,.009),m['cream'],head)
            cone('cheek_horn',(sign*.15,.03,-.005),.031,.12,m['pale'],head,(0,sign*1.1,0))
        jaw=empty('thorny_jaw',(0,-.035,-.061),head)
        box('narrow_lower_jaw',(0,-.11,-.006),(.19,.23,.032),m['pale'],jaw,.010)
        line('mouth_seam',[(-.085,-.234,-.052),(0,-.24,-.054),(.085,-.234,-.052)],m['navy'],.005,head)
        cone('false_head_hump',(0,.16,.095),.074,.13,m['ochre'],head)
        for r in range(7):
            y=-.24+r*.085
            for c in range(-2,3):
                x=c*.086;z=.12-.12*abs(c)/2;h=.058+((r+c)%3)*.017
                cone('dorsal_spine',(x,y,z+h/2),.034,h,m['brown'] if (r+c)%4==0 else m['pale'],body,(0,c*.17,0))
        for sign in (-1,1):
            for r in range(6):cone('flank_spine',(sign*.255,-.17+r*.075,.02),.027,.09,m['pale'],body,(0,sign*1.18,0))
        tail=empty('thorny_tail',(0,.31,0),body)
        for j in range(9):
            width=.105*(1-j/10);y=j*.07;z=j*j*.002
            box('tapered_tail',(0,y,z),(width,.09,width*.7),m['amber'] if j%2 else m['ochre'],tail,.006)
            cone('tail_spike',(0,y,z+width*.6),width*.26,.05,m['pale'],tail)
        limbs=[]
        for sign in (-1,1):
            for row,y in enumerate((-.20,.23)):
                a=empty('thorny_leg',(sign*.19,y,-.01),body);limbs.append(a)
                up=box('splayed_thigh',(sign*.085,.015,-.065),(.20,.075,.075),m['ochre'],a,.011);up.rotation_euler.y=sign*.38
                lo=box('bent_foreleg',(sign*.16,-.048,-.133),(.065,.17,.067),m['amber'],a,.012);lo.rotation_euler.x=.2
                box('flat_foot',(sign*.18,-.10,-.171),(.09,.10,.026),m['ochre'],a,.006)
                for toe in range(4):
                    o=box('toe',(sign*(.155+toe*.022),-.148,-.176),(.018,.10,.014),m['pale'],a,.003);o.rotation_euler.z=(toe-1.5)*.22
        root['model_id']='THORNY_V2'
        return {'root':root,'body':body,'head':head,'jaw':jaw,'tail':tail,'limbs':limbs}

class WorldFactory:
    def __init__(self,m):self.m=m
    def desert(self):
        m=self.m;box('sand_ground',(0,0,-.06),(70,70,.12),m['sand'])
        rng=random.Random(406)
        for i in range(28):
            a=i*2.399;r=2.0+(i%7)*.57
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1)
            o=bpy.context.object;o.name='sandstone';o.location=(math.cos(a)*r,math.sin(a)*r,.06);o.scale=(.16+rng.random()*.16,.13,.12);o.data.materials.append(m['rock'])
        for i in range(12):
            x=-4+i*.76;y=1.6+(i%3)*.8
            for j in range(3):cone('dry_grass',(x+j*.035,y,.14),.018,.28,m['pale'],rotation=(0,(j-1)*.35,.2))
        for i in range(7):
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1)
            o=bpy.context.object;o.name='distant_dune';o.location=(-10+i*3.6,9,.1);o.scale=(3,2,.8+(i%3)*.3);o.data.materials.append(m['sand'])
        # Polygonal, irregular free-water supply; not just damp sand.
        for name,r,z,mat in [('wet_sand',.54,.005,m['wet']),('free_water',.44,.023,m['water'])]:
            verts=[(-.10,-.28,z)]+[(-.10+math.cos(a*math.tau/13)*r*(.9+.1*math.sin(a*3)), -.28+math.sin(a*math.tau/13)*r*.72,z) for a in range(13)]
            mesh(name,verts,[(0,j+1,(j+1)%13+1) for j in range(13)],mat)
        return empty('water_anchor',(-.31,-.22,.1))
    def micro(self):
        m=self.m;root=empty('MICRO_EXTERNAL_SCALES',(20,0,0))
        box('skin_base',(0,0,-.18),(2.75,2.75,.35),m['ochre'],root,.03)
        for r in range(5):
            for c in range(5):
                x=(c-2)*.52;y=(r-2)*.52
                box('angular_scale',(x,y,.07),(.44,.44,.16),m['amber'] if (r+c)%2 else m['pale'],root,.035)
                cone('scale_tip',(x+.04,y+.06,.19),.05,.13,m['ochre'],root)
        channels=[]
        for axis in range(2):
            for row in range(4):
                c=(row-1.5)*.52
                for j in range(34):
                    a=-1.30+j*.078;p=(a,c,.036) if axis==0 else (c,a,.036)
                    o=box('wet_channel_segment',p,(.082,.062,.034) if axis==0 else (.062,.082,.034),m['cyan'],root)
                    channels.append((o,math.hypot(p[0]+.26,p[1]+.26)))
        anchor=empty('micro_anchor',(19.74,-.26,.045))
        return root,channels,anchor
