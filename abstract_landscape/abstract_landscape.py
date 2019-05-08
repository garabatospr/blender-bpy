import bpy

import mathutils

import numpy as np

from math import radians

import fnmatch

############################################################
## "abstract_landscape" by Elio Ramos (aka garabatospr)
## Blender 2.79 BPY
## Licensed under Creative Commons Attribution
## ShareAlike https://creativecommons.org/licenses/by-sa/3.0
## https://creativecommons.org/licenses/GPL/2.0/
## Feel free to do whatever you want with this code.
## If you do use it,I would like to see what you did.
## Send me an email to mecobi@gmail.com
############################################################

## switch to object mode

def objectMode():
    bpy.ops.object.mode_set(mode='OBJECT')

## select all the meshes

def select():
    bpy.ops.mesh.select_all(action='SELECT')

## deselect all the meshes

def deselect():
    bpy.ops.mesh.select_all(action='DESELECT')

## select active object

class act:

    def location(v):
        bpy.context.object.location = v
    def scale(v):
        bpy.context.object.scale = v

## point camera to location

def point_at(ob,target):
    ob_loc = ob.location
    dir_vec = target - ob.location
    ob.rotation_euler = dir_vec.to_track_quat('-Z','Y').to_euler()


context = bpy.context

scene = bpy.context.scene

################
## cycles render
################

scene.render.engine = 'CYCLES'

## GPU

scene.cycles.device = 'GPU'

## render window size

scene.render.resolution_x = 1080
scene.render.resolution_y = 1350

#######################
## set background color
######################@

world = bpy.data.worlds['World']

world.use_nodes = True

bg = world.node_tree.nodes['Background']
bg.inputs[0].default_value[:3] = (0.0,0.0,0.0)
bg.inputs[1].default_value = 1.0

#################
## set lamp specs
#################

bpy.data.lamps["Lamp"].use_nodes = True

bpy.data.lamps["Lamp"].type = 'AREA'
bpy.data.lamps["Lamp"].size = 5
bpy.data.lamps["Lamp"].size_y = 5
bpy.data.lamps["Lamp"].node_tree.nodes["Emission"].inputs[1].default_value = 2000

scene.world.use_nodes = True

objs = bpy.data.objects

# remove default cube

objs.remove(objs["Cube"],do_unlink=True)

# read svg file
# depending of the shapes in the SVG file some of the parameters, camera locations, etc. may
# require tunning


bpy.ops.import_curve.svg (filepath="landscape1.svg")

# list of curve objects

curve_objs = [obj for obj in bpy.context.scene.objects if fnmatch.fnmatchcase(obj.name, "Curve*")]

# list of camera objects

camera_objs = [obj for obj in bpy.context.scene.objects if fnmatch.fnmatchcase(obj.name, "Camera*")]

inx = 0

# this parameter sets the height of each mesh "layer"..depending of the svg image may need tunning

altura = 0.00015

for curve in curve_objs[::-1]:

    bpy.context.scene.objects.active = curve

    curve.select = True

    curve.location = (0,0,inx)

    curve.scale= (120,120,120)

    bpy.context.scene.objects.active = curve

    bpy.ops.object.convert(target='MESH')

    curve.select = True

    act.location((0,0,inx))

    bpy.ops.object.modifier_add(type='SOLIDIFY')
    context.object.modifiers["Solidify"].thickness = altura

    ## this parameter sets the separation between each "layer" ode meshes

    inx += 0.01

## join all the meshes

bpy.ops.object.join()

## set origin

bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')

# mesh location

act.location((0,-10,0))


# camera location

camera = camera_objs[0]

camera.location = (0.0, 0, 16.0)

piece = bpy.context.scene.objects[0]

piece.location = (0.0,0.0,0.0)

# point camera

point_at(camera, mathutils.Vector((0,0,0)))

