# Library Imports
from nicegui import ui, app
import pandas as pd
import asyncio
### Local Imports
from functions.basics import mem_df_use
from memory import init_mem
from functions.groups import groups_gathered_check
import containers.welcome as welcome
import containers.overview as overview
import containers.left_sidebar as left_sidebar
import containers.right_hiding_sidebar as right_hiding_sidebar

########## UI To Convert ##########
"""
Tab/Sidebar/Menu screens
    "Overview"
        Turn Track (ref 60)
        Combat Interface (ref 88)
            Flavor Data Handling (ref 156)
"""

########## UI Elements ##########
#basics
darkMode = True

#pages
@ui.page('/')
async def main_page():
    # Initialize client connection
    await ui.context.client.connected()
    await asyncio.sleep(1)

    # Create quick ref memory variable
    mem = app.storage.general
    user = app.storage.user
    # Initialize memory variables on first load
    if 'audit' not in mem:
        init_mem()
    # Initialize new users
    if 'role' not in user:
        user['type'] = "dm"
        user['id'] = 0
    # UI Settings
    darkMode = ui.dark_mode(True)
    ui.colors(
        primary = '#4f000c',
        secondary = '#711c00',
        accent = '#2f4858'
    )

    # Main Page Layout
    with ui.header(elevated=True).classes('items-center justify-between'):
        # Display Logo
        ui.image('assets/Images/Villains_turn_logo.svg').style('max-width: 300px;')
        ui.markdown(f'''
                    PlayerID: {user["id"]}
                    ''')
        ui.markdown('''
                    Next Coding Priorities:
                    Group Functions
                    ''')
        ui.button(on_click=lambda: right_drawer.toggle(), icon='menu').props('flat color=white')
    with ui.left_drawer(top_corner=True, bottom_corner=True):
        left_sidebar.create_content(main_container)
    with ui.right_drawer(fixed=False).props('bordered') as right_drawer:
        right_hiding_sidebar.create_content(main_container)
    #with ui.footer():

    main_container() # Refreshable container for main content
    
@ui.refreshable
def main_container() -> None:
    print("~~ Refreshing Main Container ~~")
    # memory setup
    mem = app.storage.general
    with ui.column():
        if len(mem['markdown_view_path']) > 0:
            print("Showing Markdown View")
            def back():
                mem['markdown_view_path'] = ''
                main_container.refresh()
            with open(mem['markdown_view_path'], 'r') as md_file:
                ui.markdown(md_file.read())
            ui.button('Back', on_click=lambda x: back()) 
        # If no data, show welcome message relevant options
        elif mem_df_use('turn_track', len) ==  0:
            print("No Data - Showing Welcome")
            welcome.create_content(main_container)
        # If groups not yet gathered, show group gathering screen
        elif not mem_df_use('turn_track',groups_gathered_check):
            print("Groups not gathered - Showing Group Gather")
            welcome.create_group_gather(main_container)
        else:
            print("Should be Ready to Go! - Showing Overview")
            overview.create_content(main_container)

############ Run Loop ##########
if __name__ in {'__main__', '__mp_main__'}:
    ui.run(title="Villain's Turn", reload=True, storage_secret="TEMPSECRETKEY_THISWILLNOTBERUNONSERVERS")