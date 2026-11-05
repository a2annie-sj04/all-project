import bpy,os
out=os.path.dirname(os.path.abspath(__file__))
for filename in ('suitcase_skyblue.blend','suitcase_interior_open.blend'):
 bpy.ops.wm.open_mainfile(filepath=out+'/'+filename)
 for name in ('Navy_Lining','Packing_Straps'):
  m=bpy.data.materials[name];nodes=m.node_tree.nodes
  tex=next(n for n in nodes if n.type=='TEX_IMAGE');uv=next(n for n in nodes if n.type=='TEX_COORD')
  m.node_tree.links.new(uv.outputs['UV'],tex.inputs['Vector'])
 for o in bpy.data.objects:
  if o.type=='MESH' and any(m and m.name in ('Navy_Lining','Packing_Straps') for m in o.data.materials):
   for uv in o.data.uv_layers.active.data:uv.uv*=8
 bpy.ops.file.pack_all()
 if filename=='suitcase_skyblue.blend':
  bpy.ops.object.select_all(action='DESELECT');root=bpy.data.objects['SUITCASE_ROOT_cm']
  root.select_set(True)
  for o in root.children_recursive:o.select_set(True)
  bpy.context.view_layer.objects.active=root
  bpy.ops.export_scene.fbx(filepath=out+'/suitcase_skyblue_cm.fbx',use_selection=True,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',add_leaf_bones=False,bake_anim=False,path_mode='COPY',embed_textures=True)
  bpy.ops.export_scene.gltf(filepath=out+'/suitcase_skyblue.glb',use_selection=True,export_apply=True)
 bpy.ops.wm.save_as_mainfile(filepath=out+'/'+filename)
print('PORTABLE_COMPLETE')
