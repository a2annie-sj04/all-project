import bpy,os,json
from mathutils import Vector
O=os.path.dirname(os.path.abspath(__file__));manifest=json.load(open(O+'/asset_manifest.json'));report=[]
for asset in manifest:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=O+'/'+asset['file']);bpy.context.view_layer.update()
 root=bpy.data.objects.get(asset['name']);assert root,asset['name'];assert root.type=='EMPTY'
 meshes=[o for o in root.children_recursive if o.type=='MESH'];assert len(meshes)>3
 pts=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box]
 b=[(min(p[i] for p in pts),max(p[i] for p in pts)) for i in range(3)]
 dims=[(hi-lo)*100 for lo,hi in b];errors=[abs(dims[i]-asset['size_cm'][i]) for i in range(3)]
 assert max(errors)<.02,(asset['name'],dims,asset['size_cm'])
 assert all(o.parent for o in meshes)
 report.append({'name':asset['name'],'mesh_count':len(meshes),'size_cm':dims,'max_dimension_error_cm':max(errors),'fbx_reimport':'passed'})
open(O+'/export_validation.json','w').write(json.dumps(report,indent=2));print('ALL_FBX_PASSED',len(report))
