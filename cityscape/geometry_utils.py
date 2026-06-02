# --- geometry_utils.py ---
"""
geometry_utils.py --- Geometry creation functions for Build City Scape
======================================================================
DIGM 131 - Week 6 | Author: Ghost Fazekas Stivala

Usage:
    import geometry_utils as geo
    geo.create_building(width=3, height=8)
"""

import maya.cmds as cmds

import math

#Material Shader Creation/ Application Utilities______________________________________________

def create_and_assign(obj_name, name="auto_mat", color=(0, 0, 0),
                      material_type="lambert"):
    """Convenience function: create a material and immediately assign it.

    Args:
        obj_name (str): The Maya object to receive the material.
        name (str): Name for the new shader.
        color (tuple): (r, g, b) color, values 0.0 to 1.0.
        material_type (str): "lambert" or "blinn".

    Returns:
        str: The name of the created shader node.
    """

    shader = cmds.shadingNode(
        material_type,
        name=name,
        asShader=True
    )

    cmds.setAttr(
        f"{shader}.color",
        *color,
        type="double3"
    )

    shader_group = cmds.sets(
        name=f"{shader}SG",
        empty=True,
        renderable=True,
        noSurfaceShader=True
    )

    cmds.connectAttr(
        f"{shader}.outColor",
        f"{shader_group}.surfaceShader"
    )

    cmds.sets(
        obj_name,
        edit=True,
        forceElement=shader_group
    )

    return shader

def assign_material(obj_name, shader_name):
    """Assign an existing shader to a Maya object.

    Looks up the shading group connected to the shader and adds the
    object to it. Pass the shader name returned from create_material();
    you do not need to track the shading group yourself.

    Args:
        obj_name (str): The name of the Maya transform or shape node.
        shader_name (str): The shader name returned from create_material().

    Returns:
        None
    """

    if not cmds.objExists(obj_name):
        cmds.warning(
            "assign_material: '{}' does not exist.".format(obj_name)
        )

        return

    if not cmds.objExists(shader_name):
        cmds.warning(
            "assign_material: shader '{}' not found.".format(shader_name)
        )

        return

    # Find the shading group connected to this shader
    shading_groups = cmds.listConnections(
        "{}.outColor".format(shader_name),
        type="shadingEngine"
    )

    if not shading_groups:
        cmds.warning(
            "No shading group found for '{}'.".format(shader_name)
        )

        return

    # Expand groups to their descendant shapes; cmds.sets on a group
    # transform alone does not always propagate to shape nodes.

    shapes = cmds.listRelatives(
        obj_name,
        allDescendents=True,
        shapes=True,
        fullPath=True
    ) or []

    targets = shapes if shapes else [obj_name]

    cmds.sets(
        targets,
        edit=True,
        forceElement=shading_groups[0]
    )

#_____________________________________________________________________________________________
# Insert functions here
def create_ground(x, z, plane_width=24, plane_depth=24):
    """
    Creates a ground plane for a 3D scene.

    This function generates a polygonal plane that can represent the ground in a 3D
    environment. The size of the plane can be adjusted by specifying its width and
    depth.

    Parameters:
    x (float): The x-coordinate where the plane will be positioned.
    z (float): The z-coordinate where the plane will be positioned.
    plane_width (float, optional): The width of the plane. Defaults to 24.
    plane_depth (float, optional): The depth of the plane. Defaults to 24.

    Returns:
    str: The name of the created polygonal plane.
    """
    ground = cmds.polyPlane(w=plane_width, h=plane_depth, )[0]
    return ground

def create_building(x, z, width=2.0, height=5.0, depth=2.0, position=(0, 0, 0)):
    """
    Creates a building at the specified x and z coordinates with the given dimensions and optional position.

    Parameters:
    x: float
        The x-coordinate where the building will be placed.
    z: float
        The z-coordinate where the building will be placed.
    width: float, optional
        The width of the building. Defaults to 2.0.
    height: float, optional
        The height of the building. Defaults to 5.0.
    depth: float, optional
        The depth of the building. Defaults to 2.0.
    position: tuple[float, float, float], optional
        The position values in a tuple as (x, y, z). Defaults to (0, 0, 0).

    Returns:
    str
        The name of the created building object.
    """
    building = cmds.polyCube(width=width, height=height, depth=depth)[0]
    position = cmds.move(x, height / 2.0, z, building)
    return building

def create_road(x, z, width=24, depth=5, name="road", position=(0, 0, 0)):
    """
    Creates a rectangular road geometry at the specified position and size
    using a polygonal plane. The road name and position can be customized.

    :param x: The x-coordinate of the road's position.
    :type x: float
    :param z: The z-coordinate of the road's position.
    :type z: float
    :param width: The width of the road. Default is 24.
    :type width: float, optional
    :param depth: The depth of the road. Default is 5.
    :type depth: float, optional
    :param name: The base name for identifying the created road object. Default is "road".
    :type name: str, optional
    :param position: A tuple representing the translation offset (x, y, z) for the road object.
                     Default is (0, 0, 0).
    :type position: tuple[float, float, float], optional
    :return: An identifier for the created road geometry object.
    :rtype: object
    """
    road = cmds.polyPlane(w=width, h=depth, name=f"road_#")
    cmds.move(x, z, position)
    return road

def create_pinetree(x, z, name="Pine_Tree_{}", trunk_radius=0.3, trunk_height=1.25, canopy_radius=1, canopy_height=3):
    """
    Creates a tree model with a cylindrical trunk and layered, coned canopies at a given
    x and z position.

    This function generates the 3D components of a tree using a trunk created as a
    cylinder and a canopy created as a cone. The components are placed based on
    the specified position and then grouped together to form a tree model.

    Parameters:
        x (float): The x-coordinate of the tree's position.
        z (float): The z-coordinate of the tree's position.
        name (str): Desired base name for the tree's transform nodes.
        trunk_radius (float): Radius of the pine tree trunk (in scene units).
        trunk_height (float): Height of the pine tree trunk (in scene units).
        canopy_radius (float): Radius of the canopy cones (in scene units).
        canopy_height (float): Height of the canopy cones (in scene units).

    Returns:
        tuple: Names of the trunk and three canopy transform nodes.
    """
    trunk = cmds.polyCylinder(
        name="trunk_{}".format(name),
        radius=trunk_radius,
        height=trunk_height,
    )[0]
    cmds.move(x, trunk_height / 2.0, z, trunk)

    canopy_1 = cmds.polyCone(
        name="canopy1_{}".format(name),
        radius=canopy_radius,
        height=canopy_height
    )[0]
    canopy_1_y = trunk_height + canopy_radius * 0.8
    cmds.move(x, canopy_1_y, z, canopy_1)

    canopy_2 = cmds.polyCone(
        name="canopy2_{}".format(name),
        radius=canopy_radius,
        height=canopy_height
    )[0]
    canopy_2_y = trunk_height + canopy_radius * 1.8
    cmds.move(x, canopy_2_y, z, canopy_2)

    canopy_3 = cmds.polyCone(
        name="canopy3_{}".format(name),
        radius=canopy_radius,
        height=canopy_height
    )[0]
    canopy_3_y = trunk_height + canopy_radius * 2.8
    cmds.move(x, canopy_3_y, z, canopy_3)

    create_and_assign(trunk, name="trunkMat", color=(0.070, 0.042, 0.02), material_type="lambert")
    create_and_assign(canopy_1, name="canopyMat", color=(0.012, 0.069, 0.034), material_type="lambert")
    create_and_assign(canopy_2, name="canopy2Mat", color=(0.032, 0.095, 0.040), material_type="lambert")
    create_and_assign(canopy_3, name="canopy3Mat", color=(0.052, 0.125, 0.050), material_type="lambert")

    return trunk, canopy_1, canopy_2, canopy_3

def create_oaktree(x, z, trunk_height=2.0, canopy_radius=1.2, position=(0, 0, 0)):
    """
    Creates a tree model with a cylindrical trunk and a spherical canopy at a given
    position, height, and radius.

    This function generates the 3D components of a tree using a trunk created as a
    cylinder and a canopy created as a sphere. The components are placed based on
    the specified position and then grouped together to form a tree model.

    Parameters:
        x (float): The x-coordinate of the tree's position.
        z (float): The z-coordinate of the tree's position.
        trunk_height (float, optional): The height of the trunk. Default is 2.0.
        canopy_radius (float, optional): The radius of the conical canopy. Default
            is 1.2.
        position (tuple[float, float, float], optional): A tuple representing the
            position of the tree in 3D space. Default is (0, 0, 0).

    Returns:
        tuple: A tuple containing the created trunk and canopy objects.
    """
    trunk_radius = 0.3
    trunk = cmds.polyCylinder(radius=trunk_radius, height=trunk_height)[0]
    position = cmds.move(x, trunk_height / 2.0, z, trunk)
    canopy = cmds.polySphere(radius=canopy_radius)[0]
    canopy_y = trunk_height + canopy_radius * 0.6
    cmds.move(x, canopy_y, z, canopy)
    cmds.group(trunk, canopy)
    position = cmds.move(x, trunk_height / 2.0, z, trunk)
    return trunk, canopy

def create_fence(length=10, height=1.5, post_count=6, position=(0, 0, 0)):
    """
    Creates a 3D fence using evenly spaced posts and a rail, grouped and
    moved to `position`.

    Parameters:
    length: float, optional
        The total length of the fence. Default is 10.
    height: float, optional
        The height of the posts. Default is 1.5.
    post_count: int, optional
        The number of posts along the fence. Default is 6.
    position: tuple[float, float, float], optional
        The (x, y, z) world position of the fence group. Default is (0, 0, 0).

    Returns:
    str
        The name of the fence group.
    """
    spacing = length / (post_count - 1) if post_count > 1 else length
    post_list = []
    for i in range(post_count):
        post = cmds.polyCube(w=0.5, h=height, d=0.5, name=f"posts_{i}")[0]
        cmds.move(i * spacing, height / 2, 0, post)
        post_list.append(post)
    fence_length = post_count * spacing
    rail = cmds.polyCube(w=fence_length, h=0.25, d=0.25, name="rail")[0]
    cmds.move((fence_length - spacing) / 2, height / 2, -0.1, rail)
    fence = cmds.group(post_list + [rail], name="fence_#")
    cmds.move(position[0], position[1], position[2], fence)
    return fence

def create_bench(x, z, bench_width=3, height=0.25, rotation_y=0):
    """
    Creates a bench with specified dimensions and rotation in a 3D scene.

    This function generates a bench consisting of a top surface and a leg,
    positions it in 3D space at the specified coordinates, and optionally
    rotates it along the Y-axis.

    Args:
        x (float): The X-coordinate of the bench in the scene.
        z (float): The Z-coordinate of the bench in the scene.
        bench_width (float, optional): The width of the bench. Default is 3.
        height (float, optional): The height of the bench's top surface.
            Default is 0.25.
        rotation_y (float, optional): The angle of rotation around the Y-axis
            for the entire bench group. Default is 0.

    Returns:
        str: The name of the group node containing the bench and its leg.
    """
    bench_width = 3
    bench_height = 0.25
    bench = cmds.polyCube(w=bench_width, h=height, d=1)[0]
    cmds.move(x, 1, z, bench)
    bench_leg = cmds.polyCube(w=1, h=1, d=1)
    cmds.move(x, 0.5, z, bench_leg)
    grp = cmds.group(bench, bench_leg, name="bench#")
    cmds.rotate(0, rotation_y, 0, grp)
    return grp

def create_lamppost(x, z, pole_height=3.0, light_radius=0.5, name="lamppost", position=(0, 0, 0)):
    """
    Creates a lamppost at the specified position with a pole and a lamp.
    This function generates a 3D lamppost with a cylindrical pole and a spherical lamp placed
    on top of the pole. The position and dimensions of the lamppost components can be adjusted
    with the provided parameters.

    Parameters:
        x (float): The x-coordinate of the lamppost base position.
        z (float): The z-coordinate of the lamppost base position.
        pole_height (float, optional): The height of the pole. Defaults to 3.0.
        light_radius (float, optional): The radius of the lamp (spherical part). Defaults to 0.5.
        position (tuple[float, float, float], optional): Ignored within this function.

    Returns:
        tuple[str, str]: A tuple containing two strings - the names of the created pole object
        and the lamp object in the 3D environment.
    """
    pole = cmds.polyCylinder(radius=0.1, height=pole_height)[0]
    cmds.move(x, pole_height / 2.0, z, pole)
    lamp = cmds.polySphere(radius=light_radius)[0]
    cmds.move(x, pole_height + 0.25, z, lamp)
    cmds.group(pole, lamp, n=f"lamppost_#")
    return pole, lamp

def create_vending_machine(x, z, width=1.5, height=3, depth=1.5, name="machine", position=(0, 0, 0)):
    """
    Creates a vending machine model in a 3D environment.

    This function generates a vending machine object using a polycube with specified
    dimensions and places it at the given coordinates. By default, the dimensions
    are set to standard vending machine proportions.

    :param x: The x-coordinate for placing the vending machine.
    :type x: float
    :param z: The z-coordinate for placing the vending machine.
    :type z: float
    :param width: The width of the vending machine. Default is 1.5 units.
    :type width: float
    :param height: The height of the vending machine. Default is 3 units.
    :type height: float
    :param depth: The depth of the vending machine. Default is 1.5 units.
    :type depth: float
    :param name: The base name of the vending machine object. Default is "machine".
    :type name: str
    :param position: The initial position offset for the vending machine. Default is
        (0, 0, 0).
    :type position: tuple[float, float, float]
    :return: The created vending machine object.
    :rtype: list
    """
    machine = cmds.polyCube(w=width, h=height, d=depth, name=f"machine_#")
    position = cmds.move(x, height / 2.0, z, machine)
    return machine

def create_person(x,z, width=1, height=2, depth=1, radius=1, name="person", position=(0, 0, 0)):
    """
    Creates a 3D person model consisting of a body and a head in the scene using Maya commands.

    The function first creates a cube to represent the body and places it at the specified
    position with the given dimensions. Next, it creates a sphere to represent the head
    and positions it above the body. Both the body and the head are grouped together under
    a single entity.

    :param x: The x-coordinate where the model will be placed.
    :type x: float
    :param z: The z-coordinate where the model will be placed.
    :type z: float
    :param width: The width of the person's body. Defaults to 1.
    :type width: float, optional
    :param height: The height of the person's body. Defaults to 2.
    :type height: float, optional
    :param depth: The depth of the person's body. Defaults to 1.
    :type depth: float, optional
    :param radius: The radius of the person's head. Defaults to 1.
    :type radius: float, optional
    :param name: Name identifier for the person model. Defaults to "person".
    :type name: str, optional
    :param position: Tuple representing the initial position of the person model. Defaults to (0, 0, 0).
    :type position: tuple[float, float, float], optional
    :return: A tuple containing the created body and head of the 3D person model.
    """
    person_body = cmds.polyCube(w=width, h=height, d=depth, name="person_body")
    cmds.move(x, height / 2.0, z, person_body)
    person_head = cmds.polySphere(r=radius, name="person_head")
    cmds.move(x, height + 1, z, person_head)
    cmds.group(person_body, person_head, n=f"person_#")
    return person_body, person_head

if __name__ == "__main__":
    # Self-test: runs only when executed directly
    cmds.file(new=True, force=True)
    print("geometry_utils self-test: TODO")