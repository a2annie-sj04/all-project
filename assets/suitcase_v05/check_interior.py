import bpy,os,json,math
from mathutils import Vector
out=os.path.dirname(os.path.abspath(__file__))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=out+'/suitcase_skyblue_cm.fbx');bpy.context.view_layer.update()
required=['Front_ZippedDividerPanel','Front_UpperDiamondMeshPocket','Rear_XCompressionBelt_0','Rear_XCompressionBelt_1','Divider_IndividualZipperTeeth','Pocket_ZipTeeth','Buckle_CentreTongue','OrganizerPocket_0','OrganizerPocket_1']
for name in required:
 o=bpy.data.objects.get(name);assert o and o.type=='MESH',name
 if any(m and m.name.startswith(('Navy_Lining','Packing_Straps')) for m in o.data.materials): assert o.data.uv_layers.active is not None,name
assert len(bpy.data.objects['Front_UpperDiamondMeshPocket'].data.polygons)>500
lid=bpy.data.objects['Lid_Hinge_OPEN_Z'];divider=bpy.data.objects['Interior_Divider_MOVE_WITH_LID']
assert divider.parent==lid
pocket=bpy.data.objects['Front_UpperDiamondMeshPocket'];assert pocket.parent==divider
anchor_count=len([o for o in bpy.data.objects if o.name.startswith('Belt_AnchorPatch_')]);assert anchor_count==4
initial=pocket.matrix_world.translation.copy()
lid.rotation_euler.z=math.radians(-115);bpy.context.view_layer.update()
assert (pocket.matrix_world.translation-initial).length>.03
images=[i for i in bpy.data.images if i.name.startswith(('lining_weave','webbing_weave'))]
assert len(images)>=2
r={'required_interior_meshes':len(required),'belt_wall_anchors':anchor_count,'mesh_pocket_has_real_lattice':True,'divider_and_pocket_follow_lid':True,'fabric_images_imported':len(images),'fbx_reimport':'passed','host':'Blender 4.3.2'}
open(out+'/interior_validation.json','w').write(json.dumps(r,indent=2));print(r)
