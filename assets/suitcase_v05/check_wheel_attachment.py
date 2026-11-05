import bpy,os,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
out=os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=out+'/suitcase_skyblue.blend');bpy.context.view_layer.update()
def tree(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
 t=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]);ev.to_mesh_clear();return t
results={}
for tag in ('L_Front','R_Front','L_Rear','R_Rear'):
 socket=bpy.data.objects['WheelSocket_'+tag]
 shell=bpy.data.objects[('Front' if tag.endswith('Front') else 'Rear')+'_ContinuousRoundedShell']
 n=len(tree(socket).overlap(tree(shell)))
 assert n>0,('detached socket',tag)
 names=['WheelSocket_','WheelSocketGasket_','SwivelBearing_','ForkBridge_','ForkCheek_','WheelAxle_','WheelTire_']
 # These adjacent pieces must have intersecting world bounds, with no vertical gap.
 def bounds(o):
  ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());pts=[o.matrix_world@Vector(v) for v in ev.bound_box]
  return [(min(p[i] for p in pts),max(p[i] for p in pts)) for i in range(3)]
 objs=[bpy.data.objects[name+tag] for name in names]
 for a,b in zip(objs,objs[1:]):
  aa,bb=bounds(a),bounds(b)
  assert all(min(aa[i][1],bb[i][1])-max(aa[i][0],bb[i][0])>=-1e-5 for i in range(3)),(a.name,b.name)
 results[tag]={'socket_shell_triangle_intersections':n,'adjacent_component_bounds_overlap':True}
open(out+'/wheel_attachment_validation.json','w').write(json.dumps(results,indent=2));print(results)
