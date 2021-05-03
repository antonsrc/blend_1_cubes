# blender --background --python 0.py

import bpy
import platform
import math
import colorsys
from random import randint, choice

BLENDER_VER = '2.91'

C = bpy.context
D = bpy.data
O = bpy.ops

FR_START = 1
FR_END = 50

FR_DIM_X = 800
FR_DIM_Y = 800

NUM_OBJS = 50

OBJ_ = 'mix'
# OBJ_ = 'torus'
# OBJ_ = 'cube'
# OBJ_ = 'cone'
# OBJ_ = 'sphere'

mylinuxname = 'ant_machine'

def degrees_to_radians(x,y,z):
    x = math.radians(x)
    y = math.radians(y)
    z = math.radians(z)
    return (x,y,z)


def del_all_objs():
    O.object.select_all(action='SELECT')
    O.object.delete(use_global=False,confirm=False)
    while len(D.meshes) != 0:
        D.meshes.remove(D.meshes[0])
    while len(D.materials) != 0:
        D.materials.remove(D.materials[0])
    while len(D.textures) != 0:
        D.textures.remove(D.textures[0])
    while len(D.images) != 0:
        D.images.remove(D.images[0])
    while len(D.lights) != 0:
        D.lights.remove(D.lights[0])


def camera_add(x,y,z,rx,ry,rz):
    O.object.camera_add(
        align = 'VIEW',
        location = (x,y,z),
        rotation = degrees_to_radians(rx,ry,rz))
    C.scene.camera = D.objects[C.active_object.name]
    return C.active_object.name


def light_add(name_type,x,y,z,energy_=80000,r=1,g=1,b=1):
    O.object.light_add(type = name_type,location = (x,y,z))
    C.object.data.color = (r,g,b)
    C.object.data.energy = energy_

    if name_type == 'AREA':
        C.object.data.size = 50
    return C.active_object.name


def light_chng(name,rgb,energy_=80000):
    D.lights[name].color = rgb
    D.lights[name].energy = energy_
    return [name,rgb,energy_]


def export_image_settings(start_,end_,x,y,render_samples,stamp):
    start = start_
    end = end_
    op_sys = platform.system()
    print('~ '*16 + op_sys)
    if op_sys == 'Linux':
        file_0 = '/snap/blender/34/'
        file_1 = '/scripts/presents/framerate/24.py'
        file_full = file_0 + BLENDER_VER + file_1
    else:
        file_0 = 'C:\\Program Files\\Blender Foundation\\Blender '
        file_1 = BLENDER_VER + '\\'
        file_2 = BLENDER_VER + '\\scripts\\presets\\framerate\\24.py'
        file_full = file_0 + file_1 + file_2
    O.script.execute_preset(
        filepath = file_full,
        menu_idname = 'RENDER_MT_framerate_presets')
    C.scene.frame_start = start
    C.scene.frame_end = end
    C.scene.render.use_file_extension = True
    C.scene.render.image_settings.file_format = 'JPEG'
    C.scene.eevee.taa_render_samples = render_samples
    C.scene.render.resolution_x = x
    C.scene.render.resolution_y = y
    C.scene.render.resolution_percentage = 100
    C.scene.render.image_settings.quality = 100

    C.scene.render.use_stamp = stamp
    C.scene.render.use_stamp_date = False
    C.scene.render.use_stamp_time = False
    C.scene.render.use_stamp_render_time = False
    C.scene.render.use_stamp_frame = False
    C.scene.render.use_stamp_camera = False
    C.scene.render.use_stamp_scene = False
    C.scene.render.use_stamp_filename = False
    C.scene.render.stamp_font_size = 20
    C.scene.render.stamp_foreground = (0,0,0,1)
    C.scene.render.stamp_background = (1,1,1,0.25)
    C.scene.render.use_stamp_note = True


def bake_animation(start,end):
    O.ptcache.free_bake_all()
    pc = C.scene.rigidbody_world.point_cache
    pc.frame_start = FR_START
    pc.frame_end = FR_END
    O.ptcache.bake_all({'point cache': pc},bake = True)


def world_color(r=1,g=1,b=1,strength_=1):
    world = D.worlds['World'].node_tree.nodes['Background']
    world.inputs[0].default_value = (r,g,b,1)
    world.inputs[1].default_value = strength_
    C.scene.eevee.use_soft_shadows = True


def rgb_rand(start,end):
    r = randint(start,end)*0.001
    g = randint(start,end)*0.001
    b = randint(start,end)*0.001

    # bicycle
    # for not gray colors
    dif = 0.05
    while ((b >= (r - dif) and b <=(r + dif))
        and (b >= (g - dif) and b <= (g + dif))):
        b = randint(start,end)*0.001
    return [r,g,b]


def rigidbody_for_obj(obj,shape,kinematic_,kg):
    O.rigidbody.object_add()
    obj.rigid_body.type = 'ACTIVE'
    obj.rigid_body.collision_shape = shape
    obj.rigid_body.kinematic = kinematic_
    obj.rigid_body.mesh_source = 'BASE'
    obj.rigid_body.collision_margin = 1
    obj.rigid_body.mass = kg
    obj.rigid_body.use_margin = True


def mat_for_obj(
    obj,
    mat_name,
    rgba = [1,1,1,1],
    shader = 'Principled BSDF',
    blend_method = 'BLEND',
    alpha = 1):
    mat = D.materials.new(name = mat_name)
    mat.use_nodes = True
    mat.node_tree.nodes.new('ShaderNodeEmission')
    mat.blend_method = blend_method
    if blend_method == 'BLEND':
        mat.use_backface_culling = False
        mat.show_transparent_back = False   # show backface
    mat_in = mat.node_tree.nodes.get(shader)
    mat_out = mat.node_tree.nodes.get('Material Output')
    node_links = mat.node_tree.links.new
    if shader == 'Principled BSDF':
        mat_in.inputs[0].default_value = rgba
        mat_in.inputs[5].default_value = 0
        mat_in.inputs[7].default_value = 1
        mat_in.inputs[18].default_value = 0
        mat_in.inputs[19].default_value = alpha
        out_name = 'BSDF'
    elif shader == 'Emission':
        mat_in.inputs['Color'].default_value = rgba
        mat_in.inputs['Strength'].default_value = 1
        out_name = 'Emission'
    node_links(mat_out.inputs['Surface'],mat_in.outputs[out_name])
    obj.active_material = mat


def mod_apply_bevel(obj,width_,segments_):
    O.object.modifier_add(type = 'BEVEL')
    obj.modifiers['Bevel'].width = width_
    obj.modifiers['Bevel'].segments = segments_
    O.object.modifier_apply(modifier='Bevel',report=True)


def mod_apply_subsurf(obj,levels_,render_levels_):
    O.object.modifier_add(type='SUBSURF')
    obj.modifiers['Subdivision'].levels = levels_
    obj.modifiers['Subdivision'].render_levels = render_levels_
    O.object.modifier_apply(modifier='Subdivision',report=True)


def torus():
    name = 'torus'
    min_size = 2
    max_size = 14
    return [name,min_size,max_size]


def cube():
    name = 'cube'
    min_size = 10
    max_size = 28
    return [name,min_size,max_size]


def cone():
    name = 'cone'
    min_size = 4
    max_size = 22
    return [name,min_size,max_size]


def sphere():
    name = 'sphere'
    min_size = 2
    max_size = 14
    return [name,min_size,max_size]


def mix():
    name = 'mix'
    min_size = 10
    max_size = 28
    return [name,min_size,max_size]


def arr_xyz(obj,arr_size,numObj):
    arr_x = []
    arr_y = []
    arr_z = []
    clearance = 0.7
    size_ratio = 0.1
    max_size_rat = obj[2]*size_ratio + clearance
    x = -(arr_size+max_size_rat)
    y = -arr_size
    z = -arr_size
    for i in range(numObj):
        if x < arr_size:
            x +=max_size_rat
        elif y < arr_size - max_size_rat:
            x = -arr_size
            y += max_size_rat
        elif z < arr_size - max_size_rat:
            x = -arr_size
            y = -arr_size
            z += max_size_rat
        arr_x.append(x)
        arr_y.append(y)
        arr_z.append(z)
    return [arr_x,arr_y,arr_z]


def obj_add(obj_type,o_size,xyz):
    if obj_type == 'cube':
        O.mesh.primitive_cube_add(
            size=o_size,
            location=xyz)
    elif obj_type == 'sphere':
        O.mesh.primitive_uv_sphere_add(
            radius=o_size,
            location=xyz)
    elif obj_type == 'torus':
        O.mesh.primitive_torus_add(
            location=xyz,
            major_segments=40,
            major_radius=o_size,
            minor_radius=o_size/4)
    elif obj_type == 'cone':
        O.mesh.primitive_cone_add(
            vertices=3,
            radius1=o_size,
            depth=o_size*1.5,
            location=xyz)

    ob = C.active_object
    r = randint(200,1000)*0.001
    g = randint(200,1000)*0.001
    b = randint(200,1000)*0.001
    mat_for_obj(ob,'Mat',[r,g,b,0])
    rigidbody_for_obj(ob,'CONVEX_HULL',False,5)

    # add modifiers
    if obj_type == 'cube':
        mod_apply_bevel(ob,round(o_size)*0.1,1)
        mod_apply_subsurf(ob,3,3)
    elif obj_type == 'cone':
        mod_apply_bevel(ob,o_size/4,4)
        mod_apply_subsurf(ob,3,3)
    elif obj_type == 'sphere':
        mod_apply_subsurf(ob,1,1)
    elif obj_type == 'torus':
        mod_apply_subsurf(ob,1,1)
    O.object.shade_smooth()


class mat_color():
    def start(self,num_obj_,mat_name_,shader_='Principled BSDF'):
        self.num_obj = num_obj_
        self.mat_name = mat_name_
        self.shader = shader_
        self.red = [0]*self.num_obj
        self.green = [0]*self.num_obj
        self.blue = [0]*self.num_obj
        self.alpha = [1]*self.num_obj
        self.strength = [1]*self.num_obj
        self.rt = -1
        self.gt = -1
        self.bt = -1
        self.at = -1
        self.stt = -1
        self.rand_rgbt = -1
        self.rand_rgb_fullt = -1
        self.rand_at = -1
        self.rand_grayt = -1

    def r(self,value):
        self.red = [value]*self.num_obj
        self.rt = self.red[0]

    def g(self,value):
        self.green = [value]*self.num_obj
        self.gt = self.green[0]

    def b(self,value):
        self.blue = [value]*self.num_obj
        self.bt = self.blue[0]

    def a(self,value):
        self.alpha = [value]*self.num_obj
        self.at = self.alpha[0]

    def st(self,value):
        self.strength = [value]*self.num_obj
        self.stt = self.strength[0]

    def rand_rgb(self,start_,end):
        self.red = []
        self.green = []
        self.blue = []
        for i in range(self.num_obj):
            rgb = rgb_rand(start_,end)
            self.red.append(rgb[0])
            self.green.append(rgb[1])
            self.blue.append(rgb[2])

        if self.num_obj == 1:
            self.rand_rgbt = [rgb[0],rgb[1],rgb[2]]
        else:
            self.rand_rgbt = [start_,end]
        
    def rand_rgb_full(self,start_,end):
        self.red = []
        self.green = []
        self.blue = []
        for i in range(self.num_obj):
            r = randint(start_,end)*0.001
            g = randint(start_,end)*0.001
            b = randint(start_,end)*0.001
            self.red.append(r)
            self.green.append(g)
            self.blue.append(b)

        if self.num_obj == 1:
            self.rand_rgb_fullt = [rgb[0],rgb[1],rgb[2]]
        else:
            self.rand_rgb_fullt = [start_,end]

    def rand_a(self,start_,end):
        self.alpha = []
        for i in range(self.num_obj):
            al = randint(start_,end)*0.001
            self.alpha.append(al)
        
        if self.num_obj == 1:
            self.rand_at = [al]
        else:
            self.rand_at = [start_,end]

    def rand_gray(self,start_,end):
        self.red = []
        self.green = []
        self.blue = []
        for i in range(self.num_obj):
            gray = randint(start_,end)*0.001
            self.red.append(gray)
            self.green.append(gray)
            self.blue.append(gray)

        if self.num_obj == 1:
            self.rand_grayt = [gray]
        else:
            self.rand_grayt = [start_,end]

    def change(self):
        for i in range(self.num_obj):
            r = self.red[i]
            g = self.green[i]
            b = self.blue[i]
            a = self.alpha[i]
            st = self.strength[i]

            if i == 0:
                mat = D.materials[self.mat_name].node_tree
            else:
                i = str(i)
                i = i.zfill(3)
                mat = D.materials[self.mat_name+'.'+str(i)].node_tree

            mat_in = mat.nodes.get(self.shader)
            mat_out = mat.nodes.get('Material Output')
            node_links = mat.links.new
            if self.shader == 'Principled BSDF':
                mat_in.inputs[0].default_value = (r,g,b,0)
                mat_in.inputs[19].default_value = a
                out_name = 'BSDF'
            elif self.shader == 'Emission':
                mat_in.inputs['Color'].default_value = (r,g,b,0)
                mat_in.inputs['Strength'].default_value = st
                out_name = 'Emission'
            node_links(mat_out.inputs['Surface'],mat_in.outputs[out_name])

        # telemetry
        out_arr = []
        if self.rt != -1:
            out_arr.append('r = ' + str(self.rt))
        if self.gt != -1:
            out_arr.append('g = ' + str(self.gt))
        if self.bt != -1:
            out_arr.append('b = ' + str(self.bt))
        if self.at != -1:
            out_arr.append('a = ' + str(self.at))
        if self.stt != -1:
            out_arr.append('st = ' + str(self.stt))
        if self.rand_rgbt != -1:
            out_arr.append('rand_rgb = ' + str(self.rand_rgbt))
        if self.rand_rgb_fullt != -1:
            out_arr.append('rand_rgb_full = ' + str(self.rand_rgb_fullt))
        if self.rand_at != -1:
            out_arr.append('rand_a = ' + str(self.rand_at))
        if self.rand_grayt != -1:
            out_arr.append('rand_gray = ' + str(self.rand_grayt))

        self.start(self.num_obj,self.mat_name,self.shader)
        return out_arr


del_all_objs()

light0 = light_add('POINT', -15, -20, 10)
light1 = light_add('POINT', 15, 25, -25)
light2 = light_add('AREA', 0, 0, 33,energy_=140000)

camera_add(20, -20, 40, 210, 180, -135)

world_color()

export_image_settings(FR_START, FR_END, FR_DIM_X, FR_DIM_Y, 16, True) # 64

# bicycle
# create big Icosphere
# Icosphere random moving and toss up objects
O.mesh.primitive_ico_sphere_add(subdivisions=1,radius=65)
ico = C.active_object
rigidbody_for_obj(ico, 'MESH', True, 15)
mat_for_obj(ico, 'Mat_icosphere',blend_method='OPAQUE')
mod_apply_bevel(ico, 1, 1)
mod_apply_subsurf(ico, 3, 3)
O.object.shade_smooth()

# frames with big Icosphere
fr_step_ico = 18
FR_END_ico = FR_END + fr_step_ico
for i in range(FR_START,FR_END_ico,fr_step_ico):
    x = randint(0, 359)
    y = randint(0, 359)
    z = randint(0, 359)
    C.scene.frame_set(i)
    ico.rotation_euler = degrees_to_radians(x,y,z)
    ico.keyframe_insert(data_path='rotation_euler')

# bicycle
# create sphere for protected camera
ico_rad = 15
O.mesh.primitive_uv_sphere_add(radius=ico_rad,location=(13,-15,27))
cam_sphere = C.active_object
rigidbody_for_obj(cam_sphere,'MESH', True, 15)
mat_for_obj(cam_sphere, 'Mat_transparent',alpha=0)
mod_apply_subsurf(cam_sphere, 3, 3)
O.object.shade_smooth()

if OBJ_ == 'mix': OBJ = mix()
elif OBJ_ == 'torus': OBJ = torus()
elif OBJ_ == 'cube': OBJ = cube()
elif OBJ_ == 'cone': OBJ = cone()
elif OBJ_ == 'sphere': OBJ = sphere()

# add array of little objs in Icosphere
ar = arr_xyz(OBJ,ico_rad,NUM_OBJS)

# add objects in array
if (OBJ[0] != 'mix'):
    for i in range(NUM_OBJS):
        obj_size = randint(OBJ[1], OBJ[2])*0.1
        xyz = [ar[0][i],ar[1][i],ar[2][i]]
        obj_add(OBJ[0], obj_size, xyz)
        print(str(i)+'.'+OBJ[0])
else:
    for i in range(NUM_OBJS):
        OBJ = choice([torus(),cube(),cone(),sphere()])
        obj_size = randint(OBJ[1], OBJ[2])*0.1
        xyz = [ar[0][i],ar[1][i],ar[2][i]]
        obj_add(OBJ[0], obj_size, xyz)
        print(str(i)+'.'+OBJ[0])

bake_animation(FR_START, FR_END)

ob = li = en = 1
ob_last = 36
li_last = 15
en_last = 8

ob_color = mat_color()
ob_color.start(NUM_OBJS,'Mat')
en_color = mat_color()
en_color.start(1,'Mat_icosphere')

arr_ob_1 = [
    0,
    0.25,
    randint(0, 1000)*0.001,
    randint(0, 750)*0.001,
    randint(0, 500)*0.001,
    randint(0, 250)*0.001,
    randint(250, 750)*0.001,
    randint(250, 500)*0.001,
    randint(250, 1000)*0.001,
    randint(500, 1000)*0.001,
    randint(750, 1000)*0.001,
    0.5,
    0.75,
    1]

arr_ob_2 = [
    [0,1000],
    [0,750],
    [0,500],
    [0,250],
    [10,990],
    [100,900],
    [randint(0, 250),randint(251, 1000)],
    [randint(0, 500),randint(501, 1000)],
    [randint(0, 750),randint(751, 1000)],
    [200,800],
    [750,1000],
    [500,1000],
    [250,1000],
    [250,750],
    [250,500]]


for fr in range(FR_START,FR_END+1):
    x = choice(arr_ob_2)
    y = choice(arr_ob_2[6:])
    if ob==1 or ob==ob_last+1:
        ob_color.r(1)
        ob_color.g(1)
        ob_color.b(1)
    elif ob==2:
        ob_color.r(0)
        ob_color.g(0)
        ob_color.b(0)
    elif ob>=3 and ob<=5:
        ob_color.rand_rgb(x[0],x[1])
    elif ob==6:
        ob_color.rand_rgb(x[0],x[1])
        ob_color.r(choice(arr_ob_1))
    elif ob==7:
        ob_color.start(NUM_OBJS,'Mat','Emission')
        C.scene.eevee.use_bloom = True  # use bloom
        ob_color.rand_rgb(x[0],x[1])
        ob_color.g(choice(arr_ob_1))
        ob_color.st(10)
    elif ob==8:
        ob_color.start(NUM_OBJS,'Mat')
        C.scene.eevee.use_bloom = False
        ob_color.rand_rgb(x[0],x[1])
        ob_color.b(choice(arr_ob_1))
    elif ob>=9 and ob<=11:
        ob_color.start(NUM_OBJS,'Mat','Emission')
        C.scene.eevee.use_bloom = True
        ob_color.rand_rgb(x[0],x[1])
        ob_color.r(choice(arr_ob_1))
        ob_color.g(choice(arr_ob_1))
        ob_color.st(10)
    elif ob>=12 and ob<=14:
        ob_color.start(NUM_OBJS,'Mat')
        C.scene.eevee.use_bloom = False
        ob_color.rand_rgb(x[0],x[1])
        ob_color.g(choice(arr_ob_1))
        ob_color.b(choice(arr_ob_1))
    elif ob>=15 and ob<=17:
        ob_color.start(NUM_OBJS,'Mat','Emission')
        C.scene.eevee.use_bloom = True
        ob_color.rand_rgb(x[0],x[1])
        ob_color.r(choice(arr_ob_1))
        ob_color.st(10)
    elif ob==18:
        ob_color.start(NUM_OBJS,'Mat')
        C.scene.eevee.use_bloom = False
        ob_color.rand_gray(x[0],x[1])
    elif ob==19:
        ob_color.start(NUM_OBJS,'Mat','Emission')
        C.scene.eevee.use_bloom = True
        ob_color.a(choice(arr_ob_1[6:]))
        ob_color.rand_gray(x[0],x[1])
    elif ob==20:
        ob_color.start(NUM_OBJS,'Mat')
        C.scene.eevee.use_bloom = False
        ob_color.rand_rgb_full(x[0],x[1])
        ob_color.rand_a(y[0],y[1])
    elif ob>=21 and ob<=23:
        ob_color.start(NUM_OBJS,'Mat','Emission')
        C.scene.eevee.use_bloom = True
        ob_color.rand_rgb_full(x[0],x[1])
    elif ob>=24 and ob<=26:
        ob_color.start(NUM_OBJS,'Mat')
        C.scene.eevee.use_bloom = False
        ob_color.rand_rgb(x[0],x[1])
        ob_color.rand_a(y[0],y[1])
    elif ob>=27 and ob<=29:
        ob_color.rand_a(y[0],y[1])
        ob_color.r(choice(arr_ob_1))
        ob_color.g(choice(arr_ob_1))
        ob_color.b(choice(arr_ob_1))
    elif ob==30:
        ob_color.rand_a(y[0],y[1])
        ob_color.rand_rgb(x[0],x[1])
    elif ob==31:
        ob_color.a(choice(arr_ob_1[6:]))
        ob_color.rand_rgb(x[0],x[1])

    elif ob==32:
        ob_color.start(NUM_OBJS,'Mat','Emission')
        C.scene.eevee.use_bloom = True
        ob_color.rand_rgb(x[0],x[1])
        ob_color.st(randint(1, 50))
    elif ob==33:
        ob_color.start(NUM_OBJS,'Mat','Emission')
        C.scene.eevee.use_bloom = True
        ob_color.rand_rgb(x[0],x[1])
        ob_color.st(randint(1, 50))
    elif ob==34:
        ob_color.start(NUM_OBJS,'Mat','Emission')
        C.scene.eevee.use_bloom = True
        ob_color.rand_rgb(x[0],x[1])
        ob_color.st(10)
    elif ob==35:
        ob_color.start(NUM_OBJS,'Mat','Emission')
        C.scene.eevee.use_bloom = True
        ob_color.rand_rgb(x[0],x[1])
        ob_color.st(10)
    elif ob==ob_last:
        ob_color.start(NUM_OBJS,'Mat')
        C.scene.eevee.use_bloom = False
        ob_color.rand_rgb_full(x[0],x[1])
        ob = 0
    ob_telem = ob_color.change()

    if li==1 or li==li_last+1:
        r0 = g0 = b0 = 1
        r1 = g1 = b1 = 1
        r2 = g2 = b2 = 1
    elif li==2:
        r0 = g0 = b0 = 1
    elif li==3:
        r1 = g1 = b1 = 1
    elif li==4:
        r2 = g2 = b2 = 1
    elif li==5:
        rgb = rgb_rand(0, 1000)
        r0 = rgb[0]
        g0 = rgb[1]
        b0 = rgb[2]
    elif li==6:
        rgb = rgb_rand(0, 1000)
        r1 = rgb[0]
        g1 = rgb[1]
        b1 = rgb[2]
    elif li==7:
        rgb = rgb_rand(0, 1000)
        r2 = rgb[0]
        g2 = rgb[1]
        b2 = rgb[2]
    elif li==8:
        rgb = rgb_rand(0, 1000)
        r0 = rgb[0]
        g0 = rgb[1]
        b0 = rgb[2]
        rgb = rgb_rand(0, 1000)
        r1 = rgb[0]
        g1 = rgb[1]
        b1 = rgb[2]
        rgb = rgb_rand(0, 1000)
        r2 = rgb[0]
        g2 = rgb[1]
        b2 = rgb[2]
    elif li==9:
        rgb = rgb_rand(0, 1000)
        r0 = rgb[0]
        g0 = rgb[1]
        b0 = rgb[2]
        rgb = rgb_rand(0, 1000)
        r1 = rgb[0]
        g1 = rgb[1]
        b1 = rgb[2]
        r2 = g2 = b2 = 1
    elif li==10:
        rgb = rgb_rand(100, 900)
        r0 = rgb[0]
        g0 = rgb[1]
        b0 = rgb[2]
        rgb = rgb_rand(100, 900)
        r1 = rgb[0]
        g1 = rgb[1]
        b1 = rgb[2]
        rgb = rgb_rand(100, 900)
        r2 = rgb[0]
        g2 = rgb[1]
        b2 = rgb[2]
    elif li==11:
        rgb = rgb_rand(100, 900)
        r0 = rgb[0]
        g0 = rgb[1]
        b0 = rgb[2]
        rgb = rgb_rand(100, 900)
        r1 = rgb[0]
        g1 = rgb[1]
        b1 = rgb[2]
        r2 = g2 = b2 = 1
    elif li==12:
        r0 = 1
        g0 = randint(0, 1000)*0.001
        b0 = randint(0, 1000)*0.001
        r1 = randint(0, 1000)*0.001
        g1 = 1
        b1 = randint(0, 1000)*0.001
        r2 = randint(0, 1000)*0.001
        g2 = randint(0, 1000)*0.001
        b2 = 1
    elif li==13:
        r0 = randint(0, 1000)*0.001
        g0 = 1
        b0 = randint(0, 1000)*0.001
        r1 = randint(0, 1000)*0.001
        g1 = randint(0, 1000)*0.001
        b1 = 1
        r2 = 1
        g2 = randint(0, 1000)*0.001
        b2 = randint(0, 1000)*0.001
    elif li==14:
        r0 = randint(0, 1000)*0.001
        g0 = randint(0, 1000)*0.001
        b0 = 1
        r1 = 1
        g1 = randint(0, 1000)*0.001
        b1 = randint(0, 1000)*0.001
        r2 = randint(0, 1000)*0.001
        g2 = 1
        b2 = randint(0, 1000)*0.001
    elif li==li_last:
        zz = rgb_rand(100, 1000)
        r0 = zz[0]
        g0 = zz[1]
        b0 = zz[2]
        zz = rgb_rand(100, 1000)
        r1 = zz[0]
        g1 = zz[1]
        b1 = zz[2]
        zz = rgb_rand(100, 1000)
        r2 = zz[0]
        g2 = zz[1]
        b2 = zz[2]
        li = 0
    li1 = light_chng(light0, [r0,g0,b0])
    li2 = light_chng(light1, [r1,g1,b1])
    li3 = light_chng(light2, [r2,g2,b2],energy_=140000)

    li_telem = [str(li1),str(li2),str(li3)]

    r0 = g0 = b0 = 0
    r1 = g1 = b1 = 0
    r2 = g2 = b2 = 0

    if en == 1 or en==en_last+1:
        en_color.r(0)
        en_color.g(0)
        en_color.b(0)
    elif en == 2 or en == 3 or en == 4:
        en_color.r(1)
        en_color.g(1)
        en_color.b(1)
    elif en == 5:
        en_color.rand_rgb(100, 900)
        en_color.r(1)
    elif en == 6:
        en_color.rand_rgb(100, 900)
        en_color.g(1)
    elif en == 7:
        en_color.rand_rgb(100, 900)
        en_color.b(1)
    elif en == en_last:
        en_color.rand_rgb_full(randint(0, 500), randint(501,1000))
        en = 0
    en_telem = en_color.change()

    C.scene.frame_set(fr)
    C.scene.render.stamp_note_text = (
        'OBJS:\n'+str('\n'.join(ob_telem))+
        '\n\nENV:\n'+str('\n'.join(en_telem))+
        '\n\nLIGHTS:\n'+str('\n'.join(li_telem)))
    C.scene.render.filepath = 'C:\\py\\out\\'+ str(fr)+'.jpeg'
    O.render.render(write_still = True)

    ob += 1
    li += 1
    en += 1




