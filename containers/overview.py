# Library Imports
from nicegui import ui, app
import pandas as pd

### Local Imports
from functions.game import turn_table_viewer

def create_content(parent):
    # memory setup
    mem = app.storage.tab

    ######## UI ########

    ui.label(f"Turn #: {mem['turn_number']}").classes('text-xl')
    ui.label(f"Action #: {mem['action_number']}").classes('text-xl')

    ui.table.from_pandas(turn_table_viewer(dm_view=False))
    # This is where the main logic for the overview tab goes

    ui.label("Groups are gathered, ready to start combat! PLACEHOLDER FOR ACTUAL COMBAT UI")