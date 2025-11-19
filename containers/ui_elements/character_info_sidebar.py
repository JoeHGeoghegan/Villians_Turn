# Imports
from nicegui import ui, app

# local imports
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
            ui.label(character).props('dense')
            ui.space()
            ui.button("Close", on_click=lambda: (set_user_mem('character_focus', ''), refresh()))
        ui.label("More to come...Will show attributes and have expandable sections for Feats, Features, Conditions, Inventory")