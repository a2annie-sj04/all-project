import bpy,math,os,json
from mathutils.bvhtree import BVHTree
from mathutils import Vector
O=os.path.dirname(os.path.abspath(__file__));bpy.ops.wm.open_mainfile(filepath=O+'/Bedroom_v01.blend')
casefile=os.path.dirname(O)+'/suitcase_v05/suitcase_skyblue.blend'
with bpy.data.libraries.load(casefile,link=False) as (src,dst):dst.objects=list(src.objects)
r=next(o for o in dst.objects if o and o.name=='SUITCASE_ROOT_cm');keep={r,*r.children_recursive}
for o in dst.objects:
 if not o:continue
 if o in keep:
  if o.name not in bpy.context.scene.objects:bpy.context.scene.collection.objects.link(o)
 else:bpy.data.objects.remove(o,do_unlink=True)
r.name='REFERENCE_Suitcase_v05_Scale048';r.scale=(.48,)*3;r.location=(-29,26,11.85);r.rotation_euler=(-math.pi/2,0,0)
bpy.data.objects['Lid_Hinge_OPEN_Z'].rotation_euler.z=math.radians(-115)
# Seat the rigid case on the duvet using sampled actual mesh surfaces, not a guessed height.
bpy.context.view_layer.update()
def union_bvh(objects):
 vs=[];fs=[];dg=bpy.context.evaluated_depsgraph_get()
 for o in objects:
  if o.type!='MESH':continue
  ev=o.evaluated_get(dg);me=ev.to_mesh();n=len(vs)
  vs.extend(o.matrix_world@v.co for v in me.vertices);fs.extend(tuple(n+i for i in f.vertices) for f in me.polygons);ev.to_mesh_clear()
 return BVHTree.FromPolygons(vs,fs),vs
bedtree,_=union_bvh([bpy.data.objects['Duvet_DrapedSageLinen'],bpy.data.objects['Duvet_FoldedBackCuff']])
casetree,points=union_bvh(r.children_recursive)
x0,x1=min(p.x for p in points),max(p.x for p in points);y0,y1=min(p.y for p in points),max(p.y for p in points)
clearances=[]
for i in range(81):
 for j in range(81):
  x=x0+(x1-x0)*i/80;y=y0+(y1-y0)*j/80
  c=casetree.ray_cast(Vector((x,y,0)),Vector((0,0,1)))[0];b=bedtree.ray_cast(Vector((x,y,45)),Vector((0,0,-1)))[0]
  if c is not None and b is not None:clearances.append(c.z-b.z)
assert clearances
adjust=min(clearances)-.025;r.location.z-=adjust
open(O+'/case_placement_validation.json','w').write(json.dumps({'uniform_scale':.48,'samples':len(clearances),'vertical_adjustment_cm':-adjust,'minimum_sampled_clearance_cm':.025,'scope':'static mesh ray samples, not animation collision validation'},indent=2))
s=bpy.context.scene;s.camera=bpy.data.objects['CAM_RoomOverview'];s.camera.location=(12,-25,37);s.camera.rotation_euler=(Vector((-33,38,15))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=34
s.render.resolution_x=1100;s.render.resolution_y=900;s.cycles.samples=24;s.render.filepath=O+'/preview_room_with_case.png'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=O+'/Bedroom_with_case_reference.blend');bpy.ops.render.render(write_still=True)
print('REFERENCE_CASE_COMPLETE')
