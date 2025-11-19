# Library Imports
from nicegui import ui, app

# local import
from containers.ui_elements import character_info_sidebar
from memory import init_mem, init_table, init_user, set_user_type

main_container: ui.refreshable = None
sidebar: ui.refreshable = None


def refresh():
    global main_container, sidebar
    main_container.refresh()
    sidebar.refresh()

def create_content(page: ui.refreshable, sidebar_page: ui.refreshable):
    global main_container, sidebar
    if main_container is None:
        main_container = page
        sidebar = sidebar_page

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
        character_info_sidebar.create_content(main_container, sidebar)
