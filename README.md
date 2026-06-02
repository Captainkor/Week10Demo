# CityScape — staged teaching demo

This folder ships **one installable package** (`cityscape/`) and three small
**stage demo scripts** that walk through the LOGIC / DATA / UI / BRIDGE
layers using that package.

## Folder layout

```
stages/
├── cityscape/          ← drop THIS folder into Maya scripts/
│   ├── __init__.py     ← re-exports build_ui, install_shelf_button, ensure_shelf_button
│   ├── main.py         ← LOGIC driver + DATA + dispatch BUILDERS
│   ├── ui.py           ← UI window + BRIDGE callback
│   ├── shelf.py        ← install_shelf_button() + ensure_shelf_button()
│   ├── geometry_utils.py   ← LOGIC (primitives)
│   ├── layout_utils.py     ← LOGIC (composites)
│   ├── material_utils.py   ← LOGIC (materials)
│   └── README.md
├── userSetup.py        ← OPTIONAL: drop this beside cityscape/ for auto-load
├── stage1_logic.py     ← Script Editor demo: logic + hardcoded data, no UI
├── stage2_ui.py        ← Script Editor demo: a minimal UI on top of logic
├── stage3_data.py      ← Script Editor demo: explicit bridge, dict made visible
└── README.md           ← this file
```

The three stage scripts are not part of the package — they are paste-and-run
demonstrations that import from it.

## Step 1 — install the package

Copy the `cityscape/` folder into Maya's scripts directory:

- **macOS** — `~/Library/Preferences/Autodesk/maya/<version>/scripts/cityscape`
- **Windows** — `Documents\maya\<version>\scripts\cityscape`

Launch Maya. In the Script Editor (Window → General Editors → Script Editor),
verify the install with:

```python
import cityscape
cityscape.build_ui()
```

A **CityScape Builder** window should open.

## Step 2 — get the shelf button

Pick one. They're alternatives.

### Option A: install it once, by hand

Still in the Script Editor:

```python
import cityscape
cityscape.install_shelf_button()
```

A **CityScape** button appears on the currently active shelf. From now on,
the artist clicks the button and the tool opens. The button persists
across Maya restarts (Maya saves the shelf as XML).

### Option B: auto-load on every Maya launch (recommended)

Copy `userSetup.py` from this folder into the **same scripts directory**
where you put `cityscape/`:

```
maya/<version>/scripts/
├── cityscape/
└── userSetup.py
```

Maya runs `userSetup.py` on startup. It calls
`cityscape.ensure_shelf_button()` (idempotent — only installs the button
if it isn't already there), so:

- First launch after install: button appears automatically.
- Every launch after that: nothing happens; the button is already there.
- Batch / `mayapy` sessions: silently no-op (no shelf to install onto).

If you already have a `userSetup.py`, **don't overwrite it** — open both
files and paste the body of ours into yours. Maya only reads one
`userSetup.py` per scripts folder.

## Step 3 — walk through the stage demos

Once the package is installed, each of the three stage scripts is a
self-contained demonstration of one layer. Open the file, paste the
contents into the Script Editor, and run it.

| Stage | What it shows | What's new from the previous stage |
|---|---|---|
| `stage1_logic.py` | Logic + a hardcoded data dict | The work runs without a UI |
| `stage2_ui.py`    | A small Maya window wired to the logic | The UI layer exists, but the bridge still hardcodes most of the dict |
| `stage3_data.py`  | An explicit bridge that builds the dict from controls | The data layer becomes visible — the bridge produces the same shape `cityscape.main.SCENE` uses |
| `cityscape/` (Stage 4) | The full shipped form: package + shelf button | All four layers in their final home |

## Rule the demo enforces

```
   UI  ──►  main  ──►  LOGIC
   (UI never reaches around main to call logic directly,
    and LOGIC never reaches up to UI.)
```

You can swap the UI (CLI, JSON loader, web form) without touching logic.
You can swap the geometry (Blender, Houdini wrappers) without touching UI.
That's the whole point of the four layers.
