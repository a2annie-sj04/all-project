import bpy,os,math,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=os.path.dirname(os.path.abspath(__file__));bpy.ops.wm.open_mainfile(filepath=O+'/travel_props_studio.blend')
root=bpy.data.objects['PROP_Folded_Pants_cm'];top=bpy.data.objects['Pants_FoldedLegTop']
# Two folded leg channels, a crotch-to-hem valley, and compressed fabric ripples.
for v in top.data.vertices:
 x,y,z=v.co;mask=max(0,min(1,(2-y)/2));valley=math.exp(-(x/.30)**2)*mask
 v.co.z-=.14*valley
 v.co.z+=.065*math.sin(y*2.7+x*.7)*math.exp(-((abs(x)-2.3)/1.0)**2)*mask
 if y< -4.25:v.co.y+=.23*math.exp(-(x/.30)**2)*max(0,(-y-4.25)/.8)
# Re-seat stitches on the shaped fabric; no thread hovering across the new creases.
bpy.context.view_layer.update();ev=top.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();tree=BVHTree.FromPolygons([v.co.copy() for v in me.vertices],[tuple(p.vertices) for p in me.polygons]);ev.to_mesh_clear()
for o in root.children_recursive:
 if o.name.startswith(('Pants_DoubleHem','Pants_FlySeam','Pants_PocketOpening')):
  for v in o.data.vertices:
   x,y,z=v.co;hit=tree.ray_cast(Vector((x,y,4)),Vector((0,0,-1)))[0]
   if hit is not None:v.co.z=hit.z+.014
# Narrow leg-fold seam makes the stacked pants read distinctly from a flat panel.
cu=bpy.data.curves.new('FoldedLegSeam','CURVE');cu.dimensions='3D';cu.bevel_depth=.016;cu.bevel_resolution=2;sp=cu.splines.new('POLY');sp.points.add(39)
for i,pt in enumerate(sp.points):
 y=-4.50+i*5.6/39;hit=tree.ray_cast(Vector((.06,y,4)),Vector((0,0,-1)))[0];pt.co=(.06,y,hit.z+.016,1)
o=bpy.data.objects.new('Pants_CentralFoldSeam',cu);bpy.context.scene.collection.objects.link(o);o.data.materials.append(bpy.data.materials['Denim_Indigo']);bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');o=bpy.context.object;o.parent=root;o.location=(0,0,0)
pos=root.location.copy();root.location=(0,0,0);bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
for o in root.children_recursive:o.select_set(True)
bpy.context.view_layer.objects.active=root
bpy.ops.export_scene.fbx(filepath=O+'/Folded_Pants_cm.fbx',use_selection=True,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',add_leaf_bones=False,bake_anim=False,path_mode='COPY',embed_textures=True)
bpy.ops.export_scene.gltf(filepath=O+'/Folded_Pants_cm.glb',use_selection=True,export_apply=True)
pts=[o.matrix_world@Vector(v) for o in root.children_recursive if o.type=='MESH' for v in o.evaluated_get(bpy.context.evaluated_depsgraph_get()).bound_box]
b=[(min(p[i] for p in pts),max(p[i] for p in pts)) for i in range(3)];manifest=json.load(open(O+'/asset_manifest.json'))
for a in manifest:
 if a['name']==root.name:a['bounds_cm']=b;a['size_cm']=[hi-lo for lo,hi in b]
open(O+'/asset_manifest.json','w').write(json.dumps(manifest,indent=2));root.location=pos
bpy.ops.wm.save_as_mainfile(filepath=O+'/travel_props_studio.blend');s=bpy.context.scene;cam=s.camera;s.cycles.samples=24;s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.filepath=O+'/preview_all.png';bpy.ops.render.render(write_still=True)
for r in [o for o in bpy.data.objects if o.name.startswith('PROP_')]:
 for o in [r]+list(r.children_recursive):o.hide_render=r!=root
cam.location=pos+Vector((12,-18,21));cam.rotation_euler=(pos+Vector((0,0,1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=13;s.render.resolution_x=900;s.render.resolution_y=900;s.render.filepath=O+'/preview_Folded_Pants_cm.png';bpy.ops.render.render(write_still=True)
print('CLOTH_REFINED')
