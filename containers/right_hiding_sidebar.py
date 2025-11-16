# Library Imports
from nicegui import ui, app


# Local Imports

def create_content(page: ui.refreshable, self_page: ui.refreshable):
    def refresh():
        self_page.refresh()
        page.refresh()

    # memory setup
    user = app.storage.user

    def set_markdown_view(path):
        user['selectable_view'] = ["markdown", path]
        refresh()

    ui.button('View Rule Changes', on_click=lambda: set_markdown_view('assets/texts/RuleChanges.md'))
    ui.button('View CSV Template Details', on_click=lambda: set_markdown_view('assets/texts/csv_details.md'))
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
