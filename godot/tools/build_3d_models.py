"""Rebuild original low-poly props: blender -b --python godot/tools/build_3d_models.py"""
import bpy
import math
from pathlib import Path
from mathutils import Vector

OUT = Path(__file__).resolve().parents[1] / 'assets' / 'models'
OUT.mkdir(parents=True, exist_ok=True)


def material(name, color, metallic=0, emission=0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    node = mat.node_tree.nodes.get('Principled BSDF')
    node.inputs['Base Color'].default_value = (*color, 1)
    node.inputs['Roughness'].default_value = .8
    node.inputs['Metallic'].default_value = metallic
    if emission:
        node.inputs['Emission Color'].default_value = (*color, 1)
        node.inputs['Emission Strength'].default_value = emission
    return mat

stone = material('weathered charcoal stone', (.22,.20,.28))
edge = material('carved stone edges', (.36,.32,.41))
iron = material('old dark iron', (.075,.065,.1), .7)
gold = material('aged gold', (.6,.34,.08), .55)
wood = material('dead wood', (.11,.08,.13))
flame = material('amber flame', (1,.26,.035), emission=3)
crystal = material('teal healing crystal', (.045,.7,.5), .15, 1.5)


def cube(name, center, size, mat=stone, bevel=.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('soft worn edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return obj


def cylinder(name, center, radius, depth, mat=stone, vertices=8):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    return obj


def branch(a, b, radius):
    a, b = Vector(a), Vector(b)
    obj = cylinder('twisted branch', (a+b)/2, radius, (b-a).length, wood, 6)
    obj.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()


def export(name, build):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    build()
    bpy.ops.export_scene.gltf(filepath=str(OUT / (name+'.glb')), export_format='GLB',
                             export_apply=True, export_yup=True)
    print('EXPORTED', name)


def pillar():
    cube('foot', (0,0,.12),(.7,.7,.24),edge)
    cylinder('octagonal shaft',(0,0,1.25),.21,2.1)
    for height in [.35,2.15,2.35]:
        cube('carved collar',(0,0,height),(.54,.54,.14),edge)
    cube('capital',(0,0,2.5),(.78,.78,.18),edge)


def arch():
    for x in [-.9,.9]:
        cube('gate pier',(x,0,1.0),(.36,.5,2.0))
        cube('base',(x,0,.12),(.56,.7,.24),edge)
        cube('capital',(x,0,2.0),(.5,.65,.2),edge)
    # Faceted pointed gothic arch, with individually carved voussoirs.
    for side in [-1,1]:
        for i in range(6):
            t = i/5
            x = side*(.9*(1-t))
            z = 2.05+.95*t
            block = cube('arch stone',(x,0,z),(.28,.55,.26),edge)
            block.rotation_euler[1] = side*math.radians(-43)
    cube('keystone',(0,0,3.05),(.32,.64,.34),gold)


def tombstone():
    cube('grave base',(0,0,.09),(.7,.5,.18),edge)
    cube('grave marker',(0,0,.52),(.48,.18,.82))
    cap=cube('gabled top',(0,0,.98),(.4,.2,.4),edge)
    cap.rotation_euler[1]=math.pi/4
    cube('cross upright',(0,-.11,.64),(.06,.025,.3),gold,0)
    cube('cross arms',(0,-.11,.68),(.22,.025,.06),gold,0)


def torch():
    cylinder('iron stand',(0,0,.65),.045,1.3,iron)
    cube('foot',(0,0,.06),(.3,.3,.12),iron)
    cylinder('brazier',(0,0,1.3),.18,.18,iron)
    for z,r in [(1.46,.14),(1.64,.09),(1.8,.025)]:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=r,location=(0,0,z))
        obj=bpy.context.object; obj.name='faceted flame';obj.scale.z=1.6;obj.data.materials.append(flame)


def tree():
    branch((0,0,0),(.1,0,1.2),.16)
    branch((.1,0,1.2),(-.15,0,2.5),.11)
    branch((-.15,0,2.5),(.12,0,3.4),.06)
    for side in [-1,1]:
        branch((.04,0,1.4),(side*.7,.15,2.1),.075)
        branch((side*.7,.15,2.1),(side*1.1,.1,2.8),.04)
        branch((side*.7,.15,2.1),(side*1.25,-.15,2.05),.03)
    for x,y in [(.4,.2),(-.4,.15),(.1,-.4)]:
        branch((0,0,.2),(x,y,0),.075)


def gem():
    cylinder('pedestal',(0,0,.08),.18,.16,edge)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.2,location=(0,0,.38))
    obj=bpy.context.object;obj.name='healing crystal';obj.scale.z=1.6;obj.data.materials.append(crystal)


def coffin():
    cube('sarcophagus',(0,0,.22),(.7,1.5,.44))
    cube('lid',(0,0,.48),(.8,1.6,.14),edge)
    cube('lid cross vertical',(0,0,.565),(.07,.8,.025),gold,0)
    cube('lid cross horizontal',(0,-.12,.565),(.4,.07,.025),gold,0)


def block():
    cube('stone block',(0,0,.225),(2,1.8,.45))
    cube('top lip',(0,0,.44),(2.03,1.83,.08),edge)
    for x in [-.5,.5]:
        cube('mortar seam',(x,-.902,.22),(.025,.01,.4),iron,0)

for name, build in [('pillar',pillar),('arch',arch),('tombstone',tombstone),('torch',torch),
                    ('dead_tree',tree),('crystal',gem),('coffin',coffin),('stone_block',block)]:
    export(name,build)
