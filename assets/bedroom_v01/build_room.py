import bpy,math,os,json,random
from mathutils import Vector,Matrix
O=os.path.dirname(os.path.abspath(__file__));os.makedirs(O+'/textures',exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=.01
random.seed(41)
root=bpy.data.objects.new('ROOM_ROOT_cm',None);s.collection.objects.link(root)
groups={}
def group(name):
 o=bpy.data.objects.new(name,None);s.collection.objects.link(o);o.parent=root;groups[name]=o;return o
arch=group('Architecture');bed=group('Bed_Assembly');night=group('Nightstand_Assembly');desk=group('Desk_Assembly');chair=group('Chair_Assembly');window=group('Window_Assembly');curtains=group('Curtains_Assembly');decor=group('Decor_Assembly');plant=group('Plant_Assembly')
materials={}
def material(name,c,rough=.6,metal=0,texture=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*c,1);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if texture:
  n=256;buffers={k:[] for k in ('BaseColor','Roughness','Normal')}
  def height(x,y):
   if texture=='wood':return .55*math.sin(y*.12+1.8*math.sin(x*.024))+.22*math.sin(y*.43+.65*math.sin(x*.08))+.13*math.sin(y*1.2+x*.05)
   if texture=='fabric':return .4*math.cos(x*math.tau/8+.4*math.sin(y*math.tau/8))+.4*math.cos(y*math.tau/8)+.1*math.sin((x+y)*math.tau/4)
   return .4*math.sin(x*.31)*math.cos(y*.27)+.15*math.sin(x*2+y*.9)
  rng=random.Random(77)
  for y in range(n):
   for x in range(n):
    h=height(x,y);noise=rng.uniform(-.018,.018);a=.09 if texture=='wood' else .025
    buffers['BaseColor'].extend((*[max(0,min(1,v*(1+a*h+noise))) for v in c],1))
    r=max(.05,min(1,rough+.035*h+noise));buffers['Roughness'].extend((r,r,r,1))
    d=.12 if texture=='fabric' else .16;dx=(height(x+1,y)-height(x-1,y))*d;dy=(height(x,y+1)-height(x,y-1))*d;v=Vector((-dx,-dy,1)).normalized();buffers['Normal'].extend(((v.x+1)/2,(v.y+1)/2,(v.z+1)/2,1))
  for key,pix in buffers.items():
   im=bpy.data.images.new(name+'_'+key,width=n,height=n)
   if key!='BaseColor':im.colorspace_settings.name='Non-Color'
   im.pixels=pix;im.filepath_raw=O+'/textures/'+name+'_'+key+'.png';im.file_format='PNG';im.save()
   tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im
   if key=='Normal':
    nm=m.node_tree.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.4;m.node_tree.links.new(tex.outputs['Color'],nm.inputs['Color']);m.node_tree.links.new(nm.outputs['Normal'],p.inputs['Normal'])
   else:m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color' if key=='BaseColor' else key])
 if texture=='fabric':p.inputs['Sheen Weight'].default_value=.18
 materials[name]=m;return m
plaster=material('Warm_Plaster',(.60,.55,.47),.91,texture='plaster')
wood=material('Natural_Oak',(.31,.19,.095),.46,texture='wood')
walnut=material('Walnut_Joinery',(.16,.085,.039),.40,texture='wood')
linen=material('Oat_Linen',(.48,.41,.32),.88,texture='fabric')
cotton=material('Ivory_Bedding',(.72,.68,.60),.9,texture='fabric')
duvetmat=material('Sage_Duvet',(.27,.34,.27),.86,texture='fabric')
curtainmat=material('Linen_Curtain',(.62,.57,.46),.89,texture='fabric')
rugmat=material('Wool_Rug',(.37,.32,.25),.97,texture='fabric')
black=material('Dark_Trim',(.025,.031,.034),.4);brass=material('Brushed_Brass',(.38,.25,.10),.32,.75)
ceramic=material('Cream_Ceramic',(.58,.53,.44),.26);paper=material('Book_Pages',(.56,.53,.45),.84)
green=material('Leaf_Green',(.045,.11,.055),.48);soil=material('Soil',(.035,.023,.013),.96)
clay=material('Terracotta',(.30,.12,.065),.86);trim=material('Painted_Trim',(.53,.49,.42),.65)
def parent(o,p):
 bpy.context.view_layer.update();w=o.matrix_world.copy();o.parent=p;o.matrix_world=w;return o

def uvmesh(o,scale=8):
 if o.type!='MESH':return
 me=o.data;uv=me.uv_layers.active or me.uv_layers.new(name='UV0')
 if any(m and m.name in ('Oat_Linen','Ivory_Bedding','Sage_Duvet','Linen_Curtain','Wool_Rug') for m in me.materials):scale=.8
 for f in me.polygons:
  axis=max(range(3),key=lambda k:abs(f.normal[k]));axes=[i for i in range(3) if i!=axis]
  for li in f.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/scale,v[axes[1]]/scale)

def box(name,co,dim,mat,p,b=.10):
 bpy.ops.mesh.primitive_cube_add(size=1,location=co);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);uvmesh(o)
 if b:
  mod=o.modifiers.new('EdgeRadius','BEVEL');mod.width=b;mod.segments=4;o.modifiers.new('WeightedNormals','WEIGHTED_NORMAL')
 return parent(o,p)

def mesh(name,vs,fs,mat,p,thickness=0):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);s.collection.objects.link(o);o.data.materials.append(mat)
 for f in me.polygons:f.use_smooth=True
 uvmesh(o,4)
 if thickness:
  so=o.modifiers.new('Thickness','SOLIDIFY');so.thickness=thickness
 return parent(o,p)

def tube(name,pts,r,mat,p,closed=False):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=3;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for a,v in zip(sp.points,pts):a.co=(*v,1)
 sp.use_cyclic_u=closed;o=bpy.data.objects.new(name,cu);s.collection.objects.link(o);o.data.materials.append(mat)
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');o=bpy.context.object;uvmesh(o);return parent(o,p)

def lathe(name,co,profile,mat,p,n=64):
 vs=[];fs=[]
 for radius,z in profile:
  vs.extend((co[0]+radius*math.cos(i*math.tau/n),co[1]+radius*math.sin(i*math.tau/n),co[2]+z) for i in range(n))
 for k in range(len(profile)-1):
  for j in range(n):a=k*n+j;b=k*n+(j+1)%n;fs.append((a,b,b+n,a+n))
 return mesh(name,vs,fs,mat,p)

# 64 x 64 cm virtual room, open toward the two display faces at X=0 and Y=0.
box('Floor_Substrate',(-32,32,-.55),(64,64,1.1),walnut,arch,.02)
for row in range(16):
 yy=2+row*4;offset=(row%3)*6
 for i in range(-1,5):
  lo=max(-64,-64+i*19+offset);hi=min(0,-64+(i+1)*19+offset)
  if hi-lo<.05:continue
  o=box('OakFloor_Plank_%02d_%02d'%(row,i),( (lo+hi)/2,yy,.035),(hi-lo-.045,3.96,.07),wood,arch,.018)
  uv=o.data.uv_layers.active
  du,dv=random.random()*4,random.random()*4
  for x in uv.data:x.uv.x+=du;x.uv.y+=dv
ceiling=box('Ceiling_Panel_DisplayOnly',(-32,32,48.35),(64,64,.7),plaster,arch,.02);ceiling.hide_render=True
box('BackWall',(-32,64.55,24),(64,1.1,48),plaster,arch,.02)
# Window opening in the left wall is actual geometry, not a bright plane pasted over a wall.
for name,co,dim in [('Below',(-64.55,32,9),(1.1,64,18)),('Above',(-64.55,32,43.5),(1.1,64,9)),('Front',(-64.55,8.5,28.5),(1.1,17,21)),('Back',(-64.55,55.5,28.5),(1.1,17,21))]:box('LeftWall_'+name,co,dim,plaster,arch,.02)
box('Back_Skirting',(-32,63.85,.7),(64,.35,1.4),trim,arch,.04)
box('Left_Skirting',(-63.85,32,.7),(.35,64,1.4),trim,arch,.04)
box('Back_Cornice',(-32,63.7,47.5),(64,.6,1),trim,arch,.08)
box('Left_Cornice',(-63.7,32,47.5),(.6,64,1),trim,arch,.08)
# Subtle wall panel mouldings and electrical fittings.
for x in (-57,-35,-13):
 for xx in (x-9,x+9):box('WallPanel_Vertical',(xx,63.85,28),(.16,.12,29),trim,arch,.025)
 for zz in (13.5,42.5):box('WallPanel_Horizontal',(x,63.85,zz),(18,.12,.16),trim,arch,.025)
for x in (-57,-8):
 box('WallOutlet_Plate',(x,63.73,4.1),(1.2,.15,1.7),trim,arch,.07)
 for xx in (-.22,.22):box('WallOutlet_Slot',(x+xx,63.63,4.15),(.10,.035,.3),black,arch,.01)
# Window frames with rails, sill and handle.
for yy in (17.25,46.75):box('Window_Jamb',(-63.55,yy,28.5),(.75,.5,21.5),trim,window,.06)
for zz in (18.25,38.75):box('Window_Rail',(-63.55,32,zz),(.75,30,.5),trim,window,.06)
box('Window_CentreMullion',(-63.3,32,28.5),(.5,.40,20.5),trim,window,.035)
box('Window_Sill',(-62.5,32,18.0),(3.0,31,.55),wood,window,.10)
windowglass=material('Window_DaylightGlass',(.50,.65,.72),.20)
p=windowglass.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(.53,.65,.75,1);p.inputs['Emission Strength'].default_value=.45
box('Window_Glass',(-64.1,32,28.5),(.08,29.0,20.0),windowglass,window,.0)
tube('Window_Handle',[(-63.05,33,27.6),(-62.65,33,27.6),(-62.65,33,29.0)],.08,brass,window)
# Pleated full-length curtains with hems, rings, rod and wall brackets.
tube('Curtain_Rod',[(-61.7,14,44),(-61.7,50,44)],.12,brass,curtains)
for yy in (14.5,49.5):tube('Curtain_RodBracket',[(-64,yy,43.6),(-61.7,yy,43.6),(-61.7,yy,44)],.10,brass,curtains)
for index,(a,b) in enumerate([(15.2,22),(43,49.8)]):
 vs=[];fs=[];nu=60;nv=75
 for j in range(nv+1):
  v=j/nv;z=1.0+42.4*v
  for i in range(nu+1):
   u=i/nu;y=a+(b-a)*u+.12*math.sin(v*5+u*2);x=-61.3+.43*math.cos(u*math.tau*5)+.07*math.sin(v*8+u*11)*(1-v)
   vs.append((x,y,z+.12*math.cos(u*math.tau*5)*(1-v)**3))
 for j in range(nv):
  for i in range(nu):k=j*(nu+1)+i;fs.append((k,k+1,k+nu+2,k+nu+1))
 mesh('Curtain_%d_PleatedLinen'%index,vs,fs,curtainmat,curtains,.028)
 for zrow in (0,nv):tube('Curtain_Hem',[vs[zrow*(nu+1)+i] for i in range(nu+1)],.035,curtainmat,curtains)
 for i in range(9):
  yy=a+(b-a)*i/8
  pts=[(-61.7+.20*math.cos(t),yy,44+.20*math.sin(t)) for t in [j*math.tau/32 for j in range(32)]]
  tube('Curtain_Ring',pts,.035,brass,curtains,True)
  tube('Curtain_Clip',[(-61.7,yy,43.8),(-61.3+.43*math.cos((i/8)*math.tau*5),yy+.12*math.sin(5+(i/8)*2),43.4)],.04,brass,curtains)
# Rug with woven border and actual fringe at the two exposed ends.
box('Rug_WovenBody',(-31,27,.12),(48,45,.20),rugmat,decor,.08)
for xx in (-54.65,-7.35):tube('Rug_BoundEdge',[(xx,4.7,.23),(xx,49.3,.23)],.055,rugmat,decor)
for yy in (4.6,49.4):
 for i in range(130):
  x=-54.6+i*47.2/129;d=-1 if yy<10 else 1;tube('Rug_Fringe',[(x,yy,.13),(x+.025*math.sin(i),yy+d*.65,.10)],.018,rugmat,decor)
# Bed frame is supported by six legs and an inset rail, with realistic mattress proportions.
for xx in (-50,-20):
 for yy in (19,37,55):box('Bed_Foot',(xx,yy,1.45),(1.7,1.7,2.9),walnut,bed,.12)
box('Bed_TimberFrame',(-35,37,4.0),(36.5,42.5,3.0),walnut,bed,.32)
box('Bed_UpholsteredBase',(-35,37,5.15),(35.8,41.8,1.7),linen,bed,.45)
box('Bed_Mattress',(-35,37,6.9),(35.7,41.7,2.3),cotton,bed,.70)
# Headboard upholstered channels with timber surround.
box('Headboard_TimberSurround',(-35,59.1,12.4),(40,1.8,23.2),walnut,bed,.55)
for i in range(8):box('Headboard_LinenChannel_%d'%i,(-52.0+i*4.85,57.95,15.0),(4.70,1.1,15.6),linen,bed,.48)
# Soft pillows: two curved surfaces meet at an actual piping seam.
def pillow(name,cx,cy,w,d,height):
 nx=50;ny=35;vs=[];fs=[]
 for side in (1,-1):
  for j in range(ny+1):
   v=j/ny;yy=(v-.5)*d
   for i in range(nx+1):
    u=i/nx;xx=(u-.5)*w;edge=max(0,math.sin(math.pi*u)*math.sin(math.pi*v))**.48
    z=8.7+side*(.12+height*edge)+.06*math.sin(yy*2+xx)*edge
    xx*=1-.035*math.cos(v*math.tau);yy*=1-.035*math.cos(u*math.tau)
    vs.append((cx+xx,cy+yy,z))
 layer=(nx+1)*(ny+1)
 for k in range(2):
  for j in range(ny):
   for i in range(nx):a=k*layer+j*(nx+1)+i;f=(a,a+1,a+nx+2,a+nx+1);fs.append(f if k==0 else tuple(reversed(f)))
 boundary=list(range(nx+1))+[j*(nx+1)+nx for j in range(1,ny+1)]+[ny*(nx+1)+i for i in range(nx-1,-1,-1)]+[j*(nx+1) for j in range(ny-1,0,-1)]
 for a,b in zip(boundary,boundary[1:]+boundary[:1]):fs.append((a,b,b+layer,a+layer))
 mesh(name,vs,fs,cotton,bed)
 tube(name+'_PipedSeam',[(vs[i][0],vs[i][1],8.7) for i in boundary],.035,cotton,bed,True)
pillow('Pillow_Left',-43.7,51.4,14.5,9.2,1.15);pillow('Pillow_Right',-26.3,51.7,14.5,9.2,1.15)
# Duvet drapes beyond the true mattress edges; keep the upper surface clear of the mattress.
def duvet_z(x,y):
 local=x+35
 drop=1.75*max(0,abs(local)-17.85)+1.35*max(0,16.15-y)
 z=8.4-min(4.0,drop)+.12*math.sin(y*1.15+local*.33)*math.exp(-((abs(local)-15)/4)**2)+.07*math.sin(local*1.3+y*.32)
 return z+.12*math.exp(-((y-40.7-.3*math.sin(local*.3))/.65)**2)

nu=110;nv=110;vs=[];fs=[]
for j in range(nv+1):
 v=j/nv;y=14.2+30*v
 for i in range(nu+1):
  u=i/nu;x=-54.5+39*u;local=x+35
  z=duvet_z(x,y)
  vs.append((x+.07*math.sin(y*.7)*math.sin(math.pi*u),y+.06*math.sin(local*.8),z))
for j in range(nv):
 for i in range(nu):a=j*(nu+1)+i;fs.append((a,a+1,a+nu+2,a+nu+1))
mesh('Duvet_DrapedSageLinen',vs,fs,duvetmat,bed,.07)
tube('Duvet_FrontBinding',[vs[i] for i in range(nu+1)],.045,duvetmat,bed)
# Folded-back upper cuff has its own thin fabric surface.
cv=[];cf=[]
for j in range(22):
 t=j/21;y=39.7+3.6*t
 for i in range(91):
  x=-52+34*i/90;z=duvet_z(x,y)+.06+.10*math.sin(math.pi*t)
  cv.append((x,y,z))
for j in range(21):
 for i in range(90):a=j*91+i;cf.append((a,a+1,a+92,a+91))
mesh('Duvet_FoldedBackCuff',cv,cf,duvetmat,bed,.045)
for row in (0,21):tube('Duvet_CuffRolledEdge',[cv[row*91+i] for i in range(91)],.045,duvetmat,bed)
# Bedside cabinet: legs, carcass and inset drawers are separate joined pieces.
for x in (-12.8,-5.2):
 for y in (47.1,54.9):box('Nightstand_Leg',(x,y,1.4),(1.0,1.0,2.8),walnut,night,.08)
box('Nightstand_Carcass',(-9,51,6.5),(10,10,7.8),wood,night,.16)
box('Nightstand_Top',(-9,51,10.7),(10.5,10.5,.70),walnut,night,.13)
for z in (4.8,8.1):
 box('Drawer_Reveal',(-9,45.94,z),(9.2,.12,3.05),black,night,.06)
 box('Drawer_Front',(-9,45.78,z),(8.95,.35,2.82),wood,night,.11)
 tube('Drawer_Pull',[(-10.4,45.58,z),(-10.4,45.25,z),(-7.6,45.25,z),(-7.6,45.58,z)],.07,brass,night)
# Bedside lamp: hollow lampshade, supported stem, bulb and local warm illumination.
lathe('Lamp_CeramicBase',(-9,51,11.05),[(0,0),(1.7,0),(1.85,.2),(1.5,1.6),(.7,2.3),(.45,2.45)],ceramic,night)
lathe('Lamp_Stem',(-9,51,13.4),[(.17,0),(.17,4.2)],brass,night)
lampfabric=curtainmat.copy();lampfabric.name='Warm_LampShade';sp=lampfabric.node_tree.nodes.get('Principled BSDF');sp.inputs['Emission Color'].default_value=(1,.65,.30,1);sp.inputs['Emission Strength'].default_value=.10
lathe('Lamp_LinenShade',(-9,51,17.0),[(3.2,0),(2.5,5.1),(2.42,5.1),(3.12,0)],lampfabric,night)
for z,r in ((17,3.2),(22.1,2.5)):tube('Lamp_ShadeBinding',[(-9+r*math.cos(t),51+r*math.sin(t),z) for t in [i*math.tau/80 for i in range(80)]],.055,curtainmat,night,True)
bpy.ops.object.light_add(type='POINT',location=(-9,51,18.8));lamp=bpy.context.object;lamp.name='LIGHT_BedsideWarm';lamp.data.energy=110;lamp.data.color=(1,.66,.33);lamp.data.shadow_soft_size=.65;parent(lamp,night)
for t in (0,math.tau/3,math.tau*2/3):tube('Lamp_ShadeSupport',[(-9,51,17.4),(-9+3.12*math.cos(t),51+3.12*math.sin(t),17.1)],.045,brass,night)
# Desk under left wall, with joined legs, drawer, notebook and hollow mug.
box('Desk_Top',(-58,8.8,13.0),(10,14.5,.7),wood,desk,.16)
for x in (-61.6,-54.4):
 for y in (3.3,14.3):box('Desk_Leg',(x,y,6.25),(.8,.8,12.5),walnut,desk,.07)
box('Desk_DrawerBody',(-57,8.8,11.4),(6.6,12.9,2.2),wood,desk,.10)
box('Desk_DrawerFront',(-53.55,8.8,11.4),(.32,12.5,1.95),wood,desk,.07)
tube('Desk_DrawerHandle',[(-53.34,7.8,11.4),(-53.05,7.8,11.4),(-53.05,9.8,11.4),(-53.34,9.8,11.4)],.06,brass,desk)
# Chair with supported seat, legs and curved timber back.
for x in (-50.4,-45.6):
 for y in (6.3,11.3):tube('Chair_Leg',[(x,y,.12),(x+( .2 if x<-48 else -.2),y,7.1)],.32,walnut,chair)
box('Chair_SeatFrame',(-48,8.8,7.2),(6.8,7.0,.65),walnut,chair,.32)
box('Chair_SeatCushion',(-48,8.8,7.85),(6.4,6.6,.95),linen,chair,.40)
for y in (6.1,11.5):tube('Chair_BackUpright',[(-45.8,y,7),(-45.0,y,16.0)],.30,walnut,chair)
box('Chair_Backrest',(-45.15,8.8,14.5),(.8,6.4,3.9),walnut,chair,.35)
# Notebook and a closed book have actual page blocks between covers.
cover=material('Notebook_Cover',(.12,.20,.20),.68)
for z in (13.40,14.04):box('Notebook_Cover',(-58,7.4,z),(5.2,3.6,.10),cover,desk,.055)
box('Notebook_Pages',(-58,7.4,13.72),(5.02,3.43,.54),paper,desk,.045)
tube('Notebook_Elastic',[(-59.5,5.6,14.11),(-59.5,9.2,14.11)],.04,black,desk)
lathe('Desk_Mug',(-58.4,12.1,13.35),[(0,0),(.75,0),(.86,.10),(.88,1.65),(.76,1.65),(.73,.18),(0,.18)],ceramic,desk)
pts=[(-58.4+.85+.60*math.cos(t),12.1,14.18+.60*math.sin(t)) for t in [-math.pi/2+i*math.pi/48 for i in range(49)]]
tube('Desk_MugHandle',pts,.12,ceramic,desk)
# Framed art, with image graphic and separate mat, frame and backing.
art=bpy.data.images.new('WallArt_Graphic',width=768,height=384);pix=[]
for y in range(384):
 for x in range(768):
  u=x/767;v=y/383;c=(.70,.62,.48)
  if (u-.72)**2+(v-.72)**2<.09**2:c=(.84,.55,.24)
  if v<.38+.11*math.sin(u*6.1):c=(.34,.42,.35)
  if v<.20+.09*math.sin(u*7+2):c=(.17,.27,.25)
  pix.extend((*c,1))
art.pixels=pix;art.filepath_raw=O+'/textures/WallArt_Graphic.png';art.file_format='PNG';art.save()
artmat=material('WallArt_Ink',(.7,.6,.4),.9);tex=artmat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=art;artmat.node_tree.links.new(tex.outputs['Color'],artmat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
box('Art_Frame',(-35,63.12,34.5),(25,.65,14),walnut,decor,.08)
box('Art_MatBoard',(-35,62.74,34.5),(23.9,.14,12.9),cotton,decor,.01)
o=mesh('Art_PrintedGraphic',[(-45.6,62.64,29.4),(-24.4,62.64,29.4),(-24.4,62.64,39.6),(-45.6,62.64,39.6)],[(0,1,2,3)],artmat,decor)
for li,uv in zip(o.data.polygons[0].loop_indices,[(0,0),(1,0),(1,1),(0,1)]):o.data.uv_layers.active.data[li].uv=uv
# Plant pot, soil and leaves connected to stems. Leaves have curved midribs, not spheres.
lathe('Plant_TerracottaPot',(-6.5,59.8,0),[(0,0),(2.0,0),(2.7,5.1),(2.85,5.2),(2.85,5.65),(2.65,5.65),(2.5,5.15),(1.85,.4),(0,.4)],clay,plant)
lathe('Plant_Soil',(-6.5,59.8,4.95),[(0,0),(2.45,0)],soil,plant)
tube('Plant_MainStem',[(-6.5,59.8,4.9),(-6.6,59.8,13),(-6.2,59.5,21)],.12,walnut,plant)
for i in range(13):
 angle=i*2.40;z=8.5+i*.85;start=Vector((-6.5,59.8,z));tip=start+Vector((math.cos(angle)*3.0,math.sin(angle)*3.0,2.1));base=start+(tip-start)*.3
 tube('Plant_LeafStem',[tuple(start),tuple(base)],.045,walnut,plant)
 vs=[];fs=[];side=Vector((-math.sin(angle),math.cos(angle),0))
 for j in range(23):
  t=j/22;center=base+(tip-base)*t+Vector((0,0,.35*math.sin(t*math.pi)));width=.85*math.sin(math.pi*t)**.7
  for u in (-1,0,1):
   p=center+side*width*u;p.z-=.16*abs(u)*math.sin(math.pi*t);vs.append(tuple(p))
 for j in range(22):
  for k in range(2):a=j*3+k;fs.append((a,a+1,a+4,a+3))
 mesh('Plant_CurvedLeaf',vs,fs,green,plant,.009)
 tube('Plant_LeafMidrib',[vs[j*3+1] for j in range(23)],.018,green,plant)
# Lighting retained in Blender; FBX mesh export excludes light objects.
def area(name,co,target,energy,size,color):
 bpy.ops.object.light_add(type='AREA',location=co);o=bpy.context.object;o.name=name;o.data.energy=energy;o.data.shape='DISK';o.data.size=size;o.data.color=color;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
area('LIGHT_WindowSoft',(-60.5,32,32),(-30,30,6),16500,18,(1,.86,.68))
area('LIGHT_FrontFill',(10,-25,44),(-32,35,12),13500,35,(.76,.85,1))
area('LIGHT_BackBounce',(-35,55,43),(-35,25,7),5000,20,(1,.76,.51))
s.world.color=(.045,.045,.045)
# Display geometry references, kept separate and hidden from room beauty renders.
guides=bpy.data.collections.new('DISPLAY_GUIDES_64x48cm');s.collection.children.link(guides)
def move_to_guides(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 guides.objects.link(o);o.hide_render=True
for name,pts in [('LEFT',[(-64,0,0),(0,0,0),(0,0,48),(-64,0,48)]),('RIGHT',[(0,0,0),(0,64,0),(0,64,48),(0,0,48)])]:
 o=tube('DISPLAY_'+name+'_64x48cm',pts,.08,black,None,True);move_to_guides(o)
eye=Vector((150/math.sqrt(2),-150/math.sqrt(2),24))
viewer=bpy.data.objects.new('VIEWER_150cm_CentreHeight',None);guides.objects.link(viewer);viewer.location=eye
# Off-axis cameras derive directly from the two physical screen rectangles.
layout={'units':'cm','coordinate_system':'Blender source coordinates, right-handed Z-up; Unreal axis mapping requires checking after import','room_bounds':{'x':[-64,0],'y':[0,64],'z':[0,48]},'observer':list(eye),'screen_angle_degrees':90,'per_face_pixels':[256,192],'output_strip_pixels':[512,192],'unreal_runtime_tested':False,'screens':[]}
for label,pa,pb,pc in [('Left',(-64,0,0),(0,0,0),(-64,0,48)),('Right',(0,0,0),(0,64,0),(0,0,48))]:
 pa,pb,pc=map(Vector,(pa,pb,pc));vr=(pb-pa).normalized();vu=(pc-pa).normalized();vn=vr.cross(vu).normalized();d=-(pa-eye).dot(vn)
 bpy.ops.object.camera_add(location=eye);cam=bpy.context.object;cam.name='DISPLAY_'+label+'_OffAxis';cam.rotation_euler=Matrix((vr,vu,vn)).transposed().to_euler();cam.data.type='PERSP';cam.data.sensor_fit='HORIZONTAL';cam.data.sensor_width=36;cam.data.lens=36*d/64
 cam.data.shift_x=((pa+pb)/2-eye).dot(vr)/64;cam.data.shift_y=((pa+pc)/2-eye).dot(vu)/64
 cam.data.clip_start=.1;cam.data.clip_end=1000
 layout['screens'].append({'name':label,'bottom_left':list(pa),'bottom_right':list(pb),'top_left':list(pc),'camera':cam.name,'lens_mm':cam.data.lens,'shift_x':cam.data.shift_x,'shift_y':cam.data.shift_y})
open(O+'/display_layout_reference.json','w').write(json.dumps(layout,indent=2))
# Export room meshes with named furniture groups; leave cameras and lights in source only.
bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
for o in root.children_recursive:
 if o.type in ('MESH','EMPTY'):o.select_set(True)
bpy.context.view_layer.objects.active=root
bpy.ops.export_scene.fbx(filepath=O+'/Bedroom_v01_cm.fbx',use_selection=True,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',add_leaf_bones=False,bake_anim=False,path_mode='COPY',embed_textures=True)
bpy.ops.export_scene.gltf(filepath=O+'/Bedroom_v01.glb',use_selection=True,export_apply=True)
# Reusable cinematic room view.
bpy.ops.object.camera_add(location=(67,-83,56));cam=bpy.context.object;cam.name='CAM_RoomOverview';cam.rotation_euler=(Vector((-33,34,17))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP';cam.data.lens=46;cam.data.clip_end=1000;s.camera=cam
s.render.engine='CYCLES';s.cycles.samples=64;s.cycles.use_denoising=False;s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=.65;s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=O+'/Bedroom_v01.blend')
s.render.filepath=O+'/preview_room.png';bpy.ops.render.render(write_still=True)
s.camera.location=(-8,1,27);s.camera.rotation_euler=(Vector((-38,42,13))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=31;s.render.resolution_x=1300;s.render.resolution_y=1000;s.render.filepath=O+'/preview_bed_detail.png';bpy.ops.render.render(write_still=True)
# Actual per-face reference outputs at panel resolution, with the fixed observer.
s.render.resolution_x=256;s.render.resolution_y=192;s.cycles.samples=48
bpy.data.objects['Ceiling_Panel_DisplayOnly'].hide_render=False
for label in ('Left','Right'):
 s.camera=bpy.data.objects['DISPLAY_'+label+'_OffAxis'];s.render.filepath=O+'/display_'+label.lower()+'_256x192.png';bpy.ops.render.render(write_still=True)
print('ROOM_COMPLETE')
