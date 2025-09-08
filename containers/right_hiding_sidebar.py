# Library Imports
from nicegui import ui, app
import pandas as pd

def create_content(main_page:ui.refreshable):
    # memory setup
    mem = app.storage.tab
    def set_markdown_view(path):
        mem['markdown_view_path'] = path
        main_page.refresh()
    ui.button('View Rule Changes', on_click=lambda: set_markdown_view('assets\\data\\RuleChanges.md'))
    ui.button('View CSV Template Details', on_click=lambda: set_markdown_view('assets\\data\\csv_details.md'))
    
    ui.markdown('''
                ### Admin/Game Options
                * "Rule Changes"
                    * Option to disable the group functionality
                * "Settings"
                    * DM Screen/Player Screen Options (Multiple Windows?)
                    * Audit Settings
                ''')