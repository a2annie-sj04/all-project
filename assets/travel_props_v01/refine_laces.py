import bpy,os,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=os.path.dirname(os.path.abspath(__file__));bpy.ops.wm.open_mainfile(filepath=O+'/travel_props_studio.blend')
for label in ('Left','Right'):
 root=bpy.data.objects['PROP_Sneaker_'+label+'_cm'];upper=bpy.data.objects['Sneaker_'+label+'_HollowUpper'];tree=BVHTree.FromPolygons([v.co.copy() for v in upper.data.vertices],[tuple(p.vertices) for p in upper.data.polygons])
 knot=bpy.data.objects['Sneaker_'+label+'_TiedKnot'];hit=tree.ray_cast(Vector((0,-.22,8)),Vector((0,0,-1)))[0];assert hit
 dz=hit.z+.15-knot.location.z;dy=-.70
 for obj in root.children_recursive:
  if obj.name.startswith(tuple('Sneaker_'+label+'_'+s for s in ('BowLoop','LaceTail','Aglet','KnotFeed'))):
   for v in obj.data.vertices:v.co.y+=dy;v.co.z+=dz
 knot.location.y+=dy;knot.location.z+=dz
 pos=root.location.copy();root.location=(0,0,0);bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
 for o in root.children_recursive:o.select_set(True)
 bpy.context.view_layer.objects.active=root;fn='Sneaker_'+label+'_cm'
 bpy.ops.export_scene.fbx(filepath=O+'/'+fn+'.fbx',use_selection=True,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',add_leaf_bones=False,bake_anim=False,path_mode='COPY',embed_textures=True)
 bpy.ops.export_scene.gltf(filepath=O+'/'+fn+'.glb',use_selection=True,export_apply=True)
 pts=[o.matrix_world@Vector(v) for o in root.children_recursive if o.type=='MESH' for v in o.evaluated_get(bpy.context.evaluated_depsgraph_get()).bound_box];b=[(min(p[i] for p in pts),max(p[i] for p in pts)) for i in range(3)]
 manifest=json.load(open(O+'/asset_manifest.json'))
 for a in manifest:
  if a['name']==root.name:a['bounds_cm']=b;a['size_cm']=[hi-lo for lo,hi in b]
 open(O+'/asset_manifest.json','w').write(json.dumps(manifest,indent=2));root.location=pos
bpy.ops.wm.save_as_mainfile(filepath=O+'/travel_props_studio.blend');s=bpy.context.scene;s.cycles.samples=24;cam=s.camera;s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.filepath=O+'/preview_all.png';bpy.ops.render.render(write_still=True)
roots=[o for o in bpy.data.objects if o.name.startswith('PROP_')]
for label in ('Left','Right'):
 r=bpy.data.objects['PROP_Sneaker_'+label+'_cm']
 for other in roots:
  for o in [other]+list(other.children_recursive):o.hide_render=other!=r
 pos=r.location.copy();cam.location=pos+Vector((12,-18,21));cam.rotation_euler=(pos+Vector((0,0,1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=13;s.render.resolution_x=900;s.render.resolution_y=900;s.render.filepath=O+'/preview_Sneaker_'+label+'_cm.png';bpy.ops.render.render(write_still=True)
print('LACES_FINISHED')
