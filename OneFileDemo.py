"""demo_ui_and_polish.py  —  DIGM 131, Week 10
Building a UI + Integration and Polish

WHAT THIS DEMO SHOWS
--------------------
For nine weeks your code has run from the Script Editor. This week it gets a
window. The whole lesson is ONE idea:

    The UI calls your functions. It never contains scene logic itself.

To keep that separation clean we use THREE layers, the same way the data-driven
scenes worked back in Weeks 4-5:

    UI  <->  DATA  <->  LOGIC

    * The UI's only job is to produce a DATA structure (a settings dict).
    * The LOGIC's only job is to consume that dict and build the scene.
    * Neither layer knows how the other works. Swap the UI for a different
      front door and the logic doesn't change at all.

We build that up in sections that match the slides:
    Section 1 — The logic (data-driven functions: consume a dict, build a scene)
    Section 2 — Anatomy of a window (window -> layout -> controls -> show)
    Section 3 — The controls toolbox (slider, text field, dropdown, checkbox)
    Section 4 — Callbacks: connecting clicks to code (the bridge function)
    Section 5 — Putting it together: UI -> settings dict -> logic
    Section 6 — Integration & polish: refactoring a messy version into a clean one
    Section 7 — Your tool will differ: the pattern is what transfers, not this tool

HOW TO RUN
----------
Open this file in Maya's Script Editor (Python tab) and run the whole thing,
or run one section at a time by calling the function at the bottom of each
section. Read the comments before you run — predict what each piece does.
"""

import maya.cmds as cmds
import maya.mel as mel   # only needed in Section 8 to find the active shelf


# =====================================================================
# SECTION 1 — THE LOGIC (DATA-DRIVEN)
# ---------------------------------------------------------------------
# Before any UI, we need functions that DO something. These are exactly
# the kind of functions you've been writing since Week 3: each does one
# job, has a docstring, validates its input, and returns what it made.
#
# The key design choice: build_city() does NOT take a pile of loose
# arguments. It takes ONE dictionary of settings — the same data-driven
# pattern from Weeks 4-5. That dict is the "data" layer. The UI will
# later produce one of these dicts; for now we just hand-write it.
#
# Notice: none of these functions know anything about a window, a button,
# or a slider. That separation is the whole point.
# =====================================================================

def create_ground(size=20.0):
    """Create a ground plane to build on.

    Args:
        size: Width and depth of the plane in world units.

    Returns:
        str: The name of the created plane transform.
    """
    plane = cmds.polyPlane(width=size, height=size, name="ground")[0]
    return plane


def build_tower(x=0.0, z=0.0, floors=5, width=2.0):
    """Build a single tower from stacked cubes.

    Args:
        x: X position in world space.
        z: Z position in world space.
        floors: Number of stacked cubes (must be >= 1).
        width: Width/depth of each floor cube.

    Returns:
        list: Names of every cube created for this tower.
    """
    # Validate input BEFORE doing any work. A UI lets users type anything,
    # so the logic has to defend itself.
    if floors < 1:
        raise ValueError("floors must be at least 1, got {}".format(floors))

    created = []
    for i in range(floors):
        cube = cmds.polyCube(width=width, height=1.0, depth=width)[0]
        # Stack each cube one unit higher than the last.
        cmds.move(x, i + 0.5, z, cube)
        created.append(cube)
    return created


def default_settings():
    """Return a fresh settings dict with sensible defaults.

    This dict IS the data layer. Anything that wants to build a scene —
    the UI, a script, a test — produces one of these and hands it to
    build_city(). Keeping the shape in one place means every layer agrees
    on what a 'scene' looks like.

    Returns:
        dict: Scene settings with keys count, floors, spacing, add_ground.
    """
    return {
        "count": 5,        # how many towers
        "floors": 5,       # floors per tower
        "spacing": 4.0,    # distance between towers along X
        "add_ground": True # whether to lay down a ground plane
    }


def build_city(settings):
    """Build a city from a settings dict. This is our 'real work' function.

    It reads everything it needs from ONE dictionary instead of a long
    list of arguments. This is the Week 4-5 data-driven pattern: the scene
    is described by data, and a thin function turns that data into geometry.

    Args:
        settings: A dict with keys 'count', 'floors', 'spacing', and
            'add_ground' (see default_settings() for the shape).

    Returns:
        list: Names of every object created.
    """
    # Pull values out of the dict. .get() lets a partial dict still work
    # by falling back to a default, which is friendlier than a KeyError.
    count = settings.get("count", 5)
    floors = settings.get("floors", 5)
    spacing = settings.get("spacing", 4.0)
    add_ground = settings.get("add_ground", True)

    # Validate the data BEFORE building. The UI lets users pick anything,
    # so the logic defends itself here, once, for every front door.
    if count < 1:
        raise ValueError("count must be at least 1, got {}".format(count))
    if floors < 1:
        raise ValueError("floors must be at least 1, got {}".format(floors))

    everything = []
    if add_ground:
        # Size the ground to roughly fit the row of towers.
        everything.append(create_ground(size=count * spacing + 5))

    for i in range(count):
        # build_city calls build_tower — functions composing functions.
        tower = build_tower(x=i * spacing, z=0.0, floors=floors)
        everything.extend(tower)
    return everything


def section_1_demo():
    """Run the logic directly, with no UI at all.

    This is how you've used your code for nine weeks: describe the scene
    as DATA, then hand that data to the builder. It works fine — but only
    YOU can run it from the Script Editor. That's the problem a UI solves:
    it becomes a friendly way to produce this same settings dict.
    """
    cmds.file(new=True, force=True)
    settings = default_settings()      # the DATA
    settings["count"] = 6              # tweak the data, not the function
    settings["floors"] = 4
    build_city(settings)               # the LOGIC consumes the data
    print("[Section 1] Built a city from a settings dict:", settings)


# =====================================================================
# SECTION 2 — ANATOMY OF A MAYA WINDOW
# ---------------------------------------------------------------------
# Three pieces, ALWAYS in this order:
#   1. a window   (the frame)
#   2. a layout   (an invisible container that arranges things)
#   3. controls   (the things the user actually touches)
# ...then you show it.
#
# The #1 gotcha: Maya remembers a window's name even after you close it.
# Re-running your script without deleting the old one throws a
# "name already exists" error. So we always delete-if-exists first.
# =====================================================================

def build_minimal_window():
    """The smallest possible real window: a frame, a layout, one button."""
    window_name = "demoMinimalWin"

    # 1. THE WINDOW — delete the old one first (the classic gotcha).
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)
    cmds.window(window_name, title="Minimal Window", widthHeight=(260, 120))

    # 2. A LAYOUT — columnLayout stacks its children top to bottom.
    #    adjustableColumn makes the children stretch to the window width.
    cmds.columnLayout(adjustableColumn=True, rowSpacing=8, columnOffset=("both", 12))

    # 3. CONTROLS — for now, just a label and a button.
    cmds.text(label="The smallest real window.")
    cmds.button(label="Close", command="cmds.deleteUI('{}')".format(window_name))

    # 4. SHOW IT — nothing appears on screen until you call this.
    cmds.showWindow(window_name)


# =====================================================================
# SECTION 3 — THE CONTROLS TOOLBOX
# ---------------------------------------------------------------------
# A tour of the controls you'll reach for most. Each one is "queried"
# later (in a callback) to read the value the user set. Don't memorize
# the flags — look them up in the Maya docs as you go. That's this
# week's habit: read the docs to find what you need.
# =====================================================================

def build_controls_tour():
    """A window showing one of each common control, with a Print button
    that reads them all back. Run it, change the values, click Print, and
    watch the Script Editor — that's how you 'query' a control."""
    window_name = "demoControlsWin"
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)
    cmds.window(window_name, title="Controls Toolbox", widthHeight=(340, 240))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=8, columnOffset=("both", 14))

    cmds.text(label="One of each common control:", align="left")

    # A labeled slider + number field. Great for counts and sizes.
    count_slider = cmds.intSliderGrp(label="Count", field=True, min=1, max=20, value=5)

    # A floating-point slider for things like spacing or scale.
    spacing_slider = cmds.floatSliderGrp(label="Spacing", field=True, min=1.0, max=10.0, value=4.0)

    # Free text — names, file paths, prefixes.
    name_field = cmds.textFieldGrp(label="Name prefix", text="tower")

    # A dropdown of fixed choices. Each menuItem is one option.
    shape_menu = cmds.optionMenu(label="Shape")
    cmds.menuItem(label="cube")
    cmds.menuItem(label="sphere")
    cmds.menuItem(label="cylinder")

    # An on/off toggle.
    ground_check = cmds.checkBox(label="Add ground plane", value=True)

    # The Print button reads EVERY control and prints it. Notice the lambda
    # passes all the control names into the callback so it can query them.
    cmds.button(
        label="Print values",
        command=lambda *_: print_control_values(
            count_slider, spacing_slider, name_field, shape_menu, ground_check
        ),
    )

    cmds.showWindow(window_name)


def print_control_values(count_slider, spacing_slider, name_field, shape_menu, ground_check):
    """Read every control with query=True and print it. This is the move
    you'll use in every real callback: query the UI, then act on the values."""
    count = cmds.intSliderGrp(count_slider, query=True, value=True)
    spacing = cmds.floatSliderGrp(spacing_slider, query=True, value=True)
    name = cmds.textFieldGrp(name_field, query=True, text=True)
    shape = cmds.optionMenu(shape_menu, query=True, value=True)
    add_ground = cmds.checkBox(ground_check, query=True, value=True)

    print("[Controls] count={}, spacing={}, name='{}', shape='{}', ground={}".format(
        count, spacing, name, shape, add_ground))


# =====================================================================
# SECTION 4 — CALLBACKS: CONNECTING CLICKS TO CODE
# ---------------------------------------------------------------------
# A callback is the function Maya runs when the user does something
# (clicks a button, drags a slider). You hand the control a function to
# "call back" later.
#
# Two things students trip on:
#   * Why a lambda?  command= wants a function. A lambda lets you call
#     YOUR function WITH your arguments, instead of Maya calling it empty.
#   * Why *_ ?       Maya always passes one bonus argument to a callback.
#     *_ absorbs it so your function doesn't crash on the surprise value.
#
# Flow:  user clicks -> Maya runs the lambda -> lambda calls your bridge
#        function -> the bridge reads the controls -> your REAL function runs.
# =====================================================================

def build_callback_demo():
    """One slider, one button. The button's callback reads the slider and
    calls build_city(). This is the bridge pattern in its simplest form."""
    window_name = "demoCallbackWin"
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)
    cmds.window(window_name, title="Callback Demo", widthHeight=(320, 140))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=10, columnOffset=("both", 14))

    cmds.text(label="Set the count, then press Build.", align="left")
    count_slider = cmds.intSliderGrp(label="Towers", field=True, min=1, max=20, value=5)

    # The lambda is the callback. It ignores Maya's bonus arg (*_) and calls
    # our bridge function, passing the slider so the bridge can read it.
    cmds.button(
        label="Build",
        command=lambda *_: on_build_simple(count_slider),
    )

    cmds.showWindow(window_name)


def on_build_simple(count_slider):
    """The BRIDGE. Its only jobs: (1) read the UI into a DATA dict,
    (2) hand that dict to the logic. It contains no scene logic of its own.

    Even with one control, we still go through the dict. That habit means
    the logic always receives the same shape, no matter the front door."""
    # 1. Read the UI into the data layer.
    settings = default_settings()
    settings["count"] = cmds.intSliderGrp(count_slider, query=True, value=True)
    # 2. Hand the data to the logic.
    cmds.file(new=True, force=True)
    build_city(settings)
    print("[Callback] Built from settings:", settings)


# =====================================================================
# SECTION 5 — PUTTING IT TOGETHER (UI -> DATA -> LOGIC)
# ---------------------------------------------------------------------
# A complete, properly separated tool. Notice there are now FOUR jobs,
# split across the three layers:
#
#   build_scene_tool_ui()   -> UI:    draws the window (NO scene logic)
#   read_scene_settings()   -> DATA:  turns the controls into a dict
#   on_build_tool()         -> BRIDGE: read settings, hand them to logic
#   build_city(settings)    -> LOGIC: consumes the dict (Section 1 — unchanged!)
#
# Why bother with read_scene_settings() as its own function? Because now
# the "what the user chose" step is testable and reusable on its own, and
# the bridge stays tiny. The UI produces data; the logic consumes data;
# neither touches the other. That is the shape your final project wants.
# =====================================================================

def build_scene_tool_ui():
    """Draw the Scene Builder window. Contains NO scene logic — every
    button just reads controls and hands the values to a worker function."""
    window_name = "sceneBuilderTool"
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)
    cmds.window(window_name, title="Scene Builder", widthHeight=(360, 220))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=8, columnOffset=("both", 14))

    cmds.text(label="Build a city, then press Build.", align="left")
    count_slider = cmds.intSliderGrp(label="Towers", field=True, min=1, max=20, value=5)
    floors_slider = cmds.intSliderGrp(label="Floors", field=True, min=1, max=15, value=5)
    spacing_slider = cmds.floatSliderGrp(label="Spacing", field=True, min=2.0, max=10.0, value=4.0)
    ground_check = cmds.checkBox(label="Add ground plane", value=True)

    # Pass every control the worker needs into the lambda.
    cmds.button(
        label="Build",
        command=lambda *_: on_build_tool(count_slider, floors_slider, spacing_slider, ground_check),
    )
    cmds.button(
        label="Clear scene",
        command=lambda *_: cmds.file(new=True, force=True),
    )

    cmds.showWindow(window_name)


def read_scene_settings(count_slider, floors_slider, spacing_slider, ground_check):
    """Turn the UI controls into a settings dict. THE DATA LAYER.

    This function is the only place that knows both 'which controls exist'
    and 'what the settings dict looks like'. It queries each control and
    packs the values into the same dict shape build_city() expects.

    Args:
        count_slider, floors_slider, spacing_slider, ground_check: the
            control names returned when the UI was built.

    Returns:
        dict: Scene settings ready to hand to build_city().
    """
    return {
        "count": cmds.intSliderGrp(count_slider, query=True, value=True),
        "floors": cmds.intSliderGrp(floors_slider, query=True, value=True),
        "spacing": cmds.floatSliderGrp(spacing_slider, query=True, value=True),
        "add_ground": cmds.checkBox(ground_check, query=True, value=True),
    }


def on_build_tool(count_slider, floors_slider, spacing_slider, ground_check):
    """The bridge for the full tool. Tiny on purpose: gather the data,
    hand it to the logic, and translate any failure into a friendly
    message. No scene logic and no control-reading live here directly —
    those belong to build_city() and read_scene_settings() respectively."""
    # 1. DATA: ask the data layer what the user chose.
    settings = read_scene_settings(count_slider, floors_slider, spacing_slider, ground_check)

    # 2. LOGIC: hand the data to the builder, handling bad data gracefully.
    try:
        cmds.file(new=True, force=True)
        build_city(settings)
        print("[Tool] Built from settings:", settings)
    except ValueError as error:
        # A real tool tells the user what went wrong in plain English.
        cmds.warning("Could not build the scene: {}".format(error))


# =====================================================================
# SECTION 6 — INTEGRATION & POLISH (THE REFACTORING CLINIC)
# ---------------------------------------------------------------------
# Below is a BEFORE and AFTER of the same idea. The "before" works, but
# it breaks the one rule TWICE: it crams scene logic into the button
# callback AND skips the data layer entirely (the slider value flows
# straight into hardcoded geometry). Walk the refactoring checklist from
# the slides to turn it into the "after":
#     * Kill duplication        * Add missing docstrings
#     * Fix the names           * Wrap the risky calls
#     * Validate inputs         * One file, one job
#     * Separate UI -> data -> logic (no logic in the callback)
#
# (We reuse build_scene_tool_ui / read_scene_settings / on_build_tool /
# build_city above as the polished 'after'. The 'before' is here only as
# a teaching contrast — don't ship code that looks like this.)
# =====================================================================

def messy_tool_BEFORE():
    """BEFORE — works, but logic is crammed into the callback and there is
    no data layer. Hard to read, impossible to test without clicking, and
    full of hardcoded magic numbers. This is what we refactor AWAY from."""
    win = "messyWin"
    if cmds.window(win, exists=True):
        cmds.deleteUI(win)
    cmds.window(win, title="Messy Tool")
    cmds.columnLayout()
    s = cmds.intSliderGrp(label="n", field=True, min=1, max=20, value=5)

    def go(*_):
        # Reading the UI, deciding the data, AND building all happen here,
        # tangled together in the callback. Don't do this.
        n = cmds.intSliderGrp(s, query=True, value=True)
        cmds.file(new=True, force=True)
        cmds.polyPlane(width=30, height=30)
        for i in range(n):
            for f in range(5):
                c = cmds.polyCube()[0]
                cmds.move(i * 4, f + 0.5, 0, c)

    cmds.button(label="Build", command=go)
    cmds.showWindow(win)


def polished_tool_AFTER():
    """AFTER — the same feature, refactored into three clean layers:
    build_scene_tool_ui() draws the window, read_scene_settings() produces
    the data dict, build_city() consumes it. Each is named, documented, and
    testable on its own. This is the target shape for your final project."""
    build_scene_tool_ui()


def install_shelf_button():
    """Add a button to the active shelf that opens this tool.

    This is STEP 2 from Section 8, as real runnable code. Run it once and
    a 'Scene Builder' button appears on your current shelf; clicking it runs
    the same two lines you'd type by hand. Rebuildable on any machine, which
    is why a script beats dragging the button manually.
    """
    # Ask Maya (via MEL, since cmds has no equivalent) for the active shelf.
    top_shelf = mel.eval("$tmp = $gShelfTopLevel")
    current = cmds.tabLayout(top_shelf, query=True, selectTab=True)
    cmds.shelfButton(
        parent=current,
        label="Scene Builder",
        annotation="Open the Scene Builder tool",
        image="commandButton.png",   # swap for your own 32x32 icon
        command="import scene_builder; scene_builder.build_scene_tool_ui()",
        sourceType="python",
    )
    print("[Shelf] Added a Scene Builder button to the '{}' shelf.".format(current))


# =====================================================================
# SECTION 7 — YOUR TOOL WILL LOOK NOTHING LIKE THIS (AND THAT'S FINE)
# ---------------------------------------------------------------------
# This demo built a city. Your final project might be a batch renamer, a
# scatter tool, a scene validator, a shader assigner — something totally
# different. The window, the controls, and the work will all be different.
#
# What does NOT change is the SHAPE. Look back at the polished tool:
#
#     build_scene_tool_ui()   UI    — draws the window (no work)
#     read_scene_settings()   DATA  — controls  ->  a settings dict
#     on_build_tool()         BRIDGE— read settings, call the logic
#     build_city(settings)    LOGIC — consumes the dict (no UI knowledge)
#
# Every good tool has exactly these layers. Swap the contents and you have
# a different tool with the identical architecture:
#
#     ----------------------------------------------------------------
#     | layer  | scene-gen (this demo) | a batch renamer             |
#     ----------------------------------------------------------------
#     | DATA   | {count, floors,       | {prefix, start, padding}    |
#     |        |  spacing, add_ground} |                             |
#     | UI     | sliders + checkbox    | text field + 2 sliders      |
#     | LOGIC  | build_city(settings)  | rename_selection(settings)  |
#     ----------------------------------------------------------------
#
# The one rule is the same for all of them: the UI produces DATA, the
# logic consumes DATA, and neither knows how the other works.
#
# WHERE TO GO NEXT
#   * tool_skeleton.py  — the blank version of this shape. Copy it and fill
#     in the TODOs for YOUR tool. Start there for the final project.
#   * Notion -> Final Project Resources -> "Tool Pattern — <your tool>" —
#     a worked example of all three layers for renamers, scatter tools,
#     validators, and shader assigners. Find the one closest to your idea.
# =====================================================================


# =====================================================================
# SECTION 8 — SHIPPING IT: FROM SCRIPT TO A SHELF BUTTON
# ---------------------------------------------------------------------
# Right now your tool runs only if YOU paste it into the Script Editor.
# A real tool lives on a SHELF BUTTON: an artist clicks an icon and the
# window opens. No code, no Script Editor. Here is the whole path.
#
# STEP 1 — Make your file importable (a "module").
#   Save this file with a clean, lowercase name, e.g.  scene_builder.py
#   Put it in Maya's scripts folder so Maya can always find it:
#       Windows:  Documents/maya/scripts/
#       macOS:    ~/Library/Preferences/Autodesk/maya/scripts/
#   Now from anywhere in Maya you can run:
#       import scene_builder
#       scene_builder.build_scene_tool_ui()
#   (If you change the file while Maya is open, force a reload:
#       import importlib; importlib.reload(scene_builder))
#
# STEP 1B — More than one file? Make a PACKAGE (recommended).
#   Real tools split across files (one job per file). Don't scatter loose
#   modules in scripts/ — wrap them in a folder with an __init__.py:
#
#       scene_builder/            <- the package (this folder name = the import)
#           __init__.py           <- makes it a package; exposes the entry point
#           geometry.py           <- the logic
#           ui.py                 <- the window
#
#   Inside the files, import each other by the package name (explicit and
#   beginner-safe):
#       # in ui.py
#       from scene_builder import geometry
#   (A tidier alternative is a relative import:  from . import geometry  —
#   either works; pick one and stay consistent.)
#
#   In __init__.py, expose the entry point so the shelf command stays simple:
#       # scene_builder/__init__.py
#       from scene_builder.ui import build_scene_tool_ui
#   Now  import scene_builder; scene_builder.build_scene_tool_ui()  still
#   works unchanged — STEP 2 and 3 below don't change at all.
#
#   RELOAD GOTCHA: reloading the package does NOT reload its submodules.
#   If you edit geometry.py, importlib.reload(scene_builder) won't pick it
#   up — reload the submodule you changed (importlib.reload(scene_builder.geometry))
#   or just restart Maya. This trips up everyone with multi-file tools.
#
# STEP 2 — Make a shelf button.
#   The slow way (do this once to understand it): open the Script Editor,
#   type the two lines below, SELECT them, then middle-mouse-DRAG the
#   selection onto a shelf. Maya makes a button that runs exactly that.
#       import scene_builder
#       scene_builder.build_scene_tool_ui()
#   Set the button's icon and tooltip via right-click > Edit.
#
#   The repeatable way (in code) — create the shelf button from a script,
#   so you can rebuild it on any machine:
#
#       def install_shelf_button():
#           \"\"\"Add a button to the current shelf that opens this tool.\"\"\"
#           shelf = cmds.tabLayout(
#               mel.eval("$tmp = $gShelfTopLevel"), query=True, selectTab=True)
#           cmds.shelfButton(
#               parent=shelf,
#               label="Scene Builder",
#               annotation="Open the Scene Builder tool",
#               image="commandButton.png",   # swap for your own icon
#               command="import scene_builder; scene_builder.build_scene_tool_ui()",
#               sourceType="python",
#           )
#   (mel.eval here just asks Maya for the name of the active shelf — one of
#   the rare times we drop to MEL because there is no cmds equivalent.)
#
# STEP 3 — Make it load every time Maya starts (optional polish).
#   Maya runs a file called  userSetup.py  (in the same scripts/ folder)
#   on startup. Add your install line there so the button is always present:
#
#       # userSetup.py
#       import maya.utils
#       def _setup():
#           import scene_builder
#           scene_builder.install_shelf_button()
#       maya.utils.executeDeferred(_setup)
#
#   executeDeferred waits until Maya's UI exists before building the button
#   (running shelf code too early, before the shelves load, fails).
#
# THE TAKEAWAY
#   Notice STEP 2's command is just the same two lines from STEP 1. The
#   shelf button is one more "front door" to build_scene_tool_ui() — exactly
#   like the data lesson: your tool's entry point stays the same; you are
#   only adding nicer ways to call it.
#
# A NOTE ON "REAL" PLUG-INS (you don't need this)
#   Maya also has a heavier path: a true plug-in — a .py file with
#   initializePlugin / uninitializePlugin that registers a custom command
#   or node, loaded through Window > Settings/Preferences > Plug-in Manager.
#   That's for extending Maya itself (new MEL/Python commands, custom
#   nodes), not for shipping a tool with a UI. For everything in this
#   course, the shelf-button + module path above is the right, standard
#   choice. Just know the term so you're not thrown when you see it online.
# =====================================================================


# =====================================================================
# RUN THE DEMO
# ---------------------------------------------------------------------
# Uncomment ONE line at a time in class to walk the progression. By the
# end, students should see the SAME logic — build_city(settings) — fed by
# the same kind of dict, no matter which front door produced it. That is
# the lesson: the UI just produces data; the logic only ever sees data.
# Section 7 makes the point that the SHAPE, not this tool, is what
# transfers; Section 8 shows how to ship it as a shelf button.
# =====================================================================

if __name__ == "__main__":
    # section_1_demo()        # logic only, called from the Script Editor
    # build_minimal_window()  # window -> layout -> control -> show
    # build_controls_tour()   # one of each control + a Print button
    # build_callback_demo()   # the bridge pattern, simplest form
    build_scene_tool_ui()     # the complete, separated tool (the target)
    # messy_tool_BEFORE()     # the contrast: what NOT to ship
    # install_shelf_button()  # Section 8: add a shelf button that opens the tool