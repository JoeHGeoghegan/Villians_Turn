# Library Imports
from nicegui import app, ui
import pandas as pd

### Local Imports
from functions.basics import mem_df_modify
from functions.data import import_file, process_party
from functions.game import auto_initiative_groups, initiative_based_group_assignment, turn_table_viewer
from functions.groups import individual_groups

def create_content(page:ui.refreshable):
    ui.label("Welcome! Add Characters or Import an existing Villain's Turn csv to get started!")
    
    with ui.row():
        col1 = ui.column()
        col2 = ui.column()
        with col1:
            ui.upload(
                on_upload=lambda file: import_file(page,file),
                label="Click or Drag to Upload CSV File"
                ).props('accept=.csv')
            ui.button("Download Template CSV", on_click=lambda: ui.download('assets\\party_data\\VilliansTurnTemplate.csv'))
        with col2:
            ui.button("Or use test data version Generic", on_click=lambda: example_import(page,'assets\\party_data\\CombatExample1.csv'))
            ui.button("Or use test data version LOTR", on_click=lambda: example_import(page,'assets\\party_data\\Party1.csv'))
            ui.button("Or use test data version GOT", on_click=lambda: example_import(page,'assets\\party_data\\Party2.csv'))
        with open("assets\\texts\\csv_details.md", 'r') as md_file:
            ui.markdown(md_file.read())
    
def example_import(page:ui.refreshable,path,import_groups=True):
    process_party(page,pd.read_csv(path),import_groups)

def create_group_gather(page:ui.refreshable):
    with ui.row():
        with ui.column():
            ui.label("Groups are not gathered, move groups to desired order or reset initiative").style('font-size: 165%; font-weight: 300')
            ui.table.from_pandas(turn_table_viewer(dm_view=True))
        with ui.column():
            ui.button("Group by Loaded Initiative", on_click=lambda: ( mem_df_modify('turn_track',initiative_based_group_assignment), page.refresh()))
            ui.button("Remove Groups", on_click=lambda: ( mem_df_modify('turn_track',individual_groups), page.refresh()))
            ui.button("Roll Initiative", on_click=lambda: ( mem_df_modify('turn_track',auto_initiative_groups), page.refresh()))