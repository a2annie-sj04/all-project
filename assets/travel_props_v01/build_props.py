import bpy,math,os,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=os.path.dirname(os.path.abspath(__file__))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=.01
os.makedirs(O+'/textures',exist_ok=True)
def material(name,c,rough=.6,metal=0,weave=False):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if weave:
  im=bpy.data.images.new(name+'_weave',width=128,height=128);pixels=[]
  for y in range(128):
   for x in range(128):
    k=.94+.035*math.sin(x*math.pi/2)+.025*math.cos(y*math.pi/2)+.015*math.sin((x+y)*1.7);pixels.extend((*[min(1,v*k) for v in c],1))
  im.pixels=pixels;im.filepath_raw=O+'/textures/'+name+'.png';im.file_format='PNG';im.save()
  n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=im;m.node_tree.links.new(n.outputs['Color'],p.inputs['Base Color'])
  bump=m.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.13;bump.inputs['Distance'].default_value=.007;m.node_tree.links.new(n.outputs['Color'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
 return m
cotton=material('Cream_Cotton',(.78,.73,.62),.87,weave=True);navy=material('Denim_Indigo',(.035,.085,.16),.83,weave=True)
thread=material('Warm_Stitch',(.56,.43,.26),.8);dark=material('Charcoal',(.035,.046,.055),.68);white=material('Ivory_Rubber',(.72,.75,.72),.58)
leather=material('Shoe_SkyGrey',(.33,.47,.55),.5);lining=material('Shoe_Lining',(.075,.10,.12),.9,weave=True);lace=material('Cotton_Laces',(.80,.79,.7),.86,weave=True)
pouchmat=material('Pouch_Sage_Nylon',(.19,.34,.29),.68,weave=True);capmat=material('Cap_Sand_Twill',(.56,.40,.24),.82,weave=True)
metal=material('Brushed_Metal',(.45,.51,.54),.28,.8)
roots=[]
def root(name):
 o=bpy.data.objects.new(name,None);s.collection.objects.link(o);roots.append(o);return o

def attach(o,parent):
 bpy.context.view_layer.update();w=o.matrix_world.copy();o.parent=parent;o.matrix_world=w;return o

def mesh_obj(name,vs,fs,mat,parent,smooth=True):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);s.collection.objects.link(o);o.data.materials.append(mat)
 for p in me.polygons:p.use_smooth=smooth
 uv=me.uv_layers.new(name='UV0')
 for p in me.polygons:
  axis=max(range(3),key=lambda k:abs(p.normal[k]));axes=[k for k in range(3) if k!=axis]
  for li in p.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]*2,v[axes[1]]*2)
 return attach(o,parent)

def box(name,loc,dims,mat,parent,b=.08):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
 if b:
  a=o.modifiers.new('SoftEdges','BEVEL');a.width=b;a.segments=4;o.modifiers.new('Normals','WEIGHTED_NORMAL')
 return attach(o,parent)

def line(name,pts,r,mat,parent,closed=False):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=2
 sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,v in zip(sp.points,pts):p.co=(*v,1)
 sp.use_cyclic_u=closed;o=bpy.data.objects.new(name,cu);s.collection.objects.link(o);o.data.materials.append(mat)
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');return attach(bpy.context.object,parent)

def ellipse(cx,cy,z,rx,ry,n=80):return [(cx+rx*math.cos(i*2*math.pi/n),cy+ry*math.sin(i*2*math.pi/n),z) for i in range(n)]
def stitch(name,pts,mat,parent,r=.012,dash=.10,gap=.085):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=1
 distance=0
 for a,b in zip(pts,pts[1:]):
  a=Vector(a);b=Vector(b);length=(b-a).length
  while distance<length:
   finish=min(length,distance+dash);sp=cu.splines.new('POLY');sp.points.add(1)
   sp.points[0].co=(*(a+(b-a)*(distance/length)),1);sp.points[1].co=(*(a+(b-a)*(finish/length)),1);distance+=dash+gap
  distance-=length
 o=bpy.data.objects.new(name,cu);s.collection.objects.link(o);o.data.materials.append(mat)
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');return attach(bpy.context.object,parent)

def rounded_path(w,d,r,z,n=12):
 pts=[]
 for cx,cy,a in [(w/2-r,d/2-r,0),(-w/2+r,d/2-r,90),(-w/2+r,-d/2+r,180),(w/2-r,-d/2+r,270)]:
  for j in range(n):
   t=math.radians(a+j*90/(n-1));pts.append((cx+r*math.cos(t),cy+r*math.sin(t),z))
 return pts

# Folded garments: softly domed surfaces, layered folded edges, neckline and stitching.
def cloth_slab(name,w,d,h,base,mat,parent,seed=0):
 nx=40;ny=44;vs=[];fs=[]
 for j in range(ny+1):
  v=j/ny;y=(v-.5)*d
  for i in range(nx+1):
   u=i/nx;x=(u-.5)*w
   edge=math.sin(math.pi*u)*math.sin(math.pi*v)
   z=base+h*(.66+.34*edge)+.045*edge*math.sin(x*3+y*1.3+seed)+.025*edge*math.cos(y*4-x)
   xx=x*(1-.025*math.cos(v*math.pi*2));yy=y*(1-.018*math.cos(u*math.pi*2))
   vs.append((xx,yy,z))
 for j in range(ny):
  for i in range(nx):
   k=j*(nx+1)+i;fs.append((k,k+1,k+nx+2,k+nx+1))
 o=mesh_obj(name,vs,fs,mat,parent);m=o.modifiers.new('ClothThickness','SOLIDIFY');m.thickness=h*.62;m.offset=-1
 b=o.modifiers.new('SoftFoldEdge','BEVEL');b.width=.075;b.segments=3
 return o
shirt=root('PROP_Folded_TShirt_cm')
cloth_slab('TShirt_FoldedSleeveLayer',8.7,9.6,.40,.02,cotton,shirt)
cloth_slab('TShirt_MainFold',9.1,10,.66,.30,cotton,shirt)
# U neckline follows fabric top and has an inner dark recess.
neckpts=[]
for i in range(65):
 t=math.pi+i*math.pi/64;neckpts.append((1.42*math.cos(t),3.4+1.15*math.sin(t),.94))
line('TShirt_RibbedCollar',neckpts,.115,cotton,shirt)
line('TShirt_NecklineShadow',[(x,y,.84) for x,y,z in neckpts],.065,thread,shirt)
for side in (-1,1):
 pts=[(side*4.20,-4.6+i*.18,.76+.025*math.sin(i*.2)) for i in range(52)];stitch('TShirt_SideDoubleStitch',pts,cotton,shirt)
stitch('TShirt_FoldedHem',[(-4.1+i*.15,-4.64,.77) for i in range(56)],thread,shirt)
box('TShirt_NeckLabel',(0,3.45,.96),(.6,.55,.025),white,shirt,.01)
# Front pocket shares the cloth surface rather than hovering above it.
cloth_slab('TShirt_ChestPocket',2.05,2.05,.055,.94,cotton,shirt)
p=bpy.data.objects['TShirt_ChestPocket'];p.location.x=-2.1;p.location.y=.65
stitch('TShirt_PocketSeam',[(-3.02,1.6,1.005),(-3.02,-.25,1.005),(-1.18,-.25,1.005),(-1.18,1.6,1.005)],thread,shirt)

pants=root('PROP_Folded_Pants_cm')
cloth_slab('Pants_FoldedLegBottom',8.9,10.3,.52,.02,navy,pants,1)
cloth_slab('Pants_FoldedLegTop',8.7,10.0,.65,.42,navy,pants,3)
# Waistband visible on the near fold, with button, fly seam and belt loops.
box('Pants_Waistband',(0,4.55,1.03),(8.4,.7,.27),navy,pants,.12)
for x in (-3.4,-1.8,1.8,3.4):box('Pants_BeltLoop',(x,4.51,1.20),(.22,.86,.095),navy,pants,.04)
for y in (-4.65,4.28):stitch('Pants_DoubleHem',[(-4+i*.15,y,1.0 if y>0 else .91) for i in range(55)],thread,pants)
stitch('Pants_FlySeam',[(.18,4.20,1.12),(.18,3.4,1.1),(.40,2.9,1.08)],thread,pants)
for side in (-1,1):stitch('Pants_PocketOpening',[(side*3.9,4.18,1.1),(side*3.0,3.48,1.11),(side*2.4,3.34,1.12)],thread,pants)
bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=1,location=(0,4.48,1.24));o=bpy.context.object;o.name='Pants_Button';o.scale=(.19,.19,.055);o.data.materials.append(metal);attach(o,pants)

# Sneakers: shaped sole, hollow upper, sewn panels, eyelets, laces and outsole tread.
def sole_outline(t):
 # front = negative Y, slightly fuller toe box, narrower heel.
 x=math.cos(t);y=math.sin(t);width=1.60*(1-.12*y)
 return width*x,4.45*y

def rings_mesh(name,rings,mat,parent,n=96,caps=True):
 vs=[p for ring in rings for p in ring];fs=[]
 for k in range(len(rings)-1):
  for j in range(n):fs.append((k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j))
 if caps:fs.extend([tuple(reversed(range(n))),tuple((len(rings)-1)*n+j for j in range(n))])
 return mesh_obj(name,vs,fs,mat,parent)
shoes=[]
for label in ('Left','Right'):
 shoe=root('PROP_Sneaker_'+label+'_cm');shoes.append(shoe)
 rings=[]
 for scale,z in [(.96,.03),(1,.13),(1,.52),(.96,.68)]:
  rings.append([(sole_outline(t)[0]*scale,sole_outline(t)[1]*scale,z) for t in [i*math.tau/96 for i in range(96)]])
 rings_mesh('Sneaker_'+label+'_MouldedMidsole',rings,white,shoe)
 outsole=[]
 for scale,z in [(.93,.0),(.97,.08),(.97,.19)]:outsole.append([(sole_outline(i*math.tau/96)[0]*scale,sole_outline(i*math.tau/96)[1]*scale,z) for i in range(96)])
 rings_mesh('Sneaker_'+label+'_RubberOutsole',outsole,dark,shoe)
 # Actual heel-to-toe grooves along bottom, kept within the sole silhouette.
 for yy in [i*.5 for i in range(-7,8)]:
  xx=1.4*math.sqrt(max(.01,1-(yy/4.45)**2));line('Sneaker_'+label+'_Tread', [(-xx,yy,.025),(0,yy+.13,.025),(xx,yy,.025)],.055,dark,shoe)
 upperrings=[]
 specs=[(1,1,0,.63),(.98,.99,0,1.0),(.90,.89,.25,1.55),(.72,.65,1.05,2.25),(.58,.36,2.0,2.90)]
 for sx,sy,cy,z in specs:
  ring=[]
  for j in range(96):
   t=j*math.tau/96;x,y=sole_outline(t);ring.append((x*sx,y*sy+cy,z+.12*math.sin(t)))
  upperrings.append(ring)
 upper=rings_mesh('Sneaker_'+label+'_HollowUpper',upperrings,leather,shoe,caps=False)
 # Roll collar inward, then down to the cavity floor: open shoe interior, no top cap.
 outer=upperrings[-1];inner=[(x*.83,(y-2)*.86+2,z-.08) for x,y,z in outer]
 floor=[(x*.8,(y-2)*.8+2,1.05) for x,y,z in inner]
 rings_mesh('Sneaker_'+label+'_PaddedInnerCollar',[outer,inner,floor],lining,shoe,caps=False)
 box('Sneaker_'+label+'_Insole',(0,2,1.02),(1.35,2.6,.15),lining,shoe,.3)
 line('Sneaker_'+label+'_CollarBinding',outer,.065,lining,shoe,True)
 # Surface sampling keeps seams and lace hardware seated on the actual upper.
 tree=BVHTree.FromPolygons([Vector(v) for v in upper.data.vertices for v in []],[]) if False else BVHTree.FromPolygons([v.co.copy() for v in upper.data.vertices],[tuple(p.vertices) for p in upper.data.polygons])
 def surface(x,y,offset=.035):
  hit=tree.ray_cast(Vector((x,y,8)),Vector((0,0,-1)))
  return (x,y,hit[0].z+offset) if hit[0] is not None else (x,y,2.5)
 # Toe panel curved seam and parallel stitch follow the vamp.
 for off in (0,.14):
  pts=[surface(-1.3+2.6*i/48,-2.5+.55*((-1.3+2.6*i/48)/1.3)**2+off) for i in range(49)]
  if off==0:line('Sneaker_'+label+'_ToePanelPiping',pts,.028,white,shoe)
  else:stitch('Sneaker_'+label+'_ToePanelStitch',pts,white,shoe,r=.01,dash=.065,gap=.07)
 # Tongue is draped onto the upper beneath the lace crossings.
 tonguepts=[surface(0,-1.7+i*.095,.055) for i in range(26)]
 tv=[];tf=[]
 for i,(x,y,z) in enumerate(tonguepts):tv.extend([surface(-.49,y,.055),surface(.49,y,.055)])
 for i in range(len(tonguepts)-1):tf.append((2*i,2*i+1,2*i+3,2*i+2))
 tongue=mesh_obj('Sneaker_'+label+'_Tongue',tv,tf,lining,shoe);so=tongue.modifiers.new('TonguePadding','SOLIDIFY');so.thickness=.05
 rows=[-1.35,-.90,-.45,0,.45]
 for yy in rows:
  for side in (-1,1):
   pt=surface(side*.63,yy,.045)
   bpy.ops.mesh.primitive_torus_add(major_segments=20,minor_segments=8,location=pt,major_radius=.095,minor_radius=.027);o=bpy.context.object;o.name='Sneaker_'+label+'_Eyelet';o.data.materials.append(metal);attach(o,shoe)
 for i in range(len(rows)-1):
  for side in (-1,1):
   pts=[]
   for j in range(20):
    t=j/19;x=side*.63*(1-2*t);y=rows[i]*(1-t)+rows[i+1]*t
    xx,yy,zz=surface(x,y,.12);pts.append((xx,yy,zz+.065*math.sin(math.pi*t)))
   line('Sneaker_'+label+'_CrossLace',pts,.046,lace,shoe)
 # Bow loops and short agleted tips sit on last lace row.
 cz=surface(0,.45,.18)[2]
 for side in (-1,1):
  pts=[(side*(.15+.52*(1-math.cos(t))),.55+.27*math.sin(t),cz+.07*math.sin(t)) for t in [i*math.tau/48 for i in range(49)]]
  line('Sneaker_'+label+'_BowLoop',pts,.045,lace,shoe)
  tip=[(side*.12,.45,cz),(side*.4,.9,cz-.1),(side*.6,1.05,cz-.23)]
  line('Sneaker_'+label+'_LaceTail',tip,.044,lace,shoe);line('Sneaker_'+label+'_Aglet',tip[-2:],.048,white,shoe)
 # Side panel stitching and heel seam, fitted to exterior ring grid.
 for side in (-1,1):
  pts=[]
  for j in range(16,78):
   t=(j/96)*math.tau
   if (math.cos(t)>0)==(side>0):
    x,y,z=upperrings[2][j];pts.append((x*1.015,y,z+.018))
  if len(pts)>2:stitch('Sneaker_'+label+'_QuarterPanelStitch',pts,white,shoe,r=.012)
 heelpts=[(0,4.44,.72),(0,4.34,1.1),(0,4.0,1.7),(0,3.65,2.35),(0,3.60,2.94)]
 line('Sneaker_'+label+'_HeelSeam',heelpts,.045,lining,shoe)
 line('Sneaker_'+label+'_HeelPullLoop',[(0,3.60,2.70),(0,3.90,3.25),(0,3.57,3.10)],.10,lining,shoe)
 line('Sneaker_'+label+'_MidsoleWelt',[(sole_outline(i*math.tau/96)[0]*.99,sole_outline(i*math.tau/96)[1]*.99,.51) for i in range(96)],.035,leather,shoe,True)

# Soft toiletry pouch, domed top with an actual zipper running over the bag.
pouch=root('PROP_ToiletryPouch_cm')
profiles=[(6.8,3.1,.7,.12),(7.4,3.7,.85,.42),(7.5,3.8,.9,1.8),(7.1,3.3,.95,2.65),(6.5,2.65,.95,2.95)]
rings=[rounded_path(w,d,r,z,n=16) for w,d,r,z in profiles]
rings_mesh('Pouch_SewnSoftBody',rings,pouchmat,pouch,n=64)
for z,w,d,r in [(.45,7.43,3.73,.85),(2.64,7.12,3.32,.95)]:
 pts=rounded_path(w,d,r,z,n=16);line('Pouch_PanelBinding',pts,.045,pouchmat,pouch,True);stitch('Pouch_PanelTopstitch',pts+[pts[0]],thread,pouch,r=.012)
# Zipper is seated on the top panel at z=2.95, no air gap.
box('Pouch_ZipperTape',(0,0,2.98),(6.1,.35,.10),dark,pouch,.04)
for i in range(41):
 x=-2.8+i*.14
 box('Pouch_ZipperTooth',(x,(-.06 if i%2 else .06),3.06),(.095,.12,.075),metal,pouch,.018)
box('Pouch_ZipperSlider',(2.4,0,3.12),(.42,.39,.16),metal,pouch,.045)
line('Pouch_ZipperPull',[(2.4,0,3.16),(2.9,-.22,3.16),(3.14,0,3.14),(2.85,.22,3.16),(2.4,0,3.16)],.047,metal,pouch)
# Carry loop attached at two reinforced points, along right end.
for yy in (-.65,.65):box('Pouch_HandleAnchor',(3.60,yy,1.7),(.20,.5,.8),pouchmat,pouch,.07)
line('Pouch_SideLoop',[(3.63,-.65,1.7),(4.0,-.65,2.2),(4.10,0,2.3),(4.0,.65,2.2),(3.63,.65,1.7)],.12,pouchmat,pouch)
box('Pouch_WovenLabel',(0,-1.87,1.55),(1.3,.045,.56),dark,pouch,.045)
for x in (-.45,.45):box('Pouch_LabelStitch',(x,-1.90,1.55),(.035,.025,.38),thread,pouch,.008)

# Baseball cap: six-panel hollow crown, bent visor, seams, eyelets and rear strap.
cap=root('PROP_BaseballCap_cm')
N=96;K=28;vs=[];fs=[]
for k in range(K+1):
 phi=(k/K)*math.pi/2
 for j in range(N):
  t=j*math.tau/N;r=math.cos(phi);z=.18+2.75*math.sin(phi)
  # slight fabric fullness by panel, not a perfect hemisphere.
  scallop=1+.012*math.sin(6*t)*math.sin(phi*2)
  vs.append((3.1*r*math.cos(t)*scallop,3.15*r*math.sin(t)*scallop+.45,z))
for k in range(K):
 for j in range(N):
  # rear adjustment opening left cut out through the lower two fifths.
  t=(j+.5)*math.tau/N
  if k<7 and abs(t-math.pi/2)<.40:continue
  fs.append((k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j))
crown=mesh_obj('Cap_SixPanelHollowCrown',vs,fs,capmat,cap);solid=crown.modifiers.new('FabricThickness','SOLIDIFY');solid.thickness=.07
# Inner sweatband joins base contour, leaving rear opening.
pts=[(2.98*math.cos(t),3.03*math.sin(t)+.45,.23) for t in [math.pi/2+.42+i*(math.tau-.84)/120 for i in range(121)]]
line('Cap_InnerSweatband',pts,.13,dark,cap)
for j in range(6):
 t=j*math.tau/6
 pts=[]
 for i in range(35):
  phi=i/34*math.pi/2;r=math.cos(phi);pts.append((3.115*r*math.cos(t),3.165*r*math.sin(t)+.45,.18+2.76*math.sin(phi)))
 line('Cap_PanelSeam',pts,.025,capmat,cap);stitch('Cap_PanelTopstitch',[(x+.035*math.cos(t+math.pi/2),y+.035*math.sin(t+math.pi/2),z+.012) for x,y,z in pts],thread,cap,r=.009,dash=.07,gap=.075)
# Visor runs under the crown at front (negative Y), then extends forward.
vs=[];fs=[];nu=50;nv=18
for k in range(nv+1):
 v=k/nv
 for i in range(nu+1):
  u=-1+2*i/nu;x=3.08*u
  back=-.65-1.95*math.sqrt(max(0,1-u*u));front=-.8-4.05*math.sqrt(max(0,1-u*u))
  y=back*(1-v)+front*v;z=.21+.27*(1-u*u)-.11*v
  vs.append((x,y,z))
for k in range(nv):
 for i in range(nu):
  a=k*(nu+1)+i;fs.append((a,a+1,a+nu+2,a+nu+1))
visor=mesh_obj('Cap_CurvedVisor',vs,fs,capmat,cap);so=visor.modifiers.new('VisorThickness','SOLIDIFY');so.thickness=.12
for fraction in (.20,.38,.56,.74,.92):
 pts=[]
 for i in range(81):
  u=-.96+1.92*i/80;x=3.08*u;back=-.65-1.95*math.sqrt(1-u*u);front=-.8-4.05*math.sqrt(1-u*u)
  pts.append((x,back*(1-fraction)+front*fraction,.225+.27*(1-u*u)-.11*fraction))
 stitch('Cap_VisorConcentricStitch',pts,thread,cap,r=.009,dash=.09,gap=.075)
# Crown button, ventilation grommets fitted tangentially to the crown.
bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=1,location=(0,.45,2.98));o=bpy.context.object;o.name='Cap_CrownButton';o.scale=(.23,.23,.11);o.data.materials.append(capmat);attach(o,cap)
for j in range(6):
 t=(j+.5)*math.tau/6;phi=.65;r=math.cos(phi);p=Vector((3.11*r*math.cos(t),3.16*r*math.sin(t)+.45,.18+2.76*math.sin(phi)))
 normal=Vector((math.cos(t)*math.cos(phi),math.sin(t)*math.cos(phi),math.sin(phi)))
 bpy.ops.mesh.primitive_torus_add(major_segments=20,minor_segments=8,major_radius=.10,minor_radius=.022,location=p);o=bpy.context.object;o.name='Cap_VentEyelet';o.rotation_euler=normal.to_track_quat('Z','Y').to_euler();o.data.materials.append(thread);attach(o,cap)
line('Cap_RearAdjustmentStrap',[(-1.2,3.31,.32),(0,3.44,.32),(1.2,3.31,.32)],.14,capmat,cap)
box('Cap_AdjustmentBuckle',(.5,3.42,.32),(.52,.24,.35),metal,cap,.06)

# Exchange files export each prop at its own bottom-centered origin.
manifest=[]
for r in roots:
 bpy.ops.object.select_all(action='DESELECT');r.select_set(True)
 for o in r.children_recursive:o.select_set(True)
 bpy.context.view_layer.objects.active=r
 fn=r.name.replace('PROP_','')
 bpy.ops.export_scene.fbx(filepath=O+'/'+fn+'.fbx',use_selection=True,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',add_leaf_bones=False,bake_anim=False,path_mode='COPY',embed_textures=True)
 bpy.ops.export_scene.gltf(filepath=O+'/'+fn+'.glb',use_selection=True,export_apply=True)
 bpy.context.view_layer.update();pts=[o.matrix_world@Vector(v) for o in r.children_recursive if o.type=='MESH' for v in o.bound_box]
 bounds=[(min(v[i] for v in pts),max(v[i] for v in pts)) for i in range(3)]
 manifest.append({'name':r.name,'file':fn+'.fbx','bounds_cm':bounds,'size_cm':[b-a for a,b in bounds]})
open(O+'/asset_manifest.json','w').write(json.dumps(manifest,indent=2))
# Studio layout for overview and individual inspection.
positions=[(-12,6,0),(0,6,0),(-12,-7,0),(-7,-7,0),(9,6,0),(7,-7,0)]
for r,p in zip(roots,positions):r.location=p
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=False;s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100
floor=material('Studio_Backdrop',(.10,.14,.18),.8)
box('STUDIO_FLOOR',(0,0,-.22),(100,100,.4),floor,None,.02)
for loc,power,size in [((0,-15,40),90000,30),((-25,10,25),65000,25),((20,20,35),95000,25)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(30,-43,47));cam=bpy.context.object;s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=43;cam.rotation_euler=(Vector((-1,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();s.world.color=(.18,.18,.18)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=O+'/travel_props_studio.blend')
s.render.filepath=O+'/preview_all.png';bpy.ops.render.render(write_still=True)
for r in roots:
 p=r.location.copy()
 for other in roots:other.hide_render=(other!=r)
 cam.location=p+Vector((12,-18,21));cam.rotation_euler=(p+Vector((0,0,1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=13
 s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.filepath=O+'/preview_'+r.name.replace('PROP_','')+'.png';bpy.ops.render.render(write_still=True)
for r in roots:r.hide_render=False
print('PROPS_COMPLETE')
