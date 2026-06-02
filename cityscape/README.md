# cityscape — the shipped package

The shipped form of Ghost Fazekas Stivala's CityScape tool. Drop this whole
folder into Maya's scripts directory; nothing else is required.

## Install

Copy this `cityscape/` folder into your Maya scripts folder:

- macOS: `~/Library/Preferences/Autodesk/maya/<version>/scripts/cityscape`
- Windows: `Documents\maya\<version>\scripts\cityscape`

Then launch Maya. (The three stage demo scripts in the parent folder also
import from this package, so once you've copied it in, every stage script
just works in the Script Editor too.)

## Run from the Script Editor

```python
import cityscape
cityscape.build_ui()
```

## Install the shelf button (once)

```python
import cityscape
cityscape.install_shelf_button()
```

A **CityScape** button appears on the currently active shelf. Click it any
time to open the tool. Maya saves the shelf, so the button survives
restarts.

## Auto-load on every Maya launch (alternative)

If you'd rather have the button install itself on first launch and verify
itself on every launch after that, drop the sibling `userSetup.py` into
the same `scripts/` folder. It calls `cityscape.ensure_shelf_button()` —
idempotent, so it never duplicates the button and safely no-ops in batch
mode. See `../README.md` for the full layout.

## Package layout

| File | Layer |
|---|---|
| `__init__.py` | Package entry point — re-exports `build_ui`, `install_shelf_button`, `ensure_shelf_button` |
| `ui.py` | UI window + bridge callback |
| `main.py` | Logic driver (`build_scene`), data contract (`SCENE`), dispatch (`BUILDERS`) |
| `geometry_utils.py` | Logic (primitives) |
| `layout_utils.py` | Logic (composites) |
| `material_utils.py` | Logic (materials) |
| `shelf.py` | Shipping helpers — `install_shelf_button` (always adds) + `ensure_shelf_button` (idempotent, for `userSetup.py`) |
