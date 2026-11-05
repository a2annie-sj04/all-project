import bpy,math,os,random,json
from mathutils import Vector
O=os.path.dirname(os.path.abspath(__file__));os.makedirs(O+'/textures',exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=.01
root=bpy.data.objects.new('TShirt_Folded_Realism_v02_cm',None);s.collection.objects.link(root)
def mat(name,c,rough):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;m.diffuse_color=(*c,1);return m
cotton=mat('Cotton_Jersey_OffWhite',(.65,.61,.54),.82);rib=mat('Cotton_RibBinding',(.61,.57,.50),.85);thread=mat('Cotton_SewingThread',(.51,.47,.40),.87);labelmat=mat('WovenLabel',(.70,.68,.61),.9);ink=mat('Label_Print',(.12,.14,.14),.9)
# Portable, seamless fine-knit base color / tangent normal / roughness images.
N=512;buffers={k:[] for k in ('BaseColor','Normal','Roughness')};rng=random.Random(711)
def height(x,y):
 a=math.tau*x/16;b=math.tau*y/16
 return .55*math.cos(b+.55*math.sin(a))+.22*math.cos(a)+.12*math.cos(2*b-a)
for yy in range(N):
 for xx in range(N):
  h=height(xx,yy);grain=rng.uniform(-.012,.012)
  buffers['BaseColor'].extend((.65*(1+.025*h+grain),.61*(1+.025*h+grain),.54*(1+.025*h+grain),1))
  dx=(height(xx+1,yy)-height(xx-1,yy))*.19;dy=(height(xx,yy+1)-height(xx,yy-1))*.19;n=Vector((-dx,-dy,1)).normalized()
  buffers['Normal'].extend(((n.x+1)/2,(n.y+1)/2,(n.z+1)/2,1))
  r=.80+.035*h+grain;buffers['Roughness'].extend((r,r,r,1))
images={}
for key,pixels in buffers.items():
 im=bpy.data.images.new('Cotton_'+key,width=N,height=N)
 if key!='BaseColor':im.colorspace_settings.name='Non-Color'
 im.pixels=pixels;im.filepath_raw=O+'/textures/Cotton_'+key+'.png';im.file_format='PNG';im.save();images[key]=im
for m in (cotton,rib):
 nodes=m.node_tree.nodes;links=m.node_tree.links;p=nodes.get('Principled BSDF');p.inputs['Sheen Weight'].default_value=.22;p.inputs['Sheen Roughness'].default_value=.75
 for key in images:
  tex=nodes.new('ShaderNodeTexImage');tex.image=images[key];tex.label=key
  if key=='BaseColor':links.new(tex.outputs['Color'],p.inputs['Base Color'])
  elif key=='Roughness':links.new(tex.outputs['Color'],p.inputs['Roughness'])
  else:
   nm=nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.42;links.new(tex.outputs['Color'],nm.inputs['Color']);links.new(nm.outputs['Normal'],p.inputs['Normal'])

def mesh(name,vs,fs,material,thick=.0):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);s.collection.objects.link(o);o.data.materials.append(material);o.parent=root
 uv=me.uv_layers.new(name='CottonUV')
 for f in me.polygons:
  f.use_smooth=True
  for li in f.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.x*1.8,v.y*1.8)
 if thick:
  so=o.modifiers.new('ActualFabricThickness','SOLIDIFY');so.thickness=thick;so.offset=-1
 return o

def pipe(name,pts,r,material,closed=False):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=2;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,v in zip(sp.points,pts):p.co=(*v,1)
 sp.use_cyclic_u=closed;o=bpy.data.objects.new(name,cu);s.collection.objects.link(o);o.data.materials.append(material)
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');o=bpy.context.object;o.parent=root;return o

def stitches(name,pts,r=.007,dash=.055,gap=.06):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=1;carry=0
 for a,b in zip(pts,pts[1:]):
  a=Vector(a);b=Vector(b);length=(b-a).length
  if length<1e-7:continue
  while carry<length:
   sp=cu.splines.new('POLY');sp.points.add(1);sp.points[0].co=(*(a+(b-a)*(carry/length)),1);sp.points[1].co=(*(a+(b-a)*(min(length,carry+dash)/length)),1);carry+=dash+gap
  carry-=length
 o=bpy.data.objects.new(name,cu);s.collection.objects.link(o);o.data.materials.append(thread)
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');o=bpy.context.object;o.parent=root

# Wrinkles follow fold compression and neckline tension; no rigid vertical box walls.
def front_z(x,y):
 dome=.12*math.exp(-((x/4.1)**4+(y/5.0)**4))
 z=.43+dome+.035*math.sin(.8*x+.3*y)
 z+=.065*math.sin(3.3*y+.65*x)*math.exp(-((abs(x)-3.55)/.70)**2)
 z+=.09*math.exp(-((y+4.15+.08*math.sin(x*1.2))/.20)**2)-.045*math.exp(-((y+3.83+.08*math.sin(x*1.2))/.17)**2)
 for side in (-1,1):
  dx=x-side*1.35;dy=y-2.9;across=dx-side*.60*dy
  z+=.08*math.exp(-(across/.18)**2)*math.exp(-((dx/2.8)**2+(dy/2.8)**2))
  z-=.035*math.exp(-((across-side*.25)/.13)**2)*math.exp(-((dx/2.6)**2+(dy/2.6)**2))
 z+=.045*math.sin(2*x+3*y)*math.exp(-((y+2.1)/1.1)**2)*math.exp(-((x-2)/2)**2)
 z+=.008*math.sin(12*x+3*y)*math.sin(7*y)*math.exp(-((abs(x)-3.6)/.8)**2)
 return z

def sd(x,y):
 # soft uneven folded silhouette, with tapered shoulders and rounded cloth corners.
 width=4.35-.20*math.exp(-((y-4.3)/1.2)**2)+.035*math.sin(y*1.3)
 qx=abs(x)-(width-.42);qy=abs(y)-(4.85-.42)
 return math.hypot(max(0,qx),max(0,qy))+min(max(qx,qy),0)-.42

def outline(t):
 dx=math.cos(t);dy=math.sin(t);lo=0;hi=20
 for i in range(32):
  mid=(lo+hi)/2
  if sd(dx*mid,3+dy*mid)>0:hi=mid
  else:lo=mid
 r=(lo+hi)/2+.025*math.sin(9*t)+.016*math.sin(17*t)
 return dx*r,3+dy*r

# An annular quad surface gives an exact neckline boundary, avoiding grid-cut jagged edges.
SEG=256;RINGS=90
for name,rx,ry,layer in [('FrontBody',1.25,.89,0),('BackBody',1.15,.62,1)]:
 vs=[];fs=[]
 for k in range(RINGS+1):
  u=k/RINGS
  for j in range(SEG):
   t=j*math.tau/SEG;dx,dy=math.cos(t),math.sin(t);ri=1/math.sqrt((dx/rx)**2+(dy/ry)**2);ox,oy=outline(t)
   x=(1-u)*ri*dx+u*ox;y=(1-u)*(3+ri*dy)+u*oy
   if layer==0:z=front_z(x,y)
   else:z=.18+.035*math.sin(x*1.4+y*.7)+.035*math.cos(y*1.7)*math.exp(-((abs(x)-3.7)/.7)**2)
   vs.append((x,y,z))
 for k in range(RINGS):
  for j in range(SEG):
   a=k*SEG+j;b=k*SEG+(j+1)%SEG;fs.append((a,b,b+SEG,a+SEG))
 mesh(name+'_ThinJersey',vs,fs,cotton,.016)
 # A curved sewn side return closes the outer edge gently, without a slab-like thickness.
 if layer==0:
  rv=[];rf=[]
  for k in range(13):
   u=k/12
   for j in range(SEG):
    t=j*math.tau/SEG;x,y=outline(t);a=front_z(x,y);b=.18+.035*math.sin(x*1.4+y*.7)+.035*math.cos(y*1.7)*math.exp(-((abs(x)-3.7)/.7)**2)
    bulge=.05*math.sin(math.pi*u);vx=x+bulge*math.cos(t);vy=y+bulge*math.sin(t);vz=(a+b)/2+(a-b)/2*math.cos(math.pi*u)
    rv.append((vx,vy,vz))
  for k in range(12):
   for j in range(SEG):a=k*SEG+j;b=k*SEG+(j+1)%SEG;rf.append((a,b,b+SEG,a+SEG))
  mesh('SoftSewnSideReturn',rv,rf,cotton,.013)
# Folded-under lower body, hem and two asymmetric folded sleeve flaps.
for side in (-1,1):
 vs=[];fs=[];nx=24;ny=36
 for j in range(ny+1):
  v=j/ny;y=-.4+4.1*v
  for i in range(nx+1):
   u=i/nx;x=side*(2.6+1.85*u+.10*math.sin(v*math.pi))
   z=.105+.05*math.sin(u*math.pi)+.025*math.sin(y*2.8+side)+.055*u
   vs.append((x,y,z))
 for j in range(ny):
  for i in range(nx):a=j*(nx+1)+i;fs.append((a,a+1,a+nx+2,a+nx+1))
 mesh(('Left' if side<0 else 'Right')+'_SleeveFoldedUnder',vs,fs,cotton,.018)
 pts=[(side*(4.42+.10*math.sin(i/60*math.pi)),-.4+4.1*i/60,.15+.025*math.sin((-.4+4.1*i/60)*2.8+side)) for i in range(61)]
 pipe('Sleeve_CuffFold',pts,.035,cotton);stitches('Sleeve_CuffCoverstitch',[(x-side*.04,y,z+.01) for x,y,z in pts])
# Curled bottom folded hem, not a rectangular extrusion.
pts=[]
for i in range(180):
 x=-3.9+7.8*i/179;y=-4.73+.035*math.sin(1.8*x);pts.append((x,y,.28+.025*math.sin(2*x)))
pipe('LowerFold_RolledHem',pts,.065,cotton)
for off in (.08,.14):stitches('Hem_DoubleCoverstitch',[(x,y+off,front_z(x,y+off)+.013) for x,y,z in pts])
# Rib-knit neckline is a flat cloth band, with fine ribs and close-set topstitch.
vs=[];fs=[];ringn=12
for k in range(ringn+1):
 u=k/ringn;rx=1.25+.24*u;ry=.89+.23*u
 for j in range(SEG):
  t=j*math.tau/SEG;x=rx*math.cos(t);y=3+ry*math.sin(t)
  z=front_z(x,y)+.018+.007*math.sin(t*128)*math.sin(math.pi*u)
  vs.append((x,y,z))
for k in range(ringn):
 for j in range(SEG):a=k*SEG+j;b=k*SEG+(j+1)%SEG;fs.append((a,b,b+SEG,a+SEG))
mesh('Collar_FlatRibKnitBinding',vs,fs,rib,.022)
for rx,ry in [(1.47,1.10),(1.42,1.05)]:
 pts=[(rx*math.cos(i*math.tau/SEG),3+ry*math.sin(i*math.tau/SEG),front_z(rx*math.cos(i*math.tau/SEG),3+ry*math.sin(i*math.tau/SEG))+.033) for i in range(SEG+1)]
 stitches('Collar_Coverstitch',pts,r=.006,dash=.04,gap=.05)
# Thin, slightly puckered chest pocket, sewn on three sides and open at top.
vs=[];fs=[];nx=36;ny=36
for j in range(ny+1):
 v=j/ny;y=.15+1.85*v
 for i in range(nx+1):
  u=i/nx;x=-3.40+1.9*u;bottom=.15+.22*abs(2*u-1);yy=bottom+(2-bottom)*v
  z=front_z(x,yy)+.020+.035*math.sin(math.pi*u)*math.sin(math.pi*v)+.012*math.sin(8*x)*v*v
  vs.append((x,yy,z))
for j in range(ny):
 for i in range(nx):a=j*(nx+1)+i;fs.append((a,a+1,a+nx+2,a+nx+1))
mesh('ChestPocket_ThinCloth',vs,fs,cotton,.013)
pts=[(-3.35,2-i*1.61/60) for i in range(61)]+[(-3.35+i*1.8/60,.20+.17*abs(2*i/60-1)) for i in range(61)]+[(-1.55,.39+i*1.61/60) for i in range(61)]
stitches('Pocket_AttachedStitch',[(x,y,front_z(x,y)+.038) for x,y in pts],r=.006)
pts=[(-3.4+i*1.9/90,2,front_z(-3.4+i*1.9/90,2)+.034) for i in range(91)]
pipe('Pocket_FoldedTopHem',pts,.018,cotton)
# A cloth label tucked into the back neck seam, with printed lines and seam.
vs=[(-.30,3.67,.258),(.30,3.67,.258),(.28,3.18,.245),(-.28,3.18,.245)]
mesh('NeckLabel_Cloth',vs,[(0,1,2,3)],labelmat,.008)
for y in (3.30,3.39,3.48):pipe('NeckLabel_Print',[(-.18,y,.266),(.18,y,.266)],.008,ink)
# Export only garment, then construct separate photographic inspection stage.
bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
for o in root.children_recursive:o.select_set(True)
bpy.context.view_layer.objects.active=root
bpy.ops.export_scene.fbx(filepath=O+'/TShirt_Folded_Realism_v02_cm.fbx',use_selection=True,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',add_leaf_bones=False,bake_anim=False,path_mode='COPY',embed_textures=True)
bpy.ops.export_scene.gltf(filepath=O+'/TShirt_Folded_Realism_v02.glb',use_selection=True,export_apply=True)
pts=[o.matrix_world@Vector(v) for o in root.children_recursive if o.type=='MESH' for v in o.evaluated_get(bpy.context.evaluated_depsgraph_get()).bound_box]
bounds=[(min(p[i] for p in pts),max(p[i] for p in pts)) for i in range(3)]
open(O+'/dimensions.json','w').write(json.dumps({'units':'cm','bounds':bounds,'size':[hi-lo for lo,hi in bounds]},indent=2))
floor=mat('Studio_Grey',(.18,.20,.21),.85)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,.035));o=bpy.context.object;o.name='STUDIO_Floor';o.data.materials.append(floor)
for loc,energy,size in [((-9,-9,19),11000,10),((12,7,15),6500,11),((-3,15,12),4000,9)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=energy;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.3))-o.location).to_track_quat('-Z','Y').to_euler()
s.world.color=(.06,.06,.06)
bpy.ops.object.camera_add(location=(11,-14,18));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((0,0,.4))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=13
s.render.engine='CYCLES';s.cycles.samples=96;s.cycles.use_denoising=False;s.render.resolution_x=1200;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=O+'/TShirt_Folded_Realism_v02.blend')
s.render.filepath=O+'/preview_overall.png';bpy.ops.render.render(write_still=True)
s.camera.location=(6,-8,4.2);s.camera.rotation_euler=(Vector((0,-2,.4))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=10.8;s.render.resolution_x=1200;s.render.resolution_y=850;s.render.filepath=O+'/preview_fold_detail.png';bpy.ops.render.render(write_still=True)
s.camera.location=(3,0,7);s.camera.rotation_euler=(Vector((0,2.5,.4))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=5.6;s.render.resolution_x=1100;s.render.resolution_y=1000;s.render.filepath=O+'/preview_collar_detail.png';bpy.ops.render.render(write_still=True)
print('COTTON_REVISION_COMPLETE')
