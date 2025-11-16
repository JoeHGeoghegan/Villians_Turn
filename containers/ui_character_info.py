# Imports
import ast

from nicegui import ui, app

# local imports
from functions.basics import df_to_dict
from functions.game import turn_track
from memory import set_user_mem


def create_content(page: ui.refreshable, sidebar: ui.refreshable):
    def refresh():
        sidebar.refresh()
        page.refresh()

    print("Showing Character Info")
    user = app.storage.user
    character = user['character_focus']
    with ui.card():
        with ui.row():
            ui.label(f"Info for :")
            ui.input(value=character).props('dense')
            ui.space()
            ui.button("Close", on_click=lambda: (set_user_mem('character_focus', ''), refresh()))
        with ui.row():
            with ui.column():
                ui.label("Character Attributes")
                create_editable_table(character, ['attributes'])


def create_editable_table(character, path_tree):
    character_sheet = turn_track()[turn_track()['name'] == character]
    items = ast.literal_eval(df_to_dict(character_sheet)[0])

    def row_creator(row_key, elements):
        item = ui.item()
        with item.props('dense'):
            with ui.item_section().props('no-wrap, side'):
                ui.item_label(row_key)
            for value in elements:
                section_label_recurse_function(row_key, value)
            return item

    for path in path_tree:
        items = items[path]

        with ui.list().style('width: fit-content;').props('bordered separator'):
            with ui.item().props('dense'):
                with ui.item_section().props('no-wrap, side'):  # Header
                    ui.item_label(path_tree[-1]).classes('text-bold')
            ui.separator()
            print(items)
            for key, values in items.items():
                row_creator(key, values)


def section_label_recurse_function(key, value):
    if type(value) == dict:
        for key, values in value.items():
            return section_label_recurse_function(key, values)
        return None
    else:
        section = ui.item_section().props('no-wrap, side')
        with section:
            ui.input(label=key, value=value)
        return section
