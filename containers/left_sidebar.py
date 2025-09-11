# Library Imports
from nicegui import ui, app
import pandas as pd

def create_content(main_page):
    # memory setup
    mem = app.storage.general

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