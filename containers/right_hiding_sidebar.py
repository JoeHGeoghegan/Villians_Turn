# Library Imports
from nicegui import ui, app
import pandas as pd

def create_content(main_page):
    # memory setup
    mem = app.storage.tab
    
    ui.markdown('''
                ### Admin/Game Options
                * "Rule Changes"
                    * Display markdown
                    * Option to disable the group functionality
                * "Settings"
                    * DM Screen/Player Screen Options (Multiple Windows?)
                    * Audit Settings
                ''')