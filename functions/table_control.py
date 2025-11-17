from nicegui import app, ui

from containers.left_sidebar import update_content as left_sidebar_update
# local imports
from containers.ui_combat import update_content as combat_interface_update
from functions.data import df_max_lengths_in_cols
from functions.game import turn_table_display


def game_list(user_type, highlight_rows, page: ui.refreshable):
    px_char_width = 9
    px_side_buffer = 7
    min_px_width = 60

    def list_creator(list_row):
        op_mode = "table_click"
        if list_row['group'] == mem['current_turn'] and highlight_rows:
            item = ui.item(on_click=lambda: (table_click_handler(list_row["name"], True, op_mode), page.refresh()))
            item.classes('w-full items-center highlighted-row')
        else:
            item = ui.item(on_click=lambda: (table_click_handler(list_row["name"], False, op_mode), page.refresh()))
        with item.props('dense'):
            for list_col in cols:
                if list_col['name'] == "name":
                    width = col_widths["name"] if col_widths["name"] > col_widths["team"] else col_widths["team"]
                    with ui.item_section().props('no-wrap, side').style(f'width: {width}px'):
                        ui.item_label(list_row["name"])  # .classes('font-ui-monospace')
                        ui.item_label(list_row["team"]).props('caption')
                elif list_col['name'] != "team":
                    with ui.item_section().props('no-wrap, side').style(f'width: {col_widths[list_col['name']]}px'):
                        ui.item_label(list_row[list_col["name"]])  # .classes('font-ui-monospace')
        return item

    mem = app.storage.general
    cols, rows, display_table = turn_table_display(user_type)
    base_col_widths = df_max_lengths_in_cols(display_table)

    # Calculate necessary pixel widths for columns
    col_widths = {}
    for col in base_col_widths.keys():
        col_width = (base_col_widths[col] * px_char_width) + px_side_buffer
        if col_width < min_px_width: col_width = min_px_width
        col_widths[col] = col_width

    with ui.list().style('width: fit-content;').props('bordered separator'):
        with ui.item().props('dense'):
            for col in cols:
                if col['name'] != "team":
                    with ui.item_section().props('no-wrap, side').style(f'width: {col_widths[col['name']]}px'):
                        ui.item_label(col['label']).classes('text-bold')
        ui.separator()
        for row in rows:
            list_creator(row)
    return


def table_click_handler(name, if_turn, op_mode):
    mem = app.storage.general
    user = app.storage.user
    if op_mode == "table_click":
        operation = mem["table_mode"]
    else:
        operation = op_mode
    print(f"Handling {operation} type operation for {name}. Turn: {if_turn}")
    if operation == 'actor':
        list_actor = list(mem["turn_data"]["actor"])
        list_actor_override = list(mem["turn_data"]["actor_override"])
        if not (name in list_actor) and (if_turn or (name in list_actor_override)):
            list_actor.append(name)
            mem["turn_data"]["actor"] = list_actor
        elif not (name in list_actor_override):
            ui.notify(f"It is not {name}'s turn. Press again to add anyway.")
            list_actor_override.append(name)
            mem["turn_data"]["actor_override"] = list_actor_override
        else:
            ui.notify(f"{name} is already selected as actor")
        combat_interface_update()
    elif operation == "remove_actor":
        list_actor = list(mem["turn_data"]["actor"])
        if name in list_actor:
            list_actor.remove(name)
            mem["turn_data"]["actor"] = list_actor
        else:
            ui.notify(f"{name} wasn't in the actor select...huh")
        combat_interface_update()
    elif operation == 'target':
        list_target = list(mem["turn_data"]["target"])
        if not (name in list_target):
            list_target.append(name)
            mem["turn_data"]["target"] = list_target
        else:
            ui.notify(f"{name} is already selected as target")
        combat_interface_update()
    elif operation == "remove_target":
        list_target = list(mem["turn_data"]["target"])
        if name in list_target:
            list_target.remove(name)
            mem["turn_data"]["target"] = list_target
        else:
            ui.notify(f"{name} wasn't in the target select...huh")
        combat_interface_update()
    elif operation == 'group':
        return
    elif operation == 'info':
        user['character_focus'] = name
        print(user['character_focus'])
        left_sidebar_update()
    print(mem["turn_data"])  # TODO DEBUG
