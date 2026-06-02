# =============================================================================
# cityscape/ui.py
# =============================================================================
# The UI + BRIDGE for the packaged CityScape.
#
# WHAT CHANGED FROM STAGE 3: nothing about the UI shape -- same controls,
# same bridge function. The only differences are:
#   - it lives in a package, so it imports its siblings with `from .main`
#   - build_ui is re-exported from __init__.py, so callers say
#     `cityscape.build_ui()` instead of pasting a script
# =============================================================================

import maya.cmds as cmds

from .main import build_scene


_WINDOW_NAME = "cityscape_win"

_CTL_GROUND_SIZE     = "cs_ground_size"
_CTL_BUILDING_COUNT  = "cs_buildings"
_CTL_PARK_TREES      = "cs_park_trees"
_CTL_PARK_RADIUS     = "cs_park_radius"
_CTL_LAMP_START      = "cs_lamp_start"
_CTL_LAMP_END        = "cs_lamp_end"
_CTL_LAMP_SPACING    = "cs_lamp_spacing"
_CTL_PEOPLE_COUNT    = "cs_people_count"
_CTL_INCLUDE_FENCE   = "cs_include_fence"


# =============================================================================
# === BRIDGE ==================================================================
# =============================================================================
def scene_from_ui():
    """Read every control and return a SCENE list (the data layer)."""
    return [
        {"type": "ground", "x": 0, "z": 0,
         "width": cmds.intField(_CTL_GROUND_SIZE, q=True, v=True),
         "depth": cmds.intField(_CTL_GROUND_SIZE, q=True, v=True)},
        {"type": "block", "x": -8, "z": -8,
         "building_count": cmds.intField(_CTL_BUILDING_COUNT, q=True, v=True)},
        {"type": "park", "x": 6, "z": 6,
         "tree_count": cmds.intField(_CTL_PARK_TREES, q=True, v=True),
         "radius":     cmds.floatField(_CTL_PARK_RADIUS, q=True, v=True)},
        {"type": "lamppost_line",
         "start_x": cmds.floatField(_CTL_LAMP_START, q=True, v=True),
         "end_x":   cmds.floatField(_CTL_LAMP_END, q=True, v=True),
         "z": 0,
         "spacing": cmds.floatField(_CTL_LAMP_SPACING, q=True, v=True)},
        {"type": "people", "x": 0, "z": 0,
         "count": cmds.intField(_CTL_PEOPLE_COUNT, q=True, v=True)},
    ] + (
        [{"type": "block_fence", "x": -8, "z": -8,
          "block_size": 5.0, "post_density": 0.6}]
        if cmds.checkBox(_CTL_INCLUDE_FENCE, q=True, v=True) else []
    )


def _on_build_clicked(*_args):
    """Button callback. Catches errors so a bad value doesn't crash Maya."""
    try:
        scene = scene_from_ui()
        build_scene(scene, new_file=True)
    except Exception as e:
        cmds.warning("CityScape build failed: {}".format(e))


# =============================================================================
# === UI ======================================================================
# =============================================================================
def _labeled_int(label, ctl_name, value, lo, hi):
    """One labeled int field row. Keeps build_ui readable."""
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(160, 120),
                   columnAlign=(1, "left"))
    cmds.text(label=label)
    cmds.intField(ctl_name, value=value, minValue=lo, maxValue=hi)
    cmds.setParent("..")


def _labeled_float(label, ctl_name, value, lo, hi):
    """One labeled float field row."""
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(160, 120),
                   columnAlign=(1, "left"))
    cmds.text(label=label)
    cmds.floatField(ctl_name, value=value, minValue=lo, maxValue=hi,
                    precision=1)
    cmds.setParent("..")


def build_ui():
    """Open the CityScape window. Closes any existing instance first."""
    if cmds.window(_WINDOW_NAME, exists=True):
        cmds.deleteUI(_WINDOW_NAME)

    cmds.window(_WINDOW_NAME, title="CityScape Builder",
                widthHeight=(340, 380), sizeable=False)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=6,
                      columnAttach=("both", 10))
    cmds.text(label="CityScape Builder", align="center", height=24)
    cmds.text(label="by Ghost Fazekas Stivala  -- DIGM 131",
              align="center", height=16)
    cmds.separator(style="in")

    _labeled_int("Ground size:",        _CTL_GROUND_SIZE,    40, 10, 200)
    _labeled_int("Buildings per block:", _CTL_BUILDING_COUNT, 4,  1, 20)
    _labeled_int("Trees in park:",       _CTL_PARK_TREES,    8,  1, 40)
    _labeled_float("Park radius:",       _CTL_PARK_RADIUS,   5.0, 1.0, 20.0)

    cmds.separator(style="in")
    _labeled_float("Lamppost start X:",  _CTL_LAMP_START,   -15.0, -100.0, 100.0)
    _labeled_float("Lamppost end X:",    _CTL_LAMP_END,      15.0, -100.0, 100.0)
    _labeled_float("Lamppost spacing:",  _CTL_LAMP_SPACING,   5.0, 1.0, 20.0)

    cmds.separator(style="in")
    _labeled_int("People count:",        _CTL_PEOPLE_COUNT,  6, 0, 50)

    cmds.rowLayout(numberOfColumns=2, columnWidth2=(160, 120),
                   columnAlign=(1, "left"))
    cmds.text(label="Include block fence:")
    cmds.checkBox(_CTL_INCLUDE_FENCE, label="", value=True)
    cmds.setParent("..")

    cmds.separator(style="in")
    cmds.button(label="Build Scene", height=32, command=_on_build_clicked)

    cmds.showWindow(_WINDOW_NAME)
