# Library Imports
from nicegui import ui, app
import pandas as pd

### Local Imports
from functions.game import auto_initiative
from functions.groups import groups_gathered_check

def create_content(parent):
    # memory setup
    mem = app.storage.tab

    ######## UI ########

    ui.label(f"Turn #: {mem['turn_number']}").classes('text-xl')
    ui.label(f"Action #: {mem['action_number']}").classes('text-xl')

    turn_table = ui.table.from_pandas(mem['turn_track'])
    # This is where the main logic for the overview tab goes
    if not groups_gathered_check(mem['turn_track']):
        ui.label("Groups are not gathered, move groups to desired order or reset initiative")
        ui.button("Roll Initiative", on_click=lambda: auto_initiative(mem["turn_track"]))
        ui.button("Refresh Table", on_click=lambda: turn_table.update())
    else:
        ui.label("Groups are gathered, ready to start combat! PLACEHOLDER FOR ACTUAL COMBAT UI")