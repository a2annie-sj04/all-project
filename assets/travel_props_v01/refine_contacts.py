import bpy,os,math,bmesh,json
from mathutils import Vector
O=os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=os.environ.get('PROPS_BASE',O+'/travel_props_studio.blend'))
# Correct details found in close-up inspection: textile contacts and a real neckline opening.
pants=bpy.data.objects['PROP_Folded_Pants_cm'];shirt=bpy.data.objects['PROP_Folded_TShirt_cm'];pouch=bpy.data.objects['PROP_ToiletryPouch_cm']
bpy.data.objects['Pants_Waistband'].location.z-=.07
for o in pants.children_recursive:
 if o.name.startswith('Pants_BeltLoop'):o.location.z-=.07
bpy.data.objects['Pants_Button'].location.z-=.11
bpy.data.objects['Pouch_WovenLabel'].location.y-=.04
for o in pouch.children_recursive:
 if o.name.startswith('Pouch_LabelStitch'):o.location.y-=.05
# Remove upper shirt faces within an ellipse; lower folded layer remains visible through it.
main=bpy.data.objects['TShirt_MainFold'];bm=bmesh.new();bm.from_mesh(main.data)
faces=[f for f in bm.faces if ((f.calc_center_median().x/1.20)**2+((f.calc_center_median().y-3.30)/.78)**2)<1]
bmesh.ops.delete(bm,geom=faces,context='FACES');bm.to_mesh(main.data);bm.free()
# Replace the previously decorative U with a complete bound collar seated on the cloth surface.
for name in ('TShirt_RibbedCollar','TShirt_NecklineShadow'):
 o=bpy.data.objects.get(name)
 if o:bpy.data.objects.remove(o,do_unlink=True)
def tshirt_z(x,y):
 edge=math.sin(math.pi*(x/9.1+.5))*math.sin(math.pi*(y/10+.5))
 return .30+.66*(.66+.34*edge)+.045*edge*math.sin(x*3+y*1.3)+.025*edge*math.cos(y*4-x)
cu=bpy.data.curves.new('Neck_RibbedBinding','CURVE');cu.dimensions='3D';cu.bevel_depth=.10;cu.bevel_resolution=4;sp=cu.splines.new('POLY');sp.points.add(95)
for i,p in enumerate(sp.points):
 t=i*math.tau/96;x=1.26*math.cos(t);y=3.3+.86*math.sin(t);p.co=(x,y,tshirt_z(x,y)+.015,1)
sp.use_cyclic_u=True;o=bpy.data.objects.new('TShirt_RibbedCollar',cu);bpy.context.scene.collection.objects.link(o);o.data.materials.append(bpy.data.materials['Cream_Cotton'])
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');o=bpy.context.object;o.parent=shirt;o.location=(0,0,0)
# Label sewn to the back of neck instead of spanning the opening.
bpy.data.objects['TShirt_NeckLabel'].location.y=4.28;bpy.data.objects['TShirt_NeckLabel'].location.z=.79
# Fit the visor back edge along the crown's actual elliptical lower edge.
cap=bpy.data.objects['PROP_BaseballCap_cm']
for obj in cap.children_recursive:
 if not obj.name.startswith(('Cap_CurvedVisor','Cap_VisorConcentricStitch')):continue
 for vertex in obj.data.vertices:
  x,y,z=vertex.co;u=max(-.99999,min(.99999,x/3.08));q=math.sqrt(max(0,1-u*u))
  oldback=-.65-1.95*q;oldfront=-.8-4.05*q
  v=max(0,min(1,(y-oldback)/(oldfront-oldback))) if abs(oldfront-oldback)>.0001 else 0
  newback=.45-3.15*math.sqrt(max(0,1-(x/3.1)**2))+.20;newfront=newback-2.10*q
  vertex.co.y=newback*(1-v)+newfront*v
  vertex.co.z=z+.03-.21*(1-u*u)+.01*v
# A central tied knot and feeding strands connect the loops to the final eyelet row.
for name in ('PROP_Sneaker_Left_cm','PROP_Sneaker_Right_cm'):
 shoe=bpy.data.objects[name];label='Left' if 'Left' in name else 'Right'
 loops=[o for o in shoe.children_recursive if o.name.startswith('Sneaker_'+label+'_BowLoop')]
 first=loops[0];cz=sum(v.co.z for v in first.data.vertices)/len(first.data.vertices)
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=1)
 knot=bpy.context.object;knot.name='Sneaker_'+label+'_TiedKnot';knot.scale=(.22,.18,.13);knot.data.materials.append(bpy.data.materials['Cotton_Laces']);knot.parent=shoe;knot.location=(0,.48,cz)
 upper=bpy.data.objects['Sneaker_'+label+'_HollowUpper']
 from mathutils.bvhtree import BVHTree
 tree=BVHTree.FromPolygons([v.co.copy() for v in upper.data.vertices],[tuple(p.vertices) for p in upper.data.polygons])
 for side in (-1,1):
  hit=tree.ray_cast(Vector((side*.63,.45,8)),Vector((0,0,-1)))[0]
  cu=bpy.data.curves.new('KnotFeed','CURVE');cu.dimensions='3D';cu.bevel_depth=.046;cu.bevel_resolution=2;sp=cu.splines.new('POLY');sp.points.add(12)
  for j,pt in enumerate(sp.points):
   t=j/12;pt.co=(side*.63*(1-t),.45+.03*t,(hit.z+.12)*(1-t)+cz*t,1)
  feed=bpy.data.objects.new('Sneaker_'+label+'_KnotFeed',cu);bpy.context.scene.collection.objects.link(feed);feed.data.materials.append(bpy.data.materials['Cotton_Laces'])
  bpy.ops.object.select_all(action='DESELECT');feed.select_set(True);bpy.context.view_layer.objects.active=feed;bpy.ops.object.convert(target='MESH');feed=bpy.context.object;feed.parent=shoe;feed.location=(0,0,0)
# Gentle mirrored toe/arch offsets distinguish the left and right shoes.
for name,sign in [('PROP_Sneaker_Left_cm',1),('PROP_Sneaker_Right_cm',-1)]:
 shoe=bpy.data.objects[name]
 for obj in shoe.children_recursive:
  if obj.type!='MESH':continue
  # Transform all connected details together, including hardware and laces.
  local=obj.matrix_local.copy();inv=local.inverted()
  for v in obj.data.vertices:
   co=local@v.co;co.x+=sign*.11*math.exp(-((co.y+1.0)/2.5)**2);v.co=inv@co
roots=[bpy.data.objects[n] for n in ('PROP_Folded_TShirt_cm','PROP_Folded_Pants_cm','PROP_Sneaker_Left_cm','PROP_Sneaker_Right_cm','PROP_ToiletryPouch_cm','PROP_BaseballCap_cm')]
manifest=[]
for r in roots:
 pos=r.location.copy();r.location=(0,0,0);bpy.context.view_layer.update()
 bpy.ops.object.select_all(action='DESELECT');r.select_set(True)
 for o in r.children_recursive:o.select_set(True)
 bpy.context.view_layer.objects.active=r;fn=r.name.replace('PROP_','')
 bpy.ops.export_scene.fbx(filepath=O+'/'+fn+'.fbx',use_selection=True,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',add_leaf_bones=False,bake_anim=False,path_mode='COPY',embed_textures=True)
 bpy.ops.export_scene.gltf(filepath=O+'/'+fn+'.glb',use_selection=True,export_apply=True)
 pts=[o.matrix_world@Vector(v) for o in r.children_recursive if o.type=='MESH' for v in o.evaluated_get(bpy.context.evaluated_depsgraph_get()).bound_box]
 b=[(min(v[i] for v in pts),max(v[i] for v in pts)) for i in range(3)];manifest.append({'name':r.name,'file':fn+'.fbx','bounds_cm':b,'size_cm':[hi-lo for lo,hi in b]});r.location=pos
open(O+'/asset_manifest.json','w').write(json.dumps(manifest,indent=2))
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=O+'/travel_props_studio.blend')
s=bpy.context.scene;s.cycles.samples=24;s.render.resolution_x=1200;s.render.resolution_y=1000;cam=s.camera;s.render.filepath=O+'/preview_all.png';bpy.ops.render.render(write_still=True)
for r in roots:
 for other in roots:
  for o in [other]+list(other.children_recursive):o.hide_render=(other!=r)
 pos=r.location.copy();cam.location=pos+Vector((12,-18,21));cam.rotation_euler=(pos+Vector((0,0,1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=13
 s.render.resolution_x=900;s.render.resolution_y=900;s.render.filepath=O+'/preview_'+r.name.replace('PROP_','')+'.png';bpy.ops.render.render(write_still=True)
print('CONTACT_REFINEMENT_COMPLETE')
