# Library Imports
from nicegui import ui, app
import asyncio
### Local Imports
from functions.basics import mem_df_use
from memory import init_mem, init_user
from functions.groups import groups_gathered_check
import containers.welcome as welcome
import containers.overview as overview
import containers.left_sidebar as left_sidebar
import containers.right_hiding_sidebar as right_hiding_sidebar

coding_priorities = "Group Functions"

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
    if 'type' not in user:
        init_user()
    ########## UI Elements ##########
    darkMode = ui.dark_mode(True)
    ui.colors(
        primary = '#4f000c',
        secondary = '#711c00',
        accent = '#2f4858'
    )
    with open('assets\\css\\style.txt', 'r', encoding='utf-8') as f:
        ui.add_head_html(f.read())

    # Main Page Layout
    with ui.header(elevated=True).classes('items-center justify-between'):
        # Display Logo
        ui.image('assets/Images/Villains_turn_logo.svg').style('max-width: 200px;')
        ui.markdown(f'''
                    Next Coding Priorities:
                    {coding_priorities}
                    ''')
        ui.button(on_click=lambda: right_drawer.toggle(), icon='menu').props('flat color=white')
    with ui.left_drawer(top_corner=True, bottom_corner=True):
        left_sidebar.create_content(main_container)
    with ui.right_drawer(value=False) as right_drawer:
        right_hiding_sidebar.create_content(main_container)
    #with ui.footer():

    main_container() # Refreshable container for main content
    
@ui.refreshable
def main_container() -> None:
    print("~~ Refreshing Main Container ~~")
    # memory setup
    mem = app.storage.general
    user = app.storage.user
    with ui.column():
        if len(user['markdown_view_path']) > 0:
            print("Showing Markdown View")
            def back():
                user['markdown_view_path'] = ''
                main_container.refresh()
            if user['markdown_view_path'][-len("csv_details.md"):] == "csv_details.md" :
                ui.button("Download Template CSV", on_click=lambda: ui.download('assets\\party_data\\VilliansTurnTemplate.csv'))
            else:
                ui.button('Back', on_click=lambda x: back())
            with open(user['markdown_view_path'], 'r') as md_file:
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
            print("Showing Overview")
            overview.create_content(main_container)

############ Run Loop ##########
if __name__ in {'__main__', '__mp_main__'}:
    ui.run(host='0.0.0.0',port=55555,title="Villain's Turn", favicon="assets\\Images\\V_favicon.svg", reload=True, storage_secret="TEMPSECRETKEY_THISWILLNOTBERUNONSERVERS")