from nicegui import app, ui

#local imports
from functions.game import turn_table_display

def game_list(user_type,highlight_rows):
    def list_creator(row):
        if (row['group'] == mem['current_turn'] and highlight_rows):
            item = ui.item(on_click=lambda: ui.notify(f'Selected Active {row["name"]}'))
            item.classes('w-full items-center highlighted-row')
        else:
            item = ui.item(on_click=lambda: ui.notify(f'Selected Inactive {row["name"]}'))
        with item.props('dense'):
            for col in cols:
                if col['name'] == "name":
                    with ui.item_section().props('no-wrap, side').classes(f'col-{col["name"]}'):
                        ui.item_label(row["name"])
                        ui.item_label(row["team"]).props('caption')
                elif col['name'] != "team":
                    with ui.item_section().props('no-wrap, side').classes(f'col-{col["name"]}'):
                        ui.item_label(row[col["name"]])
        return item
    
    mem = app.storage.general
    cols, rows = turn_table_display(user_type)
    with ui.list().style('width: fit-content;').props('bordered separator'):
        with ui.item().props('dense'):
            for col in cols:
                if col['name'] != "team" :
                    with ui.item_section().props('no-wrap, side').classes(f'col-{col["name"]}'):
                        ui.item_label(col['label']).classes('text-bold')
        ui.separator()
        for row in rows:
            list_creator(row)
    return


def set_user_type(role):
    print(f"Currently {app.storage.user["type"]} and setting to {role}")
    app.storage.user["type"] = role
    print(app.storage.user["type"])

def overview_table_row_style(row, group):
    if row["Group"] == group :
        return f'background-color: {ui.colors.accent};'