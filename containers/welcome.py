# Library Imports
import os

from nicegui import ui, app

from containers.ui_elements.group_modification import create_group_content
from containers.ui_elements.turn_table_interface import turn_track_ui_list_create_content
from functions.basics import mem_df_modify
from functions.data import import_file
from functions.groups import auto_initiative_groups, group_in_place, individual_groups, \
    initiative_based_group_assignment


### Local Imports

def create_content(page: ui.refreshable):
    ui.label("Welcome! Add Characters or Import an existing Villain's Turn csv to get started!")

    def create_characters(head_page: ui.refreshable):
        app.storage.user["selectable_view"] = ["character_editor"]
        head_page.refresh()

    ui.button("Start creating characters!", on_click=lambda: create_characters(page))

    with ui.row():
        # col1 = ui.column()
        # col2 = ui.column()
        # with col1:
        #     ui.upload(
        #         on_upload=lambda file: import_file(page, file),
        #         label="Click or Drag to Upload CSV File"
        #     ).props('accept=.csv')
        #     ui.button("Download Template CSV",
        #               on_click=lambda: ui.download('assets/party_data/VilliansTurnTemplate.csv'))
        # with col2:
        #     ui.button("Or use test data version Generic",
        #               on_click=lambda: example_import(page, 'assets/party_data/CombatExample1.csv'))
        #     ui.button("Or use test data version LOTR",
        #               on_click=lambda: example_import(page, 'assets/party_data/Party1.csv'))
        #     ui.button("Or use test data version GOT",
        #               on_click=lambda: example_import(page, 'assets/party_data/Party2.csv'))
        with open("assets/texts/csv_details.md", 'r') as md_file:
            ui.markdown(md_file.read())


def example_import(page: ui.refreshable, path_root, import_groups=True):
    for root, _, files in os.walk(path_root):
        for file_name in files:
            full_path = os.path.join(root, file_name)
            relative_path = os.path.relpath(full_path, path_root)
            import_file(page, relative_path, file_name, import_groups)


def create_group_gather(page: ui.refreshable,sidebar_page: ui.refreshable):
    with ui.row():
        with ui.column():
            ui.label("Groups are not gathered, move characters/groups to desired order or reset initiative").style(
                'font-size: 110%; font-weight: 300')
            ui.label("Click characters in order to modify").style('font-size: 90%; font-weight: 300')
            turn_track_ui_list_create_content("Host", highlight_rows=True, page=page, sidebar_page=sidebar_page)
        with ui.column():
            with ui.button_group():
                ui.button("Group by Loaded Initiative",
                          on_click=lambda: (mem_df_modify('character_details', initiative_based_group_assignment),
                                            page.refresh()))
                ui.button("Group as is",
                          on_click=lambda: (mem_df_modify('character_details', group_in_place), page.refresh()))
                ui.button("Remove Groups",
                          on_click=lambda: (mem_df_modify('character_details', individual_groups), page.refresh()))
            ui.button("Roll Initiative",
                      on_click=lambda: (mem_df_modify('character_details', auto_initiative_groups), page.refresh()))
            ui.separator()
            create_group_content(page)
