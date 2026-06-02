# =============================================================================
# userSetup.py  --  auto-load CityScape on every Maya launch
# =============================================================================
# WHAT THIS FILE IS:
#   Maya scans its scripts folder for a file literally named `userSetup.py`
#   and runs it during startup. We use it to register the CityScape shelf
#   button so the artist doesn't have to run any setup command by hand.
#
# WHERE TO PUT IT:
#   Drop this file into the SAME scripts folder where the `cityscape/`
#   package lives:
#     macOS    ~/Library/Preferences/Autodesk/maya/<version>/scripts/userSetup.py
#     Windows  Documents\maya\<version>\scripts\userSetup.py
#
#   Layout when you're done:
#     scripts/
#     ├── cityscape/           (the package folder)
#     └── userSetup.py         (this file)
#
# IF YOU ALREADY HAVE A userSetup.py:
#   Don't overwrite it -- Maya only reads one. Paste the body of this file
#   into your existing userSetup.py instead.
#
# WHY executeDeferred:
#   userSetup.py runs BEFORE Maya's UI is fully built. shelfButton() needs
#   the shelf to exist, so we defer the call into Maya's idle loop with
#   maya.utils.executeDeferred -- by the time it fires, the shelves are
#   ready.
#
# WHY ensure_shelf_button (not install_shelf_button):
#   ensure_* is idempotent: if the CityScape button is already on the
#   active shelf, it does nothing. Safe to run on every launch. Calling
#   install_shelf_button() here instead would pile up duplicate buttons
#   every time Maya starts.
# =============================================================================

import maya.utils


def _register_cityscape():
    """Defer one tick, then add the shelf button if it isn't there yet."""
    try:
        import cityscape
        cityscape.ensure_shelf_button()
    except Exception as e:
        # Never let a tool's startup crash Maya. Log and move on.
        try:
            import maya.cmds as cmds
            cmds.warning("CityScape autoload failed: {}".format(e))
        except Exception:
            # Not even cmds is available -- batch mode quirk. Print only.
            print("CityScape autoload failed:", e)


# Defer until Maya's UI exists. In batch mode executeDeferred still runs
# the callback, but ensure_shelf_button() no-ops because there's no shelf.
maya.utils.executeDeferred(_register_cityscape)
