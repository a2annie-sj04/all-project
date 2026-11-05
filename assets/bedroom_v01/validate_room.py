import bpy,os,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
O=os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=O+'/Bedroom_v01.blend');s=bpy.context.scene
s.render.resolution_x=256;s.render.resolution_y=192;s.render.resolution_percentage=100
layout=json.load(open(O+'/display_layout_reference.json'));projection=[]
for info in layout['screens']:
 cam=bpy.data.objects[info['camera']];pts=[info['bottom_left'],info['bottom_right'],info['top_left']]
 actual=[world_to_camera_view(s,cam,Vector(p)) for p in pts];expected=[(0,0),(1,0),(0,1)]
 errors=[max(abs(a.x-e[0]),abs(a.y-e[1])) for a,e in zip(actual,expected)]
 assert max(errors)<.0001,(info['name'],[list(a) for a in actual])
 projection.append({'screen':info['name'],'max_normalized_corner_error':max(errors)})
# Geometric surface check for the visible bedding defect found in the first render.
def bvh(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
 tree=BVHTree.FromPolygons([o.matrix_world@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons]);ev.to_mesh_clear();return tree
mattress=bpy.data.objects['Bed_Mattress'];duvet=bpy.data.objects['Duvet_DrapedSageLinen']
intersections=len(bvh(mattress).overlap(bvh(duvet)));assert intersections==0,intersections
# PBR source images must be present and packed in the source file.
packed=[i.name for i in bpy.data.images if i.packed_file];assert len(packed)>=20
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=O+'/Bedroom_v01_cm.fbx');bpy.context.view_layer.update();r=bpy.data.objects.get('ROOM_ROOT_cm');assert r
for name in ('Bed_Assembly','Desk_Assembly','Chair_Assembly','Nightstand_Assembly','Window_Assembly','Curtains_Assembly','Plant_Assembly'):
 assert bpy.data.objects.get(name) and bpy.data.objects[name].parent==r,name
meshes=[o for o in r.children_recursive if o.type=='MESH'];assert len(meshes)>300
assert not any(o.type in ('CAMERA','LIGHT') for o in r.children_recursive)
# Bed footprint must retain its designed 36.5 x 42.5cm size after import.
frame=bpy.data.objects['Bed_TimberFrame'];points=[frame.matrix_world@Vector(v) for v in frame.bound_box];dims=[(max(p[i] for p in points)-min(p[i] for p in points))*bpy.context.scene.unit_settings.scale_length*100 for i in range(3)]
assert abs(dims[0]-36.5)<.02 and abs(dims[1]-42.5)<.02,dims
report={'duvet_mattress_triangle_intersections':intersections,'fbx_reimport':'passed','mesh_count':len(meshes),'bed_frame_dimensions_cm':dims,'source_packed_images':len(packed),'offaxis_camera_corner_projection':projection,'unreal_or_hardware_tested':False}
open(O+'/validation.json','w').write(json.dumps(report,indent=2));print(report)
