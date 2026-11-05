import bpy,os
from mathutils import Vector
out=os.path.dirname(os.path.abspath(__file__))
for file in ('suitcase_skyblue.blend','suitcase_interior_open.blend'):
 bpy.ops.wm.open_mainfile(filepath=out+'/'+file)
 for prefix,sign,parent in [('Rear',1,bpy.data.objects['Body_Assembly']),('Front',-1,bpy.data.objects['Lid_Hinge_OPEN_Z'])]:
  # Coordinates are defined in the closed suitcase frame, then transformed with the lid.
  for xx in (-7.8,7.8):
   bpy.ops.mesh.primitive_cube_add(size=1);o=bpy.context.object;o.name=prefix+'_PaddedWheelHousing'
   o.dimensions=(2.5,4.2,1.2);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
   mod=o.modifiers.new('PaddedSoftEdges','BEVEL');mod.width=.40;mod.segments=5;o.modifiers.new('Weighted_Normals','WEIGHTED_NORMAL')
   o.data.materials.append(bpy.data.materials['Navy_Lining'])
   # Hinge origin is (-10.1,0,18.9); preserve the designed closed-world attachment.
   o.parent=parent;o.location=(xx+10.1,sign*3.2,5.9-18.9) if prefix=='Front' else (xx,sign*3.2,5.9)
   for poly in o.data.polygons:
    axis=max(range(3),key=lambda k:abs(poly.normal[k]));axes=[k for k in range(3) if k!=axis]
    for li in poly.loop_indices:
     v=o.data.vertices[o.data.loops[li].vertex_index].co;o.data.uv_layers.active.data[li].uv=(v[axes[0]]/20,v[axes[1]]/20)
 bpy.ops.wm.save_as_mainfile(filepath=out+'/'+file)
 if file=='suitcase_interior_open.blend':
  s=bpy.context.scene
  s.camera.location=(40,-90,60);s.camera.rotation_euler=(Vector((-9,0,18))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=62
  s.render.filepath=out+'/preview_open.png';bpy.ops.render.render(write_still=True)
  s.camera.location=(0,-70,30);s.camera.rotation_euler=(Vector((0,3,19))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=34
  s.render.filepath=out+'/preview_main_interior.png';bpy.ops.render.render(write_still=True)
print('HOUSING_FINISHED')
