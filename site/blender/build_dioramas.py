import bpy, math, os, json
from mathutils import Vector
from pathlib import Path
import argparse, sys
REPO=Path(__file__).resolve().parents[2]
OUT=REPO/'site/public/dioramas'
RENDERS=REPO/'docs/dioramas'
OUT.mkdir(parents=True,exist_ok=True); RENDERS.mkdir(parents=True,exist_ok=True)
PALETTE={'skin':'C89473','hair':'574338','beard':'6E594B','jacket':'303C50','shirt':'9BAF9C','pants':'53677E','boot':'695044','sole':'363B40','blue':'729BCB','metal':'B4BFC7','dark':'303943','wood':'C8A47E','ivory':'F4EEE0','sage':'91A38C','clay':'C98F72'}
MATS={}; CURRENT=None; counter=0

def color(hex):
 h=PALETTE.get(hex,hex).strip('#');return tuple((int(h[i:i+2],16)/255)**2.2 for i in (0,2,4))
def material(c,metal=0,emission=0):
 key=(c,metal,emission)
 if key in MATS:return MATS[key]
 m=bpy.data.materials.new('MAT_'+c);m.diffuse_color=(*color(c),1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color(c),1);bs.inputs['Roughness'].default_value=.48 if metal else .72;bs.inputs['Metallic'].default_value=metal
 if emission:bs.inputs['Emission Color'].default_value=(*color(c),1);bs.inputs['Emission Strength'].default_value=emission
 MATS[key]=m;return m

def pos(v):return Vector((v[0],-v[2],v[1]))
def finish(o,name,c,parent=None):
 o.name=name;o.data.materials.append(material(c, .62 if c=='metal' else 0));
 if parent:o.parent=parent
 for poly in o.data.polygons:poly.use_smooth=True
 return o

def empty(name,x=0,y=0,z=0,parent=None,rot=0):
 o=bpy.data.objects.new(name,None);CURRENT.collection.objects.link(o);o.location=pos((x,y,z));o.rotation_euler[2]=rot
 if parent:o.parent=parent
 return o

def box(name,w,h,d,c,x=0,y=0,z=0,parent=None,bevel=.035):
 bpy.ops.mesh.primitive_cube_add(size=1,location=pos((x,y,z)));o=bpy.context.object;o.scale=(w,d,h);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 b=o.modifiers.new('Soft crafted edges','BEVEL');b.width=min(bevel,min(w,h,d)*.32);b.segments=3
 n=o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
 return finish(o,name,c,parent)
def sphere(name,r,c,x=0,y=0,z=0,parent=None,scale=(1,1,1)):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=r,location=pos((x,y,z)));o=bpy.context.object;o.scale=(scale[0],scale[2],scale[1]);return finish(o,name,c,parent)
def cylinder(name,r,h,c,x=0,y=0,z=0,parent=None,top=None):
 if top is not None:
  bpy.ops.mesh.primitive_cone_add(vertices=24,radius1=r,radius2=top,depth=h,location=pos((x,y,z)))
 else:bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=h,location=pos((x,y,z)))
 o=bpy.context.object;b=o.modifiers.new('Edge finish','BEVEL');b.width=min(.018,h*.1,r*.15);b.segments=2;return finish(o,name,c,parent)
def rod(name,a,b,r,c,parent=None):
 v1,v2=pos(a),pos(b);o=cylinder(name,r,(v2-v1).length,c,parent=parent);o.location=(v1+v2)/2;o.rotation_euler=(v2-v1).to_track_quat('Z','Y').to_euler();return o

def ring(name,r,tube,c,x=0,y=0,z=0,parent=None,flat=False):
 bpy.ops.mesh.primitive_torus_add(major_segments=32,minor_segments=10,location=pos((x,y,z)),major_radius=r,minor_radius=tube)
 o=bpy.context.object
 if not flat:o.rotation_euler[0]=math.pi/2
 return finish(o,name,c,parent)
def text(name,words,size,c,x,y,z,parent=None):
 curve=bpy.data.curves.new(name,'FONT');curve.body=words;curve.align_x='CENTER';curve.align_y='CENTER';curve.size=size;curve.extrude=.0015;curve.bevel_depth=.0004
 o=bpy.data.objects.new(name,curve);CURRENT.collection.objects.link(o);o.location=pos((x,y,z));o.rotation_euler[0]=math.pi/2
 if parent:o.parent=parent
 curve.materials.append(material(c));return o

def plant(x,z,s=1,parent=None):
 p=empty('Potted greenery',x,0,z,parent);p.scale=(s,s,s);cylinder('Terracotta planter',.18,.33,'clay',0,.17,0,p,top=.23);cylinder('Soil',.20,.013,'574C3B',0,.342,0,p)
 for i in range(7):
  a=i*2.4;tip=(math.cos(a)*.23,.59+(i%3)*.12,math.sin(a)*.23);rod('Stem',(0,.33,0),tip,.012,'687A60',p);o=sphere('Leaf',.13,'sage',*tip,p,scale=(.6,1.6,.4));o.rotation_euler[1]=math.cos(a)*.5
 return p

def camera(parent,x,y,z,s=1):
 p=empty('Camera',x,y,z,parent);p.scale=(s,s,s);box('Camera body',.4,.27,.18,'dark',parent=p,bevel=.05);box('Viewfinder',.13,.07,.15,'dark',0,.16,0,p)
 lens=cylinder('Lens barrel',.115,.22,'dark',0,0,.15,p);lens.rotation_euler[0]=math.pi/2;ring('Focus ring',.107,.019,'metal',0,0,.255,p)
 gl=cylinder('Lens glass',.086,.008,'5B7D99',0,0,.271,p);gl.rotation_euler[0]=math.pi/2
 sphere('Shutter',.02,'metal',.14,.15,.02,p);return p

def character(parent,x=0,z=0,pose='stand',rot=0):
 root=empty('MICHAEL',x,0,z,parent,rot);seated=pose in ('desk','ride','family');hip=.75 if seated else (.35 if pose=='kneel-low' else .48 if pose=='kneel' else .92)
 box('Hips',.43,.21,.31,'pants',0,hip,0,root,bevel=.07)
 for side in (-1,1):
  sx=side*.14
  if pose in ('kneel','kneel-low'):
   knee=(sx,.15,-.21) if side==-1 else (sx,.42,.35)
   ankle=(sx,.12,-.50) if side==-1 else (sx,.13,.38)
   rod('Kneeling thigh',(sx,hip,0),knee,.098,'pants',root);rod('Kneeling shin',knee,ankle,.084,'pants',root);footz=ankle[2]+.08
  elif seated:
   rod('Thigh',(sx,hip,0),(sx,.735,.40),.098,'pants',root);rod('Shin',(sx,.735,.40),(sx,.17,.50),.084,'pants',root);footz=.58
  else:
   rod('Trouser leg',(sx,hip,0),(sx,.16,.015),.101,'pants',root);footz=.08
  box('Boot',.215,.16,.36,'boot',sx,.13,footz,root,bevel=.055);box('Sole',.222,.044,.37,'sole',sx,.063,footz,root,bevel=.015)
  for j in range(3):box('Boot laces',.115,.012,.015,'BCA98D',sx,.21,footz-.01+j*.04,root,bevel=.003)
 body=empty('TORSO',0,hip+.13,0,root)
 jacket='ivory' if pose=='cook' else 'jacket';box('Jacket body',.62,.69,.39,jacket,0,.31,0,body,bevel=.1);box('Shirt',.2,.52,.016,'shirt',0,.32,.20,body,bevel=.008)
 for side in (-1,1):
  lapel=box('Lapel',.08,.42,.034,jacket,side*.145,.37,.218,body,bevel=.008);lapel.rotation_euler[1]=side*.17
  box('Pocket',.135,.07,.022,jacket,side*.21,.43,.22,body,bevel=.013)
 for j in range(3):sphere('Shirt buttons',.012,'ivory',0,.23+j*.12,.219,body)
 cylinder('Neck',.103,.14,'skin',0,.72,0,body)
 head=empty('HEAD',0,.95,0,body);sphere('Face',.286,'skin',0,.012,0,head,scale=(1,1.15,.92));sphere('Short beard',.255,'beard',0,-.086,-.005,head,scale=(.99,.66,.9))
 sphere('Muzzle',.112,'skin',0,-.065,.212,head,scale=(1,.63,.40));box('Smile',.075,.012,.009,'705348',0,-.094,.257,head,bevel=.006)
 sphere('Goatee',.109,'beard',0,-.181,.206,head,scale=(.91,.83,.45))
 for side in (-1,1):
  sphere('Moustache',.062,'8C7560',side*.052,-.059,.259,head,scale=(1.15,.4,.29))
  sphere('Silver at the temples',.064,'95887A',side*.259,.113,-.01,head,scale=(.33,1,.8))
 for side in (-1,1):sphere('Ear',.064,'skin',side*.28,.016,-.01,head,scale=(.6,1,.75))
 sphere('Hair cap',.29,'hair',0,.185,-.048,head,scale=(1,.65,.88))
 for i in range(6):
  o=sphere('Swept hair',.102,['hair','6B5747','7B6756'][i%3],-.185+i*.072,.275+i*.009,-.04,head,scale=(.69,.78,1.7));o.rotation_euler[1]=-.35
 # Features sit on the face sphere's real surface, so nothing hovers in front of it.
 def skin(x,y):return .286*.92*math.sqrt(max(0,1-(x/.286)**2-((y-.012)/(.286*1.15))**2))
 inner=[]
 for side in (-1,1):
  xx=side*.129;d=skin(xx,.052)
  sphere('Eye white',.040,'F1E8DC',xx,.052,d+.002,head,scale=(1,.71,.25));sphere('Eye',.023,'35474E',xx,.052,d+.009,head,scale=(.8,1,.38));sphere('Eye catchlight',.007,'FFFFFF',xx-.004,.06,d+.016,head)
  # Each lens is a small frame tilted to follow the cheek, resting just proud of the eye.
  tilt=math.atan2(skin(side*.05,.055)-skin(side*.21,.055),.16);lens_d=skin(xx,.055)+.034
  lens=empty('Glasses lens',xx,.055,lens_d,head,side*tilt)
  box('Blue pearl glasses top',.17,.024,.024,'blue',0,.05,0,lens,bevel=.009);box('Blue pearl glasses bottom',.17,.024,.024,'blue',0,-.05,0,lens,bevel=.009)
  for k in (-1,1):box('Glasses rim',.024,.124,.024,'blue',k*.081,0,0,lens,bevel=.009)
  ox=xx+side*.081*math.cos(tilt);od=lens_d-.081*math.sin(tilt);inner.append(lens_d+.081*math.sin(tilt))
  rod('Glasses temple',(ox+side*.008,.075,od-.01),(side*.283,.066,-.02),.012,'blue',head)
  brow=box('Brow',.11,.025,.018,'hair',xx,.145,skin(xx,.145)+.01,head,bevel=.012);brow.rotation_euler[1]=side*.06;brow.rotation_euler[2]=side*tilt
 box('Glasses bridge',.08,.018,.022,'blue',0,.072,max(inner),head,bevel=.006);sphere('Nose',.058,'skin',0,.015,.278,head,scale=(.66,.88,1.07))
 arms=[]
 for side in (-1,1):
  ar=empty('ARM_R' if side==1 else 'ARM_L',side*.34,.54,0,body);elbow=(side*.05,-.27,.055);hand=(side*.055,-.54,.09)
  if pose in ('desk','family'):elbow=(side*.07,-.15,.26);hand=(side*.02,-.13,.55)
  if pose in ('kneel','kneel-low'):elbow=(side*.025,-.30,.22);hand=(-side*.04,-.58 if pose=='kneel-low' else -.48,.53)
  if pose=='photo':elbow=(side*.15,-.02,.27);hand=(-side*.11,.36,.38)
  if pose=='ride':elbow=(side*.06,-.29,.42);hand=(side*.03,-.32,.94)
  if pose=='arts':elbow=(side*.02,-.24,.26);hand=(-side*.12,-.28,.59)
  if pose=='cook' and side==1:elbow=(.1,-.20,.24);hand=(.03,-.08,.64)
  if pose=='mechanic' and side==1:elbow=(.07,-.24,.27);hand=(.025,-.29,.56)
  if pose=='event' and side==-1:elbow=(-.07,-.22,.22);hand=(.04,-.23,.36)
  rod('Upper sleeve',(0,0,0),elbow,.094,jacket,ar);sphere('Elbow',.094,jacket,*elbow,ar);rod('Forearm',elbow,hand,.068,'skin',ar);sphere('Hand',.086,'skin',*hand,ar,scale=(.85,1,1));arms.append(ar)
 if pose=='photo':
  cam=camera(body,0,.85,.49,.87);cam.rotation_euler[0]=.32;head.rotation_euler[0]=.17
 if pose=='event':
  board=box('Clipboard',.34,.43,.042,'wood',-.28,.23,.46,body);board.rotation_euler[0]=-.2;box('Notes',.275,.33,.013,'ivory',-.28,.24,.49,body);box('Clip',.08,.045,.02,'metal',-.28,.44,.50,body)
 if pose=='cook':
  box('Apron',.46,.61,.023,'6E9389',0,.2,.222,body,bevel=.05);rod('Apron strap',(-.19,.64,.21),(-.18,.43,.25),.023,'6E9389',body);rod('Apron strap',(.19,.64,.21),(.18,.43,.25),.023,'6E9389',body);rod('Spoon',(.37,.46,.66),(.28,.18,.91),.016,'wood',body);sphere('Spoon bowl',.065,'wood',.28,.18,.91,body,scale=(.65,.2,1.1))
 if pose=='mechanic':
  rod('Wrench handle',(.36,.25,.58),(.36,.12,.78),.024,'metal',body);ring('Wrench head',.057,.018,'metal',.36,.1,.8,body)
 return root,head,arms

def desk(parent,x,z,w=2.5):
 p=empty('DESK',x,0,z,parent);box('Oak desktop',w,.13,1.05,'wood',0,1.05,0,p)
 for a in (-1,1):
  for b in (-1,1):box('Desk leg',.065,1.02,.065,'metal',a*(w/2-.13),.51,b*.4,p)
 return p

def screen(p,x,y,z,w=1.1,h=.7):
 q=empty('Monitor',x,y,z,p);box('Foot',.38,.035,.24,'metal',0,.02,.05,q);box('Stand',.05,.23,.05,'metal',0,.12,0,q);box('Monitor frame',w,h,.075,'dark',0,.23+h/2,0,q);box('Screen glass',w-.07,h-.07,.012,'263C53',0,.23+h/2,.044,q)
 for i in range(6):
  width=w*(.25+(i%3)*.16);box('Code line',width,.018,.005,['A9C6CD','B8AED3','DDC8A0'][i%3],-(w-.15-width)/2,.32+i*.075,.053,q,bevel=.002)
 return q

def motorcycle(parent,x=0,z=0,s=1):
 p=empty('MOTORCYCLE',x,0,z,parent);p.scale=(s,s,s)
 # A low road-bike silhouette: smooth tires, a stepped saddle and twin rear shocks.
 for xx in (-1.0,1.02):
  wheel=empty('WHEEL',xx,.46,0,p);ring('Road tire',.35,.10,'dark',parent=wheel);ring('Chrome rim',.272,.024,'metal',parent=wheel)
  for i in range(20):
   a=i*math.tau/20;rod('Spoke',(0,0,0),(math.cos(a)*.27,math.sin(a)*.27,0),.007,'metal',wheel)
  axle=cylinder('Hub',.072,.28,'metal',parent=wheel);axle.rotation_euler[0]=math.pi/2
  disc=cylinder('Brake disc',.16,.018,'metal',0,0,.135,wheel);disc.rotation_euler[0]=math.pi/2
 for zz in (-.15,.15):
  for a,b in [((-1.,.46,zz),(-.47,.48,zz)),((-.47,.48,zz),(.38,.43,zz)),((.38,.43,zz),(.59,1.16,zz)),((.59,1.16,zz),(-.54,.95,zz)),((-.54,.95,zz),(-.47,.48,zz))]:rod('Cradle frame',a,b,.032,'dark',p)
  rod('Front fork',(.61,1.19,zz),(1.02,.46,zz),.034,'metal',p)
  rod('Fork slider',(.85,.76,zz),(1.02,.46,zz),.045,'metal',p)
  low=(-.98,.49,zz*1.6);high=(-.59,.98,zz*1.6)
  shock=empty('Exposed rear shock',*low,p)
  shock.rotation_euler=(pos(high)-pos(low)).to_track_quat('Z','Y').to_euler()
  length=(pos(high)-pos(low)).length
  cylinder('Shock damper',.035,length,'dark',0,length/2,0,shock)
  for j in range(10):ring('Shock spring',.051,.012,'metal',0,.08+j*.045,0,shock,flat=True)
 # The separate, canted banks remain readable below the tank from either side.
 engine=empty('V_TWIN_ENGINE',-.06,.53,0,p)
 case=cylinder('Crankcase',.215,.36,'798891',parent=engine);case.rotation_euler[0]=math.pi/2
 cover=cylinder('Timing cover',.15,.035,'metal',0,0,.20,engine);cover.rotation_euler[0]=math.pi/2
 for side in (-1,1):
  bank=empty('V_TWIN_REAR_CYLINDER' if side<0 else 'V_TWIN_FRONT_CYLINDER',side*.09,.08,0,engine)
  bank.rotation_euler[1]=side*math.radians(22.5)
  cylinder('Black cylinder barrel',.122,.32,'dark',0,.20,0,bank)
  for j in range(7):box('Cylinder cooling fin',.29,.018,.31,'metal',0,.07+j*.047,0,bank,bevel=.006)
  box('Rocker cover',.31,.09,.32,'metal',0,.405,0,bank,bevel=.025)
  for xx in (-.075,.075):rod('Pushrod tube',(xx,.04,.16),(xx,.365,.16),.012,'metal',bank)
  cable('Swept exhaust header',[(side*.23,.91,.18),(side*.29,.84,.29),(.16+side*.09,.59,.32),(.10,.39+side*.07,.34),(-.92,.39+side*.07,.34)],p,.035,'metal')
  rod('Twin exhaust silencer',(-.38,.39+side*.07,.34),(-1.10,.39+side*.07,.34),.051,'metal',p)
 cleaner=cylinder('Air cleaner',.115,.055,'metal',.05,.78,.24,p);cleaner.rotation_euler[0]=math.pi/2
 sphere('Teardrop petrol tank',.30,'829AA9',.19,1.22,0,p,scale=(1.45,.60,.80))
 cylinder('Fuel cap',.047,.019,'metal',.27,1.405,0,p)
 box('Low rider saddle',.48,.10,.34,'boot',-.55,1.00,0,p,bevel=.055)
 box('Raised pillion',.30,.12,.30,'boot',-.91,1.065,0,p,bevel=.055)
 for j in range(4):box('Seat stitching',.01,.008,.27,'957862',-.71+j*.10,1.053,0,p,bevel=.003)
 # Narrow curved steel fenders hug the road tires instead of adding off-road bulk.
 for xx,width in [(-1.,.29),(1.02,.24)]:
  vertices=[];faces=[]
  for j in range(21):
   angle=math.radians(25+j*6.5)
   for zz in (-width/2,width/2):vertices.append(pos((xx+math.cos(angle)*.475,.46+math.sin(angle)*.475,zz)))
  for j in range(20):faces.append((2*j,2*j+1,2*j+3,2*j+2))
  mesh=bpy.data.meshes.new('Rolled fender');mesh.from_pydata(vertices,[],faces);mesh.update()
  fender=bpy.data.objects.new('Road fender',mesh);CURRENT.collection.objects.link(fender);finish(fender,'Road fender','829AA9',p)
  solid=fender.modifiers.new('Fender thickness','SOLIDIFY');solid.thickness=.022
 rod('Handlebar riser',(.59,1.16,0),(.57,1.37,0),.027,'metal',p)
 cable('Pullback handlebar',[(.40,1.40,-.34),(.55,1.43,-.23),(.57,1.37,0),(.55,1.43,.23),(.40,1.40,.34)],p,.024,'metal')
 for zz in (-.34,.34):rod('Grip',(.40,1.40,zz),(.27,1.39,zz),.032,'dark',p)
 lamp=cylinder('Round headlight housing',.13,.18,'metal',.77,1.17,0,p);lamp.rotation_euler[1]=math.pi/2
 glass=cylinder('Round headlight',.112,.012,'F5E4BA',.865,1.17,0,p);glass.rotation_euler[1]=math.pi/2
 for zz in (-.15,.15):rod('Foot peg',(-.17,.45,zz),(-.17,.45,zz*2.6),.028,'dark',p)
 sphere('Tail light',.045,'B86253',-1.25,.89,0,p)
 return p

def tripod(p,x,z,h=2):
 for i in range(3):
  a=i*math.pi*2/3;rod('Tripod foot',(x,.7,z),(x+math.cos(a)*.35,.05,z+math.sin(a)*.35),.022,'dark',p)
 rod('Tripod stem',(x,.25,z),(x,h,z),.023,'metal',p)

def base(p,c):
 box('Square floating plinth',5.2,.34,5.2,c,0,-.18,0,p,bevel=.12);box('Ivory lower edge',5.23,.065,5.23,'ivory',0,-.38,0,p,bevel=.035)

def family_person(p,name,x,z,scale=.7,seated=True,working=False):
 root=empty(name,x,0,z,p);root.scale=(scale,scale,scale);hip=.7 if seated else .94
 cloth='C8A3C0' if name=='DAUGHTER' else 'B4BDA4'
 box('Soft sweater',.56,.62,.35,cloth,0,hip+.4,0,root,bevel=.11)
 box('Jeans',.43,.20,.32,'7589A2',0,hip,0,root,bevel=.07)
 for side in (-1,1):
  footz=.49 if seated else .08
  rod('Leg',(side*.13,hip,0),(side*.15,.18,footz-.09),.083,'7589A2',root)
  box('Sneaker',.2,.14,.29,'ivory',side*.15,.13,footz,root,bevel=.05)
 neck=hip+.76;cylinder('Neck',.085,.14,'skin',0,neck,0,root)
 head=empty('HEAD_'+name,0,neck+.25,0,root)
 sphere('Hair back',.30,'655047',0,.04,-.075,head,scale=(1,1.25,.7))
 sphere('Face',.26,'skin',0,0,.01,head,scale=(1,1.1,.91))
 sphere('Hair crown',.27,'655047',0,.17,-.048,head,scale=(1,.64,.95))
 for side in (-1,1):
  sphere('Hair side',.09,'655047',side*.235,-.04,-.055,head,scale=(.65,2.2,.8))
  sphere('Eye',.024,'dark',side*.105,.025,.01+.26*.91*math.sqrt(1-(.105/.26)**2-(.025/.286)**2)+.004,head,scale=(.8,1,.3))
 sphere('Nose',.044,'skin',0,-.023,.258,head)
 box('Smile',.072,.013,.009,'81574E',0,-.092,.243,head,bevel=.005)
 if name=='DAUGHTER':
  sphere('Ponytail',.13,'655047',.2,.06,-.27,head,scale=(.8,1.75,.9))
  ring('Hair tie',.063,.014,'C99567',.2,.15,-.21,head)
 for side in (-1,1):
  arm=empty('ARM_R_'+name if side==1 else 'ARM_L_'+name,side*.29,hip+.61,0,root)
  elbow=(side*.04,-.28,.18 if seated else .02);hand=(side*.015,-.33,.49) if seated else (-side*.13,-.42,.20)
  if working:elbow=(side*.04,-.22,.23);hand=(-side*.08,-.30,.51)
  rod('Sweater sleeve',(0,0,0),elbow,.085,cloth,arm);rod('Forearm',elbow,hand,.058,'skin',arm);sphere('Hand',.072,'skin',*hand,arm)
 return root

def bmx(p,x=0,z=0):
 q=empty('BMX_BICYCLE',x,0,z,p)
 # Twenty-inch wheels relative to the family, with a short rear triangle and low seat.
 for xx in (-.73,.73):
  wheel=empty('MOTION_bmx_wheel',xx,.365,0,q)
  ring('BMX tire',.275,.047,'dark',parent=wheel);ring('Alloy rim',.232,.014,'metal',parent=wheel)
  for i in range(24):
   angle=i*math.pi/12;rod('BMX spoke',(0,0,0),(math.cos(angle)*.23,math.sin(angle)*.23,0),.0045,'metal',wheel)
  hub=cylinder('BMX axle',.037,.24,'metal',parent=wheel);hub.rotation_euler[0]=math.pi/2
  for side in (-1,1):
   peg=cylinder('Axle peg',.027,.14,'dark',0,0,side*.16,wheel);peg.rotation_euler[0]=math.pi/2
 rear=(-.73,.365,0);crank=(-.13,.32,0);seat=(-.30,.78,0);head=(.43,.89,0)
 for name,v1,v2 in [('Top tube',seat,head),('Down tube',head,crank),('Seat tube',crank,seat)]:rod(name,v1,v2,.032,'729BCB',q)
 for side in (-1,1):
  rr=(rear[0],rear[1],side*.065);cc=(crank[0],crank[1],side*.05);ss=(seat[0],seat[1],side*.03)
  rod('Chain stay',rr,cc,.020,'729BCB',q);rod('Seat stay',rr,ss,.019,'729BCB',q)
  rod('BMX fork',(.43,.89,side*.065),(.73,.365,side*.065),.023,'metal',q)
 rod('Short seatpost',(-.30,.76,0),(-.32,.85,0),.021,'metal',q)
 box('Low BMX saddle',.29,.07,.18,'boot',-.35,.86,0,q,bevel=.045)
 rod('Stem',(.43,.89,0),(.44,.97,0),.024,'metal',q)
 rod('Handlebar crossbar',(.42,1.055,-.19),(.42,1.055,.19),.017,'metal',q)
 rod('Bar base',(.44,.97,-.12),(.44,.97,.12),.020,'metal',q)
 for side in (-1,1):
  rod('BMX bar rise',(.44,.97,side*.12),(.39,1.17,side*.22),.020,'metal',q)
  rod('BMX grips',(.39,1.17,side*.21),(.36,1.17,side*.35),.028,'dark',q)
 # Drivetrain faces Dad, who kneels on this side of the bike.
 ring('Chainring',.09,.014,'metal',-.13,.32,-.14,q)
 ring('Rear sprocket',.037,.010,'metal',-.73,.365,-.14,q)
 rod('Top chain run',(-.13,.41,-.14),(-.73,.402,-.14),.009,'dark',q)
 rod('Lower chain run',(-.13,.23,-.14),(-.73,.328,-.14),.009,'dark',q)
 for side in (-1,1):
  rod('Crank arm',(-.13,.32,side*.15),(-.13-side*.13,.32+side*.08,side*.15),.016,'metal',q)
  box('Platform pedal',.12,.041,.14,'dark',-.13-side*.13,.32+side*.08,side*.20,q,bevel=.012)
 text('Frame decal','BMX',.067,'ivory',.10,.82,.036,q)
 return q


# Every major assembly has one transform, a practical footprint, and a clear role.
# Coordinates throughout are x / height / depth; positive depth faces the visitor.
def face_toward(obj,x,z):
 here=obj.location;obj.rotation_euler[2]=math.atan2(x-here.x,z+here.y)

def cable(name,points,parent,r=.014,c='dark'):
 curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.bevel_depth=r;curve.bevel_resolution=2
 spline=curve.splines.new('POLY');spline.points.add(len(points)-1)
 for point,xyz in zip(spline.points,points):point.co=(*pos(xyz),1)
 obj=bpy.data.objects.new(name,curve);CURRENT.collection.objects.link(obj);obj.parent=parent;curve.materials.append(material(c));return obj

def tray(parent,x,y,z,w=.52,d=.32):
 q=empty('Organized parts tray',x,y,z,parent)
 box('Tray base',w,.025,d,'dark',0,0,0,q)
 for xx in (-w/2,w/2):box('Tray side',.024,.065,d,'metal',xx,.025,0,q)
 for zz in (-d/2,d/2):box('Tray rim',w,.065,.024,'metal',0,.025,zz,q)
 return q

def wrench(parent,x,y,z,length=.24):
 rod('Service wrench',(x,y,z),(x,y+length,z),.018,'metal',parent)
 ring('Service wrench jaw',.044,.012,'metal',x,y+length+.035,z,parent)

def cabinet(parent,x,z,w=.85,h=.85,d=.58,c='78938A'):
 q=empty('Tool cabinet',x,0,z,parent)
 box('Cabinet body',w,h,d,c,0,h/2+.07,0,q)
 box('Worktop',w+.05,.06,d+.05,'wood',0,h+.10,0,q)
 for i in range(4):
  yy=.18+i*(h-.12)/4;box('Inset drawer',w-.09,(h-.16)/4,.018,c,0,yy,d/2+.012,q)
  box('Drawer handle',w*.38,.024,.035,'metal',0,yy+.035,d/2+.045,q)
 for xx in (-w*.35,w*.35):
  for zz in (-d*.32,d*.32):sphere('Cabinet caster',.063,'dark',xx,.064,zz,q)
 return q

def pegboard(parent,x,y,z,w=1.4,h=.75):
 q=empty('Organized tool board',x,y,z,parent)
 box('Pegboard panel',w,h,.05,'C0A98D',parent=q)
 for row in range(4):
  for col in range(7):sphere('Pegboard hole',.011,'897865',-w*.43+col*w*.143,-h*.38+row*h*.25,.03,q)
 for i in range(4):wrench(q,-w*.34+i*w*.22,-h*.25,.067,.25)
 return q

def ai(p):
 work=empty('AI_WORKSTATION',-.15,0,-.15,p,-.48)
 box('Workstation rug',3.65,.025,2.9,'B4C4D7',0,.013,.22,work)
 d=desk(work,0,-.58,2.65)
 # One primary display and a secondary angled toward the same seated operator.
 screen(d,-.40,1.125,-.29,1.16,.72)
 secondary=screen(d,.66,1.125,-.20,.78,.61);secondary.rotation_euler[2]=-.18
 box('Desk mat',1.62,.016,.47,'758C9D',-.10,1.125,.26,d)
 box('Keyboard',.83,.028,.25,'C3CCD0',-.26,1.146,.27,d)
 for i in range(9):
  for j in range(3):box('Key',.055,.007,.048,'8C9EA9',-.58+i*.078,1.164,.19+j*.07,d,bevel=.003)
 box('Mouse',.14,.045,.2,'C3CCD0',.48,1.16,.27,d,bevel=.045)
 cylinder('Cup coaster',.13,.012,'boot',1.02,1.128,.30,d)
 cylinder('Coffee cup',.083,.15,'clay',1.02,1.21,.30,d);ring('Mug handle',.045,.014,'clay',1.12,1.23,.30,d)
 # The tower lives under the desktop, with cables routed along its rear edge.
 box('Computer tower',.38,.75,.53,'586A7D',1.04,.40,-.63,work)
 for i in range(4):
  box('Server vent',.26,.021,.012,'99AEBC',1.04,.23+i*.13,-.359,work)
  sphere('Status light',.012,'BFE3C0',1.18,.23+i*.13,-.35,work)
 cable('Display cable',[(-.40,1.35,-.94),(-.40,.95,-1.02),(1.04,.95,-1.02),(1.04,.63,-.91)],work)
 c,h,a=character(work,-.23,.22,'desk',math.pi);h.rotation_euler[2]=-.38
 chair=empty('Task chair',-.23,0,.22,work)
 box('Chair seat',.65,.11,.59,'788FA6',0,.57,0,chair)
 box('Chair back',.66,.58,.1,'788FA6',0,.90,.31,chair,bevel=.07)
 rod('Chair support',(0,.12,0),(0,.54,0),.052,'metal',chair)
 for i in range(5):
  angle=i*math.tau/5;end=(math.cos(angle)*.35,.08,math.sin(angle)*.35)
  rod('Chair feet',(0,.14,0),end,.024,'metal',chair);sphere('Caster',.047,'dark',*end,chair)
 # A useful storage nook, with grouped books and a closed project archive.
 shelf=empty('Project library',-1.94,0,-1.68,p)
 for i in range(3):box('Library shelf',1.02,.055,.48,'wood',0,.38+i*.54,0,shelf)
 for xx in (-.47,.47):box('Library upright',.04,1.52,.04,'metal',xx,.76,-.17,shelf)
 for i in range(5):box('Reference book',.11,.31+(i%2)*.05,.29,['9CABC0','BDA8C3','C9B08A'][i%3],-.34+i*.135,.57,0,shelf)
 for i in range(2):box('Project archive',.36,.23,.34,'A5B1BD',-.24+i*.46,1.06,0,shelf)
 plant(-1.94,-1.68,.65,empty('Shelf plant riser',0,1.49,0,p))
 # Workflow diagram is mounted on a freestanding board, above the rear storage.
 board=empty('Systems planning board',.65,0,-2.22,p)
 for xx in (-.85,.85):
  rod('Board leg',(xx,.02,.14),(xx,2.45,0),.022,'metal',board)
  rod('Board foot',(xx,.03,-.20),(xx,.03,.28),.024,'metal',board)
 box('Planning board frame',1.97,1.04,.065,'wood',0,1.98,0,board)
 box('Planning board surface',1.87,.94,.012,'ivory',0,1.98,.041,board)
 for i,(xx,yy) in enumerate([(-.6,2.17),(0,2.17),(.6,2.17),(0,1.80)]):
  box('Workflow card',.36,.21,.018,['9BB8D1','A6B498','C9A984','B4A6D4'][i],xx,yy,.058,board)
 for a1,b1 in [((-.41,2.17,.063),(-.19,2.17,.063)),((.19,2.17,.063),(.41,2.17,.063)),((0,2.06,.063),(0,1.91,.063))]:rod('Workflow connection',a1,b1,.012,'586A7D',board)
 plant(2.12,-1.66,1.05,p)
 return c,h,a

def photo(p):
 shoot=empty('PRODUCT_SET',.35,0,-.10,p,-.58)
 # The entire sweep, subject and operator share one shooting axis.
 verts=[];faces=[];profile=[(.0,.02),(-1.30,.02),(-1.55,.10),(-1.72,.28),(-1.80,.52),(-1.80,2.25)]
 for xx in (-1.13,1.13):
  for zz,yy in profile:verts.append(tuple(pos((xx,yy,zz))))
 for i in range(len(profile)-1):faces.append((i,i+1,i+1+len(profile),i+len(profile)))
 mesh=bpy.data.meshes.new('Continuous paper sweep');mesh.from_pydata(verts,[],faces);mesh.update()
 sweep=bpy.data.objects.new('Curved photo backdrop',mesh);CURRENT.collection.objects.link(sweep);sweep.parent=shoot;mesh.materials.append(material('E4C5BA'));sweep.modifiers.new('Paper thickness','SOLIDIFY').thickness=.018
 cylinder('Product pedestal',.34,1.10,'ivory',0,.57,-.93,shoot)
 box('Product bottle',.23,.36,.17,'739195',0,1.30,-.93,shoot,bevel=.045)
 cylinder('Product cap',.065,.07,'dark',0,1.51,-.93,shoot)
 box('Bottle label',.16,.13,.006,'ivory',0,1.29,-.84,shoot,bevel=.009)
 # Camera is deliberately off-center enough to reveal Michael's profile.
 c,h,a=character(shoot,-.52,1.04,'photo',0);face_toward(c,0,-.93)
 # Actual photographic fixtures point toward the product, rather than out of frame.
 lights=empty('LIGHTING_POSITIONS',0,0,0,shoot)
 for name,x,z,yy in [('Key softbox',-1.63,-.23,2.10),('Fill softbox',1.55,-.67,1.78)]:
  tripod(lights,x,z,yy);q=empty(name,x,yy,z,lights);face_toward(q,0,-.93)
  box('Softbox housing',.70,.65,.18,'dark',parent=q,bevel=.05)
  box('Diffuser',.64,.59,.012,'FFF4DF',0,0,.099,q)
  for dx in (-.18,.18):box('Diffuser rib',.008,.56,.004,'E4DCCB',dx,0,.109,q,bevel=.002)
  box('Stand sandbag',.32,.10,.26,'58616A',x+.15,.08,z+.04,lights)
 # Equipment is stored together outside the shooting lane, not on a second camera stand.
 cart=empty('CAMERA_CART',-1.87,0,1.15,p,-.12)
 for y in (.24,.94):box('Cart shelf',.92,.06,.62,'dark',0,y,0,cart)
 for xx in (-.40,.40):
  for zz in (-.25,.25):rod('Cart post',(xx,.10,zz),(xx,1.02,zz),.022,'metal',cart);sphere('Cart wheel',.065,'dark',xx,.07,zz,cart)
 box('Camera case',.72,.35,.47,'58616A',0,.445,0,cart)
 box('Case handle',.25,.035,.09,'metal',0,.64,0,cart)
 for xx in (-.23,.14):
  cylinder('Spare lens',.095,.21,'dark',xx,1.075,0,cart)
  ring('Lens focus ring',.096,.012,'metal',xx,1.11,0,cart,flat=True)
 box('Folded microfiber',.24,.025,.17,'ivory',.27,.985,.15,cart)
 # Marks describe real operator/subject positions without adding scene titles.
 cable('Lighting cable',[(-1.63,.025,-.23),(-1.66,.025,-1.10),(-1.40,.025,-2.08),(1.20,.025,-2.08),(1.55,.025,-1.30),(1.55,.025,-.67)],shoot,.012)
 return c,h,a

def graphic_arts(p):
 printbay=empty('PRINT_WORKSTATION',-.28,0,.17,p,.12)
 d=desk(printbay,0,0,2.64)
 box('Cutting mat',2.18,.016,.86,'698F9A',0,1.125,0,d)
 box('Print bed',1.52,.035,.77,'dark',-.23,1.15,0,d)
 box('Cotton paper',1.36,.009,.64,'ivory',-.23,1.174,0,d,bevel=.002)
 for xx in (-.94,.48):box('Screen side',.045,.08,.80,'wood',xx,1.21,0,d)
 for zz in (-.38,.38):box('Screen rail',1.46,.08,.045,'wood',-.23,1.21,zz,d)
 cylinder('Printed sun',.21,.008,'C97C61',-.44,1.183,-.02,d)
 for i in range(3):box('Printed stripe',.34,.009,.045,'698F9A',.06,1.184,-.16+i*.14,d)
 c,h,a=character(printbay,-.23,-.86,'arts',0)
 box('MOTION_squeegee_handle',.58,.065,.06,'wood',-.23,-.28,.59,a[1])
 box('Squeegee blade',.63,.10,.022,'72918A',-.23,-.345,.59,a[1])
 ink=tray(d,.91,1.15,.02,.40,.73)
 for i,col in enumerate(('CB7865','698F9A','DDB763')):
  cylinder('Ink jar',.075,.13,col,0,.085,-.24+i*.24,ink)
  cylinder('Ink surface',.06,.008,col,0,.154,-.24+i*.24,ink)
 # Blank stock is stored directly beneath the print table, close to the working hand.
 box('Paper storage shelf',2.30,.05,.78,'wood',0,.35,0,printbay)
 for i in range(4):box('Blank paper stack',.76,.021,.54,'ivory',-.54,.39+i*.024,0,printbay)
 box('Studio storage box',.65,.27,.57,'C9B08A',.55,.51,0,printbay)
 # Finished prints line the rear, with their lower row clear of Michael's silhouette.
 rack=empty('DRYING_RACK',-1.18,0,-2.12,p)
 for xx in (-.78,.78):
  rod('Rack upright',(xx,.02,0),(xx,2.20,0),.026,'metal',rack)
  rod('Rack foot',(xx,.03,-.22),(xx,.03,.25),.027,'metal',rack)
 rod('Drying line',(-.78,2.05,0),(.78,2.05,0),.012,'dark',rack)
 for i in range(3):
  paper=empty('MOTION_paper',-.51+i*.51,1.72,0,rack)
  box('Art paper',.43,.59,.013,'ivory',parent=paper)
  box('Wooden clip',.032,.08,.035,'wood',0,.30,.018,paper)
  sphere('Printed circle',.13,['C97C61','698F9A','C1A35A'][i],0,.07,.0075,paper,scale=(1,1,.03))
  box('Printed bar',.29,.065,.004,'394C62',0,-.14,.0085,paper,bevel=.0015)
 # Press and paper rolls form one finishing station; open floor remains in front.
 station=empty('FINISHING_STATION',1.72,0,-.12,p,-.20)
 t=desk(station,0,0,.95)
 box('Press base',.84,.06,.62,'698F9A',0,1.15,0,t)
 roll=empty('MOTION_roller',0,1.38,0,t);r=cylinder('Print roller',.14,.75,'metal',parent=roll);r.rotation_euler[1]=math.pi/2
 for xx in (-.40,.40):box('Roller bearing',.06,.29,.18,'dark',xx,1.28,0,t)
 rod('Press crank',(.48,1.38,0),(.48,1.38,.24),.022,'metal',t)
 rod('Crank grip',(.48,1.38,.24),(.63,1.38,.24),.03,'wood',t)
 cylinder('Roll stock bin',.24,.40,'clay',.03,.21,-.81,station)
 for i in range(3):cylinder('Rolled stock',.064,.84+i*.10,'ivory',-.12+i*.13,.46+i*.05,-.81,station)
 easel=empty('FINISHED_POSTER',1.43,0,-1.86,p,-.18)
 # The board leans on the front legs and rests on a ledge, instead of the legs passing through it.
 lean=math.atan2(.18,2.10)
 for xx in (-.40,.40):rod('Easel front leg',(xx,.02,.18),(xx*.72,2.08,-.0),.03,'wood',easel)
 rod('Easel back leg',(0,.02,-.42),(0,2.02,-.02),.03,'wood',easel)
 box('Easel ledge',.98,.045,.12,'wood',0,.86,.16,easel,bevel=.012)
 board=empty('Poster on easel',0,.89,.17,easel);board.rotation_euler[0]=-lean
 box('Poster board',.96,1.30,.05,'ivory',0,.65,0,board)
 text('Poster title','IN GOOD COMPANY',.085,'dark',0,1.18,.03,board)
 sphere('Poster sun',.24,'C97C61',0,.80,.028,board,scale=(1,1,.04))
 for i in range(3):box('Poster wave',.62,.055,.008,'698F9A',0,.24+i*.10,.029,board,bevel=.02)
 return c,h,a

def events(p):
 stage=empty('STAGE_ASSEMBLY',.25,0,-1.07,p)
 box('Stage deck',3.50,.24,1.78,'666B8C',0,.13,0,stage)
 box('Stage fascia',3.50,.13,.045,'5C547A',0,.11,.90,stage)
 box('Event graphic',2.70,1.48,.07,'5C547A',0,.99,-.79,stage)
 for xx in (-1.15,1.15):box('Backdrop foot',.10,.04,.42,'metal',xx,.27,-.79,stage,bevel=.01)
 text('Event title','MAKE IT\nHAPPEN',.27,'F2E3CE',0,1.06,-.744,stage)
 for xx in (-1.97,1.97):
  box('Truss baseplate',.38,.035,.42,'metal',xx,.018,-.75,stage)
  for zz in (-.87,-.64):rod('Truss upright',(xx,.04,zz),(xx,2.71,zz),.030,'metal',stage)
  for i in range(7):rod('Truss diagonal',(xx,.09+i*.36,-.87),(xx,.42+i*.36,-.64),.015,'metal',stage)
 for zz in (-.87,-.64):rod('Truss beam',(-1.97,2.71,zz),(1.97,2.71,zz),.030,'metal',stage)
 for i in range(9):rod('Beam brace',(-1.97+i*.438,2.71,-.87),(-1.532+i*.438,2.71,-.64),.015,'metal',stage)
 for i,xx in enumerate((-1.35,-.45,.45,1.35)):
  fixture=empty('Stage fixture',xx,2.52,-.75,stage)
  body=cylinder('Spotlight housing',.105,.22,'dark',parent=fixture);body.rotation_euler[0]=.44
  glass=cylinder('Spotlight lens',.086,.012,'C2B1EB' if i<2 else 'F0C798',0,-.10,.048,fixture);glass.rotation_euler[0]=.44
 # Side speakers leave the center access route unobstructed.
 for xx in (-1.96,1.96):
  speaker=empty('PA speaker',xx,0,.45,stage);speaker.rotation_euler[2]=-.12 if xx<0 else .12
  box('Speaker cabinet',.42,.91,.37,'dark',0,.48,0,speaker)
  for yy in (.25,.66):ring('Speaker cone',.115,.022,'596472',0,yy,.193,speaker)
 box('Stage lower step',.89,.08,.31,'8185A0',.42,.04,1.16,stage)
 box('Stage upper step',.89,.16,.25,'8185A0',.42,.08,.94,stage)
 # Production desk + road case become a single technical station off the walkway.
 tech=empty('FRONT_OF_HOUSE',-1.50,0,.90,p,-.20)
 box('Console roadcase',1.12,.83,.77,'dark',0,.48,0,tech)
 for xx in (-.53,.53):box('Case corner',.025,.86,.79,'metal',xx,.48,0,tech)
 for yy in (.10,.87):box('Case edge',1.10,.025,.79,'metal',0,yy,0,tech)
 box('Roadcase handle',.24,.055,.018,'metal',0,.47,.40,tech)
 box('Mixing console',1.02,.09,.66,'58616A',0,.95,0,tech)
 for i in range(7):
  xx=-.36+i*.12;box('Fader slot',.01,.007,.25,'metal',xx,1.002,.05,tech)
  box('Fader cap',.04,.018,.05,'ivory',xx,1.006,(i%3)*.07-.06,tech)
  for zz in (-.19,-.12):cylinder('Mixer knob',.018,.026,'metal',xx,1.008,zz,tech)
 box('Console meter',.22,.008,.095,'9BB8D1',.33,1.002,-.22,tech)
 for xx in (-.43,.43):
  for zz in (-.26,.26):sphere('Roadcase wheel',.075,'dark',xx,.075,zz,tech)
 c,h,a=character(p,.16,.95,'event',-.38);h.rotation_euler[2]=-.20
 # All cable runs stay at the technical edge, with a low protector at the crossing.
 cable('Stage signal run',[(-1.5,.025,.61),(-2.28,.025,.61),(-2.28,.025,-1.55),(2.22,.025,-1.55),(2.22,.025,-.62)],p,.019)
 box('Cable protector',.17,.035,1.25,'58616A',-2.28,.025,-.04,p)
 for i in range(2):box('Taped route marker',.035,.004,.15,'C9A984',-2.28,.046,-.46+i*.78,p)
 return c,h,a

def fabrication(p):
 bay=empty('MOTORCYCLE_SERVICE_BAY',.24,0,.40,p,-.17)
 box('Motorcycle lift',3.05,.15,.85,'6E827B',0,.085,.16,bay)
 box('Lift side rail',3.0,.035,.045,'metal',0,.17,.56,bay)
 bike=motorcycle(bay,0,0,1.04);bike.location.z=.13
 # A front-wheel chock and rear tie points make the lift a credible work fixture.
 for zz in (-.17,.17):box('Wheel chock',.42,.14,.045,'dark',1.06,.23,zz,bay)
 for xx in (-1.28,1.28):ring('Lift tie-down',.037,.013,'metal',xx,.18,.48,bay,flat=True)
 c,h,a=character(bay,-.02,-.93,'kneel',0);h.rotation_euler[0]=.16
 rod('Mechanic socket extension',(-.04,-.48,.53),(-.04,-.42,.70),.019,'metal',a[1])
 # Back bench, storage, vise and tools occupy one continuous wall-free workshop edge.
 bench=empty('SERVICE_BENCH',-.28,0,-1.94,p)
 d=desk(bench,0,0,3.76)
 box('Bench backsplash',3.72,.12,.045,'wood',0,1.16,-.49,bench)
 pegboard(bench,.48,1.82,-.47,2.25,.84)
 for xx in (-.65,1.60):rod('Toolboard upright',(xx,1.11,-.50),(xx,2.3,-.50),.025,'metal',bench)
 box('Bench vise',.45,.20,.27,'697985',-1.37,1.23,.11,bench)
 box('Vise jaws',.46,.09,.30,'metal',-1.37,1.36,.11,bench)
 rod('Vise screw',(-1.37,1.23,.22),(-1.37,1.23,.44),.027,'metal',bench)
 rod('Vise handle',(-1.37,1.10,.44),(-1.37,1.36,.44),.018,'metal',bench)
 parts=tray(bench,.50,1.15,.13,.72,.40)
 for i in range(4):cylinder('Labeled socket',.03,.08,'metal',-.24+i*.15,.06,0,parts)
 box('Underbench shelf',3.40,.05,.72,'wood',0,.27,0,bench)
 for x in (-.60,.65):box('Parts bin',.73,.33,.57,'91A38C',x,.46,0,bench)
 # Mobile tool cart sits within the mechanic's reach, not in the viewing foreground.
 cart=cabinet(p,-1.94,-.35,.71,.73,.53,'78938A')
 tools=tray(cart,0,.86,0,.53,.34)
 for xx in (-.16,0,.16):rod('Ready socket tool',(xx,.04,-.10),(xx,.04,.10),.018,'metal',tools)
 # Spare tire and stool are stored at the rear service edge.
 spare=ring('Spare tire',.32,.085,'dark',1.72,.445,-1.94,p);spare.rotation_euler=(math.pi/2,-.10,math.pi/2)
 stool=empty('Mechanic stool',-1.93,0,.67,p)
 cylinder('Stool seat',.24,.08,'boot',0,.50,0,stool)
 for i in range(3):
  angle=i*math.tau/3;rod('Stool leg',(0,.47,0),(math.cos(angle)*.21,.03,math.sin(angle)*.21),.021,'metal',stool)
 return c,h,a

def family(p):
 for zz in (-1.55,.05,1.65):box('Driveway joint',5.05,.006,.012,'BCB8AF',0,.005,zz,p)
 box('Bicycle repair mat',3.88,.025,2.12,'B4BDB8',-.02,.02,.56,p,bevel=.08)
 # Bicycle, people and tools are arranged around the drivetrain and front wheel.
 repair=empty('FAMILY_REPAIR',-.18,0,.55,p,-.10)
 bike=bmx(repair,0,0)
 dad,h,a=character(repair,-.49,-.95,'kneel-low',0);h.rotation_euler[0]=.16
 ar=a[1];rod('Dad socket handle',(-.04,-.58,.53),(-.04,-.67,.73),.020,'metal',ar)
 ring('Dad socket',.035,.012,'metal',-.04,-.68,.75,ar)
 daughter=family_person(repair,'DAUGHTER',1.00,-.30,.74,False,True);face_toward(daughter,.60,.10)
 arm=next(o for o in daughter.children if o.name.startswith('ARM_R'))
 rod('Daughter Allen key',(-.08,-.30,.51),(-.08,-.41,.56),.015,'metal',arm)
 rod('Allen key tip',(-.08,-.41,.56),(-.18,-.41,.56),.015,'metal',arm)
 wife=family_person(p,'WIFE',.40,-1.20,.97,False,True);wife.rotation_euler[2]=-.32
 ar=next(o for o in wife.children if o.name.startswith('ARM_R'))
 rod('Wife wrench handle',(-.08,-.30,.51),(-.08,-.08,.51),.022,'metal',ar)
 ring('Wife wrench head',.058,.018,'metal',-.08,-.035,.51,ar)
 ar=next(o for o in wife.children if o.name.startswith('ARM_L'))
 rod('Wife screwdriver grip',(.08,-.30,.51),(.08,-.18,.51),.03,'clay',ar)
 rod('Wife screwdriver shaft',(.08,-.18,.51),(.08,.02,.51),.011,'metal',ar)
 # Cradle supports the bottom bracket rather than leaving the bicycle floating.
 box('Repair stand foot',.66,.045,.47,'dark',-.14,.04,-.04,repair)
 for zz in (-.13,.13):rod('Repair cradle',(-.14,.06,zz),(-.14,.29,zz),.022,'dark',repair)
 # Open toolbox is beside Dad's left knee, safely outside the wheel and walk path.
 toolbox=empty('FAMILY_TOOLBOX',-1.57,0,-.12,p,.13)
 box('Toolbox body',.64,.19,.37,'C98F72',0,.12,0,toolbox)
 box('Toolbox tray',.55,.015,.29,'dark',0,.224,0,toolbox)
 box('Toolbox lid',.64,.31,.04,'C98F72',0,.27,-.20,toolbox)
 for i in range(3):rod('Sorted spare tool',(-.19+i*.18,.25,-.09),(-.19+i*.18,.25,.09),.014,'metal',toolbox)
 # Garage frontage frames the family, with the door raised above their heads.
 garage=empty('GARAGE_FRONT',0,0,-2.28,p)
 box('Garage interior',4.65,2.64,.07,'66757A',0,1.32,-.06,garage)
 for xx in (-2.33,2.33):box('Garage pier',.25,2.73,.28,'E6DED0',xx,1.37,.05,garage)
 box('Garage lintel',4.97,.22,.30,'E6DED0',0,2.70,.05,garage)
 box('Garage top trim',4.99,.07,.32,'B2B0A5',0,2.84,.05,garage)
 for i in range(3):box('Raised garage slat',4.37,.16,.055,'CBCFC8',0,2.22+i*.17,.13,garage)
 for xx in (-2.20,2.20):box('Door track',.045,2.5,.055,'metal',xx,1.28,.11,garage)
 d=desk(p,-1.38,-1.79,1.39);pegboard(p,-1.38,1.70,-2.278,1.28,.77)
 tray(d,0,1.145,.02,.53,.30)
 cabinet(p,1.58,-1.91,.78,.79,.49,'829B94')
 ring('Stored BMX tire',.275,.047,'dark',1.58,1.68,-2.255,p);rod('Tire hook',(1.58,1.93,-2.32),(1.58,1.93,-2.22),.016,'metal',p)
 # Pump is parked against the storage cabinet, hose secured to its barrel.
 pump=empty('Parked floor pump',2.02,0,-1.16,p)
 box('Pump foot',.32,.05,.18,'dark',0,.03,0,pump);cylinder('Pump barrel',.047,.66,'metal',0,.37,0,pump)
 rod('Pump rod',(0,.70,0),(0,.90,0),.016,'metal',pump)
 rod('Pump handle',(-.14,.91,0),(.14,.91,0),.027,'dark',pump)
 cable('Secured pump hose',[(0,.60,.05),(.12,.68,.05),(.13,.22,.05),(.04,.16,.05)],pump,.012)
 return dad,h,a

BUILDERS=[('ai','DBE4ED',ai),('photography','EBDADF',photo),('graphic-arts','E7D8CA',graphic_arts),('events','DCD5E8',events),('fabrication','DCE3D4',fabrication),('family','E4DDD4',family)]

def setup_scene(name,resolution,samples):
 global CURRENT
 scene=bpy.data.scenes.new(name);bpy.context.window.scene=scene;CURRENT=scene
 scene.render.engine='CYCLES';scene.cycles.samples=samples;scene.cycles.use_denoising=True;scene.cycles.max_bounces=5
 scene.render.resolution_x=resolution;scene.render.resolution_y=round(resolution*1000/1100);scene.render.resolution_percentage=100
 scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True
 scene.world=bpy.data.worlds.new(name+' world');scene.world.use_nodes=True
 scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.78,.83,.95,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.8
 scene.view_settings.view_transform='AgX'
 data=bpy.data.cameras.new(name+' review camera');cam=bpy.data.objects.new('Review camera',data);scene.collection.objects.link(cam)
 cam.location=(8,-10,8);target=Vector((0,0,.75));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=8.8;scene.camera=cam
 data=bpy.data.lights.new('Fixed studio key','AREA');light=bpy.data.objects.new('Fixed studio key',data);scene.collection.objects.link(light)
 light.location=(-3,-5,8);light.rotation_euler=(Vector((0,0,.5))-light.location).to_track_quat('-Z','Y').to_euler();data.energy=900;data.shape='DISK';data.size=5;data.color=(1,.94,.87)
 return scene

def main():
 args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
 parser=argparse.ArgumentParser(description='Rebuild the six authored portfolio dioramas with Blender.')
 parser.add_argument('--scene',choices=[s for s,_,_ in BUILDERS]);parser.add_argument('--resolution',type=int,default=1100)
 parser.add_argument('--samples',type=int,default=32);parser.add_argument('--no-render',action='store_true');parser.add_argument('--review-angles',action='store_true')
 opts=parser.parse_args(args);built=[]
 for slug,col,builder in BUILDERS:
  if opts.scene and opts.scene!=slug:continue
  print('BUILDING',slug,flush=True);scene=setup_scene(slug,opts.resolution,opts.samples)
  root=empty('DIORAMA_'+slug);base(root,col);builder(root)
  root['environment']=slug;root['authored_in']='Blender';root['composition_revision']='purposeful-workspaces-v3'
  bpy.ops.object.select_all(action='DESELECT')
  for obj in list(scene.objects):
   if obj.type in {'FONT','CURVE'}:
    bpy.context.view_layer.objects.active=obj;obj.select_set(True);bpy.ops.object.convert(target='MESH');obj.select_set(False)
  for obj in scene.objects:
   if obj.type in {'MESH','EMPTY'}:obj.select_set(True)
  bpy.ops.export_scene.gltf(filepath=str(OUT/(slug+'.glb')),export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_animations=False,export_cameras=False,export_lights=False,export_yup=True,export_extras=True)
  built.append(slug);print('EXPORTED',slug,flush=True)
 if 'Scene' in bpy.data.scenes and len(bpy.data.scenes)>1:bpy.data.scenes.remove(bpy.data.scenes['Scene'])
 if not opts.scene:bpy.ops.wm.save_as_mainfile(filepath=str(REPO/'site/blender/dioramas.blend'))
 if not opts.no_render:
  for slug in built:
   scene=bpy.data.scenes[slug];bpy.context.window.scene=scene;scene.render.filepath=str(RENDERS/(slug+'.png'))
   print('RENDERING',slug,flush=True);bpy.ops.render.render(write_still=True)
   if opts.review_angles:
    for suffix,loc in [('rear',(-8,10,8)),('plan',(0,0,14))]:
     cam=scene.camera;cam.location=loc;cam.rotation_euler=(Vector((0,0,.75))-cam.location).to_track_quat('-Z','Y').to_euler()
     scene.render.filepath=str(RENDERS/(slug+'-'+suffix+'.png'));bpy.ops.render.render(write_still=True)
 print('ALL DONE',flush=True)

if __name__=='__main__':main()
