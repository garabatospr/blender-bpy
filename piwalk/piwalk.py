import bpy
import numpy as np
import random
import bmesh
import math,random

from mathutils import Vector
from bpy import context

##########################
## to select active object
##########################

class act:

    def location(v):
        bpy.context.object.location = v
    def scale(v):
        bpy.context.object.scale = v


####################
## utility functions
####################

def editMode():
    bpy.ops.object.mode_set(mode='EDIT')

def objectMode():
    bpy.ops.object.mode_set(mode='OBJECT')

def smooth():
    bpy.ops.mesh.subdivide(smoothness=1)

def select():
    bpy.ops.mesh.select_all(action='SELECT')

def deselect():
    bpy.ops.mesh.select_all(action='DESELECT')


#########################################
# set directions using a fibonacci sphere
#########################################

def fibonacci_sphere(samples=1,randomize=True):
    rnd = 1.
    if randomize:
        rnd = random.random() * samples

    points = []
    offset = 2./samples
    increment = math.pi * (3. - math.sqrt(5.));

    for i in range(samples):
        y = ((i * offset) - 1) + (offset / 2);
        r = math.sqrt(1 - pow(y,2))

        phi = ((i + rnd) % samples) * increment

        x = math.cos(phi) * r
        z = math.sin(phi) * r

        points.append([x,y,z])

    return points



#############
## set Cycles
#############

def setCycles():
    bpy.context.scene.render.engine = 'CYCLES'


##########
## set GPU
##########

def setGPU():
    bpy.context.scene.cycles.device = 'GPU'


#########################
## set render window size
#########################

def setRenderSize():
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1920


#######################
## set background color
#######################

def setBackground():

    world = bpy.data.worlds['World']

    world.use_nodes = True

    bg = world.node_tree.nodes['Background']
    bg.inputs[0].default_value[:3] = (0.0,0.0,0.0)


#################
## set lamp specs
#################

def setLamp():
    bpy.data.lamps["Lamp"].use_nodes = True

    bpy.data.lamps["Lamp"].type = 'AREA'
    bpy.data.lamps["Lamp"].size = 10
    bpy.data.lamps["Lamp"].size_y = 10
    bpy.data.lamps["Lamp"].node_tree.nodes["Emission"].inputs[1].default_value = 1000



bpy.ops.mesh.primitive_cube_add()

## don't show splash

bpy.context.user_preferences.view.show_splash = False

bpy.context.scene.world.use_nodes = True

# use cycles

setCycles()

# use GPU

setGPU()

# set render size

setRenderSize()

# set background color

setBackground()

# set lamp

setLamp()

objs = bpy.data.objects

## remove default cube

objs.remove(objs["Cube"], do_unlink=True)

digitos = np.load("digitos.npy")

# initial position at origin

x = 0
y = 0
z = 0

# empty vertex list

verts = []

inx  = 0
temp = 0

objectMode()

bpy.ops.object.delete()

## obtain 10 posible walk directions (0..9) using fibonacci sphere

direction = np.array(fibonacci_sphere(samples=10,randomize=False))

xdir = direction[:,0]
ydir = direction[:,1]
zdir = direction[:,2]

stepSize = 3.0

for choice in  digitos[0:1000]:

    xp = x
    yp = y
    zp = z

    x = xp + xdir[choice]*stepSize
    y = yp + ydir[choice]*stepSize
    z = zp + zdir[choice]*stepSize

    x = x % 10
    y = y % 10
    z = z % 10

    inx += 1

    # add coordinates to vertex list

    verts.append([x,y,z])


# create curve "mesh" from vertex list and attach to scene

edges = [[i, i+1] for i in range(len(verts)-1)]

mesh = bpy.data.meshes.new("mesh_name")

mesh.from_pydata(verts,edges, faces=[])

obj = bpy.data.objects.new("curve",mesh)

scene = bpy.context.scene

scene.objects.link(obj)

bpy.context.scene.objects.active = obj

# apply smooth modifier

bpy.ops.object.modifier_apply(modifier="SMOOTH")

bpy.ops.object.modifier_add(type='SMOOTH')

bpy.context.object.modifiers["Smooth"].iterations=100

bpy.data.objects['curve'].select = True

## half bevel

bpy.ops.object.convert(target='CURVE')

bpy.context.object.data.fill_mode = 'HALF'

bpy.context.object.data.bevel_depth = 0.15
bpy.context.object.data.bevel_resolution = 100

bpy.context.object.data.twist_smooth = 100

bpy.ops.object.convert(target='MESH')

bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')

# mesh location

act.location((0,0,0))

act.scale((0.7,0.7,0.7))

bpy.ops.object.shade_smooth()

act.select = True

## assign pbr material

mat = bpy.data.materials.new(name="curveMaterial")

obj.data.materials.append(mat)

bpy.context.scene.pbr_material_settings.enabled = True

bpy.context.scene.thumbs_mats_dielectrics = 'Skin'

mat.use_nodes = True


