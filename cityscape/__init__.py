# =============================================================================
# cityscape/__init__.py  --  the public face of the package
# =============================================================================
# WHAT CHANGED FROM PREVIOUS STAGE: CityScape is now a PACKAGE. Drop this
# folder (renamed to `cityscape/`) into Maya's scripts folder and any Maya
# session can launch it with:
#
#     import cityscape
#     cityscape.build_ui()
#
# No sys.path hacks. No file paths in the code. The user just imports the
# package by name.
#
# To install the shelf button once (manual):
#
#     import cityscape
#     cityscape.install_shelf_button()
#
# Or to have it auto-install on every Maya launch, drop the sibling
# userSetup.py into the same scripts/ folder. That calls:
#
#     cityscape.ensure_shelf_button()   # idempotent: only adds if missing
#
# WHY __init__.py is short:
#   __init__.py is the package's lobby -- it shouldn't do work, it should
#   just point upstairs. The three re-exports below put build_ui,
#   install_shelf_button, and ensure_shelf_button at the top level
#   (`cityscape.build_ui` instead of `cityscape.ui.build_ui`).
# -----------------------------------------------------------------------------

from .ui import build_ui
from .shelf import install_shelf_button, ensure_shelf_button

__all__ = ["build_ui", "install_shelf_button", "ensure_shelf_button"]
__version__ = "0.5.0"  # auto-load support
