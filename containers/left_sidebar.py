# Library Imports
from nicegui import ui, app
import pandas as pd

from functions.interface import set_user_type
from memory import init_mem

def create_content(page:ui.refreshable):
    # memory setup
    mem = app.storage.general
    user = app.storage.user
    with ui.dropdown_button('Debug Menu', auto_close=True):
        ui.item('Clear Memory', on_click=lambda: (user.clear(), init_mem(), page.refresh()))
        ui.item('Become a Host', on_click=lambda: (set_user_type("Host"), page.refresh()))
        ui.item('Become a Player', on_click=lambda: (set_user_type("Player"), page.refresh()))
    ui.markdown('''
                ### Always Present Options
                * "Modifications"
                    * Add Person
                    * Add File (opens submenu)
                        * "Import/Export"
                            * Importing
                            * Exporting
                    * Remove Person/Team (when not empty)
                    * Change Initiatives (when not empty)
                * "Manual Group Functions"
                    * "Assign Groups"
                    * "Move Group"
                    * "Move Person to Other Group"
                    * "Merge Groups"
                    * "Split Group"
                    * "Change Group Name"
                ''')