import bpy,os,json
from mathutils import Vector
O=os.path.dirname(os.path.abspath(__file__));expected=json.load(open(O+'/dimensions.json'))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=O+'/TShirt_Folded_Realism_v02_cm.fbx');bpy.context.view_layer.update()
r=bpy.data.objects.get('TShirt_Folded_Realism_v02_cm');assert r
for name in ('FrontBody_ThinJersey','BackBody_ThinJersey','Collar_FlatRibKnitBinding','SoftSewnSideReturn','ChestPocket_ThinCloth'):
 o=bpy.data.objects.get(name);assert o and o.parent==r;assert o.data.uv_layers.active
pts=[o.matrix_world@Vector(v) for o in r.children_recursive if o.type=='MESH' for v in o.bound_box];size=[(max(p[i] for p in pts)-min(p[i] for p in pts))*100 for i in range(3)]
assert max(abs(size[i]-expected['size'][i]) for i in range(3))<.02
assert size[0]<10 and size[1]<11 and size[2]<1.2
image_names=[i.name for i in bpy.data.images if 'Cotton_' in i.name];assert len(image_names)>=3
report={'fbx_reimport':'passed','size_cm':size,'mesh_parts':len([o for o in r.children_recursive if o.type=='MESH']),'pbr_images':image_names,'scope':'Blender import and dimensions only; no Max/Unreal or cloth simulation validation'}
open(O+'/validation.json','w').write(json.dumps(report,indent=2));print(report)
