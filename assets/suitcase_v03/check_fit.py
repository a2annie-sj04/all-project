import bpy,os,json
from mathutils.bvhtree import BVHTree
out=os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=out+'/suitcase_skyblue.blend')
bpy.context.view_layer.update()
report={}
for prefix in ('Front','Rear'):
 vs=[];fs=[]
 for suffix in ('_ContinuousRoundedShell','_Face'):
  o=bpy.data.objects[prefix+suffix];dg=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(dg);m=ev.to_mesh();n=len(vs)
  vs.extend(o.matrix_world@v.co for v in m.vertices)
  fs.extend(tuple(n+i for i in p.vertices) for p in m.polygons);ev.to_mesh_clear()
 tree=BVHTree.FromPolygons(vs,fs)
 guards=[o for o in bpy.data.objects if o.name.startswith(prefix+'_FittedCornerGuard')]
 distances=[tree.find_nearest(o.matrix_world@v.co)[3] for o in guards for v in o.data.vertices]
 report[prefix]={'guard_count':len(guards),'max_skin_gap_cm':max(distances)}
 assert len(guards)==4
 assert max(distances)<.06,report
open(out+'/corner_fit_validation.json','w').write(json.dumps(report,indent=2));print(report)
