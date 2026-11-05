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
# Interior crossed retention straps in rear cavity.
for angle in (-33,33):
 o=cube('Interior_RetentionStrap',(0,1.0,18.9),(.7,.15,29),mesh,.08); o.rotation_euler[1]=math.radians(angle)
cube('Interior_Buckle',(0,.85,18.9),(1.7,.4,1.6),rubber,.2)
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
for o in [root,body,lid,telescope]+parts+[o for o in bpy.data.objects if o.name.startswith('Caster_')]:o.select_set(True)
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
s.camera.location=(28,-65,44);s.camera.rotation_euler=(Vector((7,-4,30))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=14
s.render.filepath=OUT+'/preview_corner_detail.png';bpy.ops.render.render(write_still=True)
s.camera.location=(29,-45,12);s.camera.rotation_euler=(Vector((8.3,-3.7,4.1))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=12
s.render.filepath=OUT+'/preview_wheel_attachment.png';bpy.ops.render.render(write_still=True)
lid.rotation_euler.z=math.radians(-115)
s.camera.data.ortho_scale=62; s.camera.location=(40,-90,60); s.camera.rotation_euler=(Vector((-9,0,18))-s.camera.location).to_track_quat('-Z','Y').to_euler()
s.render.filepath=OUT+'/preview_open.png';bpy.ops.render.render(write_still=True)
print('ASSET_COMPLETE',len(parts))
