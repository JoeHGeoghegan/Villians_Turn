# Library Imports
from nicegui import ui, app
import pandas as pd
import asyncio
### Local Imports
from memory import init_mem
from functions.groups import groups_gathered_check
#from layout import create_layout
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
    mem = app.storage.tab
    # Initialize memory variables on first load
    if 'audit' not in mem:
        init_mem()

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
        ui.button(on_click=lambda: right_drawer.toggle(), icon='menu').props('flat color=white')
    with ui.left_drawer(top_corner=True, bottom_corner=True):
        left_sidebar.create_content(main_page)
    with ui.right_drawer(fixed=False).props('bordered') as right_drawer:
        right_hiding_sidebar.create_content(main_page)
    #with ui.footer():

    main_container() # Refreshable container for main content
    
@ui.refreshable
def main_container() -> None:
    # memory setup
    mem = app.storage.tab
    with ui.column():
     # If no data, show welcome message relevant options
        if len(mem['turn_track']) ==  0:
            welcome.create_content(main_container)
        else:
            overview.create_content(main_container)

############ Run Loop ##########
if __name__ in {'__main__', '__mp_main__'}:
    ui.run(title="Villain's Turn", reload=True)