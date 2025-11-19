# Library Imports
import asyncio

from nicegui import ui, app

### Local Imports
import containers.ui_elements.character_editor as character_editor
import containers.left_sidebar as left_sidebar
import containers.overview as overview
import containers.right_hiding_sidebar as right_hiding_sidebar
import containers.welcome as welcome
from functions.groups import groups_gathered_check
from memory import init_mem, init_table, init_user, set_user_type

coding_priorities = "Character Info Editor"


# pages
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
    ui.dark_mode(True)
    ui.colors(
        primary='#4f000c',
        secondary='#711c00',
        accent='#2f4858'
    )
    with open('assets/css/style.txt', 'r', encoding='utf-8') as f:
        ui.add_head_html(f.read())

    # Main Page Layout
    with ui.header(elevated=True).classes('items-center justify-between'):
        # Display Logo
        ui.image('assets/Images/Villains_turn_logo.svg').style('max-width: 200px;')
        ui.markdown(f'''
                    Next Coding Priorities:
                    {coding_priorities}
                    ''')
        with ui.dropdown_button('Debug Menu', auto_close=True):
            ui.item('Clear Memory', on_click=lambda: (user.clear(), mem.clear(), init_mem(), main_container.refresh()))
            ui.item('Clear Table', on_click=lambda: (init_table(), main_container.refresh()))
            ui.item('Become a Host', on_click=lambda: (set_user_type("Host"), main_container.refresh()))
            ui.item('Become a Player', on_click=lambda: (set_user_type("Player"), main_container.refresh()))
            ui.item('Refresh Memory', on_click=lambda: (init_user(), init_mem(), main_container.refresh()))
        ui.button(on_click=lambda: right_drawer.toggle(), icon='menu').props('flat color=white')

    main_container()

    with ui.left_drawer(top_corner=True, bottom_corner=True):
        left_container()
    with ui.right_drawer(value=False) as right_drawer:
        right_container()

    # main_container() # Refreshable container for main content


@ui.refreshable
def main_container():
    print("~~ Refreshing Main Container ~~")
    # memory setup
    mem = app.storage.general
    user = app.storage.user
    with ui.column():
        if len(user['selectable_view']) > 0:
            if user['selectable_view'][0] == "markdown":
                print("Showing Markdown View")

                def back():
                    user['selectable_view'] = []
                    main_container.refresh()

                if user['selectable_view'][1][-len("csv_details.md"):] == "csv_details.md":
                    ui.button("Download Template CSV",
                              on_click=lambda: ui.download('assets/party_data/VilliansTurnTemplate.csv'))
                else:
                    ui.button('Back', on_click=lambda x: back())
                with open(user['selectable_view'][1], 'r') as md_file:
                    ui.markdown(md_file.read())
                ui.button('Back', on_click=lambda x: back())
            elif user['selectable_view'][0] == "character_editor":
                character_editor.create_content(main_container,left_container)
        # If no data, show welcome message relevant options
        elif all(cell is None for cell in mem['character_details'][0].values()):
            print("No Data - Showing Welcome")
            welcome.create_content(main_container)
        # If groups not yet gathered, show group gathering screen
        elif not groups_gathered_check(mem['character_details']):
            print("Groups not gathered - Showing Group Gather")
            welcome.create_group_gather(main_container,left_container)
        else:
            print("Showing Overview")
            overview.create_content(main_container,left_container)


@ui.refreshable
def left_container() -> None:
    left_sidebar.create_content(main_container, left_container)


@ui.refreshable
def right_container() -> None:
    right_hiding_sidebar.create_content(main_container, right_container)


############ Run Loop ##########
if __name__ in {'__main__', '__mp_main__'}:
    ui.run(host='0.0.0.0', port=55555, title="Villain's Turn", favicon="assets/Images/V_favicon.svg", reload=True,
           storage_secret="TEMP_SECRET_KEY_THIS_WILL_NOT_BE_RUN_ON_SERVERS")
