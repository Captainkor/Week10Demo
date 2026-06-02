# =============================================================================
# cityscape/shelf.py
# =============================================================================
# Drops a shelf button onto Maya's currently active shelf. After running
# install_shelf_button() once, the artist clicks the button and the tool
# opens -- no Script Editor needed.
# =============================================================================

import maya.cmds as cmds
import maya.mel as mel


_BUTTON_LABEL = "CityScape"
_BUTTON_COMMAND = "import cityscape\ncityscape.build_ui()"


def _active_shelf():
    """Return the name of Maya's currently visible shelf.

    We drop into maya.mel here because the active-shelf API is exposed in
    MEL ($gShelfTopLevel + tabLayout -selectTab) and there is no clean
    maya.cmds equivalent. This is the only MEL call in the package.
    """
    top_level = mel.eval('$tmpVar = $gShelfTopLevel')
    return cmds.tabLayout(top_level, q=True, selectTab=True)


def _existing_button(shelf):
    """Return the name of a CityScape button already on `shelf`, or None.

    Identifies "our" button by matching both the label and the command --
    cheap, no metadata required, survives Maya re-saving the shelf as XML.
    """
    children = cmds.shelfLayout(shelf, q=True, childArray=True) or []
    for child in children:
        if cmds.objectTypeUI(child) != "shelfButton":
            continue
        try:
            label = cmds.shelfButton(child, q=True, label=True)
            cmd   = cmds.shelfButton(child, q=True, command=True)
        except Exception:
            continue
        if label == _BUTTON_LABEL and cmd == _BUTTON_COMMAND:
            return child
    return None


def install_shelf_button():
    """Add a 'CityScape' button to the active shelf.

    Run this once per machine:

        import cityscape
        cityscape.install_shelf_button()

    Returns the shelf button's name.
    """
    shelf = _active_shelf()
    if not shelf:
        cmds.warning("install_shelf_button: no active shelf found.")
        return None

    button = cmds.shelfButton(
        parent=shelf,
        label=_BUTTON_LABEL,
        annotation="Open the CityScape Builder",
        image="commandButton.png",
        imageOverlayLabel="City",
        sourceType="python",
        command=_BUTTON_COMMAND,
    )
    return button


def ensure_shelf_button():
    """Idempotent installer: add the button only if it isn't already there.

    Safe to call on every Maya startup from userSetup.py:

        import maya.utils
        import cityscape
        maya.utils.executeDeferred(cityscape.ensure_shelf_button)

    No-ops cleanly when:
      - Maya is in batch mode (no UI, no active shelf)
      - the CityScape button is already present on the active shelf

    Returns the existing or newly-created button name, or None if neither
    applied (e.g. batch mode).
    """
    # Batch / mayapy: no GUI, so no shelf to install onto. This must not
    # raise -- userSetup.py runs in every Maya, including command-line.
    if cmds.about(q=True, batch=True):
        return None
    shelf = _active_shelf()
    if not shelf:
        return None
    existing = _existing_button(shelf)
    if existing:
        return existing
    return install_shelf_button()
