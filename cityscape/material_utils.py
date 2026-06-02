# --- material_utils.py ---
"""
material_utils.py --- Shader creation for Build City Scape
======================================================================
DIGM 131 - Week 6 | Author: Ghost Fazekas Stivala

Usage:
    Assign and create materials for Build City Scape
    import material_utils as mat
    mat.create_and_assign(obj_name)
"""

import maya.cmds as cmds

def create_material(name="custom_mat", color=(0.5, 0.5, 0.5),
                    material_type="lambert"):
    shader = cmds.shadingNode(material_type, asShader=True, name=name)
    shader_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=name + "_SG")
    cmds.connectAttr(shader + ".outColor", shader_group + ".surfaceShader", force=True)
    cmds.setAttr(shader + ".color", *color, type="double3")
    return shader

def assign_material(obj_name, shader_name):
    sgs = cmds.listConnections(shader_name + ".outColor", type="shadingEngine")
    cmds.sets(obj_name, edit=True, forceElement=sgs[0])

def create_and_assign(obj_name, name="auto_mat", color=(0.5, 0.5, 0.5),
                      material_type="lambert"):
    shader = create_material(name, color, material_type)
    assign_material(obj_name, shader)
    return shader
