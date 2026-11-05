import bpy,os,math,json
from mathutils import Vector
O=os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=os.path.dirname(O)+'/suitcase_v05/suitcase_skyblue.blend')
# Hide only packing-bay belts for this layout study; no suitcase source is changed.
for o in list(bpy.data.objects):
 if o.name.startswith(('Rear_XCompressionBelt','Belt_','Buckle_')):o.hide_render=True;o.hide_set(True)
with bpy.data.libraries.load(O+'/travel_props_studio.blend',link=False) as (src,dst):
 dst.objects=[n for n in src.objects if n.startswith(('PROP_','TShirt_','Pants_','Sneaker_','Pouch_','Cap_'))]
for o in dst.objects:
 if o and o.name not in bpy.context.scene.objects:bpy.context.scene.collection.objects.link(o)
layout={'PROP_Folded_Pants_cm':(0,4.97,25.0),'PROP_Folded_TShirt_cm':(0,3.6,25.0),'PROP_Sneaker_Left_cm':(-6.0,4.97,11.3),'PROP_Sneaker_Right_cm':(-2.0,4.97,11.3),'PROP_ToiletryPouch_cm':(4.2,4.97,8.7),'PROP_BaseballCap_cm':(4.7,4.97,15.8)}
for name,co in layout.items():
 r=bpy.data.objects[name];r.location=co;r.rotation_euler=(math.pi/2,0,0)
bpy.context.view_layer.update();bounds={}
for name in layout:
 r=bpy.data.objects[name];points=[]
 for o in r.children_recursive:
  if o.type!='MESH':continue
  ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());points.extend(o.matrix_world@Vector(v) for v in ev.bound_box)
 b=[(min(p[i] for p in points),max(p[i] for p in points)) for i in range(3)];bounds[name]=b
 # Conservative rectangular packing envelope, inside curved walls at the chosen locations.
 assert b[0][0]>=-8.8 and b[0][1]<=8.8,(name,b)
 assert b[1][0]>=.7 and b[1][1]<=5.2,(name,b)
 assert b[2][0]>=6.3 and b[2][1]<=31.3,(name,b)
checks=[]
for i,a in enumerate(layout):
 for b in list(layout)[i+1:]:
  overlap=[min(bounds[a][k][1],bounds[b][k][1])-max(bounds[a][k][0],bounds[b][k][0]) for k in range(3)]
  assert not all(v>.025 for v in overlap),(a,b,overlap)
  checks.append({'a':a,'b':b,'overlap_cm':overlap})
open(O+'/packing_validation.json','w').write(json.dumps({'units':'cm','bounds':bounds,'pairwise_checks':checks,'packing_envelope':'passed','belts':'hidden for layout study','scope':'AABB clearance, not soft-body or exact mesh collision simulation'},indent=2))
lid=bpy.data.objects['Lid_Hinge_OPEN_Z'];lid.rotation_euler.z=math.radians(-115)
s=bpy.context.scene;s.camera=bpy.data.objects['Product_Preview'];s.camera.location=(38,-83,63);s.camera.rotation_euler=(Vector((-8,1,18))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=62
s.render.resolution_x=1100;s.render.resolution_y=1000;s.cycles.samples=24;s.render.filepath=O+'/preview_packing.png'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=O+'/packing_layout.blend');bpy.ops.render.render(write_still=True)
print('PACKING_COMPLETE')
