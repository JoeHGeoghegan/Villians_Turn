# Library Imports
from nicegui import ui, app
import pandas as pd
### Local Imports
from functions.groups import groups_gathered_check
#from layout import create_layout
import containers.overview as overview

########## UI To Convert ##########
"""
                                                                        Memory - data block & cache
Logo
Tab/Sidebar/Menu screens
    "Overview"
        Welcome Message
        Turn Track (ref 60)
        Combat Interface (ref 88)
            Flavor Data Handling (ref 156)
    "Modifications"
        Add Person
        Remove Person/Team
        Change Initiatives
    "Settings"
        Turn Tracker Visuals
        Audit Settings
    "Import/Export"
        Importing
        Exporting
    "Rule Changes"
        Display markdown
    "Group Functions"
        "Assign Groups"
        "Move Group"
        "Move Person to Other Group"
        "Merge Groups"
        "Split Group"
        "Change Group Name"
DM View/Player View Toggles
"""
########## Global Variables ##########


########## UI Elements ##########
ui.image(".\\assets\Images\Villains_turn_logo.png")

@ui.page('/')
def main_page():
    # Layout with rows and columns
    with ui.row().classes('w-full items-center justify-between'):
        ui.image("Images/Villains_turn_logo.png")
        with ui.column():
            # Use labels for displaying state
            ui.label(f"Turn #: {ui.storage.page['turn_number']}").classes('text-xl')
            ui.label(f"Action #: {ui.storage.page['action_number']}").classes('text-xl')

    # Tabs
    with ui.tabs().classes('w-full') as tabs:
        ui.tab('Overview')
        ui.tab('Modifications')
        ui.tab('Settings')
        ui.tab('Import/Export')
        ui.tab('Rule Changes')
    
    with ui.tab_panels(tabs, value='Overview').classes('w-full'):
        with ui.tab_panel('Overview'):
            # This is where the main logic for the overview tab goes
            if ui.storage.page['turn_track'].empty:
                ui.label("Welcome! Add Characters in the Modifications tab or Import an existing Villain's Turn csv to get started!")
            elif not groups_gathered_check(ui.storage.page['turn_track']):
                ui.label("Groups are not gathered, move groups to desired order or reset initiative")
            else:
                # Turn tracking displays
                with ui.row().classes('w-full justify-between'):
                    with ui.column():
                        ui.label(f"{ui.storage.page['current_turn']}'s turn").classes('text-lg')
                        # Displaying names from the dataframe
                        current_group = ui.storage.page['turn_track'].loc[ui.storage.page['turn_track']['group']==ui.storage.page['current_turn']]
                        for name in current_group['name']:
                            ui.label(name)
                    
                    with ui.column():
                        next_turn = next_turn(ui.storage.page['turn_track'], ui.storage.page['current_turn'])
                        ui.label(f"{next_turn} is on deck").classes('text-lg')
                        on_deck_group = ui.storage.page['turn_track'].loc[ui.storage.page['turn_track']['group']==next_turn]
                        for name in on_deck_group['name']:
                            ui.label(name)

                    with ui.column():
                        # Buttons with explicit callbacks
                        def next_turn_action():
                            ui.storage.page['current_turn'] = next_turn(ui.storage.page['turn_track'], ui.storage.page['current_turn'])
                            ui.storage.page['turn_number'] += 1
                            main_page.update()

                        ui.button("Next Turn", on_click=next_turn_action)
                        # More buttons for previous turn, jump to turn, etc.
    #overview.create_content()

############ Run Loop ##########
if __name__ in {'__main__', '__mp_main__'}:
    ui.run()
