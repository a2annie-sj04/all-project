import bpy,os,json
O=os.path.dirname(os.path.abspath(__file__));bpy.ops.wm.open_mainfile(filepath=O+'/Bedroom_v01.blend')
bpy.ops.mesh.primitive_cube_add(size=1,location=(-32,32,48.35));o=bpy.context.object;o.name='Ceiling_Panel_DisplayOnly';o.dimensions=(64,64,.7);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(bpy.data.materials['Warm_Plaster'])
bpy.context.view_layer.update();w=o.matrix_world.copy();o.parent=bpy.data.objects['Architecture'];o.matrix_world=w;o.hide_render=True
uv=o.data.uv_layers.active
for f in o.data.polygons:
 for li in f.loop_indices:
  v=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(v.x/8,v.y/8)
r=bpy.data.objects['ROOM_ROOT_cm'];bpy.ops.object.select_all(action='DESELECT');r.select_set(True)
for c in r.children_recursive:
 if c.type in ('MESH','EMPTY'):c.select_set(True)
bpy.context.view_layer.objects.active=r
bpy.ops.export_scene.fbx(filepath=O+'/Bedroom_v01_cm.fbx',use_selection=True,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',add_leaf_bones=False,bake_anim=False,path_mode='COPY',embed_textures=True)
bpy.ops.export_scene.gltf(filepath=O+'/Bedroom_v01.glb',use_selection=True,export_apply=True)
bpy.ops.wm.save_as_mainfile(filepath=O+'/Bedroom_v01.blend')
s=bpy.context.scene;s.render.resolution_x=256;s.render.resolution_y=192;s.cycles.samples=48;o.hide_render=False
for label in ('Left','Right'):
 s.camera=bpy.data.objects['DISPLAY_'+label+'_OffAxis'];s.render.filepath=O+'/display_'+label.lower()+'_256x192.png';bpy.ops.render.render(write_still=True)
p=O+'/display_layout_reference.json';d=json.load(open(p));d['coordinate_system']='Blender source coordinates, right-handed Z-up; Unreal axis mapping requires checking after import';open(p,'w').write(json.dumps(d,indent=2))
print('CEILING_COMPLETE')
