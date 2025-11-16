# Library Imports
from nicegui import ui, app

from containers import ui_character_info
from memory import init_mem, init_table, init_user
from memory import set_user_type

containing_page: ui.refreshable = None


def update_content():
    global containing_page
    containing_page.refresh()


def create_content(page: ui.refreshable, self_page: ui.refreshable):
    def refresh():
        self_page.refresh()
        page.refresh()

    global containing_page
    if containing_page is None:
        containing_page = page

    # memory setup
    user = app.storage.user
    mem = app.storage.general
    with ui.dropdown_button('Debug Menu', auto_close=True):

        ui.item('Clear Memory', on_click=lambda: (user.clear(), mem.clear(), init_mem(), refresh()))
        ui.item('Clear Table', on_click=lambda: (init_table(), refresh()))
        ui.item('Become a Host', on_click=lambda: (set_user_type("Host"), refresh()))
        ui.item('Become a Player', on_click=lambda: (set_user_type("Player"), refresh()))
        ui.item('Refresh Memory', on_click=lambda: (init_user(), init_mem(), refresh()))
    ui.markdown('''
                Tabs
                Host Only
                    Settings
                        Host Password
                        Assignable Teams
                        Add Team/Remove Team
                        Replace Settings, modify settings, download settings
                Character Clicked -> load character into display, add Character Info Tab
                    Has close button
                    Editable if host, specifiable if assigned character
                If not host, no team assignable - Does not show unless character selected
                ''')
    if user['character_focus'] != '':
        ui_character_info.create_content(containing_page, self_page)
