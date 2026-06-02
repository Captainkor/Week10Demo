# =============================================================================
# cityscape/main.py
# =============================================================================
# The LOGIC driver + DATA contract for the packaged form of CityScape.
#
# Ghost's main.py from the loose-files version had a sys.path patch at the
# top so the sibling imports would work. Inside a package we don't need
# that -- relative imports (`from . import ...`) just work.
#
# Public surface:
#   - build_scene(scene, new_file=True)  -- the driver (LOGIC)
#   - BUILDERS                            -- the dispatch table (BRIDGE-ish)
#   - SCENE                               -- a sample DATA payload
# =============================================================================

import maya.cmds as cmds

from . import geometry_utils as geo
from . import layout_utils as lay


# =============================================================================
# === DATA ====================================================================
# =============================================================================
# A demo scene shipped with the package. ui.py builds its own SCENE from
# control values; this one is here so the package is useful straight away:
#
#     import cityscape
#     cityscape.main.build_scene()   # builds the demo scene
# -----------------------------------------------------------------------------
SCENE = [
    {"type": "ground",         "x": 0,   "z": 0,   "width": 60, "depth": 60},
    {"type": "block",          "x": -10, "z": -10, "building_count": 4},
    {"type": "block",          "x":  10, "z":  10, "building_count": 4},
    {"type": "block_fence",    "x": -10, "z": -10, "block_size": 5,  "post_density": 0.5},
    {"type": "park",           "x": 0,   "z": 0,   "tree_count": 8,  "radius": 6},
    {"type": "lamppost_line",  "start_x": -20, "end_x": 20, "z": 0,  "spacing": 5},
    {"type": "road",           "x": 0,   "z": 0,   "width": 40, "depth": 4},
    {"type": "people",         "x": 0,   "z": 0,   "count": 6},
]


# =============================================================================
# === BRIDGE (data-type -> logic call) =======================================
# =============================================================================
# This is the data->logic bridge. Each entry takes a data item and calls
# the matching logic function. Same shape Ghost wrote in the loose-files
# version; only the imports above changed.
# -----------------------------------------------------------------------------
BUILDERS = {
    "ground":        lambda i: geo.create_ground(i["x"], i["z"],
                                                 plane_width=i.get("width", 24),
                                                 plane_depth=i.get("depth", 24)),
    "building":      lambda i: geo.create_building(i["x"], i["z"],
                                                   width=i.get("width", 2.0),
                                                   height=i.get("height", 5.0),
                                                   depth=i.get("depth", 2.0)),
    "block":         lambda i: lay.build_city_block(i["x"], i["z"],
                                                    building_count=i.get("building_count", 4)),
    "park":          lambda i: lay.build_park(i["x"], i["z"],
                                              tree_count=i.get("tree_count", 6),
                                              radius=i.get("radius", 5.0)),
    "lamppost_line": lambda i: lay.line_street_with_lampposts(i["start_x"], i["end_x"],
                                                              i["z"],
                                                              spacing=i.get("spacing", 4.0)),
    "block_fence":   lambda i: lay.line_block_with_fence(i["x"], i["z"],
                                                         block_size=i.get("block_size", 5.0),
                                                         post_density=i.get("post_density", 0.5)),
    "road":          lambda i: geo.create_road(i["x"], i["z"],
                                               width=i.get("width", 24),
                                               depth=i.get("depth", 5)),
    "people":        lambda i: lay.place_people(i["x"], i["z"], i["count"]),
    "lamppost":      lambda i: geo.create_lamppost(i["x"], i["z"]),
    "vending":       lambda i: geo.create_vending_machine(i["x"], i["z"]),
    "pinetree":      lambda i: geo.create_pinetree(i["x"], i["z"]),
    "oaktree":       lambda i: geo.create_oaktree(i["x"], i["z"]),
    "person":        lambda i: geo.create_person(i["x"], i["z"]),
}


# =============================================================================
# === LOGIC (driver) ==========================================================
# =============================================================================
def _validate_item(item):
    """Validate one scene item at the LOGIC boundary. Raises ValueError."""
    if not isinstance(item, dict):
        raise ValueError("scene item must be a dict, got: {!r}".format(type(item).__name__))
    if "type" not in item:
        raise ValueError("scene item missing required key 'type': {!r}".format(item))


def build_scene(scene=None, new_file=True):
    """Build every item in `scene`. Pass new_file=False to add to current scene.

    Args:
        scene (list[dict] | None): A list of scene-item dicts. Defaults to
            the SCENE constant.
        new_file (bool): If True, start a fresh Maya file first.

    Returns:
        list: Whatever each builder returned, one per item.
    """
    if scene is None:
        scene = SCENE
    if new_file:
        cmds.file(new=True, force=True)
    results = []
    for item in scene:
        try:
            _validate_item(item)
        except ValueError as e:
            cmds.warning("Skipped invalid scene item: {}".format(e))
            continue
        builder = BUILDERS.get(item["type"])
        if builder is None:
            cmds.warning("Unknown scene item type: {!r}".format(item["type"]))
            continue
        try:
            results.append(builder(item))
        except Exception as e:
            cmds.warning("Failed to build {!r}: {}".format(item, e))
    return results
