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
# Hollow tray construction: base panel and four perimeter walls, no solid filled block.
def tray(label,front,parent):
 sign=-1 if front else 1
 outer=sign*5.6; middle=sign*2.9
 cube(label+'_OuterPanel',(0,outer,18.9),(20.4,.8,28.8),blue,.65,parent)
 cube(label+'_Lining',(0,outer-sign*.5,18.9),(18.7,.22,26.8),fabric,.55,parent)
 for x in (-9.8,9.8):cube(label+'_SideWall',(x,middle,18.9),(.85,5.8,28.8),blue,.35,parent)
 for z in (4.9,32.9):cube(label+'_EndWall',(0,middle,z),(19.6,5.8,.85),blue,.35,parent)
 # contrasting seam, individually formed around rim
 for x in (-9.8,9.8):cube(label+'_Rim',(x,sign*.18,18.9),(.9,.22,28),rubber,.08,parent)
 for z in (4.9,32.9):cube(label+'_Rim',(0,sign*.18,z),(19.6,.22,.85),rubber,.08,parent)
 for i in range(9):
  x=(i-4)*1.9
  cube(label+'_RaisedFlute_%02d'%i,(x,outer+sign*.5,18.9),(.38,.35,24.3),blue,.17,parent)
 for x in (-8.8,8.8):
  for z in (6.1,31.7):
   cube(label+'_CornerGuard',(x,outer+sign*.48,z),(2.7,.3,2.7),silver,.65,parent)
   cyl(label+'_Rivet',(x,outer+sign*.69,z),.13,.1,silver,parent)
tray('Rear',False,body); tray('Front',True,lid)
# Interior crossed retention straps in rear cavity.
for angle in (-33,33):
 o=cube('Interior_RetentionStrap',(0,1.0,18.9),(.7,.15,29),mesh,.08); o.rotation_euler[1]=math.radians(angle)
cube('Interior_Buckle',(0,.85,18.9),(1.7,.4,1.6),rubber,.2)
for z in (10,27):cube('Hinge',(-10.35,0,z),(.5,1.2,2.4),silver,.18)
for z in (13,25):cube('Latch',(10.4,-.15,z),(.55,1.8,2),silver,.16)
# Four independently parented wheel assemblies, eight rolling tires.
for x in (-8.6,8.6):
 for y in (-4.2,4.2):
  caster=empty('Caster_%s_%s'%(x,y),(x,y,2.0),body)
  cube('Caster_Fork',(x,y,3.3),(1.8,1.1,2.6),rubber,.3,caster)
  for dy in (-.65,.65):
   cyl('Wheel_Tire',(x,y+dy,1.65),1.65,.65,rubber,caster)
   cyl('Wheel_Hub',(x,y+dy*1.55,1.65),.78,.12,silver,caster)
# Top grip and side grip with raised bridge.
for x in (-3.5,3.5):cube('TopHandle_Mount',(x,1.7,33.5),(1.2,1.6,.5),silver,.2)
cube('Top_CarryHandle',(0,1.7,34),(7.8,1.25,.65),rubber,.3)
cube('Side_CarryHandle',(10.6,2.6,19),(.8,1.2,7),rubber,.35)
# Telescopic assembly: folded by default, animate local Z to extend.
telescope=empty('TelescopicHandle_MOVE_Z',(0,0,0),body)
for x in (-3.1,3.1):cube('Telescopic_Rail',(x,4.8,27),(.55,.6,12),silver,.1,telescope)
cube('Telescopic_Grip',(0,4.8,33.3),(7.4,1.2,.8),rubber,.35,telescope)
cube('Blank_Nameplate',(0,-6.22,28),(4,.2,2.1),silver,.3,lid)
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
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=False
s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100
s.world.color=(.2,.2,.2)
s.render.image_settings.file_format='PNG';s.render.filepath=OUT+'/preview_closed.png'
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/suitcase_skyblue.blend')
bpy.ops.render.render(write_still=True)
lid.rotation_euler.z=math.radians(-115)
s.render.filepath=OUT+'/preview_open.png';bpy.ops.render.render(write_still=True)
print('ASSET_COMPLETE',len(parts))
