# Library Imports
from nicegui import ui, app
import pandas as pd

### Local Imports
from functions.data import import_file, add_to_turn_track
from functions.groups import individual_groups

def create_content(parent):
    # memory setup
    mem = app.storage.tab

    ui.label("Welcome! Add Characters or Import an existing Villain's Turn csv to get started!")
    ui.upload(
        on_upload=lambda file: import_file(parent,file),
        label="Click or Drag to Upload CSV File"
        ).props('accept=.csv')
    ui.button("Or use test data version 1 (LOTR)", on_click=lambda: example_import(parent,'assets\\party_data\\Party1.csv'))
    ui.button("Or use test data version 1 (GOT)", on_click=lambda: example_import(parent,'assets\\party_data\\Party2.csv'))
    
def example_import(refresh_target:ui.refreshable,path,import_groups=True):
    # memory setup
    mem = app.storage.tab
    party = pd.read_csv(path)
    if not ( import_groups and ('group' in list(party))):
        party = individual_groups(party)
    add_to_turn_track(party)
    refresh_target.refresh()