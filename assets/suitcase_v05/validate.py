import bpy, math, json, os
from mathutils import Vector
out=os.path.dirname(os.path.abspath(__file__))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=out+'/suitcase_skyblue_cm.fbx')
bpy.context.view_layer.update()
lid=bpy.data.objects['Lid_Hinge_OPEN_Z']
casters=[o for o in bpy.data.objects if o.name.startswith('Caster_')]
front=[o for o in casters if o.parent==lid];rear=[o for o in casters if o.parent and o.parent.name=='Body_Assembly']
assert len(front)==2 and len(rear)==2
before={o.name:o.matrix_world.translation.copy() for o in casters}
local={o.name:o.matrix_local.copy() for o in front}
lid.rotation_euler.z=math.radians(-115);bpy.context.view_layer.update()
for o in front:
 assert (o.matrix_world.translation-before[o.name]).length>.03
 print('LOCAL_DELTA',o.name,(o.matrix_local.translation-local[o.name].translation).length); assert (o.matrix_local.translation-local[o.name].translation).length<1e-4
for o in rear:assert (o.matrix_world.translation-before[o.name]).length<1e-6
report={'fbx_reimport':'passed','front_casters_follow_lid':len(front),'rear_casters_stay_with_body':len(rear),'lid_test_degrees':-115,'tested_in':'Blender 4.3.2; not 3ds Max or Unreal'}
open(out+'/validation.json','w').write(json.dumps(report,indent=2))
print(report)
