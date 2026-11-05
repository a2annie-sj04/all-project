import bpy, math, os
from mathutils import Vector
OUT=os.path.dirname(os.path.abspath(__file__))
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
s=bpy.context.scene
s.unit_settings.system='METRIC'; s.unit_settings.scale_length=0.01

def mat(name,color,metal=0,rough=.35):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
 return m
blue=mat('SkyBlue_SatinShell',(.28,.56,.73),.45,.28)
silver=mat('Silver_Trim',(.65,.7,.74),.8,.24)
rubber=mat('Rubber',(.018,.024,.03),0,.65)
fabric=mat('Navy_Lining',(.025,.055,.09),0,.85)
mesh=mat('Packing_Straps',(.08,.13,.18),0,.75)
parts=[]
def empty(name,loc,parent=None):
 o=bpy.data.objects.new(name,None); s.collection.objects.link(o); o.location=loc; o.parent=parent; return o
root=empty('SUITCASE_ROOT_cm',(0,0,0))
body=empty('Body_Assembly',(0,0,0),root)
# Front lid rotates around a vertical hinge at its left edge.
lid=empty('Lid_Hinge_OPEN_Z',( -10.1,0,18.9),root)
def cube(name,loc,scale,material,bevel=.15,parent=body):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=scale
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('Rounded_Edges','BEVEL'); mod.width=bevel; mod.segments=4
  mod=o.modifiers.new('Weighted_Normals','WEIGHTED_NORMAL')
 o.data.materials.append(material)
 if parent:
  world=o.matrix_world.copy(); o.parent=parent; o.matrix_world=world
 parts.append(o); return o

def cyl(name,loc,radius,depth,material,parent=body):
 bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=radius,depth=depth,location=loc,rotation=(math.pi/2,0,0)); o=bpy.context.object; o.name=name
 o.data.materials.append(material); b=o.modifiers.new('Edge_Soften','BEVEL'); b.width=.08; b.segments=3
 for p in o.data.polygons:p.use_smooth=True
 world=o.matrix_world.copy(); o.parent=parent; o.matrix_world=world; parts.append(o); return o
# Rounded rectangular contours in X/Z; radius is independent of wall thickness.
def contour(w,h,r):
 pts=[]
 for cx,cz,a in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
  for j in range(17):
   t=math.radians(a+j*90/16)
   pts.append((cx+r*math.cos(t),18.9+cz+r*math.sin(t)))
 return pts

def loft(name,rings,material,parent,cap=False):
 verts=[]
 for w,h,r,y in rings:
  verts.extend((x,y,z) for x,z in contour(w,h,r))
 n=68; faces=[]
 for k in range(len(rings)-1):
  for j in range(n):
   a=k*n+j;b=k*n+(j+1)%n
   faces.append((a,b,b+n,a+n))
 if cap:faces.extend([tuple(reversed(range(n))),tuple((len(rings)-1)*n+j for j in range(n))])
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
 o=bpy.data.objects.new(name,me);s.collection.objects.link(o);o.data.materials.append(material)
 for poly in me.polygons:poly.use_smooth=True
 bpy.context.view_layer.update();world=o.matrix_world.copy();o.parent=parent;o.matrix_world=world;parts.append(o)
 return o

def tray(label,front,parent):
 sign=-1 if front else 1
 # Continuous shell lip -> rounded shoulder -> face -> inner floor -> inner lip.
 profile=[(20.4,28.8,2.6,sign*.17),(20.4,28.8,2.6,sign*4.3),
 (20.25,28.65,2.65,sign*5.0),(19.8,28.2,2.7,sign*5.55),
 (19.0,27.4,2.65,sign*5.85),(18.0,26.4,2.5,sign*5.95),
 (18.0,26.4,2.5,sign*5.55),(18.8,27.2,2.5,sign*5.2),
 (19.6,28.0,2.3,sign*4.3),(19.6,28.0,2.3,sign*.17)]
 loft(label+'_ContinuousRoundedShell',profile,blue,parent)
 loft(label+'_Face',[(18,26.4,2.5,sign*5.95),(18,26.4,2.5,sign*5.72)],blue,parent,True)
 loft(label+'_InteriorLining',[(18.6,27,2.4,sign*5.48),(18.6,27,2.4,sign*5.38)],fabric,parent,True)
 loft(label+'_ThinSeam',[(20.43,28.83,2.6,sign*.13),(20.43,28.83,2.6,sign*.30)],rubber,parent)
 loft(label+'_AluminiumRim',[(20.45,28.85,2.6,sign*.32),(20.45,28.85,2.6,sign*.46)],silver,parent)
 # Shallow rounded longitudinal flutes, tapering near curved shoulders.
 for i in range(11):
  x=(i-5)*1.56; length=24.7 if abs(x)<6 else 23.2
  o=loft(label+'_Flute_%02d'%i,[(.46,length,.23,sign*5.94),(.42,length-.06,.21,sign*6.09),(.25,length-.23,.125,sign*6.14)],blue,parent,True)
  o.location.x+=x
 # Guards use the SAME shoulder sections as the shell, with a 0.025 cm skin allowance.
 for side in (-1,1):
  for top in (-1,1):
   vs=[];fs=[]
   sections=[(20.4,28.8,2.6,4.1),(20.4,28.8,2.6,4.3),
    (20.25,28.65,2.65,5.0),(19.8,28.2,2.7,5.55),
    (19,27.4,2.65,5.85),(18,26.4,2.5,5.95),
    (17.3,25.7,2.15,5.95),(16.4,24.8,1.7,5.95)]
   for w,h,r,y in sections:
    for j in range(33):
     t=math.pi/2*j/32
     vs.append((side*(w/2-r+(r+.018)*math.cos(t)),sign*(y+.025),18.9+top*(h/2-r+(r+.018)*math.sin(t))))
   for k in range(len(sections)-1):
    for j in range(32):
     a=k*33+j;fs.append((a,a+1,a+34,a+33))
   me=bpy.data.meshes.new('ConformalGuardSurface');me.from_pydata(vs,[],fs);me.update()
   o=bpy.data.objects.new(label+'_FittedCornerGuard',me);s.collection.objects.link(o);o.data.materials.append(silver)
   solid=o.modifiers.new('MetalThickness_0.35mm','SOLIDIFY');solid.thickness=.035;solid.offset=0
   bevel=o.modifiers.new('SoftMetalEdge','BEVEL');bevel.width=.025;bevel.segments=3
   for poly in me.polygons:poly.use_smooth=True
   bpy.context.view_layer.update();world=o.matrix_world.copy();o.parent=parent;o.matrix_world=world;parts.append(o)
   # Rivets lie on the flat face of the guard, inside its perimeter.
   for t in (.25,1.32):
    rx=side*(6.5+1.94*math.cos(t));rz=18.9+top*(10.7+1.94*math.sin(t))
    cyl(label+'_FlushRivet',(rx,sign*6.025,rz),.105,.07,silver,parent)
    cyl(label+'_RivetRecess',(rx,sign*6.068,rz),.035,.008,rubber,parent)
tray('Rear',False,body); tray('Front',True,lid)
# Interior details use real geometry and portable fabric image textures.
thread=mat('LightGrey_Stitch',(.30,.40,.48),0,.9)
zipmat=mat('Gunmetal_Zipper',(.12,.15,.18),.65,.34)
# Fine woven texture, saved as images rather than Blender-only procedural shaders.
os.makedirs(OUT+'/textures',exist_ok=True)
for material,base,name in [(fabric,(.13,.19,.25),'lining_weave'),(mesh,(.20,.27,.32),'webbing_weave')]:
 image=bpy.data.images.new(name,width=256,height=256)
 pixels=[]
 for yy in range(256):
  for xx in range(256):
   weave=.88+.08*math.cos(xx*math.pi/2)+.06*math.cos(yy*math.pi/2)+.03*math.sin((xx+yy)*.7)
   pixels.extend((*[v*weave for v in base],1))
 image.pixels=pixels;image.filepath_raw=OUT+'/textures/'+name+'.png';image.file_format='PNG';image.save()
 nodes=material.node_tree.nodes;links=material.node_tree.links;pbr=nodes.get('Principled BSDF')
 uv=nodes.new('ShaderNodeTexCoord');mapping=nodes.new('ShaderNodeVectorMath');mapping.operation='SCALE';mapping.inputs[3].default_value=8
 tex=nodes.new('ShaderNodeTexImage');tex.image=image;links.new(uv.outputs['UV'],mapping.inputs[0]);links.new(mapping.outputs[0],tex.inputs['Vector']);links.new(tex.outputs['Color'],pbr.inputs['Base Color'])
 bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.15;bump.inputs['Distance'].default_value=.012
 links.new(tex.outputs['Color'],bump.inputs['Height']);links.new(bump.outputs['Normal'],pbr.inputs['Normal'])

def parent_world(o,parent):
 bpy.context.view_layer.update();w=o.matrix_world.copy();o.parent=parent;o.matrix_world=w;parts.append(o);return o

def tube(name,coords,radius,material,parent,closed=False):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=radius;cu.bevel_resolution=2
 sp=cu.splines.new('POLY');sp.points.add(len(coords)-1)
 for pt,co in zip(sp.points,coords):pt.co=(*co,1)
 sp.use_cyclic_u=closed
 o=bpy.data.objects.new(name,cu);s.collection.objects.link(o);o.data.materials.append(material)
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
 return parent_world(bpy.context.object,parent)

def blockmesh(name,blocks,material,parent):
 vs=[];fs=[]
 for (x,y,z),(w,d,h) in blocks:
  n=len(vs)
  vs.extend((x+sx*w/2,y+sy*d/2,z+sz*h/2) for sx,sy,sz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)])
  fs.extend(tuple(n+i for i in face) for face in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);s.collection.objects.link(o);o.data.materials.append(material);return parent_world(o,parent)

def perimeter(w,h,r,y):return [(x,y,z) for x,z in contour(w,h,r)]

def samples(coords,spacing):
 coords=coords+[coords[0]];out=[];carry=0
 for a,b in zip(coords,coords[1:]):
  a=Vector(a);b=Vector(b);d=(b-a).length
  while carry<d:
   out.append(a+(b-a)*(carry/d));carry+=spacing
  carry-=d
 return out

def stitch_loop(name,w,h,r,y,parent):
 pts=samples(perimeter(w,h,r,y),.28)
 blockmesh(name,[(tuple(v),(.08,.035,.035)) for v in pts],thread,parent)

# Textile gussets cover the entire inside wall, with rolled piping on the opening.
for prefix,sign,parent in [('Rear',1,body),('Front',-1,lid)]:
 o=loft(prefix+'_FabricSideGusset',[(19.5,27.9,2.3,sign*.40),(19.5,27.9,2.3,sign*4.15),(18.65,27.05,2.4,sign*5.22)],fabric,parent)
 solid=o.modifiers.new('FabricThickness','SOLIDIFY');solid.thickness=.045
 tube(prefix+'_RolledLiningPiping',perimeter(19.48,27.88,2.3,sign*.42),.065,mesh,parent,True)
 tube(prefix+'_FloorSeam',perimeter(18.0,26.4,2.25,sign*5.21),.045,mesh,parent,True)
 stitch_loop(prefix+'_OpeningStitch',19.22,27.62,2.24,sign*.38,parent)
 for xx in (-7.8,7.8):cube(prefix+'_PaddedWheelHousing',(xx,sign*3.2,5.9),(2.5,4.2,1.2),fabric,.40,parent)
 # Cloth-covered channels lie against the cavity floor rather than exposed metal tubes.
 if sign==1:
  for x in (-3.1,3.1):cube('Rear_PaddedRailChannel',(x,5.14,18.9),(1.25,.35,24.0),fabric,.16,parent)

# Main packing bay: straps are attached to four inner wall anchors.
anchors=[(-9.68,3.9,8.0),(9.68,3.9,29.8),(-9.68,3.9,29.8),(9.68,3.9,8.0)]
for i,co in enumerate(anchors):
 cube('Belt_AnchorPatch_%d'%i,co,(.14,1.5,1.8),mesh,.045,body)
 # small stitched attachment outlines
 x,y,z=co
 tube('Belt_AnchorStitch_%d'%i,[(x-math.copysign(.08,x),y-.55,z-.65),(x-math.copysign(.08,x),y+.55,z-.65),(x-math.copysign(.08,x),y+.55,z+.65),(x-math.copysign(.08,x),y-.55,z+.65)],.018,thread,body,True)

def ribbon(name,coords,width,parent):
 vs=[];fs=[]
 for i,co in enumerate(coords):
  t=Vector(coords[min(i+1,len(coords)-1)])-Vector(coords[max(0,i-1)])
  side=Vector((t.z,0,-t.x)).normalized()*width/2
  vs.extend([tuple(Vector(co)-side),tuple(Vector(co)+side)])
 for i in range(len(coords)-1):fs.append((2*i,2*i+1,2*i+3,2*i+2))
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);s.collection.objects.link(o);o.data.materials.append(mesh)
 solid=o.modifiers.new('WebbingThickness','SOLIDIFY');solid.thickness=.065
 parent_world(o,parent)
 for side in (0,1):tube(name+'_EdgeBinding_'+str(side),[vs[2*i+side] for i in range(len(coords))],.018,thread,parent)
 return o
for i,(a,b) in enumerate([(anchors[0],anchors[1]),(anchors[2],anchors[3])]):
 # Belt descends from its wall attachment to the floor, staying supported in an empty case.
 points=[a,(a[0]*.84,5.0,a[2]+(1 if a[2]<18 else -1)),(0,4.95,18.9),(b[0]*.84,5.0,b[2]+(1 if b[2]<18 else -1)),b]
 ribbon('Rear_XCompressionBelt_%d'%i,points,.74,body)
# Actual open frame buckle with insert/prongs, not a solid square block.
for x in (-.75,.75):cube('Buckle_FrameSide',(x,4.77,18.9),(.20,.25,1.35),rubber,.075)
for z in (18.25,19.55):cube('Buckle_FrameEnd',(0,4.77,z),(1.65,.25,.2),rubber,.07)
cube('Buckle_CentreTongue',(0,4.68,18.9),(.7,.28,.85),rubber,.09)
for z in (18.52,19.28):cube('Buckle_ReleaseEar',(.67,4.63,z),(.28,.19,.20),rubber,.055)
for x in (-5.8,5.8):
 cube('Belt_LengthAdjuster',(x,4.83,25.96 if x>0 else 11.84),(1.08,.18,.64),rubber,.07)

# Front divider is a separate removable panel just inside the rim.
# An empty within the lid makes future opening/removal animation possible.
divider=empty('Interior_Divider_MOVE_WITH_LID',(0,0,0))
bpy.context.view_layer.update();w=divider.matrix_world.copy();divider.parent=lid;divider.matrix_world=w
loft('Front_ZippedDividerPanel',[(18.7,27.1,2.0,-.82),(18.7,27.1,2.0,-.68)],fabric,divider,True)
tube('Divider_ZipperTape',perimeter(18.8,27.2,2.0,-.58),.12,mesh,divider,True)
pts=samples(perimeter(18.8,27.2,2.0,-.45),.24)
blockmesh('Divider_IndividualZipperTeeth',[(tuple(v),(.10,.12,.10)) for v in pts],zipmat,divider)
stitch_loop('Divider_DoubleTopstitch',18.2,26.6,1.8,-.48,divider)
# Zipper slider and ring-shaped pull, attached to top edge.
cube('Divider_ZipperSlider',(5.0,-.26,32.5),(.52,.3,.78),zipmat,.10,divider)
tube('Divider_ZipperPull',[(4.85,-.05,32.5),(4.65,.10,31.6),(5.10,.10,31.4),(5.32,-.05,32.4)],.055,silver,divider,True)
# Mesh pocket: real diagonal lattice, with an underlying fabric backing.
# Keep all strand geometry in one mesh per pocket for reasonable object counts.
def mesh_pocket(name,x0,x1,z0,z1,y,parent):
 curves=[]
 for slope in (-1,1):
  for k in range(-50,80):
   intercept=k*.40
   intersections=[]
   for x in (x0,x1):
    z=slope*x+intercept
    if z0<=z<=z1:intersections.append((x,y,z))
   for z in (z0,z1):
    x=(z-intercept)/slope
    if x0<=x<=x1:intersections.append((x,y,z))
   if len(intersections)>=2 and (Vector(intersections[0])-Vector(intersections[1])).length>.02:curves.append(intersections[:2])
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=.018;cu.bevel_resolution=1
 for coords in curves:
  sp=cu.splines.new('POLY');sp.points.add(1)
  for pt,co in zip(sp.points,coords):pt.co=(*co,1)
 o=bpy.data.objects.new(name,cu);s.collection.objects.link(o);o.data.materials.append(mesh)
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');parent_world(bpy.context.object,parent)
 tube(name+'_BoundEdge',[(x0,y,z0),(x1,y,z0),(x1,y,z1),(x0,y,z1)],.085,mesh,parent,True)
 # Fabric side/bottom bellows join mesh face to divider backing; no free-floating pocket.
 for x in (x0,x1):cube(name+'_SideGusset',(x,(y-.68)/2,(z0+z1)/2),(.13,y+.68,z1-z0),fabric,.04,parent)
 cube(name+'_BottomGusset',((x0+x1)/2,(y-.68)/2,z0),(x1-x0,y+.68,.13),fabric,.04,parent)
mesh_pocket('Front_UpperDiamondMeshPocket',-7.5,7.5,21.0,29.9,-.16,divider)
# Upper pocket zipper teeth + tape and tab.
cube('Pocket_ZipTape',(0,-.09,29.9),(15.2,.12,.26),mesh,.045,divider)
blockmesh('Pocket_ZipTeeth',[((x*.24,-.005,29.9),(.11,.10,.11)) for x in range(-30,31)],zipmat,divider)
cube('Pocket_ZipSlider',(5.9,.07,29.9),(.4,.2,.4),silver,.06,divider)
tube('Pocket_ZipPull',[(5.9,.15,29.9),(5.7,.22,29.2),(6.05,.22,29.05),(6.2,.15,29.8)],.045,silver,divider,True)
# Two lower pleated organizer pockets, connected at the sides and bottom.
for i,(x0,x1) in enumerate([(-7.5,-.4),(.4,7.5)]):
 y=-.24;z0=8.5;z1=18.8
 cube('OrganizerPocket_%d'%i,((x0+x1)/2,y,(z0+z1)/2),(x1-x0,.12,z1-z0),fabric,.055,divider)
 for x in (x0,x1):cube('Organizer_SideGusset_%d'%i,(x,-.45,(z0+z1)/2),(.13,.5,z1-z0),fabric,.04,divider)
 cube('Organizer_BottomGusset_%d'%i,((x0+x1)/2,-.45,z0),(x1-x0,.5,.12),fabric,.04,divider)
 tube('Organizer_ElasticHem_%d'%i,[(x0,-.11,z1),((x0+x1)/2,-.06,z1-.14),(x1,-.11,z1)],.085,mesh,divider)
 for x in (x0+.25,x1-.25):tube('Organizer_Stitch_%d'%i,[(x,-.15,z0+.15),(x,-.15,z1-.25)],.016,thread,divider)
# Small woven care label attached to the divider, unbranded.
cube('Interior_CareLabel',(-6.1,-.45,20.1),(1.8,.04,.7),thread,.015,divider)
for z in (19.94,20.1,20.26):cube('CareLabel_Print',(-6.1,-.42,z),(1.35,.015,.035),fabric,.005,divider)
# Ensure custom textile meshes carry UV coordinates for exchange formats.
for o in parts:
 if o.type=='MESH' and any(m in (fabric,mesh) for m in o.data.materials):
  uv=o.data.uv_layers.active or o.data.uv_layers.new(name='FabricUV')
  for poly in o.data.polygons:
   axis=max(range(3),key=lambda k:abs(poly.normal[k]));axes=[i for i in range(3) if i!=axis]
   for li in poly.loop_indices:
    v=o.data.vertices[o.data.loops[li].vertex_index].co
    uv.data[li].uv=(v[axes[0]]/20,v[axes[1]]/20)
for z in (10,27):cube('Hinge',(-10.35,0,z),(.5,1.2,2.4),silver,.18)
for z in (13,25):
 cube('Latch_Recess',(10.23,0,z),(.12,1.65,2.25),rubber,.06)
 cube('Latch_Frame',(10.35,0,z),(.18,1.45,2.05),silver,.07)
 cube('Latch_Lever',(10.48,-.15,z),(.16,.8,1.35),silver,.06)
 cube('Latch_Release',(10.57,-.15,z+.37),(.035,.43,.22),rubber,.025)
# Combination lock on side, three separate number barrels with index marks.
cube('Lock_Inset',(10.23,1.8,25),(.15,1.75,3.6),rubber,.1)
cube('Lock_Housing',(10.37,1.8,25),(.18,1.55,3.4),silver,.1)
for z in (24.2,25,25.8):
 cube('Combination_Dial',(10.5,1.8,z),(.15,.85,.55),rubber,.09)
 for yy in (1.56,1.8,2.04):cube('Dial_Index',(10.585,yy,z),(.015,.045,.23),silver,.008)

# Mechanically connected caster: embedded socket -> swivel -> fork -> axle -> tires.
for x in (-8.6,8.6):
 for y in (-4.2,4.2):
  tag=('L' if x<0 else 'R')+('_Front' if y<0 else '_Rear')
  caster=empty('Caster_'+tag,(x,y,2.0))
  bpy.context.view_layer.update();world=caster.matrix_world.copy();caster.parent=lid if y<0 else body;caster.matrix_world=world
  # Broad molded seat reaches into the rounded lower shell, not merely toward it.
  cube('WheelSocket_'+tag,(x,y,4.65),(3.0,2.7,1.65),blue,.35,caster)
  cube('WheelSocketGasket_'+tag,(x,y,3.95),(2.25,2.15,.45),rubber,.15,caster)
  swivel=cyl('SwivelBearing_'+tag,(x,y,3.65),.76,.65,rubber,caster)
  swivel.rotation_euler=(0,0,0)
  cube('ForkBridge_'+tag,(x,y,3.17),(1.65,1.16,.65),rubber,.18,caster)
  for side in (-1,1):
   cube('ForkCheek_'+tag,(x,y+side*.37,2.28),(1.05,.24,2.25),rubber,.12,caster)
  cyl('WheelAxle_'+tag,(x,y,1.45),.21,2.22,silver,caster)
  for side in (-1,1):
   dy=side*.82
   cyl('WheelTire_'+tag,(x,y+dy,1.45),1.45,.56,rubber,caster)
   cyl('WheelRim_'+tag,(x,y+side*1.10,1.45),.88,.10,rubber,caster)
   cyl('WheelAxleCap_'+tag,(x,y+side*1.17,1.45),.27,.08,silver,caster)
# Real handle bridges: feet contact shell and the middle has a finger clearance.
def bridge(name,points,radius,material,parent):
 curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.resolution_u=16
 curve.bevel_depth=radius;curve.bevel_resolution=5
 sp=curve.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
 for bp,co in zip(sp.bezier_points,points):bp.co=co;bp.handle_left_type='AUTO';bp.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,curve);s.collection.objects.link(o);o.data.materials.append(material)
 bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o=bpy.context.object
 bpy.context.view_layer.update();world=o.matrix_world.copy();o.parent=parent;o.matrix_world=world;parts.append(o)
for x in (-3.5,3.5):
 cube('TopHandle_Seat',(x,1.7,33.36),(1.15,1.5,.18),rubber,.075)
 cube('TopHandle_Bracket',(x,1.7,33.52),(.85,1.2,.2),silver,.09)
bridge('Top_CarryHandle',[(-3.5,1.7,33.58),(-2.9,1.7,34.15),(0,1.7,34.35),(2.9,1.7,34.15),(3.5,1.7,33.58)],.30,rubber,body)
for z in (15.7,22.3):
 cube('SideHandle_Seat',(10.24,2.6,z),(.14,1.45,1.05),rubber,.06)
 cube('SideHandle_Bracket',(10.37,2.6,z),(.18,1.15,.8),silver,.07)
bridge('Side_CarryHandle',[(10.4,2.6,15.7),(11.0,2.6,16.4),(11.15,2.6,19),(11.0,2.6,21.6),(10.4,2.6,22.3)],.28,rubber,body)
# Telescopic assembly: folded by default, animate local Z to extend.
telescope=empty('TelescopicHandle_MOVE_Z',(0,0,0),body)
for x in (-3.1,3.1):cube('Telescopic_Rail',(x,6.0,27),(.55,.6,12),silver,.1,telescope)
cube('Telescopic_Grip',(0,6.0,33.3),(7.4,1.2,.8),rubber,.35,telescope)
cube('Blank_Nameplate',(0,-6.20,28),(3.6,.12,1.8),silver,.3,lid)
for x in (-1.45,1.45):
 for z in (27.4,28.6):cyl('Nameplate_Fastener',(x,-6.28,z),.075,.035,silver,lid)
# Select asset only and export; stage never enters interchange exports.
bpy.ops.object.select_all(action='DESELECT')
for o in [root,body,lid,telescope,divider]+parts+[o for o in bpy.data.objects if o.name.startswith('Caster_')]:o.select_set(True)
bpy.context.view_layer.objects.active=root
bpy.ops.export_scene.fbx(filepath=OUT+'/suitcase_skyblue_cm.fbx',use_selection=True,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',add_leaf_bones=False,bake_anim=False)
bpy.ops.export_scene.gltf(filepath=OUT+'/suitcase_skyblue.glb',use_selection=True,export_apply=True)
# Stage: two 64 x 48 cm faces meet on vertical corner, floor at Z=0.
stage=empty('DISPLAY_GUIDE_64x48cm_90deg',(0,0,0))
guide=mat('Display_Guide',(.075,.1,.15),0,.8)
a=cube('Display_Left',(-32,12,24),(64,.15,48),guide,.0,stage)
b=cube('Display_Right',(0,44,24),(.15,64,48),guide,.0,stage)
stage.hide_render=True
for o in stage.children:o.hide_render=True
observer=empty('ANAMORPHIC_VIEW_150cm',(106.066,-94.066,24))
# Camera is a product review view, independent of installation reference.
def camera(name,loc,target):
 bpy.ops.object.camera_add(location=loc); c=bpy.context.object;c.name=name;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=48;return c
s.camera=camera('Product_Preview',(56,-85,51),(0,0,17))
bg=mat('Studio_Floor',(.11,.15,.2),0,.65)
cube('StudioFloor',(0,0,-.4),(200,200,.5),bg,.1,None)
for loc,power,size in [((20,-40,65),110000,45),((-35,-15,35),65000,35),((15,30,55),125000,30)]:
 bpy.ops.object.light_add(type='AREA',location=loc); l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(Vector((0,0,17))-l.location).to_track_quat('-Z','Y').to_euler()
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=False
s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100
s.world.color=(.2,.2,.2)
s.render.image_settings.file_format='PNG';s.render.filepath=OUT+'/preview_closed.png'
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/suitcase_skyblue.blend')
bpy.ops.render.render(write_still=True)
lid.rotation_euler.z=math.radians(-115)
s.camera.data.ortho_scale=62; s.camera.location=(40,-90,60); s.camera.rotation_euler=(Vector((-9,0,18))-s.camera.location).to_track_quat('-Z','Y').to_euler()
s.render.filepath=OUT+'/preview_open.png';bpy.ops.render.render(write_still=True)
print('ASSET_COMPLETE',len(parts))

# Face-on interior inspection camera: look into rear cavity, and onto open lid.
s.camera.location=(0,-70,30);s.camera.rotation_euler=(Vector((0,3,19))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=34
s.render.filepath=OUT+'/preview_main_interior.png';bpy.ops.render.render(write_still=True)
# Camera follows lid's transformed inward normal; frame the entire divider.
bpy.context.view_layer.update()
center=lid.matrix_world@Vector((10.1,-.3,0));normal=lid.matrix_world.to_3x3()@Vector((0,1,0))
s.camera.location=center+normal*70+Vector((0,0,4));s.camera.rotation_euler=(center-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=34
s.render.filepath=OUT+'/preview_lid_interior.png';bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/suitcase_interior_open.blend')
print('INTERIOR_V05_COMPLETE')
