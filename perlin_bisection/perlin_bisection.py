import bpy

import bmesh

import math

import numpy as np

import colorsys

import decimal

import noise

############################################################
## "perlin_bisection" by Elio Ramos (aka garabatospr)
## Blender 2.79 BPY
## Licensed under Creative Commons Attribution
## ShareAlike https://creativecommons.org/licenses/by-sa/3.0
## https://creativecommons.org/licenses/GPL/2.0/
## Feel free to do whatever you want with this code.
## If you do use it,I would like to see what you did.
## Send me an email to mecobi@gmail.com
############################################################

#################
## bisect object
#################

def bisect():

    editMode()

    bpy.ops.mesh.select_all(action='TOGGLE')

    bpy.ops.mesh.bisect(plane_co=(5.7957, 7.44908, 0), plane_no=(0.774166, -0.632921, -0.00879672), use_fill=False,clear_outer = True,xstart=829, xend=475, ystart=550, yend=117)

    objectMode()


##########
## set GPU
##########

def setGPU():
    bpy.context.scene.cycles.device = 'GPU'


#############
## set Cycles
#############

def setCycles():
    bpy.context.scene.render.engine = 'CYCLES'


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
    bg.inputs[0].default_value[:3] = (1.0,1.0,1.0)

#################
## set lamp specs
#################

def setLamp():
    bpy.data.lamps["Lamp"].use_nodes = True

    bpy.data.lamps["Lamp"].type = 'AREA'
    bpy.data.lamps["Lamp"].size = 10
    bpy.data.lamps["Lamp"].size_y = 10
    bpy.data.lamps["Lamp"].node_tree.nodes["Emission"].inputs[1].default_value = 1000

###############
## set editMode
###############

def editMode():
    bpy.ops.object.mode_set(mode='EDIT')


#################
## set objectMode
#################


def objectMode():
    bpy.ops.object.mode_set(mode='OBJECT')


##################################
## split sequence utility function
##################################

def split_seq(seq,size):
    """ Split up seq in pieces of size """
    return [seq[i:i+size] for i in range(0, len(seq), size)]


## number of random steps

ndat = 5000


## to asign the colors in a deterministic way I am using the digits of the irrational sqrt(3)!!!

miDecimal = decimal.Context(prec=ndat)
n = miDecimal.sqrt(3)
digitos = [int(d) for d in str(n)[2:]]


def drawSurface(nPoints):

    xp = 0.1
    yp = 1000.0
    zp = 10000.0

    verts = []

    for inx in range(nPoints):

        x = noise.pnoise1(xp)*10
        y = noise.pnoise1(yp)*10
        z = noise.pnoise1(zp)*10

        verts.append([x,y,z])

        xp +=0.05
        yp +=0.05
        zp +=0.05


    edges = [[i, i+1] for i in range(len(verts)-1)]


    ####### mesh #######

    mesh = bpy.data.meshes.new("mesh_name")
    mesh.from_pydata(verts, edges, faces=[])

    obj = bpy.data.objects.new("curva", mesh)

    scene = bpy.context.scene
    scene.objects.link(obj)

    bpy.context.scene.objects.active = obj

    bpy.ops.object.modifier_apply(modifier="SMOOTH")
    bpy.ops.object.modifier_add(type='SMOOTH')
    bpy.context.object.modifiers["Smooth"].iterations=100

    bpy.data.objects['curva'].select = True

    bpy.ops.object.convert(target='CURVE')

    bpy.context.object.data.fill_mode = 'FRONT'

    bpy.context.object.data.bevel_depth = 0.50

    bpy.context.object.data.bevel_resolution = 100

    bpy.context.object.data.twist_smooth = 100

    bpy.ops.object.convert(target='MESH')



## erase default cube

objs = bpy.data.objects

objs.remove(objs["Cube"],do_unlink=True)

setBackground()

## para utilizar el render de CYCLES

setCycles()

## GPU

setGPU()

## set render size

setRenderSize()

## set lamp specs

setLamp()

## read palette from file

colores = np.load("mypalette.npy")

## sometimes the saturation from the color palette is not quite right..convert to HSV and increase a bit

for inx in range(0,len(colores)):

    colorHSV = colorsys.rgb_to_hsv(colores[inx][0],colores[inx][1],colores[inx][2])

    colores[inx] = colorsys.hsv_to_rgb(colorHSV[0],colorHSV[1] + 0.2,colorHSV[2])


drawSurface(nPoints=ndat)

bpy.data.objects['curva'].select = True

objetoActivo = bpy.context.active_object
objetoActivo.data.materials.append(bpy.data.materials.new(name="Gris"))
bpy.context.object.active_material.diffuse_color = (0.9,0.9,0.9)

ob = bpy.context.object
me = ob.data

mat_offset = len(me.materials)
mat_count = 10

mats = []
for i in range(mat_count):
    mat = bpy.data.materials.new("Mat_%i" % i)
    rgb = colores[i % 9]
    mat.diffuse_color = rgb[0],rgb[1],rgb[2]
    me.materials.append(mat)


bpy.data.objects['curva'].select = True

bpy.ops.object.mode_set(mode='OBJECT')

face_list = [face for face in me.polygons]

temp = split_seq(face_list,34)

i = 0

while  i < len(temp):
    for face in temp[i]:
        face.material_index = digitos[i] + 1
    i+=1

bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')

bpy.ops.object.shade_smooth()

bisect()

##########################################################################################################################################
## Important: the resulting model may need some minimal post-production/exploration like zooming in interesting areas using Blender's GUI.
## Most the time the iteresting areas are near the center of the resulting 3D structure
##########################################################################################################################################
