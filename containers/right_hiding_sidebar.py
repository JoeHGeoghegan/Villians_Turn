# Library Imports
from nicegui import ui, app
# Local Imports

def create_content(page:ui.refreshable):
    # memory setup
    mem = app.storage.general
    user = app.storage.user
    def set_markdown_view(path):
        user['markdown_view_path'] = path
        page.refresh()
    ui.button('View Rule Changes', on_click=lambda: set_markdown_view('assets\\texts\\RuleChanges.md'))
    ui.button('View CSV Template Details', on_click=lambda: set_markdown_view('assets\\texts\\csv_details.md'))
    ui.markdown('''
                ### Admin/Game Options
                * "Rule Changes"
                    * Option to disable the group functionality
                * "Settings"
                    * DM Screen/Player Screen Options (Multiple Windows?
                        * Pass DM Role
                        * Viewer Customizer
                    * Audit Settings
                ''')